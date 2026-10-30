"""Narration generation (Local Kokoro-82M Neural TTS + Microsoft Edge Neural TTS + Offline Fallback),
user-audio alignment, storyboard timing revision, and word-highlighted caption generation + validation."""
from __future__ import annotations
import asyncio, hashlib, json, math, os, re, subprocess
from dataclasses import dataclass, field
from pathlib import Path
from ..config import REPO_ROOT
from ..storyboard.schema import Storyboard, Scene, words
from ..workspace import Workspace
from .filmcraft import CaptionEntry, CaptionWord, AudioPlacement, write_srt
from .mcp_client import EngineError

KOKORO_PYTHON_CANDIDATES = [
    os.environ.get("KOKORO_PYTHON", ""),
    "/home/omthakur/yt-motion-studio-phase-c-final/.ytms/kokoro-venv/bin/python",
]

AVAILABLE_VOICES = [
    # Top Neural Voices (Local Kokoro-82M $0.00)
    {"id": "kokoro:am_michael", "name": "Kokoro Michael (US Documentary Male — Local Neural)", "label": "Kokoro-82M — Michael (US Documentary Male)", "provider": "kokoro_local", "cost_usd": 0.0, "gender": "male", "accent": "US"},
    {"id": "kokoro:af_heart", "name": "Kokoro Heart (US Warm Female — Local Neural)", "label": "Kokoro-82M — Heart (US Expressive Female)", "provider": "kokoro_local", "cost_usd": 0.0, "gender": "female", "accent": "US"},
    {"id": "kokoro:af_bella", "name": "Kokoro Bella (US Storyteller Female — Local Neural)", "label": "Kokoro-82M — Bella (US Storyteller Female)", "provider": "kokoro_local", "cost_usd": 0.0, "gender": "female", "accent": "US"},
    {"id": "kokoro:am_adam", "name": "Kokoro Adam (US Deep Gritty Male — Local Neural)", "label": "Kokoro-82M — Adam (US Motivation Male)", "provider": "kokoro_local", "cost_usd": 0.0, "gender": "male", "accent": "US"},
    {"id": "kokoro:bm_george", "name": "Kokoro George (UK BBC Documentary Male — Local Neural)", "label": "Kokoro-82M — George (UK BBC Male)", "provider": "kokoro_local", "cost_usd": 0.0, "gender": "male", "accent": "UK"},
    {"id": "kokoro:bf_emma", "name": "Kokoro Emma (UK Presenter Female — Local Neural)", "label": "Kokoro-82M — Emma (UK Presenter Female)", "provider": "kokoro_local", "cost_usd": 0.0, "gender": "female", "accent": "UK"},

    # Indian Voices (English & Hindi Natural Neural TTS)
    {"id": "en-IN-PrabhatNeural", "name": "Prabhat (Indian English Male — Natural Neural)", "label": "Indian English — Prabhat (Male Natural)", "provider": "edge_tts", "cost_usd": 0.0, "gender": "male", "accent": "IN"},
    {"id": "en-IN-NeerjaExpressiveNeural", "name": "Neerja (Indian English Female — Expressive Neural)", "label": "Indian English — Neerja (Female Expressive)", "provider": "edge_tts", "cost_usd": 0.0, "gender": "female", "accent": "IN"},
    {"id": "hi-IN-MadhurNeural", "name": "Madhur (Hindi Indian Male — Storyteller Neural)", "label": "Hindi Indian — Madhur (Male Storyteller)", "provider": "edge_tts", "cost_usd": 0.0, "gender": "male", "accent": "IN"},
    {"id": "hi-IN-SwaraNeural", "name": "Swara (Hindi Indian Female — Conversational Neural)", "label": "Hindi Indian — Swara (Female Conversational)", "provider": "edge_tts", "cost_usd": 0.0, "gender": "female", "accent": "IN"},

    # Nepali Voices (Authentic Himalayan Neural TTS)
    {"id": "ne-NP-SagarNeural", "name": "Sagar (Nepali Male — Authentic Neural)", "label": "Nepali — Sagar (Male Authentic)", "provider": "edge_tts", "cost_usd": 0.0, "gender": "male", "accent": "NP"},
    {"id": "ne-NP-HemkalaNeural", "name": "Hemkala (Nepali Female — Authentic Neural)", "label": "Nepali — Hemkala (Female Authentic)", "provider": "edge_tts", "cost_usd": 0.0, "gender": "female", "accent": "NP"},

    # Global High-Retention Narrators
    {"id": "en-US-GuyNeural", "name": "Guy (US Tech / Explainer Male — Edge Neural)", "label": "Microsoft Edge — Guy (US Male Explainer)", "provider": "edge_tts", "cost_usd": 0.0, "gender": "male", "accent": "US"},
    {"id": "en-US-AriaNeural", "name": "Aria (US Dynamic Presenter Female — Edge Neural)", "label": "Microsoft Edge — Aria (US Female Presenter)", "provider": "edge_tts", "cost_usd": 0.0, "gender": "female", "accent": "US"},
    {"id": "en-GB-RyanNeural", "name": "Ryan (UK Documentary Male — Edge Neural)", "label": "Microsoft Edge — Ryan (UK Male)", "provider": "edge_tts", "cost_usd": 0.0, "gender": "male", "accent": "UK"},
]

KOKORO_VOICE_MAP = {
    "am_michael", "af_heart", "af_bella", "am_adam", "bm_george", "bf_emma",
    "af_sarah", "af_nova", "am_fenrir", "bm_lewis",
}


def find_kokoro_python() -> str | None:
    for p in KOKORO_PYTHON_CANDIDATES:
        if p and Path(p).is_file():
            return p
    return None


DEFAULT_VOICE = "kokoro:am_michael" if find_kokoro_python() else "en-US-GuyNeural"
MAX_CHARS_PER_LINE = 38
MAX_WORDS_PER_CAPTION = 7
MAX_LINES = 2
MAX_CPS = 34.0
MIN_CAP_DUR = 0.8
MAX_CAP_DUR = 5.5


@dataclass
class SceneAudio:
    scene_id: str
    rel_wav: str
    duration_s: float
    word_timings: list[dict]  # [{"word": str, "start_s": float, "end_s": float}]
    reused_cache: bool = False
    provider: str = "kokoro_local"


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


def _to_wav_48k(src: Path, dst_wav: Path, ffmpeg: str = "ffmpeg", pad_tail_s: float = 0.20) -> float:
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


def _is_kokoro_voice(voice: str) -> bool:
    return voice.startswith("kokoro:") or voice in KOKORO_VOICE_MAP


def _kokoro_synth(text: str, voice: str, raw_wav: Path, dst_wav: Path, ffmpeg: str = "ffmpeg") -> tuple[float, list[dict]]:
    kpy = find_kokoro_python()
    script_path = REPO_ROOT / "scripts" / "tts_kokoro.py"
    if not kpy or not script_path.is_file():
        raise EngineError("Kokoro Python environment not found.")
    vname = voice.replace("kokoro:", "").strip() or "am_michael"
    raw_wav.parent.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(
        [kpy, str(script_path), "--text", text, "--voice", vname, "--out", str(raw_wav)],
        capture_output=True, text=True, timeout=180,
    )
    if r.returncode != 0 or not raw_wav.is_file():
        raise EngineError(f"Kokoro synthesis failed: {(r.stderr or r.stdout).strip()[:240]}")
    lines = [ln.strip() for ln in r.stdout.splitlines() if ln.strip().startswith("{")]
    payload = json.loads(lines[-1]) if lines else {}
    words_out = payload.get("words", [])
    dur = _to_wav_48k(raw_wav, dst_wav, ffmpeg, pad_tail_s=0.20)
    raw_wav.unlink(missing_ok=True)
    return dur, words_out


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
                return SceneAudio(scene.id, f"narration/{scene.id}.wav", float(meta["duration_s"]), meta["words"], reused_cache=True, provider=meta.get("provider", "kokoro_local"))
        except Exception:
            pass

    provider_used = "edge_tts"
    if voice == "synthetic":
        dur, timings = _synth_offline_wav(scene.narration_text, wav_path, ffmpeg)
        provider_used = "synthetic"
    elif _is_kokoro_voice(voice) and find_kokoro_python():
        raw_tmp = nar_dir / f"_{scene.id}_kokoro24k.wav"
        try:
            dur, timings = _kokoro_synth(scene.narration_text, voice, raw_tmp, wav_path, ffmpeg)
            provider_used = f"kokoro_local ({voice.replace('kokoro:', '')})"
            if not timings:
                wlist = re.findall(r"\S+", scene.narration_text.strip())
                step = max(0.2, (dur - 0.2) / max(1, len(wlist)))
                timings = [{"word": w, "start_s": round(i * step, 3), "end_s": round((i + 0.9) * step, 3)} for i, w in enumerate(wlist)]
        except Exception as e:
            log(f"Kokoro local TTS error on {scene.id} ({e}); falling back to Edge Neural TTS.")
            mp3_tmp = nar_dir / f"_{scene.id}.mp3"
            timings = asyncio.run(_edge_tts_synth(scene.narration_text, "en-US-GuyNeural", mp3_tmp))
            dur = _to_wav_48k(mp3_tmp, wav_path, ffmpeg, pad_tail_s=0.20)
            mp3_tmp.unlink(missing_ok=True)
            provider_used = "edge_tts"
    else:
        mp3_tmp = nar_dir / f"_{scene.id}.mp3"
        try:
            edge_v = voice if not _is_kokoro_voice(voice) else "en-US-GuyNeural"
            timings = asyncio.run(_edge_tts_synth(scene.narration_text, edge_v, mp3_tmp))
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


def revise_storyboard_with_audio(sb: Storyboard, scene_audios: dict[str, SceneAudio], lead_s: float = 0.10) -> Storyboard:
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

        # Word-level beat matching: Align element entrance and text pop-ins to Kokoro audio word timestamps
        if sa and sa.word_timings:
            _align_timings_to_words(sc, sa.word_timings, new_dur, lead_s)
    return Storyboard.model_validate(data)


def _align_timings_to_words(sc: dict, word_timings: list[dict], new_dur: float, lead_s: float = 0.10) -> None:
    if not word_timings:
        return
    SKIP_WORDS = {"the", "and", "of", "in", "to", "a", "an", "for", "with", "at", "by", "from",
                  "icon", "marker", "region", "box", "card", "layer", "element", "item"}
    wt_clean: list[tuple[str, float, float]] = []
    for w in word_timings:
        cleaned = re.sub(r"[^\w]", "", str(w.get("word", ""))).lower()
        if cleaned:
            wt_clean.append((cleaned, float(w.get("start_s", 0.0)), float(w.get("end_s", 0.0))))

    def find_keyword_time(keywords: list[str]) -> float | None:
        for kw in keywords:
            kw_low = kw.lower().strip()
            if len(kw_low) < 3 or kw_low in SKIP_WORDS:
                continue
            for tok, st, _ in wt_clean:
                if tok == kw_low or (len(kw_low) >= 4 and (tok.startswith(kw_low) or kw_low.startswith(tok))):
                    return st
        return None

    el_spoken_time: dict[str, float] = {}
    for el in sc.get("visual_elements", []):
        eid = str(el.get("id", ""))
        lbl = str(el.get("label", ""))
        tokens = re.split(r"[_\s]+", f"{lbl} {eid}".lower())
        st = find_keyword_time(tokens)
        if st is not None:
            el_spoken_time[eid] = st

    for a in sc.get("animation_sequence", []):
        act = str(a.get("action", ""))
        targets = [str(t) for t in a.get("targets", [])]
        matched_times = [el_spoken_time[t] for t in targets if t in el_spoken_time]
        if matched_times:
            earliest = min(matched_times)
            if act in ("appear", "fade_in", "grow", "draw", "flow", "scale_pop"):
                a["at"] = round(max(0.15, min(new_dur - 0.2, earliest - lead_s)), 3)
            elif act in ("pulse", "highlight"):
                a["at"] = round(max(0.2, min(new_dur - 0.2, earliest + 0.05)), 3)
            a["duration"] = round(max(0.1, min(new_dur - a["at"], float(a.get("duration", 0.5)))), 3)

    for t in sc.get("on_screen_text", []):
        txt = str(t.get("text", ""))
        tokens = re.split(r"[_\s]+", txt.lower())
        st = find_keyword_time(tokens)
        if st is not None:
            t["at"] = round(max(0.15, min(new_dur - 0.2, st - lead_s)), 3)
            t["duration"] = round(max(0.1, min(new_dur - t["at"], float(t.get("duration", 2.0)))), 3)

    # Final pass to guarantee all timings stay inside scene bounds [0, new_dur]
    for a in sc.get("animation_sequence", []):
        if a["at"] + a["duration"] > new_dur:
            a["duration"] = round(max(0.05, new_dur - a["at"]), 3)
    for t in sc.get("on_screen_text", []):
        if t["at"] + t["duration"] > new_dur:
            t["duration"] = round(max(0.1, new_dur - t["at"]), 3)


def _wrap_caption_text(words_list: list[str]) -> str:
    text = " ".join(words_list).strip()
    if len(text) <= MAX_CHARS_PER_LINE:
        return text
    mid = len(text) // 2
    split_at = text.rfind(" ", 0, mid + 8)
    if split_at == -1:
        split_at = text.find(" ", mid)
    if split_at == -1:
        return text[:MAX_CHARS_PER_LINE * 2]
    return text[:split_at].strip() + "\n" + text[split_at + 1:].strip()


def build_synchronized_captions(sb: Storyboard, scene_audios: dict[str, SceneAudio]) -> list[CaptionEntry]:
    """Build 2-4 word phrase captions with exact per-word timestamps for active word highlighting."""
    entries: list[CaptionEntry] = []
    scene_offset = 0.0
    idx = 1
    for sc in sb.scenes:
        sa = scene_audios.get(sc.id)
        dur = sc.duration
        raw_tokens = re.findall(r"\S+", sc.narration_text.strip())
        w_timings = sa.word_timings if (sa and sa.word_timings) else []
        if len(w_timings) == len(raw_tokens):
            aligned = [{"token": tok, "start_s": w["start_s"], "end_s": w["end_s"]} for tok, w in zip(raw_tokens, w_timings)]
        elif w_timings:
            span_start = w_timings[0]["start_s"]
            span_end = w_timings[-1]["end_s"]
            step = max(0.12, (span_end - span_start) / max(1, len(raw_tokens)))
            aligned = [{"token": tok, "start_s": round(span_start + i * step, 3), "end_s": round(span_start + (i + 0.92) * step, 3)} for i, tok in enumerate(raw_tokens)]
        else:
            step = max(0.15, (dur - 0.2) / max(1, len(raw_tokens)))
            aligned = [{"token": tok, "start_s": round(i * step, 3), "end_s": round((i + 0.92) * step, 3)} for i, tok in enumerate(raw_tokens)]

        chunk_items: list[dict] = []
        chunk_start: float | None = None
        chunk_end: float = 0.0

        def flush():
            nonlocal idx, chunk_items, chunk_start, chunk_end
            if not chunk_items or chunk_start is None:
                return
            st = round(scene_offset + max(0.0, chunk_start), 3)
            en = round(min(scene_offset + dur - 0.04, max(st + MIN_CAP_DUR, scene_offset + chunk_end + 0.08)), 3)
            if entries and st < entries[-1].end_s:
                st = round(entries[-1].end_s + 0.02, 3)
            if en <= st + 0.2:
                en = round(st + MIN_CAP_DUR, 3)

            chunk_tokens = [x["token"] for x in chunk_items]
            cap_words: list[CaptionWord] = []
            for x in chunk_items:
                wst = round(max(st, min(en - 0.05, scene_offset + float(x["start_s"]))), 3)
                wen = round(max(wst + 0.05, min(en, scene_offset + float(x["end_s"]))), 3)
                cap_words.append(CaptionWord(word=x["token"], start_s=wst, end_s=wen))

            entries.append(CaptionEntry(
                index=idx,
                start_s=st,
                end_s=en,
                text=_wrap_caption_text(chunk_tokens),
                words=cap_words,
            ))
            idx += 1
            chunk_items = []
            chunk_start = None

        for item in aligned:
            tok = item["token"]
            cand = " ".join([x["token"] for x in chunk_items] + [tok])
            dur_if_added = (item["end_s"] - (chunk_start if chunk_start is not None else item["start_s"]))
            if chunk_items and (len(cand) > MAX_CHARS_PER_LINE * 2 or len(chunk_items) >= MAX_WORDS_PER_CAPTION or dur_if_added > 3.6):
                flush()
            if chunk_start is None:
                chunk_start = item["start_s"]
            chunk_items.append(item)
            chunk_end = item["end_s"]
            if tok.endswith((".", "!", "?")) and len(chunk_items) >= 4:
                flush()
            elif tok.endswith((",", ";", ":")) and len(chunk_items) >= 6:
                flush()
        flush()
        scene_offset = round(scene_offset + dur, 3)
    return entries


def validate_captions(captions: list[CaptionEntry], sb: Storyboard, total_video_s: float) -> CaptionValidationReport:
    issues: list[str] = []
    if not captions:
        return CaptionValidationReport(ok=False, caption_count=0, issues=["No caption segments were generated."])

    expected_words = words(" ".join(s.narration_text for s in sb.scenes))
    caption_words = words(" ".join(c.text for c in captions))
    if len(caption_words) < len(expected_words) * 0.9:
        issues.append(f"Missing caption words: captions contain {len(caption_words)}/{len(expected_words)} script words.")

    prev_end = -1.0
    for c in captions:
        dur = c.end_s - c.start_s
        if dur <= 0:
            issues.append(f"Caption #{c.index} has non-positive duration ({c.start_s:.2f}s -> {c.end_s:.2f}s).")
        if dur < 0.22:
            issues.append(f"Caption #{c.index} is too brief ({dur:.2f}s < 0.22s).")
        if dur > MAX_CAP_DUR + 1.0:
            issues.append(f"Caption #{c.index} is too long ({dur:.2f}s).")
        if c.start_s < prev_end - 0.005:
            issues.append(f"Caption #{c.index} overlaps previous caption ({c.start_s:.2f}s < {prev_end:.2f}s).")
        if c.end_s > total_video_s + 0.35:
            issues.append(f"Caption #{c.index} extends past video end ({c.end_s:.2f}s > {total_video_s:.2f}s).")
        lines = c.text.splitlines()
        if len(lines) > MAX_LINES:
            issues.append(f"Caption #{c.index} exceeds {MAX_LINES} lines (safe area violation).")
        if any(len(ln) > MAX_CHARS_PER_LINE + 8 for ln in lines):
            issues.append(f"Caption #{c.index} line exceeds safe width ({max(len(ln) for ln in lines)} chars).")
        cps = len(c.text.replace("\n", " ")) / max(0.1, dur)
        if cps > MAX_CPS + 8:
            issues.append(f"Caption #{c.index} reading speed too high ({cps:.1f} chars/s).")
        prev_end = c.end_s

    return CaptionValidationReport(ok=(len(issues) == 0), caption_count=len(captions), issues=issues)
