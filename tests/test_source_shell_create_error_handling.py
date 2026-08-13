# Make the core library importable as `waste_collection_schedule`. Import the
# stdlib modules the component shadows (calendar) before extending sys.path.
import calendar  # noqa: F401
import os
import sys

sys.path.append(
    os.path.join(
        os.path.dirname(__file__), "../custom_components/waste_collection_schedule"
    )
)

from waste_collection_schedule.source_shell import SourceShell

SOURCE = "republicservices_com"


def test_create_returns_none_and_logs_on_missing_source(caplog):
    """A source that no longer exists must be logged and skipped, not raised."""
    shell = SourceShell.create(
        source_name="a_source_that_does_not_exist",
        customize={},
        source_args={},
    )

    assert shell is None
    assert any(
        "source not found: a_source_that_does_not_exist" in record.message
        for record in caplog.records
    )


def test_create_returns_none_and_logs_on_unexpected_kwarg(caplog):
    """A stale/invalid config (e.g. renamed/removed source argument, or a
    'customize' block accidentally nested under 'args') must not raise and
    crash the whole integration setup. It should be logged and skipped."""
    shell = SourceShell.create(
        source_name=SOURCE,
        customize={},
        source_args={"this_is_not_a_real_argument": "value"},
    )

    assert shell is None
    assert any(
        f"error creating source {SOURCE}" in record.message for record in caplog.records
    )


def test_create_succeeds_with_valid_args():
    """Sanity check: valid arguments still create a working shell.

    `create` only constructs the source, it does not fetch, so this stays
    offline.
    """
    shell = SourceShell.create(
        source_name=SOURCE,
        customize={},
        source_args={"street_address": "117 Roxie Ln, Georgetown, KY 40324"},
    )

    assert shell is not None
    assert shell.title == "Republic Services"
