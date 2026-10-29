"""Pydantic request/response models."""
from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field, field_validator

AspectRatio = Literal["16:9", "9:16"]
RESOLUTIONS = {"16:9": (1920, 1080), "9:16": (1080, 1920)}


class NarrationSettings(BaseModel):
    mode: Literal["none", "user_audio", "generate"] = "none"
    voice: str | None = None


class CaptionSettings(BaseModel):
    enabled: bool = False
    font_size: int = Field(default=38, ge=12, le=200)


class ProjectSettings(BaseModel):
    aspect_ratio: AspectRatio = "16:9"
    fps: int = Field(default=30, ge=1, le=120)
    target_duration_s: int = Field(default=30, ge=5, le=1800)
    visual_style: str = "clean-technical"
    approval_mode: Literal["manual", "automatic"] = "manual"
    narration: NarrationSettings = NarrationSettings()
    captions: CaptionSettings = CaptionSettings()
    topic: str | None = None
    reference_description: str | None = None
    ai_model: str | None = None
    niche_category: str | None = None


class ProjectCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    script: str = Field(default="", max_length=200_000)
    settings: ProjectSettings = ProjectSettings()

    @field_validator("title")
    @classmethod
    def _strip(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("title must not be blank")
        return v


class ScriptUpdate(BaseModel):
    script: str = Field(max_length=200_000)
