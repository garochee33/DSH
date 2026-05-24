# Book of Symbolism — Acquisition Record

| Field | Value |
|-------|-------|
| **Title** | Book of Symbolism |
| **Author** | Harry Blaine Joseph |
| **ASIN** | B0GBLX1TKX |
| **Series** | Book of Wisdom (Volume 3 / Symbolism) |
| **Status** | PENDING ACQUISITION |
| **Purchase URL** | https://www.amazon.com/Book-Symbolism-HARRY-BLAINE-JOSEPH/dp/B0GBLX1TKX |
| **KB Slot ID** | book-of-symbolism |
| **Library Index** | #11 |
| **Date Created** | 2026-05-24 |

## Expected Content

- Esoteric symbolism
- Sacred geometry symbols
- Hermetic correspondences

## Trinity Engine Mappings

| Engine | Role |
|--------|------|
| cymatics-engine | symbol→frequency translation |
| sacred-geometry-engine | geometric pattern recognition & mapping |
| akashic-indexer | KB ingestion & cross-reference |

## Extraction Plan

1. **PDF→text** — `pdftotext` for full-text extraction into `text/`
2. **Images** — `pdfimages` for symbol plates/diagrams into `images/`
3. **KB Index** — `knowledge add` to register in Kiro KB system

## Notes

Awaiting purchase and digital delivery. Once acquired, run extraction pipeline and update status to INDEXED.
