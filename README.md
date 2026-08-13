# Waste Collection Schedule — Republic Services

A stripped-down fork of [mampfes/hacs_waste_collection_schedule](https://github.com/mampfes/hacs_waste_collection_schedule)
that keeps only the **Republic Services** source. Everything else — the other
~950 community sources, their documentation, the shared scrapers, the wizards,
the YAML configuration path and the upstream maintenance tooling — has been
removed, so this repository stops changing every time an unrelated municipality
changes its website.

The Home Assistant integration keeps the upstream domain
(`waste_collection_schedule`), entity IDs and config-entry format, so an
existing installation keeps working after switching to this fork.

## Installation

Add this repository to HACS as a custom repository (category: Integration),
install it, and restart Home Assistant. Then add the integration under
**Settings → Devices & Services → Add Integration → Waste Collection Schedule**.

Because there is only one source, the country and provider pickers are skipped
and configuration starts directly at the source arguments.

## Configuration

| Option | Required | Description |
| --- | --- | --- |
| `street_address` | yes | The service address as Republic Services knows it, e.g. `117 Roxie Ln, Georgetown, KY 40324`. |
| `method` | no (default `1`) | `1` reports the waste type names returned by the API. `2` maps them onto `Solid Waste`, `Recycle`, `Yard Waste` and `Bulk Waste`. |

Sensors, calendars, per-type customisation, dedicated calendars and the
`waste_collection_schedule.fetch_data` service all behave as they do upstream.

## How the source works

`custom_components/waste_collection_schedule/waste_collection_schedule/source/republicservices_com.py`
calls three Republic Services endpoints:

1. `GET /api/v1/addresses` — resolves the street address to an `addressHash`
   plus latitude/longitude.
2. `GET /api/v1/publicPickup` — returns the container/service records. Records
   with a weekly or fortnightly period are projected forward from their seed
   date for 182 days; other records use the `nextServiceDays` list verbatim.
3. `POST /api/v2/holidaySchedules/schedule` — returns holidays for the lines of
   business the address actually has containers for. Impacted pickups are then
   adjusted the way the website does it: `Not Running` cancels the collection,
   `Service Moved` jumps to the supplied alternate date, and `One Day Delay`
   slides that collection and every later same-week collection (Sunday-start
   week) forward one day.

## Repository layout

```
custom_components/waste_collection_schedule/
├── __init__.py, init_ui.py, config_flow.py   # HA integration + UI config flow
├── calendar.py, sensor.py, service.py        # entities and the fetch_data service
├── wcs_coordinator.py                        # update coordinator
├── sources.json, source_metadata.json        # the single source entry + its help text
├── translations/en.json                      # English UI strings only
└── waste_collection_schedule/
    ├── collection.py, collection_aggregator.py, icons.py, exceptions.py
    ├── source_shell.py                       # source wrapper: customize, day offset, dedup
    ├── service/DeviceKeyStore.py             # HA Store helper used by init_ui
    └── source/republicservices_com.py        # the source itself
tests/                                        # source_shell + coordinator tests
```

## Keeping up with upstream

The `upstream` remote still points at mampfes/hacs_waste_collection_schedule. To
pull in a fix to the shared integration layer (not the sources), cherry-pick it:

```bash
git fetch upstream
git log upstream/master --oneline -- custom_components/waste_collection_schedule/*.py
git cherry-pick <sha>
```

A straight merge is not advisable — it would restore every deleted file.

## Licence

MIT, inherited from upstream. See [LICENSE](LICENSE).
