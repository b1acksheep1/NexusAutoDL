"""Application configuration model."""

from typing import Optional

from pydantic import BaseModel, Field

from models.browser_type import BrowserType


class AppConfig(BaseModel):
    """Application configuration."""

    browser: Optional[BrowserType] = None
    vortex: bool = False
    verbose: bool = False
    legacy: bool = False
    debug_frame_dir: Optional[str] = None
    force_primary: bool = False
    window_title: Optional[str] = None

    # Detection parameters
    min_matches: int = Field(default=8, ge=1)
    ratio_threshold: float = Field(default=0.75, ge=0.0, le=1.0)
    click_delay: float = Field(default=2.0, ge=0.1)
    retry_delay: float = Field(default=1.0, ge=0.1)
    wabbajack_retry_limit: int = Field(default=5, ge=1)
