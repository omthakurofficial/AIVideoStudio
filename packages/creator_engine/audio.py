"""Creator Audio Pipeline: Local Neural Narration, Tech Beat Synth, and Sidechain Ducking."""
from __future__ import annotations

import json
import math
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import soundfile as sf


def find_kokoro_python() -> str:
    """Locate Python environment with Kokoro-82M installed."""
    candidates = [
        "/home/omthakur/yt-motion-studio-phase-c-final/.ytms/kokoro-venv/bin/python",
        sys.executable,
        os.path.expanduser("~/.ytms/kokoro-venv/bin/python"),
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return sys.executable


def synthesize_narration(
    text: str,
    out_wav: str,
    voice: str = "am_adam",
    speed: float = 1.0,
) -> Dict[str, Any]:
    """Generate local neural speech with exact word-level timestamps."""
    kokoro_py = find_kokoro_python()
    root_dir = Path(__file__).resolve().parents[2]
    tts_script = root_dir / "scripts" / "tts_kokoro.py"

    cmd = [
        kokoro_py,
        str(tts_script),
        "--text", text,
        "--voice", voice,
        "--speed", str(speed),
        "--out", out_wav,
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"Kokoro synthesis failed: {proc.stderr}")

    for line in reversed(proc.stdout.strip().split("\n")):
        line = line.strip()
        if line.startswith("{") and line.endswith("}"):
            try:
                data = json.loads(line)
                if data.get("ok"):
                    return data
            except json.JSONDecodeError:
                pass
    raise RuntimeError(f"Could not parse Kokoro output: {proc.stdout}")


def synthesize_tech_beat(
    duration_s: float,
    out_wav: str,
    bpm: float = 122.0,
    sr: int = 48000,
) -> str:
    """Synthesize a dynamic 122 BPM tech creator beat (808 kick, clap, hats, bass, chord stabs)."""
    n_samples = int(duration_s * sr)
    mix = np.zeros(n_samples, dtype=np.float32)

    beat_dur = 60.0 / bpm
    step_dur = beat_dur / 4.0  # 16th note

    # Pre-render drum elements
    # 1. 808 Kick
    kick_len = int(0.35 * sr)
    t_k = np.linspace(0, 0.35, kick_len, endpoint=False)
    f_k = 155.0 * np.exp(-t_k * 24.0) + 45.0
    phase_k = np.cumsum(2 * np.pi * f_k / sr)
    env_k = np.exp(-t_k * 8.0)
    kick = np.sin(phase_k) * env_k * 0.95

    # 2. Clap / Snare
    clap_len = int(0.20 * sr)
    t_c = np.linspace(0, 0.20, clap_len, endpoint=False)
    noise_c = np.random.uniform(-1.0, 1.0, clap_len).astype(np.float32)
    env_c = np.exp(-t_c * 20.0)
    burst = np.zeros(clap_len, dtype=np.float32)
    for off_ms in [0, 12, 24]:
        idx = int((off_ms / 1000.0) * sr)
        if idx < clap_len:
            burst[idx:min(idx + int(0.015 * sr), clap_len)] += 0.4
    clap = (noise_c * env_c * 0.7 + burst) * 0.45

    # 3. Closed Hi-Hat (crisp 16th notes)
    hat_len = int(0.045 * sr)
    t_h = np.linspace(0, 0.045, hat_len, endpoint=False)
    noise_h = np.random.uniform(-1.0, 1.0, hat_len).astype(np.float32)
    # Simple high-pass via difference
    diff_h = np.diff(noise_h, prepend=0)
    hat = diff_h * np.exp(-t_h * 85.0) * 0.18

    # 4. Open Hi-Hat
    ohat_len = int(0.18 * sr)
    t_oh = np.linspace(0, 0.18, ohat_len, endpoint=False)
    noise_oh = np.random.uniform(-1.0, 1.0, ohat_len).astype(np.float32)
    diff_oh = np.diff(noise_oh, prepend=0)
    ohat = diff_oh * np.exp(-t_oh * 16.0) * 0.22

    # Step through 16th notes
    total_steps = int(duration_s / step_dur) + 1
    # Simple F-minor bass notes: F1 (43.65), Ab1 (51.91), Bb1 (58.27), C2 (65.41)
    bass_freqs = [43.65, 43.65, 51.91, 58.27]

    for step in range(total_steps):
        t_start = step * step_dur
        s_idx = int(t_start * sr)
        if s_idx >= n_samples:
            break

        step_in_bar = step % 16
        beat_in_bar = step_in_bar // 4

        # Kick on beats 0 and 2 (steps 0 and 8), plus occasional syncopation on step 14
        if step_in_bar in [0, 8] or (step_in_bar == 14 and (step // 16) % 2 == 1):
            e_idx = min(s_idx + kick_len, n_samples)
            mix[s_idx:e_idx] += kick[:e_idx - s_idx] * 0.75

        # Clap on beats 1 and 3 (steps 4 and 12)
        if step_in_bar in [4, 12]:
            e_idx = min(s_idx + clap_len, n_samples)
            mix[s_idx:e_idx] += clap[:e_idx - s_idx] * 0.65

        # Hats: 16th pattern, open hat on off-beats (steps 2, 6, 10, 14)
        if step_in_bar in [2, 6, 10, 14]:
            e_idx = min(s_idx + ohat_len, n_samples)
            mix[s_idx:e_idx] += ohat[:e_idx - s_idx] * 0.40
        else:
            velocity = 0.55 if step_in_bar % 2 == 0 else 0.35
            e_idx = min(s_idx + hat_len, n_samples)
            mix[s_idx:e_idx] += hat[:e_idx - s_idx] * velocity

        # Bassline on 8th notes
        if step_in_bar % 2 == 0:
            bar_num = (step // 16) % len(bass_freqs)
            bf = bass_freqs[bar_num]
            bass_len = int(0.22 * sr)
            t_b = np.linspace(0, 0.22, bass_len, endpoint=False)
            b_wave = np.sin(2 * np.pi * bf * t_b) + 0.35 * np.sin(4 * np.pi * bf * t_b)
            b_env = np.exp(-t_b * 6.0)
            e_idx = min(s_idx + bass_len, n_samples)
            mix[s_idx:e_idx] += (b_wave * b_env)[:e_idx - s_idx] * 0.38

    # Light stereo width simulation
    stereo = np.column_stack([mix, mix])
    Path(out_wav).parent.mkdir(parents=True, exist_ok=True)
    sf.write(out_wav, stereo, sr, subtype="PCM_16")
    return out_wav


def duck_and_mix(
    vocal_wav: str,
    beat_wav: str,
    out_wav: str,
    duck_gain: float = 0.22,
    swell_gain: float = 0.60,
    target_sr: int = 48000,
) -> str:
    """Dynamic sidechain ducking in NumPy: cuts beat during voice, swells during breaks."""
    # Convert vocal to 48kHz stereo float
    v_data, v_sr = sf.read(vocal_wav, dtype="float32")
    if len(v_data.shape) == 1:
        v_mono = v_data
    else:
        v_mono = np.mean(v_data, axis=1)

    # Resample vocal to 48k if needed
    if v_sr != target_sr:
        num_target = int(len(v_mono) * target_sr / v_sr)
        from scipy.signal import resample
        v_mono = resample(v_mono, num_target).astype(np.float32)

    # Read beat
    b_data, b_sr = sf.read(beat_wav, dtype="float32")
    if b_sr != target_sr:
        num_target = int(len(b_data) * target_sr / b_sr)
        from scipy.signal import resample
        b_data = resample(b_data, num_target).astype(np.float32)

    if len(b_data.shape) == 1:
        b_data = np.column_stack([b_data, b_data])

    total_len = max(len(v_mono), len(b_data))

    # Pad arrays to match length
    if len(v_mono) < total_len:
        v_mono = np.pad(v_mono, (0, total_len - len(v_mono)))
    if len(b_data) < total_len:
        b_data = np.pad(b_data, ((0, total_len - len(b_data)), (0, 0)))

    # Compute RMS envelope for voiceover (Attack 10ms, Release 320ms)
    att_coeff = np.exp(-1.0 / (0.010 * target_sr))
    rel_coeff = np.exp(-1.0 / (0.320 * target_sr))

    env = np.zeros(total_len, dtype=np.float32)
    curr_env = 0.0
    abs_v = np.abs(v_mono)

    for i in range(total_len):
        val = abs_v[i]
        if val > curr_env:
            curr_env = (1.0 - att_coeff) * val + att_coeff * curr_env
        else:
            curr_env = (1.0 - rel_coeff) * val + rel_coeff * curr_env
        env[i] = curr_env

    # Map envelope to ducking gain:
    # 0 envelope -> swell_gain (0.60)
    # High envelope -> duck_gain (0.22)
    threshold = 0.035
    norm_env = np.clip(env / threshold, 0.0, 1.0)
    music_gain = swell_gain - norm_env * (swell_gain - duck_gain)

    # Apply gain to music
    ducked_beat = b_data * music_gain[:, np.newaxis]

    # Voice boost + soft saturation (tanh)
    boosted_voice = np.tanh(v_mono * 2.2) * 0.85
    voice_stereo = np.column_stack([boosted_voice, boosted_voice])

    final_mix = ducked_beat + voice_stereo

    # Normalize peak to -1.0 dB (0.89)
    peak = np.max(np.abs(final_mix))
    if peak > 0.89:
        final_mix = final_mix * (0.89 / peak)

    Path(out_wav).parent.mkdir(parents=True, exist_ok=True)
    sf.write(out_wav, final_mix, target_sr, subtype="PCM_16")

    # Also output MP3 for browser player embedding
    out_mp3 = str(Path(out_wav).with_suffix(".mp3"))
    cmd = [
        "ffmpeg", "-y", "-i", out_wav,
        "-codec:a", "libmp3lame", "-qscale:a", "2",
        out_mp3
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    return out_wav
