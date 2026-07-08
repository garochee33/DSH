# akashic — Akashic Record System

Persistent memory layer using ChromaDB for semantic storage.

| File | Purpose |
|------|---------|
| `record.py` | `write()` and `query()` — ChromaDB-backed |
| `watcher.py` | File watcher — auto-indexes changes in logs/, kb/, agents/ |
| `assembler.py` | Context assembler — builds prompts from records |
| `schema.md` | Record schema documentation |
