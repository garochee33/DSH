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

The canonical high-quality runner now lives at:

`compute/sim_evolved.py`

It includes real E8 k-NN structured connectivity, per-neuron heterogeneity, and the full AMMA meridian projection lens by default.

Recommended invocation (using the Trinity Lava 3.10 sidecar):

```bash
LAVA_PY="~/projects/trinity-consortium/python/lava/.venv/bin/python"

$LAVA_PY compute/sim_evolved.py \
  --neurons 240 --steps 2000 --k 6 --tag e8-240-struct --json --save-projection
```

This is now the recommended reference implementation for E8-240 + AMMA work.

## 4. Architecture the runner uses (current canonical)

- **Neurons**: 240 (one per E8 root), heterogeneous LIF parameters (per-neuron vth/du/dv/bias).
- **Connectivity**: k-nearest neighbors in actual E8 geometry (real E8 root distances, not random).
- **Monitor**: `lava.proc.monitor` probes `lif.s_out`.
- **RunCfg**: `Loihi2SimCfg(select_tag="floating_pt")`. Same source runs on real Loihi 2 via `Loihi2HwCfg()`.
- **Post-processing**: Real AMMA meridian projection lens applied over time windows (E8 quantization scoring).

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

The script writes to the directory specified by `--output-dir` (default `docs/reports`):

- `e8_240_projection_<tag>.npz` — AMMA lens time series (scores, residuals, nearest roots)
- Optional: full spike raster + JSON summary when `--json` is used

With current recommended parameters (E8 k-NN + heterogeneity), expect ~35–60% population sparsity, high rate CV (0.6–0.9), and meaningful AMMA quantization scores. Runtime is longer than the old minimal demo because of richer structure.

## 7. Interpretation (when the user asks "is this good?")

- **Very low sparsity (< 0.15)** → recurrent excitation too strong or bias too high relative to vth.
- **Low rate CV (< 0.3)** → parameters too uniform across neurons. Increase heterogeneity.
- **All windows snap to the same root** → activity is too globally uniform; E8 structure not yet expressed in band activity.
- **Very high sparsity (> 0.85) with almost no active neurons** → parameters too conservative; network is dying.
- Good target for AMMA visuals: 0.35–0.65 sparsity + rate CV > 0.6 + varying nearest-root over time.

## 8. When to escalate to hardware

If the user has real Intel Loihi 2 access (INRC membership + NxSDK):

```python
# Replace in e8_240_with_amma_lens.py (or the canonical runner):
from lava.magma.core.run_configs import Loihi2HwCfg   # instead of Loihi2SimCfg
cfg = Loihi2HwCfg()                                   # instead of Loihi2SimCfg(...)
```

Everything else stays identical. Expected: ~100–1000× speedup and ~1000× lower energy per spike. The metrics format does not change.

## Non-negotiables

- **Never modify the Trinity proprietary engines** to run SNN on them. This skill uses stock Lava primitives only.
- **Never expose per-neuron raw spike data** from proprietary Trinity workloads over a public interface. The aggregate-metrics format is the only safe egress.
- **Never install lava-nc into the wrong venv.** It requires Python 3.10 exactly; putting it in DOME-HUB's 3.14 venv will fail at `pip install`.
- **Never interpret absolute Hz as real-time frequencies.** In simulation each timestep is a discrete event; `mean_rate_hz_equivalent` assumes 1 ms/step mapping, which is the Loihi 2 hardware convention but not a physical measurement here.
