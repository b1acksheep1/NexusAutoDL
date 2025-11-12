"""Detection result model."""
from typing import Optional

from pydantic import BaseModel, Field

from models.button_type import ButtonType


class DetectionResult(BaseModel):
    """Result of button detection."""
    button_type: ButtonType
    x: int
    y: int
    confidence: float = Field(ge=0.0, le=1.0)
    num_matches: int = Field(ge=0)
    template_width: Optional[int] = Field(default=None, ge=1)
    template_height: Optional[int] = Field(default=None, ge=1)

    class Config:
        frozen = True
