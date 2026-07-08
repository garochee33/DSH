"""Warm local Whisper ASR worker.

This backend keeps a Python Whisper model loaded inside the current process.
It is used by the FastAPI process when `openai-whisper` is installed in the
DSH venv; the CLI adapter remains the fallback path.
"""

from __future__ import annotations

import threading
from pathlib import Path
from typing import Any

from agents.voice.types import SpeechSegment


class WarmWhisperUnavailable(RuntimeError):
    """Raised when the Python Whisper backend cannot run."""


class WarmWhisperAsr:
    """In-process Whisper model cache."""

    def __init__(
        self,
        model: str,
        model_dir: str | Path,
        allow_model_download: bool,
        device: str = "cpu",
    ) -> None:
        self.model = model
        self.model_dir = Path(model_dir).expanduser()
        self.allow_model_download = allow_model_download
        self.device = device
        self._lock = threading.RLock()
        self._model: Any | None = None

    def model_cached(self) -> bool:
        return (self.model_dir / f"{self.model}.pt").is_file()

    def warm(self) -> None:
        with self._lock:
            if self._model is not None:
                return
            if not self.allow_model_download and not self.model_cached():
                raise WarmWhisperUnavailable(
                    f"Whisper model '{self.model}' is not cached in {self.model_dir}."
                )
            try:
                import whisper
            except ImportError as e:
                raise WarmWhisperUnavailable(
                    "Python package 'openai-whisper' is not installed in the DSH venv."
                ) from e

            self.model_dir.mkdir(parents=True, exist_ok=True)
            self._model = whisper.load_model(
                self.model,
                device=self.device,
                download_root=str(self.model_dir),
            )

    def transcribe(
        self,
        audio_path: str | Path,
        speech_segments: list[SpeechSegment],
        language: str | None = None,
    ) -> str:
        self.warm()
        clips = ",".join(f"{s.start:.3f},{s.end:.3f}" for s in speech_segments)
        kwargs: dict[str, Any] = {
            "fp16": False,
            "verbose": False,
        }
        if language:
            kwargs["language"] = language
        if clips:
            kwargs["clip_timestamps"] = clips

        with self._lock:
            if self._model is None:
                raise WarmWhisperUnavailable("Whisper model is not loaded.")
            result = self._model.transcribe(str(Path(audio_path).expanduser()), **kwargs)
        return str(result.get("text", "")).strip()


_worker: WarmWhisperAsr | None = None
_worker_lock = threading.Lock()


def get_warm_worker(
    model: str,
    model_dir: str | Path,
    allow_model_download: bool,
    device: str = "cpu",
) -> WarmWhisperAsr:
    """Return a process-wide worker for the requested model."""

    global _worker
    with _worker_lock:
        if (
            _worker is None
            or _worker.model != model
            or _worker.model_dir != Path(model_dir).expanduser()
            or _worker.device != device
            or _worker.allow_model_download != allow_model_download
        ):
            _worker = WarmWhisperAsr(
                model=model,
                model_dir=model_dir,
                allow_model_download=allow_model_download,
                device=device,
            )
        return _worker


def warm_worker_available() -> bool:
    try:
        import whisper  # noqa: F401
    except ImportError:
        return False
    return True
