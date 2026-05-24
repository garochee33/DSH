#!/usr/bin/env bash
set -euo pipefail

DOME_ROOT="${DOME_ROOT:-$HOME/DOME-HUB}"
VAD_MODEL="${DOME_VAD_MODEL:-$DOME_ROOT/models/asr/silero_vad.onnx}"
WHISPER_MODEL="${DOME_ASR_MODEL:-base}"
WHISPER_MODEL_DIR="${DOME_WHISPER_MODEL_DIR:-$DOME_ROOT/models/asr/whisper}"
TMP_WAV="$(mktemp -t dome-voice-bootstrap.XXXXXX.wav)"
TMP_OUT="$(mktemp -d -t dome-voice-bootstrap.XXXXXX)"

cleanup() {
  rm -f "$TMP_WAV"
  rm -rf "$TMP_OUT"
}
trap cleanup EXIT

mkdir -p "$(dirname "$VAD_MODEL")" "$WHISPER_MODEL_DIR"

if [[ ! -f "$VAD_MODEL" ]]; then
  echo "[voice] downloading Silero VAD ONNX -> $VAD_MODEL"
  curl -L \
    "https://github.com/snakers4/silero-vad/raw/master/src/silero_vad/data/silero_vad.onnx" \
    -o "$VAD_MODEL"
else
  echo "[voice] Silero VAD already present -> $VAD_MODEL"
fi

if ! command -v whisper >/dev/null 2>&1; then
  echo "[voice] whisper CLI not found. Install openai-whisper or the Homebrew whisper package."
  exit 1
fi

if [[ ! -f "$WHISPER_MODEL_DIR/$WHISPER_MODEL.pt" ]]; then
  echo "[voice] priming Whisper model '$WHISPER_MODEL' -> $WHISPER_MODEL_DIR"
  python3 - "$TMP_WAV" <<'PY'
import math
import struct
import sys
import wave

path = sys.argv[1]
sample_rate = 16_000
duration = 0.25
samples = int(sample_rate * duration)

with wave.open(path, "wb") as wav:
    wav.setnchannels(1)
    wav.setsampwidth(2)
    wav.setframerate(sample_rate)
    frames = bytearray()
    for i in range(samples):
        value = int(0.01 * 32767 * math.sin(2 * math.pi * 440 * i / sample_rate))
        frames.extend(struct.pack("<h", value))
    wav.writeframes(bytes(frames))
PY
  whisper "$TMP_WAV" \
    --model "$WHISPER_MODEL" \
    --model_dir "$WHISPER_MODEL_DIR" \
    --output_dir "$TMP_OUT" \
    --output_format txt \
    --verbose False \
    --fp16 False >/dev/null
else
  echo "[voice] Whisper model already present -> $WHISPER_MODEL_DIR/$WHISPER_MODEL.pt"
fi

echo "[voice] ready"
