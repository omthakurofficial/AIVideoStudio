"""Provider abstraction. Providers must not assume other providers' request formats or capabilities."""
from __future__ import annotations
import json, os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol
from ..config import REPO_ROOT


class ProviderError(Exception):
    """Raised with a user-actionable message (never contains secrets)."""
    def __init__(self, message: str, retryable: bool = False):
        super().__init__(message)
        self.retryable = retryable


@dataclass
class ModelSpec:
    provider: str
    model_id: str
    structured_mode: str = "tool"
    max_tokens: int = 4000
    temperature: float = 0.3


@dataclass
class StructuredResult:
    data: dict
    model_id: str
    input_tokens: int = 0
    output_tokens: int = 0
    latency_s: float = 0.0
    raw_stop_reason: str = ""
    extra: dict[str, Any] = field(default_factory=dict)


class LLMProvider(Protocol):
    name: str
    def generate_structured(self, spec: ModelSpec, system: str, messages: list[dict], schema: dict, tool_name: str,
                            tool_description: str) -> StructuredResult: ...
    def generate_text(self, spec: ModelSpec, system: str, prompt: str) -> tuple[str, StructuredResult]: ...


def load_config(path: Path | None = None) -> dict:
    return json.loads((path or REPO_ROOT / "config" / "models.json").read_text(encoding="utf-8"))


def load_model_specs(path: Path | None = None) -> dict[str, ModelSpec]:
    cfg = load_config(path)
    out = {}
    for task, d in cfg["tasks"].items():
        d = dict(d)
        d["model_id"] = os.environ.get(f"AIVS_MODEL_{task.upper()}", d["model_id"])
        out[task] = ModelSpec(**d)
    return out


def get_provider(name: str, region: str = "") -> LLMProvider:
    if name == "bedrock":
        from .bedrock import BedrockProvider
        return BedrockProvider(region)
    raise ProviderError(f"Unknown AI provider '{name}'. Supported: bedrock.")
