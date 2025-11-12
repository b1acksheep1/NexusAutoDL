"""
Debug frame recording utilities.
"""
from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import numpy.typing as npt
from loguru import logger

from models import DetectionResult

DEFAULT_DEBUG_WIDTH = 200
DEFAULT_DEBUG_HEIGHT = 80


class DebugRecorder:
    """Writes annotated detection frames for troubleshooting."""

    def __init__(self, output_dir: Path | None) -> None:
        self.output_dir = output_dir
        if self.output_dir:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Debug frames will be saved to {self.output_dir}")

    def record(
        self,
        image: npt.NDArray[np.uint8],
        detection: DetectionResult,
        iteration: int,
        label: str,
    ) -> None:
        """Save an annotated frame if debug directory configured."""
        if not self.output_dir:
            return

        annotated = image.copy()
        self._draw_detection_box(annotated, detection, label)
        filename = f"frame_{iteration:06d}_{label}.png"
        output_path = self.output_dir / filename
        cv2.imwrite(
            str(output_path),
            cv2.cvtColor(annotated, cv2.COLOR_RGB2BGR),
        )
        logger.debug(f"Wrote debug frame to {output_path}")

    def _draw_detection_box(
        self,
        image: npt.NDArray[np.uint8],
        detection: DetectionResult,
        label: str,
    ) -> None:
        """Draw a bounding box and caption for a detection."""
        img_height, img_width = image.shape[:2]
        box_width = detection.template_width or DEFAULT_DEBUG_WIDTH
        box_height = detection.template_height or DEFAULT_DEBUG_HEIGHT
        half_w = box_width // 2
        half_h = box_height // 2

        x1 = max(int(detection.x - half_w), 0)
        y1 = max(int(detection.y - half_h), 0)
        x2 = min(int(detection.x + half_w), img_width - 1)
        y2 = min(int(detection.y + half_h), img_height - 1)

        color = (0, 255, 0)
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
        text = (
            f"{label} | {detection.button_type.value} | "
            f"conf={detection.confidence:.2f} | matches={detection.num_matches}"
        )
        text_pos = (x1, max(15, y1 - 10))
        cv2.putText(
            image,
            text,
            text_pos,
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            color,
            1,
            cv2.LINE_AA,
        )
