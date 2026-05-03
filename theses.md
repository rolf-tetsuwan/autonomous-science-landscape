<!-- GENERATED — edit data/*.yaml and run `python3 scripts/generate.py` -->

# Theses

Why isn't lab automation more widespread? Each company implicitly answers. 
Below: bet, what it predicts, what would falsify it, and who holds it (sorted by influence).

## Closed loop

> The missing piece is end-to-end loop closure: hypothesis → plan → execute → data →
model update → next hypothesis, with no human in the inner loop.

**Predicts:** The winning shape is autonomous-lab-as-a-product, where the customer hands over a goal (not a protocol) and the system iterates.

**Falsifier:** If customers keep wanting human-in-the-loop checkpoints (regulatory, scientific judgment, trust), closed-loop PMF narrows to a few high-volume use cases (mAb discovery, cell line dev) and doesn't generalize.

**Holders (influence-sorted):**

- ★ Arctoris — m4/i3
- Ginkgo Bioworks — m3/i3
- ★ Lila Sciences — m5/i2
- ★ Medra — m5/i2
- Emerald Cloud Lab — m3/i2
- Strateos `[acquired]` — m3/i2
- Tetsuwan Scientific — m5/i1
- Monomer Bio — m2/i1

## Dexterity

> The actual bottleneck is physical: robots can't reliably manipulate fragile biology.
Better hands and perception unlock the rest.

**Predicts:** Humanoid or high-DoF arms, not gantry liquid handlers, eat the long tail.

**Falsifier:** Standardization (SiLA + SBS plates) makes dexterity moot for 90% of tasks because everything moves through standardized fixtures.

**Holders (influence-sorted):**

- Multiply Labs — m4/i3
- Cellares — m3/i3
- Medra — m5/i2
- ★ Robot On Rails — m5/i1
- Tetsuwan Scientific — m5/i1
- Zeon Systems — m5/i1

## VLA / mimicking scientists

> Vision-language-action models that watch a scientist and imitate the manipulations
are the cheapest path to general-purpose autonomy — bypassing formal protocol specs.

**Predicts:** Companies bet on data collection from human bench work. Hardware looks general-purpose (humanoid or arm-on-cart), not assay-specific.

**Falsifier:** Formal protocol authoring (Antha-style, Briefly-style) plus deterministic hardware is enough — imitation learning turns out unnecessary.

**Holders (influence-sorted):**

- Medra — m5/i2
- ★ Tetsuwan Scientific — m5/i1
- ★ Zeon Systems — m5/i1
- Robot On Rails — m4/i1

## Hardware modularity

> Lab automation has been killed by monolithic islands. The win is mix-and-match
modules with common interfaces — the lab equivalent of PCIe.

**Predicts:** Rail-and-cart systems, swappable end-effectors, decoupled scheduler from instruments.

**Falsifier:** Customers consistently prefer turnkey integrated cells because the integration cost of "modular" still falls on them.

**Holders (influence-sorted):**

- ★ Beckman Coulter Life Sciences — m4/i4
- ★ Cytiva — m4/i4
- ★ HighRes Biosolutions `[acquired]` — m4/i4
- Hamilton — m3/i4
- ★ Sartorius — m3/i4
- ★ Thermo Fisher Scientific — m3/i4
- ★ Automata — m5/i3
- Cellares — m4/i3
- ★ Multiply Labs — m4/i3
- ★ Agilent — m3/i3
- ★ Miltenyi Biotec — m3/i3
- ★ Molecular Devices — m3/i3
- ★ Revvity — m3/i3
- Tecan — m3/i3
- ★ Celltrio — m3/i2
- ★ Trilobio — m5/i1
- Robot On Rails — m3/i1
- Zeon Systems — m2/i1

## Compiler / abstraction / interface

> Lab work needs an LLVM: a high-level protocol language that compiles down to whatever
hardware is available. Without this, every protocol is bound to a specific instrument.

**Predicts:** Declarative protocol DSLs, hardware-abstraction layers, scheduler-agnostic protocol formats.

**Falsifier:** The abstraction leaks too much (liquid-class effects, instrument quirks) to compile cleanly, so people fall back to vendor-specific scripts.

**Holders (influence-sorted):**

- ★ Synthace — m5/i3
- ★ Artificial — m4/i3
- Biosero — m3/i3
- UniteLabs — m4/i2
- ★ Scispot — m3/i2
- RetiSoft — m2/i2
- ★ Cheshire Labs — m4/i1
- ★ Monomer Bio — m4/i1
- ★ Spaero Bio — m4/i1
- Trilobio — m4/i1
- Phylo — m3/i1
- ★ Genie Life Sciences `[defunct]` — m4/i0

## Standardization

> The bottleneck is interop. Until there's a SiLA-equivalent that everyone implements,
every integration is N×M custom work.

**Predicts:** Open driver standards, consortium work, and tools that only work if many vendors play.

**Falsifier:** Vendors continue to defect (proprietary advantages outweigh interop benefits) and the de facto standard ends up being whichever orchestrator has critical mass.

**Holders (influence-sorted):**

- ★ SiLA — m5/i4
- ★ Biosero — m4/i4
- ★ PyLabRobot — m4/i3
- ★ RetiSoft — m4/i3
- Artificial — m3/i3
- HighRes Biosolutions `[acquired]` — m3/i3
- ★ UniteLabs — m5/i2
- Cheshire Labs — m3/i1

## DOE — Design of experiments

> Scientists are running too few well-designed experiments. The constraint is in
planning, not execution. Bayesian / active-learning planners win.

**Predicts:** Thin-software companies that sit on top of any execution layer and tell scientists "run these 16 conditions next."

**Falsifier:** Execution capacity is so limited that even naive experimental designs saturate it — better DOE doesn't help until throughput catches up.

**Holders (influence-sorted):**

- Synthace — m4/i3
- ★ Kiin Bio — m5/i2
- Phylo — m3/i1

## Accountability

> Nobody automates because nobody wants to own the failure mode. The unblocker is
GMP-grade traceability, audit trails, signed protocol versions.

**Predicts:** Companies emphasize compliance, 21 CFR Part 11, ALCOA+, electronic signatures.

**Falsifier:** Small biotechs (the actual buyers of new automation) don't care about this and the pharma-grade compliance load is a tax that prevents the modern stack from competing.

**Holders (influence-sorted):**

- Charles River — m5/i5
- Miltenyi Biotec — m5/i5
- Cytiva — m4/i5
- Hamilton — m4/i5
- Sartorius — m4/i5
- Thermo Fisher Scientific — m3/i5
- ★ Cellares — m5/i4
- Agilent — m3/i4
- Beckman Coulter Life Sciences — m3/i4
- Benchling — m3/i4
- Revvity — m3/i4
- Tecan — m3/i4
- Multiply Labs — m5/i3
- Dash Bio — m4/i3
- Arctoris — m3/i3
- Labguru — m3/i3
- Celltrio — m2/i2
- Monomer Bio — m3/i1

## Trust

> Humans won't act on automated results unless they can see the work — replay the
experiment, inspect the data, see the LLM's reasoning.

**Predicts:** Rich provenance UIs, replay features, structured chain-of-thought logs, video review.

**Falsifier:** Customers actually treat automation like the dishwasher — once it works, they stop watching, and trust UX is over-invested.

**Holders (influence-sorted):**

- Briefly Bio — m3/i1
- Potato — m3/i1

## Scale

> Centralized mega-foundries beat distributed cottage automation on cost-per-experiment.
Aggregate demand into a few cloud labs and amortize hardware capex.

**Predicts:** Cloud labs, biofoundries, "send us your protocol, get data back" services.

**Falsifier:** Turnaround latency, IP-leakage fears, or the "I need to watch my cells" instinct keep most science on-prem despite worse unit economics. (This has been the empirical pattern.)

**Holders (influence-sorted):**

- ★ Charles River — m5/i5
- Cellares — m5/i4
- ★ Emerald Cloud Lab — m5/i4
- ★ Ginkgo Bioworks — m5/i4
- Recursion — m5/i4
- ★ Plasmidsaurus — m4/i4
- Arctoris — m4/i3
- ★ Dash Bio — m4/i3
- ★ Strateos `[acquired]` — m4/i3
- Lila Sciences — m4/i2
- ★ Cromatic — m3/i2
- Cornucopia Bio — m3/i1

## Knowledge work bottlenecks

> The constraint isn't bench execution — it's the cognitive layer above: literature
review, hypothesis generation, protocol authoring, data interpretation.

**Predicts:** AI co-scientists, lit-review agents, ELN copilots, protocol generators.

**Falsifier:** Cognitive automation produces plausible-sounding but scientifically poor outputs that fail to translate; the bench execution problem reasserts itself.

**Holders (influence-sorted):**

- ★ Benchling — m4/i4
- ★ Labguru — m3/i3
- ★ Edison Scientific — m5/i2
- ★ Potato — m5/i2
- Lila Sciences — m4/i2
- Medra — m4/i2
- Scispot — m4/i2
- Artificial — m3/i2
- Kiin Bio — m3/i2
- Opentrons — m2/i2
- ★ Phylo — m5/i1
- Cornucopia Bio — m4/i1
- Monomer Bio — m4/i1
- Zeon Systems — m4/i1
- Briefly Bio — m3/i1
- Cheshire Labs — m3/i1
- Robot On Rails — m3/i1
- Cromatic — m2/i1

## Liquid classes

> The unsexy real bottleneck of automation: dispensing accurately across viscosities,
surfactants, volumes, surface chemistry. Whoever solves this owns the bottom of the stack.

**Predicts:** Investment in non-contact dispensing (acoustic, drop-on-demand), better calibration, instrument-side ML for liquid-class detection.

**Falsifier:** Standard plate formats and reagent vendors converge on a small number of liquid classes, commoditizing this expertise.

**Holders (influence-sorted):**

- ★ Hamilton — m5/i5
- ★ Dispendix — m5/i4
- ★ Cytena — m4/i4
- ★ SPT Labtech — m4/i4
- ★ Tecan — m4/i4
- Beckman Coulter Life Sciences — m3/i4
- Formulatrix — m3/i3
- Miltenyi Biotec — m2/i3
- Revvity — m2/i3
- Dynamic Devices — m3/i2
- Integra Biosciences — m2/i2

## Hardware cost

> Automation is gated by per-workstation capex. Drop the entry-level cost an order
of magnitude and adoption follows the way Opentrons proved at the low end.

**Predicts:** Open-source hardware, China-made supply chains, OEM-lite plays, subscription/leasing.

**Falsifier:** Total cost of ownership is dominated by integration and reagent consumables, not capex — so a cheaper instrument doesn't move the adoption needle.

**Holders (influence-sorted):**

- ★ Opentrons — m5/i4
- ★ Formulatrix — m4/i4
- ★ Dynamic Devices — m4/i3
- ★ Integra Biosciences — m4/i3
- PyLabRobot — m3/i3
- SPT Labtech — m3/i3
- Automata — m2/i2
- Trilobio — m4/i1
- Genie Life Sciences `[defunct]` — m3/i0

## Predictive validity

> Most of the data we automate doesn't predict in-vivo / clinic. More-AI-friendly
modalities (high-content phenomics, organoids on chip, multi-modal omics) close
the gap.

**Predicts:** Phenotypic-screening platforms, organoid players, multi-modal data companies, AI-native CROs that own the readout.

**Falsifier:** Existing assays are predictive enough; the real bottleneck is throughput on those assays, not new readouts.

**Holders (influence-sorted):**

- ★ Insilico Medicine — m5/i4
- ★ Isomorphic Labs — m5/i4
- ★ Recursion — m5/i4
- ★ Relay Therapeutics — m5/i4
- ★ Owkin — m5/i3
- ★ Chai Discovery — m4/i3
- Lila Sciences — m4/i2
- Arctoris — m2/i2
- Edison Scientific — m2/i1

## Eroom's law / R&D productivity

> Drug R&D productivity has been falling for 60 years. Automation is the only thing
that bends the curve. The thesis is macro, not technical.

**Predicts:** The background fundraising thesis for the entire category.

**Falsifier:** Newer modalities (ML-derived targets, GLP-1-style hits) drive productivity recovery without needing automation, and the curve bends without lab autonomy.

**Holders (influence-sorted):**

- Recursion — m5/i4
- Insilico Medicine — m5/i3
- Ginkgo Bioworks — m4/i3
- Isomorphic Labs — m4/i3
- Lila Sciences — m4/i2
- Owkin — m3/i2
- Edison Scientific — m3/i1

## Protocol libraries

> The win is a shared, versioned, executable corpus of protocols — like GitHub for
wet lab. Once enough protocols are machine-readable, everything downstream gets easier.

**Predicts:** Companies that obsess over protocol formats, version control, sharing, and converting between them.

**Falsifier:** Protocols are too tacit / lab-specific to share at scale, and the corpus never reaches critical mass.

**Holders (influence-sorted):**

- Opentrons — m4/i3
- ★ Briefly Bio — m5/i2
- PyLabRobot — m2/i2
- Spaero Bio — m3/i1
- Potato — m2/i1

## Next-generation hardware

> Incremental modularity isn't enough — the path forward is fundamentally new form
factors: humanoid arms, novel actuators, bench-scale robots that look nothing like
a Hamilton STAR.

**Predicts:** General-purpose arms, glass-cube robotic scientists, rail-and-cart fleets, bipedal/wheeled mobile manipulators that share a deck with a human.

**Falsifier:** Standardized SBS plates plus deterministic gantries are sufficient for >90% of biology, and "next-generation hardware" is a fundraising thesis that doesn't survive contact with assay-specific reality.

**Holders (influence-sorted):**

- Cellares — m4/i4
- Multiply Labs — m4/i3
- Medra — m4/i2
- Automata — m3/i2
- Tetsuwan Scientific — m5/i1
- Robot On Rails — m4/i1
- Zeon Systems — m4/i1
- Trilobio — m3/i1

## Remote execution

> The binding constraint is physical proximity — scientists having to be in the
building. Decoupling design from execution (cloud lab, browser-prompt CRO,
distributed lab) is the unlock.

**Predicts:** Browser/API-first interfaces, asynchronous protocols, no-physical-presence workflows, geographically distributed teams running experiments together.

**Falsifier:** The "I need to watch my cells" instinct holds; remote execution stays niche because lab work has too much tacit, in-person knowledge transfer.

**Holders (influence-sorted):**

- Emerald Cloud Lab — m5/i5
- Plasmidsaurus — m3/i4
- Arctoris — m4/i3
- Dash Bio — m4/i3
- Strateos `[acquired]` — m4/i3
- Charles River — m2/i3
- ★ Cornucopia Bio — m5/i2
- Lila Sciences — m3/i2
- Medra — m3/i2
- Ginkgo Bioworks — m2/i2

## Multi-modal sensing

> Visible-light cameras alone (the VLA route) miss too much: pipette aspiration
feedback, weight, temperature, vibration, capacitance, force. The unlock is
instruments that combine many sensor modalities.

**Predicts:** Capacitive liquid-level detection, force-feedback dispensing, weight-on-deck integration, multi-spectral imaging, audio for failure detection.

**Falsifier:** Vision + a small number of standardized fixtures is enough; richer sensing is over-engineered and the cost-per-error-caught isn't worth the integration burden.

**Holders (influence-sorted):**

- Molecular Devices — m4/i4
- Hamilton — m3/i4
- Dynamic Devices — m4/i3
- Cellares — m2/i3
- Cytena — m2/i3
- Multiply Labs — m3/i2
- Formulatrix — m2/i2
- Spaero Bio — m4/i1
- Genie Life Sciences `[defunct]` — m3/i0
