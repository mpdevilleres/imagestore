from enum import Enum

from pydantic import BaseModel, Field, model_validator


class ColorMap(Enum):
    VIRIDIS = "viridis"
    PLASMA = "plasma"
    INFERNO = "inferno"
    MAGMA = "magma"


class ImageFilterParams(BaseModel):
    depth_min: float = Field(..., ge=0, le=10000)
    depth_max: float = Field(..., ge=0, le=10000)
    colormap: ColorMap = Field(...)

    @model_validator(mode="after")
    def check_passwords_match(self):
        if self.depth_min <= self.depth_max:
            return self
        raise ValueError("depth_min must be less than or equal to depth_max")
