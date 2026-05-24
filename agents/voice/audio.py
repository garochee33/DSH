"""Audio loading helpers for local voice inference."""

from __future__ import annotations

import shutil
import subprocess
import wave
from pathlib import Path

import numpy as np

SAMPLE_RATE = 16_000


class AudioLoadError(RuntimeError):
    """Raised when audio cannot be decoded into mono 16 kHz PCM."""


def load_audio_mono_16k(audio_path: str | Path) -> np.ndarray:
    """Decode any ffmpeg-supported audio file to float32 mono 16 kHz samples."""

    path = Path(audio_path).expanduser()
    if not path.is_file():
        raise AudioLoadError(f"Audio file does not exist: {path}")

    if shutil.which("ffmpeg"):
        return _load_with_ffmpeg(path)

    if path.suffix.lower() == ".wav":
        return _load_wav_fallback(path)

    raise AudioLoadError("ffmpeg is required for non-WAV audio decoding")


def audio_duration_seconds(audio_path: str | Path) -> float:
    samples = load_audio_mono_16k(audio_path)
    return len(samples) / SAMPLE_RATE


def _load_with_ffmpeg(path: Path) -> np.ndarray:
    cmd = [
        "ffmpeg",
        "-nostdin",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(path),
        "-ac",
        "1",
        "-ar",
        str(SAMPLE_RATE),
        "-f",
        "f32le",
        "-",
    ]
    proc = subprocess.run(cmd, capture_output=True, check=False)
    if proc.returncode != 0:
        error = proc.stderr.decode("utf-8", errors="replace").strip()
        raise AudioLoadError(f"ffmpeg failed to decode {path}: {error}")
    return np.frombuffer(proc.stdout, dtype="<f4").astype(np.float32, copy=False)


def _load_wav_fallback(path: Path) -> np.ndarray:
    with wave.open(str(path), "rb") as wav:
        channels = wav.getnchannels()
        sample_rate = wav.getframerate()
        sample_width = wav.getsampwidth()
        frames = wav.readframes(wav.getnframes())

    if sample_rate != SAMPLE_RATE:
        raise AudioLoadError("ffmpeg is required to resample WAV files")

    if sample_width == 1:
        audio = (np.frombuffer(frames, dtype=np.uint8).astype(np.float32) - 128.0) / 128.0
    elif sample_width == 2:
        audio = np.frombuffer(frames, dtype="<i2").astype(np.float32) / 32768.0
    elif sample_width == 4:
        audio = np.frombuffer(frames, dtype="<i4").astype(np.float32) / 2147483648.0
    else:
        raise AudioLoadError(f"Unsupported WAV sample width: {sample_width}")

    if channels > 1:
        audio = audio.reshape(-1, channels).mean(axis=1)
    return audio.astype(np.float32, copy=False)
