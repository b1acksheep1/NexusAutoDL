"""Button assets model."""
from typing import Optional

import numpy as np
import numpy.typing as npt
from pydantic import BaseModel


class ButtonAssets(BaseModel):
    """Container for button image assets and descriptors."""
    vortex_img: npt.NDArray[np.uint8]
    vortex_new_img: Optional[npt.NDArray[np.uint8]] = None
    web_img: npt.NDArray[np.uint8]
    web_new_img: Optional[npt.NDArray[np.uint8]] = None
    wabbajack_img: npt.NDArray[np.uint8]
    click_img: npt.NDArray[np.uint8]
    understood_img: npt.NDArray[np.uint8]
    staging_img: npt.NDArray[np.uint8]

    vortex_desc: Optional[npt.NDArray[np.float32]] = None
    vortex_new_desc: Optional[npt.NDArray[np.float32]] = None
    web_desc: Optional[npt.NDArray[np.float32]] = None
    web_new_desc: Optional[npt.NDArray[np.float32]] = None
    wabbajack_desc: Optional[npt.NDArray[np.float32]] = None
    click_desc: Optional[npt.NDArray[np.float32]] = None
    understood_desc: Optional[npt.NDArray[np.float32]] = None
    staging_desc: Optional[npt.NDArray[np.float32]] = None

    class Config:
        arbitrary_types_allowed = True
