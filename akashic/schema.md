# Akashic Record — Dimensional Schema

The Akashic Record is not a log. It is a dimensional field.
Each entry is a point in semantic space — retrievable by resonance, not by time.

---

## Entry Structure

```
id          uuid4           unique record identifier
timestamp   ISO8601         when this entered the field
domain      enum            what layer of reality this belongs to
depth       enum            how fundamental this record is
node        string          who/what generated this (agent, human principal, system)
content     string          the record itself
resonance   [uuid, ...]     linked entries — semantic neighbors, causal chains
tags        [string, ...]   free-form dimensional markers
vector      float[]         ChromaDB embedding (auto-generated)
```

---

## Domains

| Domain     | What it holds |
|------------|---------------|
| `security` | Hardening events, threat responses, access decisions |
| `agent`    | Agent outputs, memory writes, tool invocations |
| `build`    | Code changes, project creation, stack decisions |
| `trinity`  | Mycelium events, consortium decisions, spore activity |
| `infra`    | System state, daemon events, DB/service changes |
| `creative` | Generative outputs, design decisions, media |
| `meta`     | Records about the record system itself |

---

## Depths

| Depth          | What it means |
|----------------|---------------|
| `event`        | Something happened — transient, observable |
| `decision`     | A choice was made — directional, consequential |
| `architecture` | A structural truth about how things are built |
| `axiom`        | A foundational principle — rarely changes |

---

## Retrieval Model

Retrieval is dimensional, not linear.

```python
# Tune to a frequency — not a timestamp
akashic.query("Mycelium activation", domain="trinity", depth="architecture")
akashic.query("agent memory design", domain="agent", depth="architecture")
akashic.query("what was decided about security", depth="decision")
```

ChromaDB namespace: `akashic`
Metadata filters map directly to domain + depth dimensions.

---

## Node Identity

Records carry their origin:
- `gadi.k` — sovereign principal
- `kiro` — Kiro CLI agent
- `claude` — Claude agent
- `system` — automated watcher/daemon
- `trinity` — Trinity Consortium input
