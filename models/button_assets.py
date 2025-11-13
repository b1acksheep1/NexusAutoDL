"""Button assets model."""

from typing import Optional

from numpy import float32, uint8
from numpy.typing import NDArray
from pydantic import BaseModel


class ButtonAssets(BaseModel):
    """Container for button image assets and descriptors."""

    vortex_img: NDArray[uint8]
    vortex_new_img: Optional[NDArray[uint8]] = None
    web_img: NDArray[uint8]
    web_new_img: Optional[NDArray[uint8]] = None
    wabbajack_img: NDArray[uint8]
    click_img: NDArray[uint8]
    understood_img: NDArray[uint8]
    staging_img: NDArray[uint8]

    vortex_desc: Optional[NDArray[float32]] = None
    vortex_new_desc: Optional[NDArray[float32]] = None
    web_desc: Optional[NDArray[float32]] = None
    web_new_desc: Optional[NDArray[float32]] = None
    wabbajack_desc: Optional[NDArray[float32]] = None
    click_desc: Optional[NDArray[float32]] = None
    understood_desc: Optional[NDArray[float32]] = None
    staging_desc: Optional[NDArray[float32]] = None

    class Config:
        arbitrary_types_allowed = True
