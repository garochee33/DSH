"""Local voice activity detection.

Prefers a local Silero ONNX model when present and falls back to a deterministic
energy gate so the pipeline still works before weights are bootstrapped.
"""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np

from agents.voice.audio import SAMPLE_RATE, load_audio_mono_16k
from agents.voice.types import SpeechSegment

DEFAULT_VAD_MODEL = Path(
    os.environ.get(
        "DOME_VAD_MODEL",
        str(Path.home() / "DOME-HUB" / "models" / "asr" / "silero_vad.onnx"),
    )
)


class VadUnavailable(RuntimeError):
    """Raised when a configured model cannot run."""


class SileroOnnxVad:
    """Minimal Silero ONNX wrapper for 16 kHz mono audio."""

    def __init__(self, model_path: str | Path = DEFAULT_VAD_MODEL) -> None:
        path = Path(model_path).expanduser()
        if not path.is_file():
            raise VadUnavailable(f"Silero VAD model not found: {path}")

        import onnxruntime as ort

        opts = ort.SessionOptions()
        opts.inter_op_num_threads = 1
        opts.intra_op_num_threads = 1
        providers = ["CPUExecutionProvider"]
        self.session = ort.InferenceSession(str(path), sess_options=opts, providers=providers)
        self._state = np.zeros((2, 1, 128), dtype=np.float32)
        self._context = np.zeros((1, 64), dtype=np.float32)

    def reset(self) -> None:
        self._state.fill(0.0)
        self._context.fill(0.0)

    def probabilities(self, samples: np.ndarray) -> list[float]:
        self.reset()
        probs: list[float] = []
        window = 512
        for start in range(0, len(samples), window):
            chunk = samples[start : start + window]
            if len(chunk) < window:
                chunk = np.pad(chunk, (0, window - len(chunk)))
            framed = np.concatenate([self._context, chunk.reshape(1, -1)], axis=1)
            outputs = self.session.run(
                None,
                {
                    "input": framed.astype(np.float32, copy=False),
                    "state": self._state,
                    "sr": np.array(SAMPLE_RATE, dtype=np.int64),
                },
            )
            prob, state = outputs[0], outputs[1]
            probs.append(float(np.ravel(prob)[0]))
            self._state = state
            self._context = framed[:, -64:]
        return probs

    def detect(
        self,
        samples: np.ndarray,
        threshold: float = 0.5,
        min_speech_ms: int = 250,
        min_silence_ms: int = 100,
        speech_pad_ms: int = 30,
    ) -> list[SpeechSegment]:
        probs = self.probabilities(samples)
        return _segments_from_probabilities(
            probs=probs,
            audio_samples=len(samples),
            threshold=threshold,
            min_speech_ms=min_speech_ms,
            min_silence_ms=min_silence_ms,
            speech_pad_ms=speech_pad_ms,
            source="silero-onnx",
        )


class VadDetector:
    """Local VAD facade with Silero-first, energy-fallback behavior."""

    def __init__(self, model_path: str | Path = DEFAULT_VAD_MODEL) -> None:
        self.model_path = Path(model_path).expanduser()

    def detect(self, audio_path: str | Path) -> list[SpeechSegment]:
        samples = load_audio_mono_16k(audio_path)
        if self.model_path.is_file():
            try:
                return SileroOnnxVad(self.model_path).detect(samples)
            except Exception:
                # Model failures should not disable the whole local pipeline.
                pass
        return energy_vad(samples)


def detect_speech(audio_path: str | Path) -> list[SpeechSegment]:
    """Detect speech regions in seconds using the configured local VAD."""

    return VadDetector().detect(audio_path)


def energy_vad(
    samples: np.ndarray,
    frame_ms: int = 30,
    hop_ms: int = 10,
    min_speech_ms: int = 250,
    min_silence_ms: int = 120,
    speech_pad_ms: int = 40,
) -> list[SpeechSegment]:
    """Small deterministic fallback VAD based on short-time energy."""

    if len(samples) == 0:
        return []

    frame = max(1, int(SAMPLE_RATE * frame_ms / 1000))
    hop = max(1, int(SAMPLE_RATE * hop_ms / 1000))
    starts = list(range(0, max(1, len(samples) - frame + 1), hop))
    if starts[-1] + frame < len(samples):
        starts.append(max(0, len(samples) - frame))

    rms = []
    for start in starts:
        chunk = samples[start : start + frame]
        rms.append(float(np.sqrt(np.mean(np.square(chunk), dtype=np.float64) + 1e-12)))

    db = 20.0 * np.log10(np.array(rms) + 1e-8)
    noise_floor = float(np.percentile(db, 20))
    active_floor = float(np.percentile(db, 80))
    threshold = max(noise_floor + 10.0, -45.0)
    if active_floor - noise_floor < 6.0:
        threshold = active_floor + 3.0

    active = db > threshold
    return _segments_from_mask(
        active=active,
        scores=np.clip((db - threshold + 20.0) / 20.0, 0.0, 1.0),
        starts=starts,
        frame=frame,
        min_speech_ms=min_speech_ms,
        min_silence_ms=min_silence_ms,
        speech_pad_ms=speech_pad_ms,
        audio_samples=len(samples),
        source="energy",
    )


def _segments_from_probabilities(
    probs: list[float],
    audio_samples: int,
    threshold: float,
    min_speech_ms: int,
    min_silence_ms: int,
    speech_pad_ms: int,
    source: str,
) -> list[SpeechSegment]:
    active = np.array(probs) >= threshold
    starts = [i * 512 for i in range(len(probs))]
    return _segments_from_mask(
        active=active,
        scores=np.array(probs, dtype=np.float32),
        starts=starts,
        frame=512,
        min_speech_ms=min_speech_ms,
        min_silence_ms=min_silence_ms,
        speech_pad_ms=speech_pad_ms,
        audio_samples=audio_samples,
        source=source,
    )


def _segments_from_mask(
    active: np.ndarray,
    scores: np.ndarray,
    starts: list[int],
    frame: int,
    min_speech_ms: int,
    min_silence_ms: int,
    speech_pad_ms: int,
    audio_samples: int,
    source: str,
) -> list[SpeechSegment]:
    min_speech = int(SAMPLE_RATE * min_speech_ms / 1000)
    min_silence = int(SAMPLE_RATE * min_silence_ms / 1000)
    step = starts[1] - starts[0] if len(starts) > 1 else frame
    min_silence_frames = max(1, int(np.ceil(min_silence / step)))
    pad = int(SAMPLE_RATE * speech_pad_ms / 1000)

    segments: list[tuple[int, int, float]] = []
    in_speech = False
    speech_start = 0
    last_active_end = 0
    silence_count = 0
    score_bucket: list[float] = []

    for is_active, start, score in zip(active, starts, scores, strict=False):
        end = min(audio_samples, start + frame)
        if is_active:
            if not in_speech:
                in_speech = True
                speech_start = start
                score_bucket = []
            last_active_end = end
            silence_count = 0
            score_bucket.append(float(score))
        elif in_speech:
            silence_count += 1
            if silence_count >= min_silence_frames:
                duration = last_active_end - speech_start
                if duration >= min_speech:
                    confidence = float(np.mean(score_bucket)) if score_bucket else 0.0
                    segments.append((speech_start, last_active_end, confidence))
                in_speech = False
                score_bucket = []

    if in_speech and last_active_end - speech_start >= min_speech:
        confidence = float(np.mean(score_bucket)) if score_bucket else 0.0
        segments.append((speech_start, last_active_end, confidence))

    out: list[SpeechSegment] = []
    for start, end, confidence in segments:
        padded_start = max(0, start - pad)
        padded_end = min(audio_samples, end + pad)
        out.append(
            SpeechSegment(
                start=round(padded_start / SAMPLE_RATE, 3),
                end=round(padded_end / SAMPLE_RATE, 3),
                confidence=round(confidence, 4),
                source=source,
            )
        )
    return _merge_close_segments(out)


def _merge_close_segments(
    segments: list[SpeechSegment],
    gap_seconds: float = 0.12,
) -> list[SpeechSegment]:
    if not segments:
        return []

    merged = [segments[0]]
    for segment in segments[1:]:
        previous = merged[-1]
        if segment.start - previous.end <= gap_seconds:
            confidence_values = [
                v for v in (previous.confidence, segment.confidence) if v is not None
            ]
            confidence = sum(confidence_values) / len(confidence_values) if confidence_values else None
            merged[-1] = SpeechSegment(
                start=previous.start,
                end=max(previous.end, segment.end),
                confidence=round(confidence, 4) if confidence is not None else None,
                source=previous.source,
            )
        else:
            merged.append(segment)
    return merged
