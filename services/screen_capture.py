"""
Screen capture and coordinate conversion utilities.
"""
from loguru import logger

import cv2
import mss
import numpy as np
import numpy.typing as npt

from models import Monitor


class ScreenCapture:
    """Handles screen capture and coordinate conversions."""

    def __init__(self, monitors: list[Monitor], force_primary: bool = False) -> None:
        """
        Initialize screen capture.

        Args:
            monitors: List of available monitors
            force_primary: Only use primary monitor
        """
        if not monitors:
            raise ValueError("No monitors provided to ScreenCapture")

        self.monitors: list[Monitor] = sorted(monitors, key=lambda m: (m.x, m.y))
        self.screen: mss.mss = mss.mss()
        self.screen_monitors: list[dict[str, int]] = self.screen.monitors
        self.force_primary = force_primary

        self.v_monitor: dict[str, int] = self._determine_capture_region()
        self.min_x: int = self.v_monitor["left"]
        self.min_y: int = self.v_monitor["top"]
        self.virtual_width: int = self.v_monitor["width"]
        self.virtual_height: int = self.v_monitor["height"]
        
        logger.info(
            f"Initialized screen capture with {len(self.monitors)} app monitors "
            f"and capturing region {self.v_monitor}"
        )

    def _determine_capture_region(self) -> dict[str, int]:
        """Select the monitor region to capture."""
        if self.force_primary or len(self.screen_monitors) <= 1:
            primary: Monitor = self.monitors[0]
            return {
                "top": primary.y,
                "left": primary.x,
                "width": primary.width,
                "height": primary.height,
            }

        # screen.monitors[0] is already the full virtual desktop
        full_virtual: dict[str, int] = self.screen_monitors[0]
        return {
            "top": full_virtual["top"],
            "left": full_virtual["left"],
            "width": full_virtual["width"],
            "height": full_virtual["height"],
        }

    def capture(self) -> npt.NDArray[np.uint8]:
        """
        Capture current screen.

        Returns:
            RGB image array
        """
        img: npt.NDArray[np.uint8] = np.array(self.screen.grab(self.v_monitor))
        logger.debug("Screen captured")
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    def img_coords_to_monitor_coords(self, x: int, y: int) -> tuple[int, int]:
        """
        Convert image coordinates to monitor coordinates.

        Args:
            x: Image X coordinate
            y: Image Y coordinate

        Returns:
            Monitor X and Y coordinates
        """
        return x + self.min_x, y + self.min_y

    def monitor_coords_to_img_coords(self, x: int, y: int) -> tuple[int, int]:
        """
        Convert monitor coordinates to image coordinates.

        Args:
            x: Monitor X coordinate
            y: Monitor Y coordinate

        Returns:
            Image X and Y coordinates
        """
        return x - self.min_x, y - self.min_y

    @property
    def capture_width(self) -> int:
        """Get capture area width."""
        return self.v_monitor["width"]

    @property
    def capture_height(self) -> int:
        """Get capture area height."""
        return self.v_monitor["height"]
