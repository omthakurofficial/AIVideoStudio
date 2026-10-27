"""FFprobe/FFmpeg helpers: verified facts about media files, and deterministic frame checks."""
from __future__ import annotations
import json, subprocess
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path
from .mcp_client import EngineError


@dataclass
class VideoFacts:
    width: int; height: int; fps: float; duration: float; frames: int | None
    has_audio: bool; audio_duration: float | None; video_codec: str; audio_codec: str | None


def probe(path: Path, ffprobe: str = "ffprobe") -> VideoFacts:
    if not Path(path).is_file() or Path(path).stat().st_size == 0:
        raise EngineError(f"Expected output file is missing or empty: {path}")
    r = subprocess.run([ffprobe, "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)], capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        raise EngineError(f"ffprobe could not read {path}: {r.stderr.strip()[:300]}")
    d = json.loads(r.stdout)
    v = next((s for s in d["streams"] if s["codec_type"] == "video"), None)
    a = next((s for s in d["streams"] if s["codec_type"] == "audio"), None)
    if not v:
        raise EngineError(f"{path} has no video stream.")
    fmt_dur = float(d.get("format", {}).get("duration", 0) or 0)
    return VideoFacts(int(v["width"]), int(v["height"]), float(Fraction(v["r_frame_rate"])), float(v.get("duration") or fmt_dur),
                      int(v["nb_frames"]) if v.get("nb_frames", "").isdigit() else None, a is not None,
                      float(a["duration"]) if a and a.get("duration") else None, v["codec_name"], a["codec_name"] if a else None)


def verify_video(path: Path, width: int, height: int, fps: float, duration: float, ffprobe: str = "ffprobe",
                 expect_audio: bool | None = None, tol_frames: float = 1.5) -> VideoFacts:
    """Raises EngineError describing every mismatch between the file and the plan."""
    f = probe(path, ffprobe)
    bad = []
    if (f.width, f.height) != (width, height): bad.append(f"resolution {f.width}x{f.height} != planned {width}x{height}")
    if abs(f.fps - fps) > 0.01: bad.append(f"frame rate {f.fps:.3f} != planned {fps}")
    if abs(f.duration - duration) > tol_frames / fps: bad.append(f"duration {f.duration:.3f}s != planned {duration:.3f}s")
    if expect_audio is not None and f.has_audio != expect_audio: bad.append("audio stream " + ("missing" if expect_audio else "unexpectedly present"))
    if bad:
        raise EngineError(f"Output {Path(path).name} does not match the plan: " + "; ".join(bad))
    return f


def extract_frame(video: Path, t: float, out_png: Path, ffmpeg: str = "ffmpeg") -> Path:
    out_png.parent.mkdir(parents=True, exist_ok=True)
    r = subprocess.run([ffmpeg, "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", str(video), "-frames:v", "1", str(out_png)], capture_output=True, text=True, timeout=60)
    if r.returncode != 0 or not out_png.is_file():
        raise EngineError(f"Could not extract frame at {t:.2f}s from {video}: {r.stderr.strip()[:200]}")
    return out_png


@dataclass
class FrameStats:
    t: float; stddev: float; nonbackground_fraction: float


def frame_stats(png: Path, t: float = 0.0) -> FrameStats:
    import numpy as np
    from PIL import Image
    a = np.asarray(Image.open(png).convert("RGB"), dtype=np.float32)
    bg = np.median(a.reshape(-1, 3), axis=0)
    diff = np.abs(a - bg).sum(axis=2)
    return FrameStats(t, float(a.std()), float((diff > 40).mean()))


def frames_differ(a: Path, b: Path) -> float:
    import numpy as np
    from PIL import Image
    x = np.asarray(Image.open(a).convert("RGB"), dtype=np.float32); y = np.asarray(Image.open(b).convert("RGB"), dtype=np.float32)
    return float(np.abs(x - y).mean())
