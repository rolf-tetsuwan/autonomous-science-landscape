# Autonomous Science Landscape

A working catalog of companies in the **autonomous science / lab automation / AI-for-bio** space, organized by what they build *and* the implicit thesis they hold about why lab automation hasn't gone the way of self-driving — i.e. why the field is still mostly stuck in islands of bespoke automation, manual SOPs, and irreproducible bench work.

Starting set was extracted from the Cheshire Labs landscape image (May 2026). Where a company sits in multiple categories on that map, it sits in multiple categories here too.

> Status: **first-pass working draft.** Some company-level fields (thesis, AI-level, maturity, premium/economical, customer focus) are educated guesses — explicitly marked with `?` when uncertain. Treat as a scaffold to refine, not an authoritative ranking.

---

## How to read this repo

| File | What it is |
|------|-----------|
| [`companies.md`](./companies.md) | Master table — one row per company with all tags |
| [`by-category.md`](./by-category.md) | Companies grouped by Cheshire-style functional category |
| [`by-thesis.md`](./by-thesis.md) | Companies grouped by which "why isn't automation more widespread" thesis they bet on |
| [`theses.md`](./theses.md) | Each thesis explained — what the bet is, who holds it, what would falsify it |
| [`companies.csv`](./companies.csv) | Same data as `companies.md`, machine-readable |

---

## The thesis framework

Each company is making (often implicitly) a bet about *the* binding constraint on autonomous science. Same plumbing problem, different theories of which valve is closed.

| Thesis | One-line bet |
|--------|--------------|
| **Closed loop** | The missing piece is end-to-end loop closure: hypothesis → experiment → data → model → next experiment, no human in the inner loop |
| **Dexterity** | Robots physically can't manipulate biology yet (cells, tissue, fragile reagents); better hands unlock everything |
| **VLA / mimicking scientists** | Vision-language-action models that watch and imitate bench scientists are the bridge to general-purpose lab autonomy |
| **Hardware modularity** | Monolithic islands kill scaling; the win is in modular, mix-and-match hardware that any orchestrator can compose |
| **Compiler / abstraction / interface** | Lab work needs the equivalent of LLVM — a high-level protocol language that targets any hardware backend |
| **Standardization** | The bottleneck is interop: SiLA, OPC-UA-for-bio, common driver layers. Without standards, every integration is custom |
| **DOE (Design of Experiments)** | Cognitive bottleneck: scientists don't run *enough* well-designed experiments. Better Bayesian / active-learning planners win |
| **Accountability** | Nobody automates because nobody wants to own the failure. Audit trails, GMP-grade traceability, regulatory plumbing unblock it |
| **Trust** | Humans don't trust automated results without seeing the work. UX of explainability/replay is the unblocker |
| **Scale** | Cloud labs / centralized mega-foundries beat distributed cottage automation on cost-per-experiment |
| **Knowledge work bottlenecks** | Bench execution isn't the constraint — protocol writing, lit review, hypothesis generation, data interpretation are. Automate the cognitive layer |
| **Liquid classes** | The unsexy real bottleneck: dispensing accuracy across viscosities, surfactants, volumes. Hardware that nails this wins |
| **Hardware cost** | Automation is gated by capex per workstation. Bring the entry-level cost down 10× and adoption follows |
| **Predictive validity** | The data we're automating doesn't predict in-vivo / clinic. More AI-friendly modalities (phenomics, organoids, ML-native readouts) are the answer |
| **Research costs / Eroom's law** | R&D productivity has been declining for decades. Automation is the only path to bend the curve |
| **Protocol libraries** | The win is a versioned, executable, shared corpus of protocols — like GitHub for wet lab |

See [`theses.md`](./theses.md) for full discussion of each.

---

## Tag legend

### `ai_level`
- **AI-native** — founded around an AI/ML thesis; product makes no sense without modern ML
- **AI-adopting** — traditional product surface, actively bolting on AI features (copilots, predictive scheduling, vision QC)
- **AI-adjacent** — instrument/software where AI is marketing veneer, not core
- **Standard / OSS** — a specification or open project, not a company

### `maturity`
- **Public** — listed on a public exchange
- **Late-stage** — Series C+ or established private with significant revenue
- **Mid-stage** — Series A/B
- **Early** — pre-seed to seed
- **Stealth** — known to exist, public profile thin
- **Mature private** — long-running private incumbent (e.g. family-owned instrument cos)
- **Standard** — not a company

### `customer`
Pharma · Big-pharma-CRO · Biotech (small/mid) · Academia · Synbio/biofoundry · Cell-therapy GMP · Diagnostics · Cloud-lab users (mostly drug-discovery startups) · All

### `pricing_posture`
- **Premium** — instrument-list-price tier; sold to pharma with a 6-figure quote
- **Mid** — accessible to series-A biotechs and well-funded academic cores
- **Economical** — designed to undercut on capex / democratize access

### `posture` (public messaging tilt)
A short phrase capturing what they *talk about* — separate from what they actually build. Useful for spotting positioning gaps and crowded narratives.

### `categories`
The Cheshire landscape columns:
- liquid-handling-hardware
- mobility-transport
- orchestration-scheduling
- hardware-integration-standards
- cell-culture-automation
- hypothesis-generation
- biofoundation-models
- lims
- eln
- experiment-planning
- flexible-protocol-generation
- closed-loop-experimentation
- data-generation
- cloud-labs
- cros-saas

A company can carry multiple.

---

## Methodology & open questions

**Sources for v1:** Cheshire Labs landscape image (May 2026), public company sites, generally-known field knowledge as of training cutoff. No primary research yet.

**What needs verification:**
- Maturity / funding stage on private companies (drift-prone)
- "Thesis" assignments — these are inferred from public posture, not stated. Worth confirming via founder talks/blog posts
- A handful of names I couldn't fully resolve from the image alone: `GENIE`, `ARES`, `DASH`, `Zeon Systems` (which Zeon?), `Cromatic bio`, `cornucopia bio`, `cheshire labs` itself
- Whether `Strateos` is still independent post-ECL discussions

**Worth adding next:**
- Founders / team size
- Last public funding round + investors
- Citation count / public talks (proxy for influence)
- Customer logos disclosed
- Open-source surface (does the company publish code? specs?)
- Geography (US / UK / EU / JP) — there's a real cluster pattern
- Whether they sell to other landscape-row companies (orchestrators selling to cloud labs, etc.)
