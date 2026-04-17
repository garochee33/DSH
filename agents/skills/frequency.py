"""Frequency skill — FFT, signal synthesis, sacred tones, brainwaves."""
from __future__ import annotations
import numpy as np
from scipy import signal as scipy_signal

SKILL = "frequency"

_SOLFEGGIO = {
    "UT":  174.0,
    "RE":  285.0,
    "MI":  396.0,
    "FA":  417.0,
    "SOL": 528.0,
    "LA":  639.0,
    "TI":  741.0,
    "SI":  852.0,
    "OM":  963.0,
}

_BRAINWAVE_BANDS = {
    "delta": (0.5, 4.0),
    "theta": (4.0, 8.0),
    "alpha": (8.0, 14.0),
    "beta":  (14.0, 30.0),
    "gamma": (30.0, 100.0),
}

_SCHUMANN = [7.83 * k for k in range(1, 8)]  # first 7 harmonics


def solfeggio() -> dict[str, float]:
    return dict(_SOLFEGGIO)


def brainwave_bands() -> dict[str, tuple]:
    return dict(_BRAINWAVE_BANDS)


def schumann_resonances() -> list[float]:
    return list(_SCHUMANN)


def synthesize(frequencies: list[float], amplitudes: list[float],
               duration: float = 1.0, sr: int = 44100) -> np.ndarray:
    """Synthesize a waveform from frequency/amplitude pairs."""
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    wave = sum(a * np.sin(2 * np.pi * f * t)
               for f, a in zip(frequencies, amplitudes))
    return wave / (np.max(np.abs(wave)) + 1e-9)  # normalize


def fft_spectrum(sig: np.ndarray, sample_rate: int = 44100) -> dict:
    """Returns frequency bins and magnitude spectrum."""
    n = len(sig)
    freqs = np.fft.rfftfreq(n, d=1/sample_rate)
    magnitudes = np.abs(np.fft.rfft(sig))
    return {"frequencies": freqs, "magnitudes": magnitudes}


def wavelet_transform(sig: np.ndarray, wavelet: str = "morl") -> tuple:
    """Continuous wavelet transform. Returns (coefficients, frequencies)."""
    widths = np.arange(1, 128)
    cwt = scipy_signal.cwt(sig, scipy_signal.morlet2, widths)
    return cwt, widths


def dominant_frequency(sig: np.ndarray, sample_rate: int = 44100) -> float:
    spec = fft_spectrum(sig, sample_rate)
    idx = np.argmax(spec["magnitudes"])
    return float(spec["frequencies"][idx])


def verify() -> bool:
    wave = synthesize([528.0], [1.0], duration=0.1, sr=44100)
    assert len(wave) == 4410
    spec = fft_spectrum(wave, 44100)
    dom = dominant_frequency(wave, 44100)
    assert abs(dom - 528.0) < 5.0, f"dominant freq off: {dom}"
    assert solfeggio()["SOL"] == 528.0
    assert len(schumann_resonances()) == 7
    return True
