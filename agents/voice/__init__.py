"""DOME-HUB local-first voice stack."""

from agents.voice.pipeline import (
    CloudProviderDisabled,
    LocalAsrUnavailable,
    LocalWhisperAsr,
    VoicePipeline,
    VoicePipelineError,
)
from agents.voice.loop import VoiceLoop
from agents.voice.types import SpeechSegment, SpeechSynthesisResult, TranscriptionResult, VoiceCost
from agents.voice.vad import VadDetector, detect_speech
from agents.voice.whisper_cpp import WhisperCppClient, WhisperCppUnavailable

__all__ = [
    "CloudProviderDisabled",
    "LocalAsrUnavailable",
    "LocalWhisperAsr",
    "SpeechSegment",
    "SpeechSynthesisResult",
    "TranscriptionResult",
    "VadDetector",
    "VoiceCost",
    "VoiceLoop",
    "VoicePipeline",
    "VoicePipelineError",
    "WhisperCppClient",
    "WhisperCppUnavailable",
    "detect_speech",
]
