"""FilmCraft video assembly adapter + authoritative TimelineManifest + FFmpeg subtitle burn-in fallback.

Verified capabilities (FilmCraft v0.13.0):
  * Headless MCP (`filmcraft-cli mcp`) and batch runner (`filmcraft-cli run`) share the 710-command registry.
  * Verified working: file.newProject, file.newSequence, file.import, timeline.place (V1/A1 with seconds/duration),
    captions.newTrack, captions.add, file.saveAs (.fcproj), file.exportMedia (h264 MP4 with AAC audio).
  * Documented limitation: FilmCraft's caption track is stored in the project (.fcproj) and can be exported as SRT,
    but `file.exportMedia` does NOT burn captions into the rendered video frames. When `burn_captions=True`, this
    adapter exports an SRT sidecar and runs a deterministic FFmpeg `subtitles` filter pass to burn captions in.
"""
from __future__ import annotations
import json, logging, subprocess, tempfile, time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field
from .mcp_client import MCPClient, EngineError
from .media import verify_video, probe, VideoFacts

log = logging.getLogger("aivs.filmcraft")

REQUIRED_TOOLS = {"command_batch", "command_list", "command_run", "doc_inspect", "media_import", "project_inspect", "sequence_inspect"}
REQUIRED_COMMANDS = {"file.newProject", "file.newSequence", "file.import", "timeline.place", "captions.newTrack", "captions.add", "file.saveAs", "file.exportMedia"}


class _M(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ClipPlacement(_M):
    scene_id: str
    source_path: str
    track: str = "V1"
    start_s: float = Field(ge=0)
    duration_s: float = Field(gt=0)
    source_in_s: float = Field(default=0.0, ge=0)
    include_audio: bool = False
    transition_in: Literal["cut", "fade", "dissolve", "wipe", "slide"] = "cut"
    transition_duration_s: float = Field(default=0.0, ge=0)


class AudioPlacement(_M):
    id: str
    source_path: str
    track: str = "A1"
    start_s: float = Field(ge=0)
    duration_s: float = Field(gt=0)


class CaptionEntry(_M):
    index: int = Field(ge=1)
    start_s: float = Field(ge=0)
    end_s: float = Field(gt=0)
    text: str = Field(min_length=1, max_length=200)


class TimelineManifest(_M):
    """Authoritative assembly plan saved in assembly/timeline_manifest.json."""
    version: Literal[1] = 1
    project_id: str
    title: str
    width: int = Field(ge=64, le=7680)
    height: int = Field(ge=64, le=7680)
    fps: float = Field(gt=0, le=120)
    sample_rate: int = 48000
    clips: list[ClipPlacement] = Field(min_length=1)
    audio_clips: list[AudioPlacement] = Field(default_factory=list)
    captions: list[CaptionEntry] = Field(default_factory=list)
    burn_captions: bool = False
    caption_font_size: int = 42

    @property
    def total_duration_s(self) -> float:
        return round(max((c.start_s + c.duration_s for c in self.clips), default=0.0), 3)


@dataclass
class Capabilities:
    version: str
    tools: list[str]
    missing_tools: list[str] = field(default_factory=list)
    missing_commands: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.missing_tools and not self.missing_commands


@dataclass
class AssemblyResult:
    output_mp4: Path
    project_fcproj: Path
    manifest_path: Path
    srt_path: Path | None
    facts: VideoFacts
    warnings: list[str]


def _fmt_srt_time(seconds: float) -> str:
    ms = int(round(max(0.0, seconds) * 1000))
    h, rem = divmod(ms, 3_600_000)
    m, rem = divmod(rem, 60_000)
    s, ms = divmod(rem, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def write_srt(captions: list[CaptionEntry], out_srt: Path) -> Path:
    out_srt.parent.mkdir(parents=True, exist_ok=True)
    blocks = []
    for i, c in enumerate(captions, 1):
        blocks.append(f"{i}\n{_fmt_srt_time(c.start_s)} --> {_fmt_srt_time(c.end_s)}\n{c.text.strip()}\n")
    out_srt.write_text("\n".join(blocks), encoding="utf-8")
    return out_srt


class FilmCraftAdapter:
    def __init__(self, cli: str, ffmpeg: str = "ffmpeg", ffprobe: str = "ffprobe", timeout: float = 600.0):
        self.cli, self.ffmpeg, self.ffprobe, self.timeout = cli, ffmpeg, ffprobe, timeout

    def discover(self) -> Capabilities:
        with MCPClient([self.cli, "mcp"], "filmcraft", timeout=30) as c:
            cmds = c.call("command_list")
            ids = {x["id"] for x in (cmds if isinstance(cmds, list) else cmds.get("commands", []))}
            return Capabilities(
                version=str(c.server_info.get("version")),
                tools=sorted(c.tools),
                missing_tools=sorted(REQUIRED_TOOLS - set(c.tools)),
                missing_commands=sorted(REQUIRED_COMMANDS - ids),
            )

    def _ensure_silence_wav(self, path: Path, duration_s: float, sample_rate: int = 48000) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        r = subprocess.run(
            [self.ffmpeg, "-v", "error", "-y", "-f", "lavfi", "-i", f"anullsrc=r={sample_rate}:cl=stereo",
             "-t", f"{duration_s:.3f}", str(path)],
            capture_output=True, text=True, timeout=60,
        )
        if r.returncode != 0 or not path.is_file():
            raise EngineError(f"Failed to synthesize silent audio track: {r.stderr.strip()[:200]}")
        return path

    def assemble(self, manifest: TimelineManifest, workspace_root: Path, out_mp4: Path, fcproj_path: Path) -> AssemblyResult:
        """Assemble video, audio, and captions through FilmCraft MCP, save .fcproj, export MP4, and verify."""
        warnings: list[str] = []
        manifest_path = workspace_root / "assembly" / "timeline_manifest.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(manifest.model_dump_json(indent=2), encoding="utf-8")

        out_mp4.parent.mkdir(parents=True, exist_ok=True)
        fcproj_path.parent.mkdir(parents=True, exist_ok=True)

        # Resolve and validate all source files before starting the engine
        video_sources: list[tuple[ClipPlacement, Path]] = []
        for clip in manifest.clips:
            p = Path(clip.source_path) if Path(clip.source_path).is_absolute() else (workspace_root / clip.source_path)
            if not p.is_file():
                raise EngineError(f"Missing video clip for scene '{clip.scene_id}': {p}")
            video_sources.append((clip, p.resolve()))

        audio_sources: list[tuple[AudioPlacement, Path]] = []
        for aclip in manifest.audio_clips:
            p = Path(aclip.source_path) if Path(aclip.source_path).is_absolute() else (workspace_root / aclip.source_path)
            if not p.is_file():
                raise EngineError(f"Missing audio file '{aclip.id}': {p}")
            audio_sources.append((aclip, p.resolve()))

        # Ensure an audio bed exists so the exported MP4 always contains an AAC audio stream
        if not audio_sources and not any(c.include_audio for c in manifest.clips):
            sil = workspace_root / "assembly" / "_silence.wav"
            self._ensure_silence_wav(sil, manifest.total_duration_s, manifest.sample_rate)
            audio_sources.append((
                AudioPlacement(id="silence_bed", source_path=str(sil), track="A1", start_s=0.0, duration_s=manifest.total_duration_s),
                sil.resolve(),
            ))

        all_paths = [str(p) for _, p in video_sources] + [str(p) for _, p in audio_sources]
        raw_mp4 = out_mp4 if not (manifest.captions and manifest.burn_captions) else (workspace_root / "assembly" / "_raw_export.mp4")
        if raw_mp4.exists():
            raw_mp4.unlink()

        with MCPClient([self.cli, "mcp"], "filmcraft", timeout=self.timeout, cwd=str(workspace_root)) as c:
            c.call("command_run", id="file.newProject", params={"name": manifest.title})
            c.call("command_run", id="file.newSequence", params={
                "name": "Main",
                "width": manifest.width,
                "height": manifest.height,
                "fps": manifest.fps,
                "sampleRate": manifest.sample_rate,
                "video": 2,
                "audio": 2,
            })
            imp = c.call("command_run", id="file.import", params={"paths": all_paths})
            items = imp.get("items", []) if isinstance(imp, dict) else []
            if len(items) != len(all_paths):
                raise EngineError(f"FilmCraft imported {len(items)}/{len(all_paths)} media items: {imp}")

            v_items = items[:len(video_sources)]
            a_items = items[len(video_sources):]

            steps: list[dict] = []
            for (clip, _), item_id in zip(video_sources, v_items):
                steps.append({
                    "id": "timeline.place",
                    "params": {
                        "item": item_id,
                        "track": clip.track,
                        "seconds": round(clip.start_s, 4),
                        "audio": clip.include_audio,
                    },
                })
                if clip.transition_in != "cut" and clip.start_s > 0:
                    warnings.append(f"scene '{clip.scene_id}': transition '{clip.transition_in}' recorded in manifest; rendered as clean cut")

            for (aclip, _), item_id in zip(audio_sources, a_items):
                steps.append({
                    "id": "timeline.place",
                    "params": {
                        "item": item_id,
                        "track": aclip.track,
                        "seconds": round(aclip.start_s, 4),
                        "video": False,
                        "audio": True,
                    },
                })

            if manifest.captions:
                steps.append({"id": "captions.newTrack", "params": {"format": "Subtitle", "name": "Captions", "language": "en"}})
                for cap in manifest.captions:
                    steps.append({
                        "id": "captions.add",
                        "params": {
                            "track": "C1",
                            "text": cap.text,
                            "seconds": round(cap.start_s, 3),
                            "durationSeconds": round(max(0.2, cap.end_s - cap.start_s), 3),
                        },
                    })

            steps.append({"id": "file.saveAs", "params": {"path": str(fcproj_path.resolve())}})
            batch_res = c.call("command_batch", steps=steps, stop_on_error=True)
            if isinstance(batch_res, dict) and batch_res.get("errors"):
                raise EngineError(f"FilmCraft timeline assembly failed: {batch_res['errors']}")

            exp = c.call("command_run", id="file.exportMedia", params={"path": str(raw_mp4.resolve()), "format": "h264", "wait": True})
            if isinstance(exp, dict) and exp.get("offlineMedia"):
                raise EngineError(f"FilmCraft export encountered offline media: {exp['offlineMedia']}")

        if not fcproj_path.is_file() or fcproj_path.stat().st_size == 0:
            raise EngineError(f"FilmCraft did not save project file at {fcproj_path}")

        srt_path: Path | None = None
        if manifest.captions:
            srt_path = write_srt(manifest.captions, workspace_root / "captions" / "captions.srt")
            if manifest.burn_captions:
                warnings.append("FilmCraft caption tracks are not burned into video frames by file.exportMedia; burned in via FFmpeg subtitles filter.")
                self._burn_subtitles(raw_mp4, srt_path, out_mp4, manifest.caption_font_size)
                raw_mp4.unlink(missing_ok=True)

        facts = verify_video(
            out_mp4,
            width=manifest.width,
            height=manifest.height,
            fps=manifest.fps,
            duration=manifest.total_duration_s,
            ffprobe=self.ffprobe,
            expect_audio=True,
            tol_frames=3.0,
        )
        return AssemblyResult(
            output_mp4=out_mp4,
            project_fcproj=fcproj_path,
            manifest_path=manifest_path,
            srt_path=srt_path,
            facts=facts,
            warnings=warnings,
        )

    def _burn_subtitles(self, in_mp4: Path, srt_path: Path, out_mp4: Path, font_size: int = 22) -> None:
        # Escape path for FFmpeg filtergraph (portable across Linux/Windows when run with cwd=srt_path.parent)
        ass_size = max(12, min(22, int(font_size * 0.36)))
        style = f"FontName=DejaVu Sans,FontSize={ass_size},PrimaryColour=&H00FFFFFF,OutlineColour=&H00101420,BackColour=&H80000000,BorderStyle=3,Outline=1,Shadow=0,MarginV=16,Alignment=2"
        r = subprocess.run(
            [self.ffmpeg, "-v", "error", "-y", "-i", str(in_mp4.resolve()),
             "-vf", f"subtitles={srt_path.name}:force_style='{style}'",
             "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-c:a", "copy", str(out_mp4.resolve())],
            cwd=str(srt_path.parent),
            capture_output=True, text=True, timeout=300,
        )
        if r.returncode != 0 or not out_mp4.is_file():
            raise EngineError(f"FFmpeg subtitle burn-in failed: {r.stderr.strip()[:300]}")
