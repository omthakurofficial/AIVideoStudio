#!/usr/bin/env python3
"""Local Kokoro-82M neural TTS synthesizer with exact word-level timestamps (`res.tokens`).
Supports single-scene CLI flags or `--batch-json` (loads KPipeline once for all scenes).
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import numpy as np
import soundfile as sf

try:
    from kokoro import KPipeline
except ImportError:
    print("Kokoro not installed in this Python environment.", file=sys.stderr)
    sys.exit(1)


def to_numpy(audio):
    if hasattr(audio, "detach"):
        audio = audio.detach()
    if hasattr(audio, "cpu"):
        audio = audio.cpu()
    if hasattr(audio, "numpy"):
        audio = audio.numpy()
    return np.asarray(audio, dtype=np.float32).reshape(-1)


def synth_one(pipelines: dict[str, KPipeline], text: str, voice: str, speed: float, out_wav: str) -> dict:
    clean = " ".join(text.split()).strip()
    if not clean:
        raise ValueError("Narration text is empty")
    vname = voice.replace("kokoro:", "").strip() or "am_michael"
    lang_code = "b" if vname.startswith("b") else "a"
    if lang_code not in pipelines:
        pipelines[lang_code] = KPipeline(lang_code=lang_code, repo_id="hexgrad/Kokoro-82M")
    pipe = pipelines[lang_code]

    sample_rate = 24000
    chunks: list[np.ndarray] = []
    words_out: list[dict] = []
    offset_s = 0.0

    for res in pipe(clean, voice=vname, speed=speed, split_pattern=r"\n{2,}"):
        if res.audio is None:
            continue
        chunk = to_numpy(res.audio)
        if chunk.size == 0:
            continue
        chunk = chunk - float(np.mean(chunk))
        chunk_dur = len(chunk) / float(sample_rate)
        if hasattr(res, "tokens") and res.tokens:
            for t in res.tokens:
                w = (getattr(t, "text", "") or "").strip()
                st = getattr(t, "start_ts", None)
                en = getattr(t, "end_ts", None)
                if w and st is not None and en is not None:
                    words_out.append({
                        "word": w,
                        "start_s": round(offset_s + float(st), 3),
                        "end_s": round(offset_s + max(float(st) + 0.06, float(en)), 3),
                    })
        chunks.append(chunk)
        offset_s += chunk_dur

    if not chunks:
        raise RuntimeError("Kokoro produced no audio chunks")

    full_audio = np.concatenate(chunks) if len(chunks) > 1 else chunks[0]
    peak = float(np.max(np.abs(full_audio))) if full_audio.size else 0.0
    if peak > 0.98:
        full_audio = full_audio * (0.95 / peak)

    Path(out_wav).parent.mkdir(parents=True, exist_ok=True)
    sf.write(out_wav, full_audio, sample_rate, subtype="PCM_16")
    dur = round(len(full_audio) / float(sample_rate), 3)
    return {"out_wav": out_wav, "duration_s": dur, "words": words_out, "voice": vname}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--text", type=str)
    ap.add_argument("--voice", type=str, default="am_michael")
    ap.add_argument("--speed", type=float, default=1.0)
    ap.add_argument("--out", type=str)
    ap.add_argument("--batch-json", type=str, help="Path to JSON file containing list of {text, voice, speed, out}")
    args = ap.parse_args()

    pipelines: dict[str, KPipeline] = {}
    if args.batch_json:
        items = json.loads(Path(args.batch_json).read_text(encoding="utf-8"))
        results = [synth_one(pipelines, it["text"], it.get("voice", "am_michael"), float(it.get("speed", 1.0)), it["out"]) for it in items]
        print(json.dumps({"ok": True, "results": results}))
        return

    if not args.text or not args.out:
        print("Provide --text and --out, or --batch-json", file=sys.stderr)
        sys.exit(1)
    res = synth_one(pipelines, args.text, args.voice, args.speed, args.out)
    print(json.dumps({"ok": True, **res}))


if __name__ == "__main__":
    main()
