"""Template metadata for button detection."""

from dataclasses import dataclass
from typing import Optional, Any

from numpy.typing import NDArray
from numpy import float32


@dataclass(frozen=True)
class TemplateCandidate:
    """Descriptor metadata for drawing debug info."""

    desc: NDArray[float32]
    width: int
    height: int
    keypoints: Optional[Any] = None  # list[cv2.KeyPoint], but avoid cv2 import here
