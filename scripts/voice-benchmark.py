#!/usr/bin/env python3
"""Benchmark the DSH local-first voice pipeline.

Cloud STT is never attempted unless --cloud is passed.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from statistics import mean
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
VENV_PYTHON = ROOT / ".venv" / "bin" / "python"
if VENV_PYTHON.is_file() and Path(sys.executable).resolve() != VENV_PYTHON.resolve():
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), *sys.argv])

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agents.voice import LocalAsrUnavailable, VoicePipeline  # noqa: E402
from agents.voice.audio import audio_duration_seconds, load_audio_mono_16k  # noqa: E402


def _round(value: float, digits: int = 4) -> float:
    return round(float(value), digits)


def _throughput(audio_seconds: float, latency_seconds: float) -> float:
    if audio_seconds <= 0 or latency_seconds <= 0:
        return 0.0
    return audio_seconds / latency_seconds


def _rtf(audio_seconds: float, latency_seconds: float) -> float:
    if audio_seconds <= 0:
        return 0.0
    return latency_seconds / audio_seconds


def _run_once(
    pipeline: VoicePipeline,
    audio_path: Path,
    allow_cloud: bool,
    language: str | None,
) -> dict[str, Any]:
    t0 = time.perf_counter()

    decode_start = time.perf_counter()
    samples = load_audio_mono_16k(audio_path)
    t_decode = time.perf_counter() - decode_start
    audio_seconds = len(samples) / 16_000

    vad_start = time.perf_counter()
    segments = pipeline.detect_speech(audio_path)
    t_vad = time.perf_counter() - vad_start

    asr_start = time.perf_counter()
    fallback_used = False
    try:
        text = pipeline.local_asr.transcribe(audio_path, segments, language=language)
        provider = pipeline.local_asr.last_provider
        cloud = False
        cost_usd = 0.0
        warning = None
    except LocalAsrUnavailable as local_error:
        if not allow_cloud:
            raise
        cloud_result = pipeline.transcribe_file(
            audio_path,
            allow_cloud_fallback=True,
            language=language,
        )
        text = cloud_result.text
        provider = cloud_result.provider
        cloud = cloud_result.cloud
        cost_usd = cloud_result.cost.estimated_usd
        fallback_used = cloud_result.fallback_used
        warning = str(local_error)
    t_asr = time.perf_counter() - asr_start

    t_total = time.perf_counter() - t0
    return {
        "audio_seconds": _round(audio_seconds, 3),
        "decode_sec": _round(t_decode),
        "vad_sec": _round(t_vad),
        "asr_sec": _round(t_asr),
        "total_sec": _round(t_total),
        "rtf_total": _round(_rtf(audio_seconds, t_total)),
        "throughput_x": _round(_throughput(audio_seconds, t_total), 2),
        "segments": len(segments),
        "speech_seconds": _round(sum(segment.duration for segment in segments), 3),
        "text_len": len(text),
        "text_preview": text[:240],
        "provider": provider,
        "cloud": cloud,
        "fallback_used": fallback_used,
        "cost_usd": _round(cost_usd, 6),
        "warning": warning,
    }


def _averages(runs: list[dict[str, Any]]) -> dict[str, Any]:
    keys = [
        "decode_sec",
        "vad_sec",
        "asr_sec",
        "total_sec",
        "rtf_total",
        "throughput_x",
        "speech_seconds",
        "text_len",
        "cost_usd",
    ]
    return {key: _round(mean(float(run[key]) for run in runs)) for key in keys}


def _print_summary(report: dict[str, Any]) -> None:
    avg = report["averages"]
    first = report["runs"][0]
    print("\n" + "=" * 72)
    print(f"{'DSH Voice Benchmark':<34} {report['audio']['path']}")
    print("-" * 72)
    print(f"{'Provider':<22} {first['provider']}")
    print(f"{'Audio Duration':<22} {report['audio']['duration_sec']:.3f}s")
    print(f"{'Speech Segments':<22} {first['segments']}")
    print(f"{'Speech Duration':<22} {avg['speech_seconds']:.3f}s")
    print("-" * 72)
    print(f"{'Decode Avg':<22} {avg['decode_sec']:.4f}s")
    print(f"{'VAD Avg':<22} {avg['vad_sec']:.4f}s")
    print(f"{'ASR Avg':<22} {avg['asr_sec']:.4f}s")
    print(f"{'Total Avg':<22} {avg['total_sec']:.4f}s")
    print(f"{'RTF':<22} {avg['rtf_total']:.4f} lower is faster")
    print(f"{'Throughput':<22} {avg['throughput_x']:.2f}x real-time")
    print(f"{'Estimated Cost':<22} ${avg['cost_usd']:.6f}")
    print("-" * 72)
    print(first["text_preview"] or "[no transcript text]")
    print("=" * 72)


def run_benchmark(
    audio: str,
    runs: int,
    allow_cloud: bool,
    language: str | None,
    model: str | None,
    allow_model_download: bool,
    warm: bool,
) -> Path:
    audio_path = Path(audio).expanduser().resolve()
    if not audio_path.is_file():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    if runs < 1:
        raise ValueError("--runs must be >= 1")

    pipeline = VoicePipeline()
    if model:
        pipeline.local_asr.model = model
    if allow_model_download:
        pipeline.local_asr.allow_model_download = True

    warm_sec = 0.0
    if warm:
        warm_start = time.perf_counter()
        pipeline.warm_asr()
        warm_sec = time.perf_counter() - warm_start

    duration = audio_duration_seconds(audio_path)
    results = []
    for index in range(runs):
        print(f"Run {index + 1}/{runs}: {audio_path.name}", flush=True)
        result = _run_once(
            pipeline=pipeline,
            audio_path=audio_path,
            allow_cloud=allow_cloud,
            language=language,
        )
        result["run"] = index + 1
        results.append(result)

    report = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "audio": {
            "path": str(audio_path),
            "duration_sec": _round(duration, 3),
        },
        "settings": {
            "runs": runs,
            "cloud_enabled": allow_cloud,
            "language": language,
            "local_asr_model": pipeline.local_asr.model,
            "allow_model_download": pipeline.local_asr.allow_model_download,
            "warm_before_runs": warm,
            "warm_sec": _round(warm_sec),
        },
        "pipeline_status": pipeline.status(),
        "averages": _averages(results),
        "runs": results,
    }

    log_dir = ROOT / "logs" / "voice"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"benchmark-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    log_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    _print_summary(report)
    print(f"Report: {log_path}")
    return log_path


def main() -> int:
    parser = argparse.ArgumentParser(description="DSH Voice Benchmark")
    parser.add_argument("audio", help="Path to a WAV/MP3/M4A/etc. audio file")
    parser.add_argument("--runs", type=int, default=3, help="Number of local benchmark runs")
    parser.add_argument("--language", default=None, help="Optional Whisper language hint, e.g. en")
    parser.add_argument("--model", default=None, help="Whisper model name, e.g. base or small")
    parser.add_argument(
        "--allow-model-download",
        action="store_true",
        help="Allow Whisper to download the selected local model if missing",
    )
    parser.add_argument(
        "--warm",
        action="store_true",
        help="Load the local ASR model before timed benchmark runs",
    )
    parser.add_argument(
        "--cloud",
        action="store_true",
        help="Allow ElevenLabs cloud fallback if local ASR cannot run",
    )
    args = parser.parse_args()

    try:
        run_benchmark(
            audio=args.audio,
            runs=args.runs,
            allow_cloud=args.cloud,
            language=args.language,
            model=args.model,
            allow_model_download=args.allow_model_download,
            warm=args.warm,
        )
    except Exception as e:  # noqa: BLE001
        print(f"voice-benchmark failed: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
