"""Bounding box model."""
from pydantic import BaseModel, field_validator


class BoundingBox(BaseModel):
    """Bounding box coordinates."""
    x1: int
    y1: int
    x2: int
    y2: int

    @field_validator('x2')
    @classmethod
    def x2_must_be_greater_than_x1(cls, v: int, info) -> int:
        if 'x1' in info.data and v <= info.data['x1']:
            raise ValueError('x2 must be greater than x1')
        return v

    @field_validator('y2')
    @classmethod
    def y2_must_be_greater_than_y1(cls, v: int, info) -> int:
        if 'y1' in info.data and v <= info.data['y1']:
            raise ValueError('y2 must be greater than y1')
        return v

    @property
    def width(self) -> int:
        return self.x2 - self.x1

    @property
    def height(self) -> int:
        return self.y2 - self.y1

    def pad(self, factor: float) -> 'BoundingBox':
        """Pad bbox by factor (0.0-1.0)."""
        w_pad = int(self.width * factor)
        h_pad = int(self.height * factor)
        return BoundingBox(
            x1=self.x1 + w_pad,
            y1=self.y1 + h_pad,
            x2=self.x2 - w_pad,
            y2=self.y2 - h_pad
        )

    class Config:
        frozen = True
