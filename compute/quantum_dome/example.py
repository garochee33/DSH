"""QuantumDome usage examples."""
import sys
import os

# Allow running directly: python example.py
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from compute.quantum_dome import QuantumDome

dome = QuantumDome()

# ── 1. Basic usage ────────────────────────────────────────────────────────────
def my_fn(data):
    return sum(data)

result = dome.run(my_fn, list(range(1000)))
print(f"[basic]   sum = {result}")

# ── 2. Torch inference routed to MPS ─────────────────────────────────────────
try:
    import torch

    def torch_inference(x):
        device = dome.scheduler.get_torch_device("inference")
        t = torch.tensor(x, dtype=torch.float32).to(device)
        return t.mean().item()

    mean_val = dome.run(torch_inference, list(range(100)), task_type="inference")
    print(f"[torch]   mean on {dome.device} = {mean_val:.4f}")
except Exception as e:
    print(f"[torch]   skipped: {e}")

# ── 3. Batch embedding with auto batch size ───────────────────────────────────
# 110M-param model (e.g. BERT-base)
batch = dome.scheduler.auto_batch_size(110_000_000)
print(f"[batch]   safe batch size for 110M-param model = {batch}")

# ── 4. Profile report ─────────────────────────────────────────────────────────
report = dome.profiler.get_report()
print(f"[profile] {len(report)} task(s) recorded")
for r in report:
    print(f"          {r['name']} | {r['device']} | {r['elapsed_s']:.4f}s | ΔRAM {r['ram_delta_gb']:.4f} GB")

# ── 5. Status snapshot ────────────────────────────────────────────────────────
status = dome.status()
print(f"[status]  device={status['device']}  RAM avail={status['available_ram_gb']:.2f}GB  "
      f"CPU={status['cpu_avg']:.1f}%  healthy={status['is_healthy']}")
