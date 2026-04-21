---
name: lava-neuro-sim
description: "Run a spiking neural network on Intel's Lava framework using the Loihi 2 simulation backend. Configurable neuron count (default 240, one per E8 root) and timestep count. Emits public-safe aggregate metrics: total spikes, active neurons, sparsity, mean firing rate, first-spike step, runtime. Same source code runs on physical Intel Loihi 2 silicon when Loihi2HwCfg is available on an NxSDK-authorized host."
---

You are running neuromorphic spiking-neural-network simulations via Intel's Lava framework. The user does not have physical Loihi 2 silicon (NxSDK is NDA-gated); they have the CPU simulation backend which executes identical Python code to what silicon would run. Treat CPU and hardware runs as interchangeable from the source perspective.

## 1. Confirm the Lava sidecar is available

Lava requires Python 3.10 exactly (hard cap < 3.11). The sidecar venv lives at `~/projects/trinity-consortium/python/lava/.venv`. Verify:

```bash
LAVA_PY="$HOME/projects/trinity-consortium/python/lava/.venv/bin/python"
test -x "$LAVA_PY" && "$LAVA_PY" --version   # Python 3.10.x
"$LAVA_PY" -c "from lava.proc.lif.process import LIF; from lava.proc.dense.process import Dense; print('lava imports ok')"
```

If the sidecar isn't present, bootstrap it:

```bash
cd ~/projects/trinity-consortium && bash scripts/lava-bootstrap.sh
```

This uses `uv` to create the 3.10 venv and install `lava-nc`. Takes ~2 min on first run.

## 2. Probe for Loihi hardware (optional)

```bash
"$LAVA_PY" ~/projects/trinity-consortium/scripts/lava-probe.py
```

Reports whether NxSDK is importable and whether any Loihi device appears on the USB/PCI bus. On a standard Mac this will show:

```
loihi_bus_signal_detected: False
probable_loihi_hardware: False
```

That's fine — the simulation backend is the intended path.

## 3. Run the SNN

The reproducible runner lives at `~/projects/trinity-consortium/scripts/lava-snn-demo.py`. Invoke with:

```bash
"$LAVA_PY" ~/projects/trinity-consortium/scripts/lava-snn-demo.py \
  --neurons <N> --steps <T> --tag <label>
```

Defaults: `--neurons 64 --steps 500`. For the canonical E8-aligned run: `--neurons 240 --steps 1000 --tag e8-240`.

For pipeline integration (another script shells out and parses output):

```bash
"$LAVA_PY" .../lava-snn-demo.py --neurons 240 --steps 1000 --json-only
```

Emits a single JSON object to stdout, no other noise.

## 4. Architecture the runner uses

- **Neurons**: Lava's floating-point `LIF` model — `du=0.1, dv=0.1, vth=1.0, bias_mant∈[0.15, 0.25]` (tuned to avoid int32 overflow in the fixed-point codepath while producing real spiking dynamics).
- **Connectivity**: random sparse `Dense` — ~10% of pairs connected, weights `~ Uniform(0.05, 0.2)`, no self-loops.
- **Monitor**: `lava.proc.monitor` probes `lif.s_out` for the full run.
- **RunCfg**: `Loihi2SimCfg(select_tag="floating_pt")`. Swap to `Loihi2HwCfg()` for hardware silicon — zero other changes.

## 5. Metrics you return

```
{
  "n_neurons":            int,
  "n_steps":              int,
  "backend":              "Loihi2SimCfg (CPU simulation of Loihi 2 dynamics)",
  "runtime_seconds":      float,
  "total_spikes":         int,
  "active_neurons":       int,
  "mean_rate_hz_equivalent": float,
  "spike_raster_sparsity": float,
  "time_to_first_spike_step": int | null,
  "timestamp":            ISO-8601 UTC
}
```

All fields are public-safe aggregates. No per-neuron raw data leaves this runner. No Trinity proprietary architecture is encoded in the network — stock Lava `LIF` + `Dense` + `Monitor` only.

## 6. Output files

Without `--json-only`, two files land at `~/projects/trinity-consortium/docs/reports/`:

- `lava-snn-demo[-<tag>].json` — raw metrics
- `LAVA_SNN_DEMO[-<TAG>].md` — human-readable report

With `--tag e8-240` on a 240-neuron run, expect a 240-of-240 active population, mean rate ~500–1000 Hz equivalent (tuning-dependent), sparsity 0.0–0.1, runtime ~0.3–0.5 s on Apple M-series CPU.

## 7. Interpretation (when the user asks "is this good?")

- **total_spikes == 0** → bias too low relative to threshold. Bump `bias_mant` or lower `vth` in `build_network()`.
- **sparsity < 0.01** → all neurons firing every step; saturation. Increase `vth` or decrease `bias_mant`.
- **active_neurons < n_neurons * 0.5** → bias distribution too narrow. Widen `rng.uniform(..., ...)` range.
- **runtime > 2× expected** → `bias_exp` set high is forcing slow integer multiplies; drop to 0.
- **RuntimeWarning: overflow** → `du`/`dv` outside [0, 1] range. They are LEAK FRACTIONS in the floating-point model, not Lava's 0–4095 fixed-point scale.

## 8. When to escalate to hardware

If the user has real Intel Loihi 2 access (INRC membership + NxSDK):

```python
# Replace in lava-snn-demo.py:
from lava.magma.core.run_configs import Loihi2HwCfg   # instead of Loihi2SimCfg
cfg = Loihi2HwCfg()                                   # instead of Loihi2SimCfg(...)
```

Everything else stays identical. Expected: ~100–1000× speedup and ~1000× lower energy per spike. The metrics format does not change.

## Non-negotiables

- **Never modify the Trinity proprietary engines** to run SNN on them. This skill uses stock Lava primitives only.
- **Never expose per-neuron raw spike data** from proprietary Trinity workloads over a public interface. The aggregate-metrics format is the only safe egress.
- **Never install lava-nc into the wrong venv.** It requires Python 3.10 exactly; putting it in DOME-HUB's 3.14 venv will fail at `pip install`.
- **Never interpret absolute Hz as real-time frequencies.** In simulation each timestep is a discrete event; `mean_rate_hz_equivalent` assumes 1 ms/step mapping, which is the Loihi 2 hardware convention but not a physical measurement here.
