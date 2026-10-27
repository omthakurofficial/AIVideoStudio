"""Scene-relative -> video-timeline mapping and audio-based timing revision."""
from __future__ import annotations
from .schema import Storyboard


def scene_starts(sb: Storyboard) -> dict[str, float]:
    t, out = 0.0, {}
    for s in sb.scenes:
        out[s.id] = round(t, 3)
        t += s.duration
    return out


def total_duration(sb: Storyboard) -> float:
    return round(sum(s.duration for s in sb.scenes), 3)


def revise_durations_from_audio(sb: Storyboard, audio_seconds: dict[str, float], tail_padding: float = 0.4) -> Storyboard:
    """Set each scene's real narration length (+ small tail) as its duration. Animations that no longer fit are clamped
    by re-validation: callers must handle ValueError by re-planning timing for that scene."""
    data = sb.model_dump()
    for sc in data["scenes"]:
        a = audio_seconds.get(sc["id"])
        if a is not None:
            sc["timing"]["narration_audio_s"] = round(a + tail_padding, 3)
            sc["timing"]["revised_from_audio"] = True
    return Storyboard.model_validate(data)
