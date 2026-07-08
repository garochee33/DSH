"""HTTP client for a resident whisper.cpp server."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import httpx

from agents.voice.types import SpeechSegment

DEFAULT_WHISPER_CPP_URL = os.environ.get(
    "DOME_WHISPER_CPP_URL",
    "http://127.0.0.1:8082",
).rstrip("/")


class WhisperCppUnavailable(RuntimeError):
    """Raised when the resident whisper.cpp server is not reachable."""


class WhisperCppClient:
    """Small client for whisper.cpp examples/server."""

    def __init__(self, base_url: str = DEFAULT_WHISPER_CPP_URL, timeout: float = 120.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def healthy(self) -> bool:
        try:
            with httpx.Client(timeout=2.0, trust_env=False) as client:
                response = client.get(f"{self.base_url}/health")
            return response.status_code == 200 and response.json().get("status") == "ok"
        except Exception:
            return False

    def transcribe(
        self,
        audio_path: str | Path,
        speech_segments: list[SpeechSegment],
        language: str | None = None,
    ) -> str:
        if not self.healthy():
            raise WhisperCppUnavailable(f"whisper.cpp server is not healthy at {self.base_url}")

        path = Path(audio_path).expanduser()
        data: dict[str, Any] = {
            "temperature": "0.0",
            "temperature_inc": "0.2",
            "response_format": "json",
            "no_timestamps": "true",
            "suppress_non_speech": "true",
        }
        if language:
            data["language"] = language
        if speech_segments:
            start_ms = int(min(segment.start for segment in speech_segments) * 1000)
            end_ms = int(max(segment.end for segment in speech_segments) * 1000)
            data["offset_t"] = str(start_ms)
            data["duration"] = str(max(0, end_ms - start_ms))

        try:
            with path.open("rb") as audio:
                with httpx.Client(timeout=self.timeout, trust_env=False) as client:
                    response = client.post(
                        f"{self.base_url}/inference",
                        data=data,
                        files={"file": (path.name, audio, "application/octet-stream")},
                    )
            response.raise_for_status()
            payload = response.json()
        except httpx.HTTPError as e:
            raise WhisperCppUnavailable(f"whisper.cpp request failed: {e}") from e
        except ValueError as e:
            raise WhisperCppUnavailable("whisper.cpp returned invalid JSON") from e

        if "error" in payload:
            raise WhisperCppUnavailable(str(payload["error"]))
        return str(payload.get("text", "")).strip()
