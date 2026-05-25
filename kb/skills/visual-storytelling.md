# Visual Storytelling Skill — KB Reference

**Canonical source:** This document.
**Last updated:** 2026-05-13
**Status:** Active, production-wired.

## Purpose

Defines Trinity's capability to design and ship **premium scroll-driven web platforms**: landing pages, marketing routes, sacred-geometry / AMMA-resonant experiences, club / event / vehicle showcases for s3xyverse, and brand-narrative pages where motion, 3D, sound, and typography serve a story arc.

## Skill chain

Three skills, layered top-down:

| Skill | Role | Lives at |
|---|---|---|
| `visual-storytelling-architect` | Narrative-arc planner. 5-act web narrative, motion intent, stack-per-beat selection. | `home/projects/trinity-consortium/skills/visual-storytelling-architect/SKILL.md` |
| `sexyverse-designer` | Implementation agent. Consumes architect plan, writes code in `s3xyverse-next`. | `home/projects/trinity-consortium/skills/sexyverse-designer/SKILL.md` |
| `ui-ux-pro-max` | BM25-searchable design intelligence — 19 stacks, 99 UX rules, 161 palettes, 57 font pairings. | `home/projects/trinity-consortium/skills/ui-ux-pro-max/` |

All three are registered in:
- `server/ai/swarm/skills-library.ts` (production runtime registry)
- `server/ai/swarm/skill-specs.json` (auto-generated specs)
- DB table `skill_registry` (auto-synced at boot via `bootstrap/registry.ts`)
- `INDEX.md` files in all 4 trinity-consortium tier locations

## Stack files (BM25-searchable)

Located in `agents/skills/ui-ux-pro-max/data/stacks/` (mirrored across agent tiers):

| Stack | Rows | Domain |
|---|---:|---|
| `framer-motion.csv` | 60 | Framer Motion 12 + Lenis smooth-scroll integration |
| `gsap.csv` | 50 | GSAP + ScrollTrigger + SplitText + Flip + MorphSVG + Draggable |
| `r3f.csv` | 54 | React Three Fiber + Drei + Draco/KTX2 + reduced-motion |
| `spline.csv` | 30 | Spline → React, GLB export → R3F, variables |
| `video.csv` | 50 | HTML5 video + codec ladder + captions + Lottie + autoplay |
| `web-audio.csv` | 34 | Web Audio API + Tone.js + Howler + foley/ASMR + ducking |
| `typography-motion.csv` | 40 | Variable fonts + SplitText + kinetic reveals + scroll-coupled type |
| `threejs.csv` | 54 | Raw Three.js (cameras, lighting, materials, particles, GSAP, raycasting) |

Query:
```bash
python3 scripts/ui-ux-search.py "<query>" --stack <name>
```

## Hard rails

Inherited from `s3xyverse-next/BRAND.md` and enforced by the architect's pre-ship checklist:

- **One ease curve:** `cubic-bezier(0.16, 1, 0.3, 1)` = `--ease-out-expo` / GSAP `expo.out`.
- **`prefers-reduced-motion`** — global gate at `globals.css:285–290`. Non-negotiable.
- **Glass-morphism** — never "holographic".
- **No new Google Font** without same-PR update to BRAND.md §4.
- **Tap targets ≥ 44 px**, focus ring red `#E31937`.
- **Captions** for every video with spoken content (WCAG 1.2.2).
- **Audio toggle** in nav with `localStorage` persistence if any sound layer.
- **No third-party social embeds** on trust-critical paths.

## 5-act web narrative

| Act | Beat | Goal | Stack |
|---|---|---|---|
| 1 | Promise / Hero | Visceral one-line claim | `typography-motion` + `framer-motion` |
| 2 | Proof / Why-it-matters | Recognizable problem | `framer-motion` `useScroll` or `gsap` ScrollTrigger |
| 3 | Mechanism / How-it-works | The artifact | `r3f` or `spline` + `framer-motion` `layoutId` |
| 4 | Texture / Detail | Secondary proof | `framer-motion` counter + stagger |
| 5 | Resolve / CTA | One decisive ask | `gsap` magnetic cursor + sticky glow |

## 3 rules of motion intent

Every animation must answer:
1. **Reveal** — bring information into view.
2. **Direct** — move the eye toward what matters next.
3. **Mark** — make the user feel they crossed a threshold.

If it answers none, cut it.

## Trinity-specific surfaces

| Surface | Stack lean |
|---|---|
| `s3xyverse-next` landing + clubs + events + marketplace | `framer-motion` (pervasive) + `r3f` + `video` + `typography-motion` |
| `s3xyverse-next/sacred-demo` + `shaders-demo` | `r3f` + custom shaders (`src/lib/shaders/`) + `web-audio` |
| Trinity dev-portal / command-center | `framer-motion` + `typography-motion` |
| AMMA-resonant content | Custom Mandelbulb + Sephirot shaders + `web-audio` (Tone.js for harmonic-frequency layers) |

## s3xyverse-next stack (2026-05-13)

- **Next.js** 16.2.5
- **React** 19.2.4
- **Tailwind** v4
- **Framer Motion** 12.38
- **R3F** 9 + **Drei** 10 + **Three.js** 0.172
- **Lenis** 1.3.23 (shipped 2026-05-13)
- Wired at `src/app/layout.tsx` via `SmoothScroll.tsx` client wrapper, `useReducedMotion`-gated.

## Cross-references

- BRAND.md: `~/projects/s3xyverse/s3xyverse-next/BRAND.md`
- Animations canonical: `~/projects/s3xyverse/s3xyverse-next/src/lib/animations.ts`
- Design tokens: `~/projects/s3xyverse/s3xyverse-next/src/lib/design-tokens.ts`
- Shaders: `~/projects/s3xyverse/s3xyverse-next/src/lib/shaders/`
- Smooth scroll: `~/projects/s3xyverse/s3xyverse-next/src/app/components/SmoothScroll.tsx`
- Competitor intel: `logs/competitor-intel/`
- Protocol: `PROTOCOLS.md` § Visual Storytelling Protocol
