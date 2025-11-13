"""Browser type enumeration."""

from enum import Enum


class BrowserType(str, Enum):
    """Supported browser types."""

    CHROME = "chrome"
    FIREFOX = "firefox"
