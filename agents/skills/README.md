# agents/skills — Extended Domain Skills

7 computational skill modules with real math (not stubs):

| Skill | What it does |
|-------|-------------|
| `math.py` | Golden ratio, Fibonacci, primes, phi |
| `compute.py` | GPU detect, numerical optimization, quantum circuits |
| `sacred_geometry.py` | Flower of Life, Metatron's Cube, platonic solids |
| `fractals.py` | Mandelbrot, Julia sets, L-systems |
| `algorithms.py` | A*, Dijkstra, graph algorithms |
| `frequency.py` | FFT, spectral analysis, resonance detection |
| `cognitive.py` | Summarize, classify, retrieve context |

Each exports `SKILL` (name) and `verify()` (returns True if working).

---

## Workstation Utility Skills (SKILL.md packages)

18 agent-consumable skill instructions for file generation, automation, security, and research.

### File Generation
| Skill | What it does |
|-------|-------------|
| `docx/` | Create/edit Word documents (.docx) |
| `pdf/` | Create/read PDFs (reportlab + pdfplumber) |
| `pptx/` | Create/edit PowerPoint presentations |
| `xlsx/` | Create/edit Excel spreadsheets |
| `pandoc/` | Universal format conversion (md↔docx↔html↔pdf↔epub) |
| `latex-tectonic/` | Compile LaTeX with Tectonic |
| `imagegen/` | AI image generation (OpenAI API) |
| `speech/` | Text-to-speech (OpenAI Audio API) |
| `transcribe/` | Audio→text with diarization |
| `jupyter-notebook/` | Scaffold/edit .ipynb files |

### Automation & DevOps
| Skill | What it does |
|-------|-------------|
| `playwright/` | Browser automation from terminal |
| `screenshot/` | OS-level screen capture |
| `github/` | GitHub repo management (PRs, issues, Actions, releases) |
| `ci-cd-architect/` | CI/CD pipeline design and deployment automation |

### Security
| Skill | What it does |
|-------|-------------|
| `security-threat-model/` | Threat modeling (trust boundaries, abuse paths) |
| `security-best-practices/` | Secure coding review (Python, JS/TS, Go) |

### Research & Meta
| Skill | What it does |
|-------|-------------|
| `deep-research/` | Multi-source research synthesis |
| `skill-generator-engine/` | Autonomous skill creation engine |

**Install deps:** `bash scripts/install-format-deps.sh`
