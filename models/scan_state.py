"""Scan state enumeration."""
from enum import Enum


class ScanState(str, Enum):
    """Scanner state machine states."""
    IDLE = "idle"
    WAITING_FOR_VORTEX = "waiting_for_vortex"
    VORTEX_CLICKED = "vortex_clicked"
    WAITING_FOR_WEB = "waiting_for_web"
    WEB_CLICKED = "web_clicked"
    HANDLING_POPUP = "handling_popup"
    ERROR = "error"
