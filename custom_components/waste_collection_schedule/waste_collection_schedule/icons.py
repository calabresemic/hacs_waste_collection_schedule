"""Canonical Material Design Icon (MDI) names for waste-collection types.

The source maps its waste-type strings to members of :class:`Icons` rather than
raw ``"mdi:..."`` strings. Upstream defined 23 categories to cover ~950 sources;
this fork keeps the four Republic Services actually produces.

Because :class:`Icons` is a :class:`~enum.StrEnum`, members are also strings::

    >>> Icons.GENERAL_WASTE == "mdi:trash-can"
    True
"""

from enum import StrEnum


class Icons(StrEnum):
    """Canonical MDI icons for waste-collection categories."""

    # General mixed/landfill waste
    GENERAL_WASTE = "mdi:trash-can"

    # Mixed dry recycling
    RECYCLING = "mdi:recycle"

    # Organic waste (yard/green waste for this provider)
    ORGANIC = "mdi:leaf"

    # Bulky / oversized items
    BULKY = "mdi:sofa"
