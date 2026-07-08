# agents/skills — Extended Domain Skills

7 computational skill modules with real math (not stubs):

| Skill | What it does |
|-------|-------------|
| `math.py` | Golden ratio, Fibonacci, primes, phi |
| `compute.py` | GPU detect, numerical optimization, quantum circuits |
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

---

## Developer Productivity Skills (added 2026-05-25)

16 skills for full-stack development, infrastructure, quality, and monetization.

| Skill | What it does |
|-------|-------------|
| `nextjs/` | Next.js App Router — SSR, Server Components, deployment |
| `fastapi/` | Python API development (Pydantic, async, DI) |
| `ai-sdk/` | Vercel AI SDK — chat, streaming, tool calling |
| `react-best-practices/` | React performance optimization |
| `shadcn/` | Component library (CLI, theming, Tailwind) |
| `database-optimizer/` | PostgreSQL + Drizzle ORM tuning |
| `neon-postgres/` | Serverless Postgres |
| `migration-specialist/` | Schema evolution, zero-downtime deploys |
| `cloudflare-deploy/` | Deploy to Cloudflare (Workers, Pages, KV, D1, R2) |
| `api-gateway-designer/` | REST/GraphQL/WebSocket design |
| `testing-strategist/` | Unit/integration/E2E test strategy |
| `refactoring-engineer/` | Tech debt reduction, modernization |
| `performance-tuner/` | Profiling, caching, bundle optimization |
| `dependency-manager/` | Vulnerability scanning, license compliance |
| `documentation-generator/` | Auto-generate API docs, READMEs |
| `stripe-best-practices/` | Payments, subscriptions, Connect |
