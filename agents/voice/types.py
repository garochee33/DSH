"""Shared result types for DSH voice pipelines."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class SpeechSegment:
    """Speech region in seconds."""

    start: float
    end: float
    confidence: float | None = None
    source: str = "vad"

    @property
    def duration(self) -> float:
        return max(0.0, self.end - self.start)

    def to_dict(self) -> dict[str, float | str | None]:
        return asdict(self)


@dataclass(frozen=True)
class VoiceCost:
    """Cost estimate for a voice provider call."""

    provider: str
    estimated_usd: float
    unit: str
    quantity: float

    def to_dict(self) -> dict[str, float | str]:
        return asdict(self)


@dataclass(frozen=True)
class TranscriptionResult:
    """Normalized ASR result across local and cloud providers."""

    text: str
    provider: str
    source: str
    cloud: bool
    audio_seconds: float
    speech_segments: list[SpeechSegment]
    cost: VoiceCost
    fallback_used: bool = False
    warning: str | None = None

    def to_dict(self) -> dict:
        data = asdict(self)
        data["speech_segments"] = [s.to_dict() for s in self.speech_segments]
        data["cost"] = self.cost.to_dict()
        return data


@dataclass(frozen=True)
class SpeechSynthesisResult:
    """Normalized TTS result."""

    audio_path: Path
    provider: str
    voice_id: str
    model: str
    output_format: str
    characters: int
    cost: VoiceCost

    def to_dict(self) -> dict:
        data = asdict(self)
        data["audio_path"] = str(self.audio_path)
        data["cost"] = self.cost.to_dict()
        return data
