<!-- GENERATED — edit data/*.yaml and run `python3 scripts/generate.py` -->

# Autonomous Science Landscape

Working catalog of **62 companies** in lab automation, autonomous science, and AI-for-bio. 
Each is tagged with the functional category it occupies *and* the implicit thesis it holds about why lab automation hasn't gone the way of self-driving.

Source v1: Cheshire Labs landscape image (May 2026). **0 entries have unverified fields** — flagged with `unverified: true` in the data.

## Views

| File | What it is |
|---|---|
| [`index.html`](./index.html) | **Sortable, filterable HTML view with logos, tag pills, and per-column filters. Open this first.** |
| [`companies.md`](./companies.md) | Master table — one row per company |
| [`by-category.md`](./by-category.md) | Companies grouped by Cheshire-style category |
| [`by-thesis.md`](./by-thesis.md) | Companies grouped by which bottleneck thesis they hold |
| [`theses.md`](./theses.md) | Each thesis written up — bet, predicts, falsifier |
| [`companies.csv`](./companies.csv) | Same data, machine-readable |

## Architecture

**Data is the source of truth.** Edit YAML; regenerate everything else.

```
data/
├── companies.yaml      ← edit me
├── categories.yaml     ← edit me
└── theses.yaml         ← edit me
scripts/
└── generate.py         ← run me
logos/                  ← cached per-company logos (favicons sz=128)
```

Regenerate everything:

```
python3 scripts/generate.py                  # rebuild MDs + HTML
python3 scripts/generate.py --fetch-logos    # also download missing logos
```

## Tag legend

### `ai_level`

| Value | Meaning |
|---|---|
| `ai-native` | Founded around an AI/ML thesis; product makes no sense without modern ML |
| `ai-adopting` | Traditional product surface, actively bolting on AI features |
| `ai-adjacent` | Instrument/software where AI is marketing veneer, not core |
| `standard-oss` | A specification or open project, not a company |

### `maturity`

`public` · `late-stage` · `mid-stage` · `early` · `stealth` · `mature-private` · `standard`

### `pricing`

`premium` (instrument-list-price tier; 6-figure pharma quote) · `mid` (Series-A biotech / academic core) · `economical` (designed to undercut on capex) · `free` (OSS / standard)

## At a glance

- **Companies:** 62
- **Categories used:** 19 of 19
- **Theses held:** 19 of 19

**By AI level:**

- `ai-adopting` — 23
- `ai-adjacent` — 21
- `ai-native` — 16
- `standard-oss` — 2

**By maturity:**

- `early` — 17
- `late-stage` — 14
- `public` — 13
- `mature-private` — 12
- `mid-stage` — 4
- `standard` — 2

## Methodology & open questions

Sources for v1: Cheshire Labs landscape image, public company sites, generally-known field knowledge as of training cutoff. No primary research yet.

**What needs verification:**

- Maturity / funding stage (drift-prone)
- Thesis assignments — inferred from public posture, not stated; worth confirming via founder talks/blog posts
- Companies couldn't be fully resolved from the image alone — see entries with `unverified: true`

**Worth adding next:**

- Founders / team size
- Last public funding round + investors
- Citation count / public talks (proxy for influence)
- Customer logos disclosed
- Open-source surface (does the company publish code? specs?)
- Geography (US / UK / EU / JP) — there's a real cluster pattern
