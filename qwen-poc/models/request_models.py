from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
import os

class GenerateImageRequest(BaseModel):
    images: List[str] = Field(..., description="List of input images: local paths or public HTTP(S) URLs (1 to 3 images allowed).")
    prompt: str = Field(..., description="Text prompt for the image generation.")
    negative_prompt: Optional[str] = Field(None, description="Negative prompt.")
    n: Optional[int] = Field(1, ge=1, le=4, description="Number of output images to generate.")
    size: Optional[str] = Field("1024*1024", description="Size of the output image (width*height).")
    seed: Optional[int] = Field(None, description="Seed for reproducible generation.")

    @field_validator('images')
    def validate_images(cls, v):
        if not (1 <= len(v) <= 3):
            raise ValueError('Exactly 1 to 3 images must be provided.')
        for img in v:
            is_url = img.startswith("http://") or img.startswith("https://")
            if not is_url and not os.path.exists(img):
                raise ValueError(f"Image file does not exist: {img}")
        return v
