<!-- GENERATED — edit data/*.yaml and run `python3 scripts/generate.py` -->

# Theses

Why isn't lab automation more widespread? Each company implicitly answers. Below: bet, what it predicts, what would falsify it, and who currently holds it.

## Closed loop

> The missing piece is end-to-end loop closure: hypothesis → plan → execute → data →
model update → next hypothesis, with no human in the inner loop.

**Predicts:** The winning shape is autonomous-lab-as-a-product, where the customer hands over a goal (not a protocol) and the system iterates.

**Falsifier:** If customers keep wanting human-in-the-loop checkpoints (regulatory, scientific judgment, trust), closed-loop PMF narrows to a few high-volume use cases (mAb discovery, cell line dev) and doesn't generalize.

**Primary holders:** LILA Sciences, Medra
**Secondary holders:** Emerald Cloud Lab, Ginkgo Bioworks, Strateos, Tetsuwan Scientific

## Dexterity

> The actual bottleneck is physical: robots can't reliably manipulate fragile biology.
Better hands and perception unlock the rest.

**Predicts:** Humanoid or high-DoF arms, not gantry liquid handlers, eat the long tail.

**Falsifier:** Standardization (SiLA + SBS plates) makes dexterity moot for 90% of tasks because everything moves through standardized fixtures.

**Secondary holders:** Medra, Multiply Labs, Tetsuwan Scientific

## VLA / mimicking scientists

> Vision-language-action models that watch a scientist and imitate the manipulations
are the cheapest path to general-purpose autonomy — bypassing formal protocol specs.

**Predicts:** Companies bet on data collection from human bench work. Hardware looks general-purpose (humanoid or arm-on-cart), not assay-specific.

**Falsifier:** Formal protocol authoring (Antha-style, Briefly-style) plus deterministic hardware is enough — imitation learning turns out unnecessary.

**Primary holders:** Tetsuwan Scientific

## Hardware modularity

> Lab automation has been killed by monolithic islands. The win is mix-and-match
modules with common interfaces — the lab equivalent of PCIe.

**Predicts:** Rail-and-cart systems, swappable end-effectors, decoupled scheduler from instruments.

**Falsifier:** Customers consistently prefer turnkey integrated cells because the integration cost of "modular" still falls on them.

**Primary holders:** Agilent, Automata, Beckman Coulter Life Sciences, Celltrio, Cytiva, HighRes Biosolutions, Miltenyi Biotec, Molecular Devices, Multiply Labs, PerkinElmer / Revvity, Robot On Rails, Sartorius, Thermo Fisher Scientific, Trilobio
**Secondary holders:** Hamilton, Tecan, Zeon Systems

## Compiler / abstraction / interface

> Lab work needs an LLVM: a high-level protocol language that compiles down to whatever
hardware is available. Without this, every protocol is bound to a specific instrument.

**Predicts:** Declarative protocol DSLs, hardware-abstraction layers, scheduler-agnostic protocol formats.

**Falsifier:** The abstraction leaks too much (liquid-class effects, instrument quirks) to compile cleanly, so people fall back to vendor-specific scripts.

**Primary holders:** Artificial, Scispot, Synthace
**Secondary holders:** Biosero, Medra, Trilobio, UniteLabs

## Standardization

> The bottleneck is interop. Until there's a SiLA-equivalent that everyone implements,
every integration is N×M custom work.

**Predicts:** Open driver standards, consortium work, and tools that only work if many vendors play.

**Falsifier:** Vendors continue to defect (proprietary advantages outweigh interop benefits) and the de facto standard ends up being whichever orchestrator has critical mass.

**Primary holders:** Biosero, PyLabRobot, RetiSoft, SiLA, UniteLabs
**Secondary holders:** Artificial, HighRes Biosolutions

## DOE — Design of experiments

> Scientists are running too few well-designed experiments. The constraint is in
planning, not execution. Bayesian / active-learning planners win.

**Predicts:** Thin-software companies that sit on top of any execution layer and tell scientists "run these 16 conditions next."

**Falsifier:** Execution capacity is so limited that even naive experimental designs saturate it — better DOE doesn't help until throughput catches up.

**Primary holders:** Kiin Bio, Phylo
**Secondary holders:** Synthace

## Accountability

> Nobody automates because nobody wants to own the failure mode. The unblocker is
GMP-grade traceability, audit trails, signed protocol versions.

**Predicts:** Companies emphasize compliance, 21 CFR Part 11, ALCOA+, electronic signatures.

**Falsifier:** Small biotechs (the actual buyers of new automation) don't care about this and the pharma-grade compliance load is a tax that prevents the modern stack from competing.

**Secondary holders:** Benchling, Charles River, Labguru, Miltenyi Biotec, Multiply Labs

## Trust

> Humans won't act on automated results unless they can see the work — replay the
experiment, inspect the data, see the LLM's reasoning.

**Predicts:** Rich provenance UIs, replay features, structured chain-of-thought logs, video review.

**Falsifier:** Customers actually treat automation like the dishwasher — once it works, they stop watching, and trust UX is over-invested.

**Secondary holders:** Briefly Bio, Potato

## Scale

> Centralized mega-foundries beat distributed cottage automation on cost-per-experiment.
Aggregate demand into a few cloud labs and amortize hardware capex.

**Predicts:** Cloud labs, biofoundries, "send us your protocol, get data back" services.

**Falsifier:** Turnaround latency, IP-leakage fears, or the "I need to watch my cells" instinct keep most science on-prem despite worse unit economics. (This has been the empirical pattern.)

**Primary holders:** Charles River, Emerald Cloud Lab, Ginkgo Bioworks, Plasmidsaurus, Strateos, Zeon Systems
**Secondary holders:** LILA Sciences, Recursion

## Knowledge work bottlenecks

> The constraint isn't bench execution — it's the cognitive layer above: literature
review, hypothesis generation, protocol authoring, data interpretation.

**Predicts:** AI co-scientists, lit-review agents, ELN copilots, protocol generators.

**Falsifier:** Cognitive automation produces plausible-sounding but scientifically poor outputs that fail to translate; the bench execution problem reasserts itself.

**Primary holders:** Benchling, Edison, Labguru, Potato
**Secondary holders:** Briefly Bio, Kiin Bio, Phylo, Scispot

## Liquid classes

> The unsexy real bottleneck of automation: dispensing accurately across viscosities,
surfactants, volumes, surface chemistry. Whoever solves this owns the bottom of the stack.

**Predicts:** Investment in non-contact dispensing (acoustic, drop-on-demand), better calibration, instrument-side ML for liquid-class detection.

**Falsifier:** Standard plate formats and reagent vendors converge on a small number of liquid classes, commoditizing this expertise.

**Primary holders:** Cytena, Dispendix, Hamilton, SPT Labtech, Tecan
**Secondary holders:** Beckman Coulter Life Sciences, Formulatrix, Integra Biosciences

## Hardware cost

> Automation is gated by per-workstation capex. Drop the entry-level cost an order
of magnitude and adoption follows the way Opentrons proved at the low end.

**Predicts:** Open-source hardware, China-made supply chains, OEM-lite plays, subscription/leasing.

**Falsifier:** Total cost of ownership is dominated by integration and reagent consumables, not capex — so a cheaper instrument doesn't move the adoption needle.

**Primary holders:** Dynamic Devices, Formulatrix, Integra Biosciences, Opentrons
**Secondary holders:** PyLabRobot, Robot On Rails, SPT Labtech, Trilobio

## Predictive validity

> Most of the data we automate doesn't predict in-vivo / clinic. More-AI-friendly
modalities (high-content phenomics, organoids on chip, multi-modal omics) close
the gap.

**Predicts:** Phenotypic-screening platforms, organoid players, multi-modal data companies, AI-native CROs that own the readout.

**Falsifier:** Existing assays are predictive enough; the real bottleneck is throughput on those assays, not new readouts.

**Primary holders:** Chai Discovery, Insilico Medicine, Isomorphic Labs, Owkin, Recursion, Relay Therapeutics
**Secondary holders:** Edison, LILA Sciences

## Eroom's law / R&D productivity

> Drug R&D productivity has been falling for 60 years. Automation is the only thing
that bends the curve. The thesis is macro, not technical.

**Predicts:** The background fundraising thesis for the entire category.

**Falsifier:** Newer modalities (ML-derived targets, GLP-1-style hits) drive productivity recovery without needing automation, and the curve bends without lab autonomy.

**Secondary holders:** Ginkgo Bioworks, Insilico Medicine, Isomorphic Labs, LILA Sciences, Recursion

## Protocol libraries

> The win is a shared, versioned, executable corpus of protocols — like GitHub for
wet lab. Once enough protocols are machine-readable, everything downstream gets easier.

**Predicts:** Companies that obsess over protocol formats, version control, sharing, and converting between them.

**Falsifier:** Protocols are too tacit / lab-specific to share at scale, and the corpus never reaches critical mass.

**Primary holders:** Briefly Bio, Spaero Bio
**Secondary holders:** Opentrons, Potato
