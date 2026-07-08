"""Local-first voice pipeline with optional ElevenLabs cloud edges."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any

import httpx

from agents.voice.audio import audio_duration_seconds
from agents.voice.types import (
    SpeechSegment,
    SpeechSynthesisResult,
    TranscriptionResult,
    VoiceCost,
)
from agents.voice.asr_worker import (
    WarmWhisperUnavailable,
    get_warm_worker,
    warm_worker_available,
)
from agents.voice.vad import DEFAULT_VAD_MODEL, VadDetector
from agents.voice.whisper_cpp import (
    DEFAULT_WHISPER_CPP_URL,
    WhisperCppClient,
    WhisperCppUnavailable,
)

DOME_ROOT = Path(os.environ.get("DOME_ROOT", str(Path.home() / "DSH"))).expanduser()
DEFAULT_WHISPER_MODEL = os.environ.get("DOME_ASR_MODEL", "base")
DEFAULT_WHISPER_MODEL_DIR = Path(
    os.environ.get(
        "DOME_WHISPER_MODEL_DIR",
        str(DOME_ROOT / "models" / "asr" / "whisper"),
    )
).expanduser()
ELEVENLABS_API_BASE = os.environ.get(
    "ELEVENLABS_API_BASE",
    "https://api.elevenlabs.io",
).rstrip("/")


class VoicePipelineError(RuntimeError):
    """Base voice pipeline failure."""


class CloudProviderDisabled(VoicePipelineError):
    """Raised when a cloud provider call is requested without opt-in."""


class LocalAsrUnavailable(VoicePipelineError):
    """Raised when local ASR cannot run."""


def _truthy(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}


def _spore_guard(provider: str) -> None:
    if os.environ.get("SPORE_GERMINATING") == "1":
        raise CloudProviderDisabled(
            f"[LOCKDOWN] Spore germinating — outbound call to {provider} blocked."
        )


def estimate_tts_cost(text: str, model: str) -> VoiceCost:
    per_1k = 0.05 if any(token in model for token in ("flash", "turbo")) else 0.10
    quantity = len(text) / 1000.0
    return VoiceCost(
        provider="elevenlabs",
        estimated_usd=round(quantity * per_1k, 6),
        unit="1k_characters",
        quantity=round(quantity, 4),
    )


def estimate_stt_cost(audio_seconds: float, model: str) -> VoiceCost:
    per_hour = 0.39 if "realtime" in model else 0.22
    quantity = audio_seconds / 3600.0
    return VoiceCost(
        provider="elevenlabs",
        estimated_usd=round(quantity * per_hour, 6),
        unit="audio_hours",
        quantity=round(quantity, 6),
    )


def zero_cost(provider: str, audio_seconds: float = 0.0) -> VoiceCost:
    return VoiceCost(
        provider=provider,
        estimated_usd=0.0,
        unit="local",
        quantity=audio_seconds,
    )


class LocalWhisperAsr:
    """Whisper CLI adapter that keeps model files under DSH by default."""

    def __init__(
        self,
        model: str = DEFAULT_WHISPER_MODEL,
        model_dir: str | Path = DEFAULT_WHISPER_MODEL_DIR,
        allow_model_download: bool | None = None,
        backend: str | None = None,
        device: str | None = None,
    ) -> None:
        self.model = model
        self.model_dir = Path(model_dir).expanduser()
        self.backend = (backend or os.environ.get("DOME_ASR_BACKEND", "auto")).lower()
        if self.backend not in {"auto", "whispercpp", "worker", "cli"}:
            self.backend = "auto"
        self.device = device or os.environ.get("DOME_ASR_DEVICE", "cpu")
        self.last_provider = "local-whisper-cli"
        self.whisper_cpp = WhisperCppClient()
        self.allow_model_download = (
            _truthy(os.environ.get("DOME_VOICE_ALLOW_MODEL_DOWNLOAD"))
            if allow_model_download is None
            else allow_model_download
        )

    def model_cached(self) -> bool:
        return (self.model_dir / f"{self.model}.pt").is_file()

    def transcribe(
        self,
        audio_path: str | Path,
        speech_segments: list[SpeechSegment],
        language: str | None = None,
    ) -> str:
        if self.backend in {"auto", "whispercpp"}:
            try:
                text = self.whisper_cpp.transcribe(audio_path, speech_segments, language)
                self.last_provider = "local-whisper-cpp-coreml"
                return text
            except WhisperCppUnavailable:
                if self.backend == "whispercpp":
                    raise LocalAsrUnavailable(
                        f"whisper.cpp server unavailable at {self.whisper_cpp.base_url}"
                    )

        if self.backend in {"auto", "worker"}:
            try:
                text = self._transcribe_worker(audio_path, speech_segments, language)
                self.last_provider = "local-whisper-worker"
                return text
            except LocalAsrUnavailable:
                if self.backend == "worker":
                    raise

        text = self._transcribe_cli(audio_path, speech_segments, language)
        self.last_provider = "local-whisper-cli"
        return text

    def warm(self) -> None:
        if self.backend in {"auto", "whispercpp"} and self.whisper_cpp.healthy():
            self.last_provider = "local-whisper-cpp-coreml"
            return
        if self.backend == "whispercpp":
            raise LocalAsrUnavailable(
                f"whisper.cpp server unavailable at {self.whisper_cpp.base_url}"
            )
        if self.backend == "cli":
            return
        try:
            worker = get_warm_worker(
                model=self.model,
                model_dir=self.model_dir,
                allow_model_download=self.allow_model_download,
                device=self.device,
            )
            worker.warm()
            self.last_provider = "local-whisper-worker"
        except WarmWhisperUnavailable as e:
            if self.backend == "worker":
                raise LocalAsrUnavailable(str(e)) from e

    def _transcribe_worker(
        self,
        audio_path: str | Path,
        speech_segments: list[SpeechSegment],
        language: str | None,
    ) -> str:
        try:
            worker = get_warm_worker(
                model=self.model,
                model_dir=self.model_dir,
                allow_model_download=self.allow_model_download,
                device=self.device,
            )
            return worker.transcribe(audio_path, speech_segments, language=language)
        except WarmWhisperUnavailable as e:
            raise LocalAsrUnavailable(str(e)) from e

    def _transcribe_cli(
        self,
        audio_path: str | Path,
        speech_segments: list[SpeechSegment],
        language: str | None,
    ) -> str:
        whisper = shutil.which("whisper")
        if not whisper:
            raise LocalAsrUnavailable("whisper CLI is not installed")

        if not self.allow_model_download and not self.model_cached():
            raise LocalAsrUnavailable(
                f"Whisper model '{self.model}' is not cached in {self.model_dir}. "
                "Run scripts/voice-bootstrap.sh or set DOME_VOICE_ALLOW_MODEL_DOWNLOAD=1."
            )

        self.model_dir.mkdir(parents=True, exist_ok=True)
        path = Path(audio_path).expanduser()
        with tempfile.TemporaryDirectory(prefix="dome-whisper-") as tmp:
            cmd = [
                whisper,
                str(path),
                "--model",
                self.model,
                "--model_dir",
                str(self.model_dir),
                "--output_dir",
                tmp,
                "--output_format",
                "json",
                "--verbose",
                "False",
                "--fp16",
                "False",
            ]
            if language:
                cmd.extend(["--language", language])
            if speech_segments:
                clips = ",".join(f"{s.start:.3f},{s.end:.3f}" for s in speech_segments)
                cmd.extend(["--clip_timestamps", clips])

            proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
            if proc.returncode != 0:
                raise LocalAsrUnavailable(proc.stderr.strip() or "whisper CLI failed")

            outputs = sorted(Path(tmp).glob("*.json"))
            if not outputs:
                raise LocalAsrUnavailable("whisper CLI did not produce JSON output")

            data = json.loads(outputs[0].read_text(encoding="utf-8"))
            return str(data.get("text", "")).strip()


class ElevenLabsClient:
    """Small HTTP adapter for ElevenLabs STT and TTS."""

    def __init__(self, api_key: str | None = None, base_url: str = ELEVENLABS_API_BASE) -> None:
        self.api_key = api_key or os.environ.get("ELEVENLABS_API_KEY")
        self.base_url = base_url.rstrip("/")

    def _headers(self) -> dict[str, str]:
        if not self.api_key:
            raise VoicePipelineError("ELEVENLABS_API_KEY is not configured")
        return {"xi-api-key": self.api_key}

    def _retention_params(self) -> dict[str, str]:
        if _truthy(os.environ.get("ELEVENLABS_ZERO_RETENTION")):
            return {"enable_logging": "false"}
        return {}

    def transcribe(self, audio_path: str | Path, model: str | None = None) -> dict[str, Any]:
        _spore_guard("ElevenLabs")
        path = Path(audio_path).expanduser()
        stt_model = model or os.environ.get("ELEVENLABS_STT_MODEL", "scribe_v2")
        try:
            with path.open("rb") as audio:
                with httpx.Client(timeout=300) as client:
                    resp = client.post(
                        f"{self.base_url}/v1/speech-to-text",
                        headers=self._headers(),
                        params=self._retention_params(),
                        data={"model_id": stt_model},
                        files={"file": (path.name, audio, "application/octet-stream")},
                    )
            resp.raise_for_status()
        except httpx.HTTPError as e:
            raise VoicePipelineError(f"ElevenLabs STT failed: {e}") from e
        return resp.json()

    def synthesize(
        self,
        text: str,
        output_path: str | Path,
        voice_id: str | None = None,
        model: str | None = None,
        output_format: str | None = None,
    ) -> SpeechSynthesisResult:
        _spore_guard("ElevenLabs")
        selected_voice = voice_id or os.environ.get("ELEVENLABS_VOICE_ID")
        if not selected_voice:
            raise VoicePipelineError("Set ELEVENLABS_VOICE_ID or pass voice_id")

        selected_model = model or os.environ.get("ELEVENLABS_TTS_MODEL", "eleven_flash_v2_5")
        selected_format = output_format or os.environ.get(
            "ELEVENLABS_OUTPUT_FORMAT",
            "mp3_44100_128",
        )
        path = Path(output_path).expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)

        params = {"output_format": selected_format}
        params.update(self._retention_params())
        try:
            with httpx.Client(timeout=120) as client:
                resp = client.post(
                    f"{self.base_url}/v1/text-to-speech/{selected_voice}",
                    headers={**self._headers(), "Content-Type": "application/json"},
                    params=params,
                    json={"text": text, "model_id": selected_model},
                )
            resp.raise_for_status()
        except httpx.HTTPError as e:
            raise VoicePipelineError(f"ElevenLabs TTS failed: {e}") from e
        path.write_bytes(resp.content)
        return SpeechSynthesisResult(
            audio_path=path,
            provider="elevenlabs",
            voice_id=selected_voice,
            model=selected_model,
            output_format=selected_format,
            characters=len(text),
            cost=estimate_tts_cost(text, selected_model),
        )


class VoicePipeline:
    """End-to-end voice chain: local VAD, local ASR, optional cloud, cloud TTS."""

    def __init__(self) -> None:
        self.vad = VadDetector()
        self.local_asr = LocalWhisperAsr()
        self.elevenlabs = ElevenLabsClient()

    def status(self) -> dict[str, Any]:
        whisper_cpp_healthy = self.local_asr.whisper_cpp.healthy()
        effective_provider = self.local_asr.last_provider
        if self.local_asr.backend in {"auto", "whispercpp"} and whisper_cpp_healthy:
            effective_provider = "local-whisper-cpp-coreml"
        return {
            "vad": {
                "provider": "silero-onnx" if DEFAULT_VAD_MODEL.is_file() else "energy",
                "model_path": str(DEFAULT_VAD_MODEL),
                "model_present": DEFAULT_VAD_MODEL.is_file(),
            },
            "local_asr": {
                "provider": effective_provider,
                "backend": self.local_asr.backend,
                "whisper_cpp_url": DEFAULT_WHISPER_CPP_URL,
                "whisper_cpp_healthy": whisper_cpp_healthy,
                "worker_available": warm_worker_available(),
                "command_present": bool(shutil.which("whisper")),
                "model": self.local_asr.model,
                "model_dir": str(self.local_asr.model_dir),
                "model_cached": self.local_asr.model_cached(),
                "allow_model_download": self.local_asr.allow_model_download,
                "device": self.local_asr.device,
            },
            "cloud_fallback": {
                "provider": "elevenlabs",
                "enabled_by_env": _truthy(
                    os.environ.get("DOME_VOICE_ALLOW_CLOUD_FALLBACK")
                ),
                "api_key_present": bool(os.environ.get("ELEVENLABS_API_KEY")),
                "stt_model": os.environ.get("ELEVENLABS_STT_MODEL", "scribe_v2"),
            },
            "tts": {
                "provider": "elevenlabs",
                "enabled_by_env": _truthy(os.environ.get("DOME_VOICE_ALLOW_CLOUD_TTS")),
                "api_key_present": bool(os.environ.get("ELEVENLABS_API_KEY")),
                "voice_id_present": bool(os.environ.get("ELEVENLABS_VOICE_ID")),
                "model": os.environ.get("ELEVENLABS_TTS_MODEL", "eleven_flash_v2_5"),
            },
        }

    def warm_asr(self) -> dict[str, Any]:
        try:
            self.local_asr.warm()
        except LocalAsrUnavailable as e:
            raise VoicePipelineError(str(e)) from e
        return self.status()["local_asr"]

    def detect_speech(self, audio_path: str | Path) -> list[SpeechSegment]:
        return self.vad.detect(audio_path)

    def transcribe_file(
        self,
        audio_path: str | Path,
        allow_cloud_fallback: bool = False,
        language: str | None = None,
    ) -> TranscriptionResult:
        audio_seconds = audio_duration_seconds(audio_path)
        segments = self.detect_speech(audio_path)
        if not segments:
            return TranscriptionResult(
                text="",
                provider="local-vad",
                source="no_speech",
                cloud=False,
                audio_seconds=round(audio_seconds, 3),
                speech_segments=[],
                cost=zero_cost("local-vad", audio_seconds),
                warning="No speech detected by local VAD.",
            )

        try:
            text = self.local_asr.transcribe(
                audio_path,
                speech_segments=segments,
                language=language,
            )
            return TranscriptionResult(
                text=text,
                provider=self.local_asr.last_provider,
                source="local",
                cloud=False,
                audio_seconds=round(audio_seconds, 3),
                speech_segments=segments,
                cost=zero_cost(self.local_asr.last_provider, audio_seconds),
            )
        except LocalAsrUnavailable as local_error:
            cloud_allowed = allow_cloud_fallback or _truthy(
                os.environ.get("DOME_VOICE_ALLOW_CLOUD_FALLBACK")
            )
            if not cloud_allowed:
                raise LocalAsrUnavailable(
                    f"{local_error}. Cloud fallback is disabled; pass allow_cloud_fallback=true "
                    "or set DOME_VOICE_ALLOW_CLOUD_FALLBACK=1."
                ) from local_error

            stt_model = os.environ.get("ELEVENLABS_STT_MODEL", "scribe_v2")
            data = self.elevenlabs.transcribe(audio_path, model=stt_model)
            return TranscriptionResult(
                text=str(data.get("text", "")).strip(),
                provider="elevenlabs-scribe",
                source="cloud_fallback",
                cloud=True,
                audio_seconds=round(audio_seconds, 3),
                speech_segments=segments,
                cost=estimate_stt_cost(audio_seconds, stt_model),
                fallback_used=True,
                warning=str(local_error),
            )

    def synthesize_speech(
        self,
        text: str,
        output_path: str | Path | None = None,
        voice_id: str | None = None,
        allow_cloud: bool = False,
    ) -> SpeechSynthesisResult:
        if not text.strip():
            raise VoicePipelineError("text is required")
        cloud_allowed = allow_cloud or _truthy(
            os.environ.get("DOME_VOICE_ALLOW_CLOUD_TTS")
        )
        if not cloud_allowed:
            raise CloudProviderDisabled(
                "ElevenLabs TTS is cloud/paid. Pass allow_cloud=true or set "
                "DOME_VOICE_ALLOW_CLOUD_TTS=1."
            )

        if output_path is None:
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            output_path = DOME_ROOT / "logs" / "voice" / f"elevenlabs-{timestamp}.mp3"

        return self.elevenlabs.synthesize(text=text, output_path=output_path, voice_id=voice_id)


__all__ = [
    "CloudProviderDisabled",
    "ElevenLabsClient",
    "LocalAsrUnavailable",
    "LocalWhisperAsr",
    "VoicePipeline",
    "VoicePipelineError",
    "estimate_stt_cost",
    "estimate_tts_cost",
]
