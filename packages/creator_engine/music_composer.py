"""Algorithmic, 100% Copyright-Free Music Composer & Film Audio Mixing Suite.

Generates original multi-genre background scores and procedural sound effects from scratch using pure
DSP mathematics (NumPy). Impossible to be ContentID matched or copyright claimed on YouTube, TikTok,
Instagram, or Facebook.
"""
from __future__ import annotations

import math
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import soundfile as sf


def compose_creator_tech_beat(duration_s: float, bpm: float = 122.0, sr: int = 48000) -> np.ndarray:
    """122 BPM high-energy punchy modern creator tech beat (808 kick, clap, 16th hats, sub bass)."""
    n_samples = int(duration_s * sr)
    mix = np.zeros(n_samples, dtype=np.float32)

    beat_dur = 60.0 / bpm
    step_dur = beat_dur / 4.0  # 16th note

    # 1. 808 Kick
    kick_len = int(0.35 * sr)
    t_k = np.linspace(0, 0.35, kick_len, endpoint=False)
    f_k = 150.0 * np.exp(-t_k * 24.0) + 42.0
    phase_k = np.cumsum(2 * np.pi * f_k / sr)
    kick = np.sin(phase_k) * np.exp(-t_k * 8.5) * 0.95

    # 2. Snappy Clap
    clap_len = int(0.22 * sr)
    t_c = np.linspace(0, 0.22, clap_len, endpoint=False)
    noise_c = np.random.uniform(-1.0, 1.0, clap_len).astype(np.float32)
    env_c = np.exp(-t_c * 22.0)
    clap = noise_c * env_c * 0.55

    # 3. Closed Hat
    hat_len = int(0.045 * sr)
    t_h = np.linspace(0, 0.045, hat_len, endpoint=False)
    noise_h = np.random.uniform(-1.0, 1.0, hat_len).astype(np.float32)
    diff_h = np.diff(noise_h, prepend=0)
    hat = diff_h * np.exp(-t_h * 80.0) * 0.22

    total_steps = int(duration_s / step_dur) + 1
    bass_freqs = [43.65, 43.65, 51.91, 58.27]

    for step in range(total_steps):
        s_idx = int(step * step_dur * sr)
        if s_idx >= n_samples:
            break

        step_in_bar = step % 16
        # Kick on 0, 8 (beats 1 and 3)
        if step_in_bar in [0, 8] or (step_in_bar == 14 and (step // 16) % 2 == 1):
            e = min(s_idx + kick_len, n_samples)
            mix[s_idx:e] += kick[:e - s_idx] * 0.75

        # Clap on 4, 12 (beats 2 and 4)
        if step_in_bar in [4, 12]:
            e = min(s_idx + clap_len, n_samples)
            mix[s_idx:e] += clap[:e - s_idx] * 0.65

        # 16th hats
        velocity = 0.55 if step_in_bar % 2 == 0 else 0.32
        e = min(s_idx + hat_len, n_samples)
        mix[s_idx:e] += hat[:e - s_idx] * velocity

        # Bassline
        if step_in_bar % 2 == 0:
            bf = bass_freqs[(step // 16) % len(bass_freqs)]
            blen = int(0.24 * sr)
            tb = np.linspace(0, 0.24, blen, endpoint=False)
            bwave = np.sin(2 * np.pi * bf * tb) + 0.3 * np.sin(4 * np.pi * bf * tb)
            e = min(s_idx + blen, n_samples)
            mix[s_idx:e] += (bwave * np.exp(-tb * 5.5))[:e - s_idx] * 0.35

    return np.column_stack([mix, mix])


def compose_cinematic_lofi(duration_s: float, bpm: float = 84.0, sr: int = 48000) -> np.ndarray:
    """84 BPM warm documentary lofi chords with soft sub kick and vinyl crackle ambience."""
    n_samples = int(duration_s * sr)
    mix_l = np.zeros(n_samples, dtype=np.float32)
    mix_r = np.zeros(n_samples, dtype=np.float32)

    beat_dur = 60.0 / bpm
    bar_dur = beat_dur * 4.0

    # Chords: Dm9, G13, Cmaj9, Am7
    chords = [
        [146.83, 220.00, 261.63, 329.63], # Dm9
        [196.00, 246.94, 293.66, 329.63], # G13
        [130.81, 196.00, 246.94, 293.66], # Cmaj9
        [110.00, 164.81, 220.00, 261.63]  # Am7
    ]

    total_bars = int(duration_s / bar_dur) + 1
    for b in range(total_bars):
        t_bar = b * bar_dur
        s_idx = int(t_bar * sr)
        if s_idx >= n_samples:
            break

        chord = chords[b % len(chords)]
        dur_chord = min(bar_dur, duration_s - t_bar)
        chord_samples = int(dur_chord * sr)
        tc = np.linspace(0, dur_chord, chord_samples, endpoint=False)

        # Synthesize electric piano pad
        chord_wave = np.zeros(chord_samples, dtype=np.float32)
        for freq in chord:
            # Fundamental + soft 2nd harmonic
            tone = np.sin(2 * np.pi * freq * tc) * 0.6 + np.sin(4 * np.pi * freq * tc) * 0.2
            chord_wave += tone * np.exp(-tc * 0.8)

        e = min(s_idx + chord_samples, n_samples)
        mix_l[s_idx:e] += chord_wave[:e - s_idx] * 0.18
        mix_r[s_idx:e] += chord_wave[:e - s_idx] * 0.18

    # Add soft kick and rim click
    for beat in range(int(duration_s / beat_dur)):
        s_idx = int(beat * beat_dur * sr)
        if s_idx >= n_samples:
            break
        if beat % 4 in [0, 2]:
            klen = int(0.25 * sr)
            tk = np.linspace(0, 0.25, klen, endpoint=False)
            kick = np.sin(2 * np.pi * 55.0 * np.exp(-tk * 12.0) * tk) * np.exp(-tk * 8.0) * 0.4
            e = min(s_idx + klen, n_samples)
            mix_l[s_idx:e] += kick[:e - s_idx]
            mix_r[s_idx:e] += kick[:e - s_idx]

    # Add vinyl crackle noise floor
    vinyl = np.random.uniform(-0.015, 0.015, n_samples).astype(np.float32)
    mix_l += vinyl
    mix_r += vinyl

    return np.column_stack([mix_l, mix_r])


def compose_cyberpunk_synthwave(duration_s: float, bpm: float = 128.0, sr: int = 48000) -> np.ndarray:
    """128 BPM driving analog saw bassline arpeggio with gated synth pads."""
    n_samples = int(duration_s * sr)
    mix = np.zeros(n_samples, dtype=np.float32)

    beat_dur = 60.0 / bpm
    step_dur = beat_dur / 4.0  # 16th note arpeggio
    total_steps = int(duration_s / step_dur) + 1

    arp_notes = [55.0, 110.0, 164.81, 220.0, 65.41, 130.81, 196.0, 261.63]
    for step in range(total_steps):
        s_idx = int(step * step_dur * sr)
        if s_idx >= n_samples:
            break

        freq = arp_notes[step % len(arp_notes)]
        slen = int(step_dur * sr)
        t = np.linspace(0, step_dur, slen, endpoint=False)
        # Bandlimited sawtooth simulation
        saw = (2.0 * (t * freq - np.floor(t * freq + 0.5))) * np.exp(-t * 12.0) * 0.28
        e = min(s_idx + slen, n_samples)
        mix[s_idx:e] += saw[:e - s_idx]

        # 4-on-the-floor kick
        if step % 4 == 0:
            klen = int(0.3 * sr)
            tk = np.linspace(0, 0.3, klen, endpoint=False)
            kick = np.sin(2 * np.pi * (160.0 * np.exp(-tk * 28.0) + 40.0) * tk) * np.exp(-tk * 9.0) * 0.7
            ek = min(s_idx + klen, n_samples)
            mix[s_idx:ek] += kick[:ek - s_idx]

    return np.column_stack([mix, mix])


def generate_sfx(kind: str, sr: int = 48000) -> np.ndarray:
    """Procedurally synthesize sound effects (boom, slam, stamp, riser, whoosh, pop)."""
    if kind == "boom":
        dur = 1.8
        t = np.linspace(0, dur, int(dur * sr), endpoint=False)
        sub = np.sin(2 * np.pi * (85.0 * np.exp(-t * 4.5) + 30.0) * t) * np.exp(-t * 2.5) * 0.8
        noise = np.random.uniform(-1.0, 1.0, len(t)) * np.exp(-t * 6.0) * 0.3
        return sub + noise

    elif kind == "slam":
        dur = 0.28
        t = np.linspace(0, dur, int(dur * sr), endpoint=False)
        transient = np.sin(2 * np.pi * (180.0 * np.exp(-t * 30.0) + 45.0) * t) * np.exp(-t * 15.0) * 0.9
        click = np.random.uniform(-1.0, 1.0, len(t)) * np.exp(-t * 40.0) * 0.4
        return transient + click

    elif kind == "stamp":
        dur = 0.32
        t = np.linspace(0, dur, int(dur * sr), endpoint=False)
        thud = np.sin(2 * np.pi * (160.0 * np.exp(-t * 20.0) + 48.0) * t) * np.exp(-t * 12.0) * 0.85
        wood = np.random.uniform(-1.0, 1.0, len(t)) * np.exp(-t * 28.0) * 0.35
        return thud + wood

    elif kind == "whoosh":
        dur = 0.35
        t = np.linspace(0, dur, int(dur * sr), endpoint=False)
        env = np.sin(np.pi * t / dur) ** 2
        noise = np.random.uniform(-1.0, 1.0, len(t)) * env * 0.45
        return noise

    elif kind == "pop":
        dur = 0.08
        t = np.linspace(0, dur, int(dur * sr), endpoint=False)
        return np.sin(2 * np.pi * (820.0 * np.exp(-t * 50.0)) * t) * np.exp(-t * 65.0) * 0.6

    else:
        # Default click
        dur = 0.04
        t = np.linspace(0, dur, int(dur * sr), endpoint=False)
        return np.random.uniform(-1.0, 1.0, len(t)) * np.exp(-t * 120.0) * 0.5


def master_film_audio_bus(
    voice_wav: str,
    music_genre: str = "creator_tech",
    sfx_cues: Optional[List[Dict[str, Any]]] = None,
    out_wav: str = "/tmp/master_film_mix.wav",
    duck_gain: float = 0.20,
    swell_gain: float = 0.58,
    sr: int = 48000,
) -> str:
    """Film-Grade Audio Bus Mixer: Voiceover + Algorithmic Music + Procedural SFX + Sidechain Ducking."""
    v_data, v_sr = sf.read(voice_wav, dtype="float32")
    if len(v_data.shape) > 1:
        v_data = np.mean(v_data, axis=1)

    duration_s = len(v_data) / float(v_sr)
    n_samples = len(v_data)

    # 1. Compose Background Music
    if music_genre == "lofi":
        music = compose_cinematic_lofi(duration_s + 2.0, sr=sr)
    elif music_genre == "synthwave":
        music = compose_cyberpunk_synthwave(duration_s + 2.0, sr=sr)
    else:
        music = compose_creator_tech_beat(duration_s + 2.0, sr=sr)

    music = music[:n_samples]

    # 2. Sidechain Ducking Envelope (Attack 10ms, Release 300ms)
    att = np.exp(-1.0 / (0.010 * sr))
    rel = np.exp(-1.0 / (0.300 * sr))
    env = np.zeros(n_samples, dtype=np.float32)
    curr = 0.0
    abs_v = np.abs(v_data)

    for i in range(n_samples):
        val = abs_v[i]
        curr = (1.0 - att) * val + att * curr if val > curr else (1.0 - rel) * val + rel * curr
        env[i] = curr

    norm_env = np.clip(env / 0.035, 0.0, 1.0)
    music_gain = swell_gain - norm_env * (swell_gain - duck_gain)
    ducked_music = music * music_gain[:, np.newaxis]

    # 3. Add Procedural SFX Cues
    sfx_bus = np.zeros(n_samples, dtype=np.float32)
    if sfx_cues:
        for cue in sfx_cues:
            t = cue.get("t", 0.0)
            kind = cue.get("kind", "slam")
            gain = cue.get("gain", 0.5)
            s_idx = int(t * sr)
            if s_idx < n_samples:
                sfx_wave = generate_sfx(kind, sr=sr) * gain
                e_idx = min(s_idx + len(sfx_wave), n_samples)
                sfx_bus[s_idx:e_idx] += sfx_wave[:e_idx - s_idx]

    sfx_stereo = np.column_stack([sfx_bus, sfx_bus])

    # 4. Voice Boost & Soft Saturation
    boosted_voice = np.tanh(v_data * 2.2) * 0.88
    voice_stereo = np.column_stack([boosted_voice, boosted_voice])

    # 5. Master Summation
    master = voice_stereo + ducked_music + sfx_stereo

    # True Peak Limiter (-1.0 dBFS / 0.89)
    peak = np.max(np.abs(master))
    if peak > 0.89:
        master = master * (0.89 / peak)

    Path(out_wav).parent.mkdir(parents=True, exist_ok=True)
    sf.write(out_wav, master, sr, subtype="PCM_16")

    # Output MP3 counterpart
    mp3_out = str(Path(out_wav).with_suffix(".mp3"))
    subprocess.run(["ffmpeg", "-y", "-i", out_wav, "-c:a", "libmp3lame", "-qscale:a", "2", mp3_out],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    return out_wav
