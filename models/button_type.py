"""Button type enumeration."""

from enum import Enum


class ButtonType(str, Enum):
    """Types of buttons to detect."""

    VORTEX = "vortex"
    WEBSITE = "website"
    WABBAJACK = "wabbajack"
    CLICK = "click"
    UNDERSTOOD = "understood"
    STAGING = "staging"
