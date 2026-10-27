"""Narration generation, user-audio alignment, storyboard timing revision, and caption generation + validation."""
from __future__ import annotations
import asyncio, hashlib, json, math, re, subprocess
from dataclasses import dataclass, field
from pathlib import Path
from ..storyboard.schema import Storyboard, Scene, words
from ..workspace import Workspace
from .filmcraft import CaptionEntry, AudioPlacement, write_srt
from .mcp_client import EngineError

DEFAULT_VOICE = "en-US-GuyNeural"
MAX_CHARS_PER_LINE = 42
MAX_LINES = 2
MAX_CPS = 26.0
MIN_CAP_DUR = 0.45
MAX_CAP_DUR = 7.5


@dataclass
class SceneAudio:
    scene_id: str
    rel_wav: str
    duration_s: float
    word_timings: list[dict]  # [{"word": str, "start_s": float, "end_s": float}]
    reused_cache: bool = False
    provider: str = "edge_tts"


@dataclass
class CaptionValidationReport:
    ok: bool
    caption_count: int
    issues: list[str] = field(default_factory=list)


def _measure_audio_seconds(path: Path, ffprobe: str = "ffprobe") -> float:
    r = subprocess.run(
        [ffprobe, "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True, timeout=30,
    )
    if r.returncode != 0 or not r.stdout.strip():
        raise EngineError(f"Could not measure audio duration for {path}: {r.stderr.strip()[:200]}")
    return round(float(r.stdout.strip()), 3)


def _to_wav_48k(src: Path, dst_wav: Path, ffmpeg: str = "ffmpeg", pad_tail_s: float = 0.25) -> float:
    dst_wav.parent.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(
        [ffmpeg, "-v", "error", "-y", "-i", str(src), "-af", f"apad=pad_dur={pad_tail_s:.2f}",
         "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", str(dst_wav)],
        capture_output=True, text=True, timeout=60,
    )
    if r.returncode != 0 or not dst_wav.is_file():
        raise EngineError(f"Audio conversion to WAV failed for {src}: {r.stderr.strip()[:200]}")
    return _measure_audio_seconds(dst_wav)


def _synth_offline_wav(text: str, dst_wav: Path, ffmpeg: str = "ffmpeg") -> tuple[float, list[dict]]:
    """Deterministic local speech-cadence tone synthesizer for offline/unit-test environments."""
    wlist = re.findall(r"\S+", text.strip()) or ["silence"]
    dur = round(max(1.8, len(wlist) / 2.6) + 0.3, 3)
    dst_wav.parent.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(
        [ffmpeg, "-v", "error", "-y", "-f", "lavfi",
         "-i", f"sine=frequency=220:duration={dur:.3f}",
         "-af", "volume=0.08,tremolo=f=4.5:d=0.6", "-ar", "48000", "-ac", "2", str(dst_wav)],
        capture_output=True, text=True, timeout=60,
    )
    if r.returncode != 0:
        raise EngineError(f"Offline audio synthesis failed: {r.stderr.strip()[:200]}")
    actual = _measure_audio_seconds(dst_wav)
    speech_dur = max(0.5, actual - 0.3)
    step = speech_dur / len(wlist)
    timings = [
        {"word": w, "start_s": round(i * step, 3), "end_s": round((i + 0.9) * step, 3)}
        for i, w in enumerate(wlist)
    ]
    return actual, timings


async def _edge_tts_synth(text: str, voice: str, mp3_path: Path) -> list[dict]:
    import edge_tts
    comm = edge_tts.Communicate(text, voice, boundary="WordBoundary")
    words_out: list[dict] = []
    mp3_path.parent.mkdir(parents=True, exist_ok=True)
    with open(mp3_path, "wb") as f:
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                st = round(chunk["offset"] / 1e7, 3)
                du = round(max(0.05, chunk["duration"] / 1e7), 3)
                words_out.append({"word": chunk["text"], "start_s": st, "end_s": round(st + du, 3)})
    return words_out


def synthesize_scene_narration(
    scene: Scene, ws: Workspace, voice: str | None = None, mode: str = "generate",
    ffmpeg: str = "ffmpeg", ffprobe: str = "ffprobe", log=lambda m: None,
) -> SceneAudio:
    voice = voice or DEFAULT_VOICE
    nar_dir = ws.root / "narration"
    nar_dir.mkdir(parents=True, exist_ok=True)
    wav_path = nar_dir / f"{scene.id}.wav"
    meta_path = nar_dir / f"{scene.id}_meta.json"
    text_hash = hashlib.sha256(f"{mode}:{voice}:{scene.narration_text.strip()}".encode("utf-8")).hexdigest()[:16]

    # Mode A: User-supplied audio
    if mode == "user_audio":
        user_candidates = [nar_dir / f"user_{scene.id}.wav", nar_dir / f"user_{scene.id}.mp3", wav_path]
        src = next((p for p in user_candidates if p.is_file()), None)
        if not src:
            raise EngineError(f"Narration mode is 'user_audio', but no audio file was found for scene {scene.id} (expected narration/user_{scene.id}.wav).")
        if src != wav_path:
            dur = _to_wav_48k(src, wav_path, ffmpeg, pad_tail_s=0.1)
        else:
            dur = _measure_audio_seconds(wav_path, ffprobe)
        wlist = re.findall(r"\S+", scene.narration_text.strip()) or ["..."]
        step = max(0.2, (dur - 0.15) / len(wlist))
        timings = [{"word": w, "start_s": round(i * step, 3), "end_s": round((i + 0.92) * step, 3)} for i, w in enumerate(wlist)]
        meta_path.write_text(json.dumps({"hash": text_hash, "duration_s": dur, "words": timings, "provider": "user_audio"}, indent=2), encoding="utf-8")
        ws.add_asset(f"narration/{scene.id}.wav", "narration_audio", {"mode": "user_audio", "duration_s": dur})
        return SceneAudio(scene.id, f"narration/{scene.id}.wav", dur, timings, reused_cache=False, provider="user_audio")

    # Reuse cached narration if narration_text and voice have not changed
    if wav_path.is_file() and meta_path.is_file():
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            if meta.get("hash") == text_hash and wav_path.stat().st_size > 0:
                return SceneAudio(scene.id, f"narration/{scene.id}.wav", float(meta["duration_s"]), meta["words"], reused_cache=True, provider=meta.get("provider", "edge_tts"))
        except Exception:
            pass

    provider_used = "edge_tts"
    if voice == "synthetic":
        dur, timings = _synth_offline_wav(scene.narration_text, wav_path, ffmpeg)
        provider_used = "synthetic"
    else:
        mp3_tmp = nar_dir / f"_{scene.id}.mp3"
        try:
            timings = asyncio.run(_edge_tts_synth(scene.narration_text, voice, mp3_tmp))
            dur = _to_wav_48k(mp3_tmp, wav_path, ffmpeg, pad_tail_s=0.25)
            mp3_tmp.unlink(missing_ok=True)
            if not timings:
                wlist = re.findall(r"\S+", scene.narration_text.strip())
                step = max(0.2, (dur - 0.25) / max(1, len(wlist)))
                timings = [{"word": w, "start_s": round(i * step, 3), "end_s": round((i + 0.9) * step, 3)} for i, w in enumerate(wlist)]
        except Exception as e:
            log(f"edge_tts unavailable for {scene.id} ({e}); falling back to local synthetic voice.")
            dur, timings = _synth_offline_wav(scene.narration_text, wav_path, ffmpeg)
            provider_used = "synthetic_fallback"

    meta_path.write_text(json.dumps({"hash": text_hash, "voice": voice, "duration_s": dur, "words": timings, "provider": provider_used}, indent=2), encoding="utf-8")
    ws.add_asset(f"narration/{scene.id}.wav", "narration_audio", {"mode": "generate", "provider": provider_used, "voice": voice, "duration_s": dur})
    return SceneAudio(scene.id, f"narration/{scene.id}.wav", dur, timings, reused_cache=False, provider=provider_used)


def revise_storyboard_with_audio(sb: Storyboard, scene_audios: dict[str, SceneAudio]) -> Storyboard:
    """Revise each scene's duration to match the actual measured narration audio, and proportionally rescale
    animation, camera, and on-screen text timings so they fit the real audio duration cleanly."""
    data = sb.model_dump()
    for sc in data["scenes"]:
        sa = scene_audios.get(sc["id"])
        if not sa:
            continue
        cur_audio = sc["timing"].get("narration_audio_s") if sc["timing"].get("revised_from_audio") else None
        old_dur = float(cur_audio if cur_audio else sc["estimated_duration"])
        new_dur = round(max(1.5, sa.duration_s), 3)
        if abs(new_dur - old_dur) < 0.005 and sc["timing"].get("revised_from_audio"):
            continue
        scale = (new_dur / old_dur) if old_dur > 0 else 1.0
        sc["timing"]["narration_audio_s"] = new_dur
        sc["timing"]["revised_from_audio"] = True

        for a in sc.get("animation_sequence", []):
            a["at"] = round(min(new_dur - 0.1, a["at"] * scale), 3)
            a["duration"] = round(max(0.1, min(new_dur - a["at"], a["duration"] * scale)), 3)
        for c in sc.get("camera_instructions", []):
            c["at"] = round(min(new_dur - 0.1, c["at"] * scale), 3)
            c["duration"] = round(max(0.1, min(new_dur - c["at"], c["duration"] * scale)), 3)
        for t in sc.get("on_screen_text", []):
            t["at"] = round(min(new_dur - 0.1, t["at"] * scale), 3)
            t["duration"] = round(max(0.1, min(new_dur - t["at"], t["duration"] * scale)), 3)
        if sc["transition"]["duration"] > new_dur * 0.5:
            sc["transition"]["duration"] = round(new_dur * 0.25, 2)
    return Storyboard.model_validate(data)


def _wrap_caption_text(words_list: list[str]) -> str:
    text = " ".join(words_list).strip()
    if len(text) <= MAX_CHARS_PER_LINE:
        return text
    # Split into 2 balanced lines
    mid = len(text) // 2
    split_at = text.rfind(" ", 0, mid + 8)
    if split_at == -1:
        split_at = text.find(" ", mid)
    if split_at == -1:
        return text[:MAX_CHARS_PER_LINE * 2]
    return text[:split_at].strip() + "\n" + text[split_at + 1:].strip()


def build_synchronized_captions(sb: Storyboard, scene_audios: dict[str, SceneAudio]) -> list[CaptionEntry]:
    """Build phrase-level captions synchronized to actual audio word timestamps across the full video timeline."""
    entries: list[CaptionEntry] = []
    scene_offset = 0.0
    idx = 1
    # Map original punctuation tokens from scene.narration_text onto word timings
    for sc in sb.scenes:
        sa = scene_audios.get(sc.id)
        dur = sc.duration
        raw_tokens = re.findall(r"\S+", sc.narration_text.strip())
        w_timings = sa.word_timings if (sa and sa.word_timings) else []
        if len(w_timings) == len(raw_tokens):
            aligned = [{"token": tok, "start_s": w["start_s"], "end_s": w["end_s"]} for tok, w in zip(raw_tokens, w_timings)]
        elif w_timings:
            # Map raw tokens proportionally across the measured word span
            span_start = w_timings[0]["start_s"]
            span_end = w_timings[-1]["end_s"]
            step = max(0.12, (span_end - span_start) / max(1, len(raw_tokens)))
            aligned = [{"token": tok, "start_s": round(span_start + i * step, 3), "end_s": round(span_start + (i + 0.92) * step, 3)} for i, tok in enumerate(raw_tokens)]
        else:
            step = max(0.15, (dur - 0.2) / max(1, len(raw_tokens)))
            aligned = [{"token": tok, "start_s": round(i * step, 3), "end_s": round((i + 0.92) * step, 3)} for i, tok in enumerate(raw_tokens)]

        chunk_tokens: list[str] = []
        chunk_start: float | None = None
        chunk_end: float = 0.0

        def flush():
            nonlocal idx, chunk_tokens, chunk_start, chunk_end
            if not chunk_tokens or chunk_start is None:
                return
            st = round(scene_offset + max(0.0, chunk_start), 3)
            en = round(min(scene_offset + dur - 0.04, max(st + MIN_CAP_DUR, scene_offset + chunk_end + 0.08)), 3)
            if entries and st < entries[-1].end_s:
                st = round(entries[-1].end_s + 0.02, 3)
            if en <= st + 0.2:
                en = round(st + MIN_CAP_DUR, 3)
            entries.append(CaptionEntry(index=idx, start_s=st, end_s=en, text=_wrap_caption_text(chunk_tokens)))
            idx += 1
            chunk_tokens = []
            chunk_start = None

        for item in aligned:
            tok = item["token"]
            cand = " ".join(chunk_tokens + [tok])
            dur_if_added = (item["end_s"] - (chunk_start if chunk_start is not None else item["start_s"]))
            if chunk_tokens and (len(cand) > MAX_CHARS_PER_LINE * MAX_LINES - 6 or len(chunk_tokens) >= 11 or dur_if_added > MAX_CAP_DUR - 0.5):
                flush()
            if chunk_start is None:
                chunk_start = item["start_s"]
            chunk_tokens.append(tok)
            chunk_end = item["end_s"]
            if tok.endswith((".", "!", "?", ";")) and len(chunk_tokens) >= 4:
                flush()
        flush()
        scene_offset = round(scene_offset + dur, 3)
    return entries


def validate_captions(captions: list[CaptionEntry], sb: Storyboard, total_video_s: float) -> CaptionValidationReport:
    issues: list[str] = []
    if not captions:
        return CaptionValidationReport(ok=False, caption_count=0, issues=["No caption segments were generated."])

    # 1. Coverage of narration words
    expected_words = words(" ".join(s.narration_text for s in sb.scenes))
    caption_words = words(" ".join(c.text for c in captions))
    if len(caption_words) < len(expected_words) * 0.9:
        issues.append(f"Missing caption words: captions contain {len(caption_words)}/{len(expected_words)} script words.")

    prev_end = -1.0
    for c in captions:
        dur = c.end_s - c.start_s
        if dur <= 0:
            issues.append(f"Caption #{c.index} has non-positive duration ({c.start_s:.2f}s -> {c.end_s:.2f}s).")
        if dur < 0.25:
            issues.append(f"Caption #{c.index} is too brief ({dur:.2f}s < 0.25s).")
        if dur > MAX_CAP_DUR + 1.0:
            issues.append(f"Caption #{c.index} is too long ({dur:.2f}s).")
        if c.start_s < prev_end - 0.005:
            issues.append(f"Caption #{c.index} overlaps previous caption ({c.start_s:.2f}s < {prev_end:.2f}s).")
        if c.end_s > total_video_s + 0.35:
            issues.append(f"Caption #{c.index} extends past video end ({c.end_s:.2f}s > {total_video_s:.2f}s).")
        lines = c.text.splitlines()
        if len(lines) > MAX_LINES:
            issues.append(f"Caption #{c.index} exceeds {MAX_LINES} lines (safe area violation).")
        if any(len(ln) > MAX_CHARS_PER_LINE + 6 for ln in lines):
            issues.append(f"Caption #{c.index} line exceeds safe width ({max(len(ln) for ln in lines)} chars).")
        cps = len(c.text.replace("\n", " ")) / max(0.1, dur)
        if cps > MAX_CPS + 6:
            issues.append(f"Caption #{c.index} reading speed too high ({cps:.1f} chars/s).")
        prev_end = c.end_s

    return CaptionValidationReport(ok=(len(issues) == 0), caption_count=len(captions), issues=issues)
