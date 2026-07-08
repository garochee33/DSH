# DSH Voice Pipeline

The voice stack is local-first:

```text
local VAD -> local ASR first -> optional cloud STT fallback -> ElevenLabs TTS
```

## Providers

| Layer | Default | Cloud | Notes |
| --- | --- | --- | --- |
| VAD | Silero ONNX if `models/asr/silero_vad.onnx` exists | No | Falls back to deterministic energy VAD before weights are present. |
| ASR | Resident whisper.cpp CoreML server; warm Python Whisper worker fallback; Whisper CLI fallback | Optional | Default model is `base` for conversational latency. Cloud fallback requires `allow_cloud_fallback=true` or `DOME_VOICE_ALLOW_CLOUD_FALLBACK=1`. |
| TTS | ElevenLabs | Yes | Requires `allow_cloud=true` or `DOME_VOICE_ALLOW_CLOUD_TTS=1`. |

## Bootstrap Open Local Weights

```bash
bash scripts/voice-bootstrap.sh
```

This downloads the MIT Silero VAD ONNX model and primes the configured Whisper model cache.

## API

```bash
pnpm serve
curl http://127.0.0.1:8001/voice/status
```

Warm ASR before the first transcription:

```bash
curl -X POST http://127.0.0.1:8001/voice/asr/warm \
  -H 'Content-Type: application/json' \
  -d '{"model":"base","backend":"whispercpp"}'
```

Detect speech:

```bash
curl -X POST http://127.0.0.1:8001/voice/vad \
  -H 'Content-Type: application/json' \
  -d '{"audio_path":"/absolute/path/to/audio.wav"}'
```

Transcribe locally, with no cloud fallback:

```bash
curl -X POST http://127.0.0.1:8001/voice/transcribe \
  -H 'Content-Type: application/json' \
  -d '{"audio_path":"/absolute/path/to/audio.wav"}'
```

Allow ElevenLabs STT fallback if local Whisper cannot run:

```bash
curl -X POST http://127.0.0.1:8001/voice/transcribe \
  -H 'Content-Type: application/json' \
  -d '{"audio_path":"/absolute/path/to/audio.wav","allow_cloud_fallback":true}'
```

Synthesize polished voice output with ElevenLabs:

```bash
curl -X POST http://127.0.0.1:8001/voice/speak \
  -H 'Content-Type: application/json' \
  -d '{"text":"DSH voice pipeline online.","allow_cloud":true}'
```

## Env Knobs

```bash
DOME_VAD_MODEL=$HOME/DSH/models/asr/silero_vad.onnx
DOME_ASR_MODEL=base
DOME_ASR_BACKEND=auto
DOME_ASR_DEVICE=cpu
DOME_WHISPER_MODEL_DIR=$HOME/DSH/models/asr/whisper
DOME_WHISPER_CPP_URL=http://127.0.0.1:8082
DOME_VOICE_ALLOW_MODEL_DOWNLOAD=0
DOME_VOICE_ALLOW_CLOUD_FALLBACK=0
DOME_VOICE_ALLOW_CLOUD_TTS=0
ELEVENLABS_API_KEY=
ELEVENLABS_VOICE_ID=
ELEVENLABS_STT_MODEL=scribe_v2
ELEVENLABS_TTS_MODEL=eleven_flash_v2_5
```

`DOME_ASR_BACKEND=auto` tries the resident whisper.cpp server first, then the
warm Python worker, then the Whisper CLI. Use `whispercpp` to require the
server path, `worker` to require in-process Python Whisper, or `cli` to force
the subprocess path.

## Local Backend Posture

Current default is whisper.cpp/CoreML `base` because it is the latency-oriented
conversational path. The warmed Python worker path for Whisper `small` reached
roughly `7.46x` real-time on a 60-second speech sample. The Homebrew CLI path for
the same `small` model cleared real time at roughly `1.09x`, mostly due to
repeated process startup and model load overhead.

Benchmark commands:

```bash
./scripts/voice-benchmark.py /tmp/dome-silero-en.wav --runs 2 --language en --model small --warm
./scripts/voice-benchmark.py /tmp/dome-silero-en.wav --runs 1 --language en --model small
```

Start the resident whisper.cpp CoreML server:

```bash
scripts/voice-whispercpp-server.sh start
scripts/voice-whispercpp-server.sh status
```

Measured result on the 60-second Silero speech sample:

```text
Provider    local-whisper-cpp-coreml
ASR Avg     0.3418s
Total Avg   0.6274s
RTF         0.0104
Throughput  96.80x real-time
```

Next backend candidates:

| Backend | Why evaluate | Expected tradeoff |
| --- | --- | --- |
| Warm Python Whisper | Removes process startup and repeated model loads inside the API server. | Same model math, lower first-hop overhead after warmup. |
| whisper.cpp / CoreML | Best fit for Apple Silicon local inference. | New binary/runtime path to manage. |
| faster-whisper | Efficient CTranslate2 runtime. | Apple Silicon acceleration depends on available backend support. |
| MLX Whisper | Native Apple Silicon direction. | Extra package and model conversion surface. |
