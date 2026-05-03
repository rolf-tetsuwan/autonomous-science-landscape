# The Theses

Why isn't lab automation more widespread, the way self-driving (sort of) is? Each company in this landscape implicitly answers that question. Below are the theses I've extracted, what they predict, and rough falsifiers.

The theses are not mutually exclusive — most serious companies hold 2–3 — but the *primary* one usually drives architecture choices.

---

## Closed loop

> The missing piece is end-to-end loop closure: hypothesis → plan → execution → data → model update → next hypothesis, with no human inside the inner loop.

**Predicts:** the winning shape is an autonomous-lab-as-a-product, where the customer hands over a goal (not a protocol) and the system iterates.

**Held by:** LILA Sciences, Medra, Tetsuwan Scientific, parts of Recursion, parts of Ginkgo.

**Falsifier:** if customers keep wanting human-in-the-loop checkpoints (because of regulatory, scientific judgment, or trust reasons) and pay more for that, closed-loop product-market-fit narrows to a few high-volume use cases (mAb discovery, cell line dev) and doesn't generalize.

---

## Dexterity

> The actual bottleneck is physical: robots can't reliably manipulate fragile biology — cells in suspension, soft tissue, irregular consumables, weird containers. Better hands and perception unlock the rest.

**Predicts:** humanoid or high-DoF arms, not gantry liquid handlers, eat the long tail.

**Held by:** Tetsuwan Scientific, Multiply Labs (manufacturing dexterity), partly Medra. (Notable: very few "pure dexterity" plays in this image — the field hasn't bet on this yet.)

**Falsifier:** if standardization (SiLA + SBS plates) makes dexterity moot for 90% of tasks because everything moves through standardized fixtures.

---

## VLA / mimicking scientists

> Vision-language-action models that watch a scientist and imitate the manipulations are the cheapest path to general-purpose autonomy — bypassing the need to specify protocols formally.

**Predicts:** companies bet on data collection from human bench work and on foundation models for lab actions. Hardware looks general-purpose (humanoid or arm-on-cart), not assay-specific.

**Held by:** Tetsuwan Scientific, parts of Edison/Potato (cognitive VLA), emerging.

**Falsifier:** if formal protocol authoring (Antha-style, Briefly-style) plus deterministic hardware is enough — i.e. the imitation-learning route turns out unnecessary because protocols can just be written.

---

## Hardware modularity

> Lab automation has been killed by monolithic islands (one Hamilton STAR, custom-integrated, never moves). The win is mix-and-match modules with common interfaces — the lab equivalent of PCIe.

**Predicts:** rail-and-cart systems, swappable end-effectors, decoupled scheduler from instruments.

**Held by:** Trilobio, Robot On Rails, Automata, Multiply Labs, HighRes Biosolutions, Zeon Systems (?).

**Falsifier:** if customers consistently prefer turnkey integrated cells because the integration cost of "modular" still falls on them.

---

## Compiler / abstraction / interface

> Lab work needs an LLVM: a high-level protocol language that compiles down to whatever hardware you happen to have. Without this, every protocol is bound to a specific instrument.

**Predicts:** declarative protocol DSLs, hardware-abstraction layers, scheduler-agnostic protocol formats.

**Held by:** Synthace (Antha), Trilobio, Scispot, Artificial, parts of Briefly Bio, parts of Potato.

**Falsifier:** the abstraction leaks too much (liquid-class effects, instrument quirks) to compile cleanly, so people fall back to vendor-specific scripts.

---

## Standardization

> The bottleneck is interop. Until there's a SiLA-equivalent that everyone implements, every integration is N×M custom work, and no orchestrator can scale.

**Predicts:** open driver standards, consortium work, and tools that *only* work if many vendors play.

**Held by:** SiLA (the standard), UniteLabs, PyLabRobot, RetiSoft, Biosero (Green Button Go's pluggable drivers).

**Falsifier:** vendors continue to defect (proprietary advantages outweigh interop benefits), and the de facto standard ends up being whichever orchestrator has critical mass — which is a different thesis (compiler).

---

## DOE — Design of Experiments

> Scientists are running too few well-designed experiments. The constraint is in planning, not execution. Bayesian / active-learning planners that decide *what* to run next move the needle more than faster execution.

**Predicts:** thin-software companies that sit on top of any execution layer and tell scientists "run these 16 conditions next."

**Held by:** Kiin Bio, Phylo, parts of LILA, parts of Synthace.

**Falsifier:** execution capacity is so limited that even naive experimental designs saturate it — better DOE doesn't help until throughput catches up.

---

## Accountability

> Nobody automates because nobody wants to own the failure mode. The unblocker is GMP-grade traceability, audit trails, signed protocol versions, and clean regulatory hand-off. (Mostly an unspoken thesis but it drives a lot of pharma adoption.)

**Predicts:** companies emphasize compliance, 21 CFR Part 11, ALCOA+, electronic signatures.

**Held by:** Benchling, labguru, Multiply Labs (cell therapy GMP), Charles River. Implicitly held by every pharma-facing tool.

**Falsifier:** small biotechs (the actual buyers of new automation) don't care about this and the pharma-grade compliance load is a tax that prevents the modern stack from competing.

---

## Trust

> Adjacent to accountability but UX-flavored: humans won't act on automated results unless they can see the work — replay the experiment, inspect the data, see the LLM's reasoning. Explainability/replay UX is the unblocker.

**Predicts:** rich provenance UIs, "replay" features, structured chain-of-thought logs, video review of bench work.

**Held by:** Briefly Bio (provenance angle), Potato (notebook explainability), parts of LILA, parts of Benchling.

**Falsifier:** customers actually treat automation like the dishwasher — once it works, they stop watching, and trust UX is over-invested.

---

## Scale

> Centralized mega-foundries beat distributed cottage automation on cost-per-experiment. Aggregate demand into a few cloud labs and amortize hardware capex.

**Predicts:** cloud labs, biofoundries, "send us your protocol, get data back" services.

**Held by:** Emerald Cloud Lab, Strateos, Ginkgo Bioworks, Zeon Systems (?), parts of LILA.

**Falsifier:** turnaround latency, IP-leakage fears, or the "I need to watch my cells" instinct keep most science on-prem despite worse unit economics. (This has been the empirical pattern for a decade.)

---

## Knowledge work bottlenecks

> The constraint isn't bench execution — it's the cognitive layer above it: literature review, hypothesis generation, protocol authoring, data interpretation. Automate the brain, not the hands.

**Predicts:** AI co-scientists, lit-review agents, ELN copilots, protocol generators.

**Held by:** Edison, Potato, Briefly Bio, Kiin Bio, Phylo, Benchling AI features, labguru AI.

**Falsifier:** cognitive automation produces plausible-sounding but scientifically poor outputs that fail to translate; the bench execution problem reasserts itself as the binding constraint.

---

## Liquid classes

> The unsexy real bottleneck of lab automation: dispensing accurately across viscosities, surfactants, volume scales, surface chemistry. Whoever solves this owns the bottom of the stack.

**Predicts:** investment in non-contact dispensing (acoustic, drop-on-demand), better calibration, instrument-side ML for liquid-class detection.

**Held by:** Hamilton (deep proprietary library), Tecan, Dispendix, SPT Labtech, Cytena, Formulatrix.

**Falsifier:** standard plate formats and reagent vendors converge on a small number of liquid classes, commoditizing this expertise.

---

## Hardware cost

> Automation is gated by per-workstation capex. Drop the entry-level cost an order of magnitude and adoption follows the way Opentrons proved at the low end.

**Predicts:** open-source hardware, China-made supply chains, OEM-lite plays, subscription/leasing models.

**Held by:** Opentrons, Trilobio, Robot On Rails, parts of PyLabRobot.

**Falsifier:** total cost of ownership is dominated by integration and reagent consumables, not capex — so a cheaper instrument doesn't move the adoption needle.

---

## Predictive validity

> Most of the data we're automating doesn't predict in-vivo or clinic outcomes. More-AI-friendly modalities (high-content phenomics, organoids on chip, multi-modal omics) close the predictive-validity gap and make automation worth doing.

**Predicts:** phenotypic-screening platforms, organoid players, multi-modal data companies, AI-native CROs that own the readout.

**Held by:** Recursion, Owkin, Insilico, Isomorphic, Chai Discovery, Relay Therapeutics.

**Falsifier:** existing assays are predictive enough; the real bottleneck is throughput on those assays, not new readouts.

---

## Research costs / Eroom's law

> Drug R&D productivity has been falling for 60 years (Eroom's law). Automation is the only thing that bends the curve. The thesis is macro, not technical: bet on automation because the alternative is industry collapse.

**Held by:** This is the *background* thesis everyone uses to raise money. Most explicitly: Recursion, Insilico, LILA, Ginkgo's pitch deck.

**Falsifier:** newer modalities (ML-derived targets, GLP-1-style hits) drive productivity recovery without needing automation, and the curve bends without lab autonomy.

---

## Protocol libraries

> The win is a shared, versioned, executable corpus of protocols — like GitHub for wet lab. Once enough protocols are in machine-readable form, everything downstream (planning, execution, reproducibility) gets easier.

**Predicts:** companies that obsess over protocol formats, version control, sharing, and converting between them.

**Held by:** Briefly Bio, Spaero Bio, Synthace, parts of Potato, Protocols.io (not in this image).

**Falsifier:** protocols are too tacit / lab-specific to share at scale, and the corpus never reaches critical mass.
