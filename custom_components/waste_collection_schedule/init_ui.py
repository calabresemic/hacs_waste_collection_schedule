"""Config flow setup logic."""

import asyncio
import importlib
import logging
from typing import Any

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryError

from .service import get_fetch_all_service
from .waste_collection_schedule.service.DeviceKeyStore import (
    initialize_device_key_store,
)
from .wcs_coordinator import WCSCoordinator

from . import const  # type: ignore # isort:skip
from .waste_collection_schedule import SourceShell, Customize  # type: ignore # isort:skip

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["calendar", "sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up component from a config entry, entry contains data from config entry database."""
    options = entry.options
    _LOGGER.debug(
        "Setting up entry %s, with data %s and options %s",
        entry.entry_id,
        entry.data,
        options,
    )

    # Initialize and load device key store
    device_store = initialize_device_key_store(hass)
    await device_store.async_load()

    customize_dicts: dict[str, dict[str, Any]] = options.get(const.CONF_CUSTOMIZE, {})

    customize: dict[str, Customize] = {}
    for waste_type, c in customize_dicts.items():
        customize[waste_type] = Customize(
            waste_type=waste_type,
            alias=c.get(const.CONF_ALIAS),
            show=c.get(const.CONF_SHOW, True),
            icon=c.get(const.CONF_ICON),
            picture=c.get(const.CONF_PICTURE),
            use_dedicated_calendar=c.get(const.CONF_USE_DEDICATED_CALENDAR, False),
            dedicated_calendar_title=c.get(const.CONF_DEDICATED_CALENDAR_TITLE, False),
        )

    shell = await hass.async_add_executor_job(
        SourceShell.create,
        entry.data[const.CONF_SOURCE_NAME],
        customize,
        entry.data[const.CONF_SOURCE_ARGS],
        options.get(const.CONF_SOURCE_CALENDAR_TITLE),
        options.get(const.CONF_DAY_OFFSET, const.CONF_DAY_OFFSET_DEFAULT),
        options.get(const.CONF_IGNORE_DUPLICATES, const.CONF_IGNORE_DUPLICATES_DEFAULT),
    )

    if shell is None:
        raise ConfigEntryError(
            f"Failed to set up source '{entry.data[const.CONF_SOURCE_NAME]}'. "
            "This is usually caused by a stale/invalid configuration, e.g. "
            "after the source's arguments changed in an update. Please "
            "reconfigure this integration entry. See the Home Assistant logs "
            "for details."
        )

    coordinator = WCSCoordinator(
        hass,
        source_shell=shell,
        separator=options.get(const.CONF_SEPARATOR, const.CONF_SEPARATOR_DEFAULT),
        fetch_time=cv.time(
            options.get(const.CONF_FETCH_TIME, const.CONF_FETCH_TIME_DEFAULT)
        ),
        fetch_interval_days=options.get(
            const.CONF_FETCH_INTERVAL_DAYS, const.CONF_FETCH_INTERVAL_DAYS_DEFAULT
        ),
        random_fetch_time_offset=options.get(
            const.CONF_RANDOM_FETCH_TIME_OFFSET,
            const.CONF_RANDOM_FETCH_TIME_OFFSET_DEFAULT,
        ),
        day_switch_time=cv.time(
            options.get(const.CONF_DAY_SWITCH_TIME, const.CONF_DAY_SWITCH_TIME_DEFAULT)
        ),
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(const.DOMAIN, {})[entry.entry_id] = coordinator

    # Pre-import platforms in parallel to avoid blocking I/O in the event loop
    await asyncio.gather(
        *[
            hass.async_add_executor_job(
                importlib.import_module,
                f"custom_components.waste_collection_schedule.{platform}",
            )
            for platform in PLATFORMS
        ]
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(async_update_listener))

    # Register new Service fetch_data
    hass.services.async_register(
        const.DOMAIN, "fetch_data", get_fetch_all_service(hass), schema=vol.Schema({})
    )

    return True


async def async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    # Reload this instance
    await hass.config_entries.async_reload(entry.entry_id)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Migrate a config entry to the current schema.

    Upstream carried migrations for every schema bump back to version 1, almost
    all of them renaming or re-arguing sources this fork no longer ships. They
    have all been dropped. Entries created by this fork are always written at
    the current version, so there is nothing left to migrate - this only guards
    against an entry from a different version showing up.
    """
    version = config_entry.version
    minor = config_entry.minor_version

    if version == const.CONFIG_VERSION and minor == const.CONFIG_MINOR_VERSION:
        return True

    if version > const.CONFIG_VERSION or (
        version == const.CONFIG_VERSION and minor > const.CONFIG_MINOR_VERSION
    ):
        _LOGGER.error(
            "Config entry schema %s.%s is newer than this integration supports "
            "(%s.%s). Downgrade is not possible - update the integration.",
            version,
            minor,
            const.CONFIG_VERSION,
            const.CONFIG_MINOR_VERSION,
        )
        return False

    _LOGGER.error(
        "Config entry schema %s.%s predates this fork (%s.%s) and its migration "
        "path was removed along with the other sources. Delete the integration "
        "entry and add it again.",
        version,
        minor,
        const.CONFIG_VERSION,
        const.CONFIG_MINOR_VERSION,
    )
    return False
