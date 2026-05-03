<!-- GENERATED — edit data/*.yaml and run `python3 scripts/generate.py` -->

# By thesis

Companies grouped by which bottleneck thesis they hold. **Primary** = first thesis listed in their record. 
Most companies hold 2–3.

*A thesis with many companies is a crowded narrative; a thesis with few is either contrarian or under-served.*

## Hardware modularity

> Lab automation has been killed by monolithic islands. The win is mix-and-match
modules with common interfaces — the lab equivalent of PCIe.

**Holders: 17 total** (**very crowded**) — 14 primary, 3 secondary

**Primary holders:** Agilent, Automata, Beckman Coulter Life Sciences, Celltrio, Cytiva, HighRes Biosolutions, Miltenyi Biotec, Molecular Devices, Multiply Labs, PerkinElmer / Revvity, Robot On Rails, Sartorius, Thermo Fisher Scientific, Trilobio
**Secondary holders:** Hamilton, Tecan, Zeon Systems

## Scale

> Centralized mega-foundries beat distributed cottage automation on cost-per-experiment.
Aggregate demand into a few cloud labs and amortize hardware capex.

**Holders: 8 total** (**very crowded**) — 6 primary, 2 secondary

**Primary holders:** Charles River, Emerald Cloud Lab, Ginkgo Bioworks, Plasmidsaurus, Strateos, Zeon Systems
**Secondary holders:** LILA Sciences, Recursion

## Knowledge work bottlenecks

> The constraint isn't bench execution — it's the cognitive layer above: literature
review, hypothesis generation, protocol authoring, data interpretation.

**Holders: 8 total** (**very crowded**) — 4 primary, 4 secondary

**Primary holders:** Benchling, Edison, Labguru, Potato
**Secondary holders:** Briefly Bio, Kiin Bio, Phylo, Scispot

## Liquid classes

> The unsexy real bottleneck of automation: dispensing accurately across viscosities,
surfactants, volumes, surface chemistry. Whoever solves this owns the bottom of the stack.

**Holders: 8 total** (**very crowded**) — 5 primary, 3 secondary

**Primary holders:** Cytena, Dispendix, Hamilton, SPT Labtech, Tecan
**Secondary holders:** Beckman Coulter Life Sciences, Formulatrix, Integra Biosciences

## Hardware cost

> Automation is gated by per-workstation capex. Drop the entry-level cost an order
of magnitude and adoption follows the way Opentrons proved at the low end.

**Holders: 8 total** (**very crowded**) — 4 primary, 4 secondary

**Primary holders:** Dynamic Devices, Formulatrix, Integra Biosciences, Opentrons
**Secondary holders:** PyLabRobot, Robot On Rails, SPT Labtech, Trilobio

## Predictive validity

> Most of the data we automate doesn't predict in-vivo / clinic. More-AI-friendly
modalities (high-content phenomics, organoids on chip, multi-modal omics) close
the gap.

**Holders: 8 total** (**very crowded**) — 6 primary, 2 secondary

**Primary holders:** Chai Discovery, Insilico Medicine, Isomorphic Labs, Owkin, Recursion, Relay Therapeutics
**Secondary holders:** Edison, LILA Sciences

## Compiler / abstraction / interface

> Lab work needs an LLVM: a high-level protocol language that compiles down to whatever
hardware is available. Without this, every protocol is bound to a specific instrument.

**Holders: 7 total** (**crowded**) — 3 primary, 4 secondary

**Primary holders:** Artificial, Scispot, Synthace
**Secondary holders:** Biosero, Medra, Trilobio, UniteLabs

## Standardization

> The bottleneck is interop. Until there's a SiLA-equivalent that everyone implements,
every integration is N×M custom work.

**Holders: 7 total** (**crowded**) — 5 primary, 2 secondary

**Primary holders:** Biosero, PyLabRobot, RetiSoft, SiLA, UniteLabs
**Secondary holders:** Artificial, HighRes Biosolutions

## Closed loop

> The missing piece is end-to-end loop closure: hypothesis → plan → execute → data →
model update → next hypothesis, with no human in the inner loop.

**Holders: 6 total** (**crowded**) — 2 primary, 4 secondary

**Primary holders:** LILA Sciences, Medra
**Secondary holders:** Emerald Cloud Lab, Ginkgo Bioworks, Strateos, Tetsuwan Scientific

## Accountability

> Nobody automates because nobody wants to own the failure mode. The unblocker is
GMP-grade traceability, audit trails, signed protocol versions.

**Holders: 5 total** (moderate) — 0 primary, 5 secondary

**Secondary holders:** Benchling, Charles River, Labguru, Miltenyi Biotec, Multiply Labs

## Eroom's law / R&D productivity

> Drug R&D productivity has been falling for 60 years. Automation is the only thing
that bends the curve. The thesis is macro, not technical.

**Holders: 5 total** (moderate) — 0 primary, 5 secondary

**Secondary holders:** Ginkgo Bioworks, Insilico Medicine, Isomorphic Labs, LILA Sciences, Recursion

## Protocol libraries

> The win is a shared, versioned, executable corpus of protocols — like GitHub for
wet lab. Once enough protocols are machine-readable, everything downstream gets easier.

**Holders: 4 total** (moderate) — 2 primary, 2 secondary

**Primary holders:** Briefly Bio, Spaero Bio
**Secondary holders:** Opentrons, Potato

## Dexterity

> The actual bottleneck is physical: robots can't reliably manipulate fragile biology.
Better hands and perception unlock the rest.

**Holders: 3 total** (thin) — 0 primary, 3 secondary

**Secondary holders:** Medra, Multiply Labs, Tetsuwan Scientific

## DOE — Design of experiments

> Scientists are running too few well-designed experiments. The constraint is in
planning, not execution. Bayesian / active-learning planners win.

**Holders: 3 total** (thin) — 2 primary, 1 secondary

**Primary holders:** Kiin Bio, Phylo
**Secondary holders:** Synthace

## Trust

> Humans won't act on automated results unless they can see the work — replay the
experiment, inspect the data, see the LLM's reasoning.

**Holders: 2 total** (thin) — 0 primary, 2 secondary

**Secondary holders:** Briefly Bio, Potato

## VLA / mimicking scientists

> Vision-language-action models that watch a scientist and imitate the manipulations
are the cheapest path to general-purpose autonomy — bypassing formal protocol specs.

**Holders: 1 total** (**very thin**) — 1 primary, 0 secondary

**Primary holders:** Tetsuwan Scientific

---

## Density ranking

| Thesis | Total holders | Primary | Secondary | Crowdedness |
|---|---:|---:|---:|---|
| Hardware modularity | 17 | 14 | 3 | very crowded |
| Scale | 8 | 6 | 2 | very crowded |
| Knowledge work bottlenecks | 8 | 4 | 4 | very crowded |
| Liquid classes | 8 | 5 | 3 | very crowded |
| Hardware cost | 8 | 4 | 4 | very crowded |
| Predictive validity | 8 | 6 | 2 | very crowded |
| Compiler / abstraction / interface | 7 | 3 | 4 | crowded |
| Standardization | 7 | 5 | 2 | crowded |
| Closed loop | 6 | 2 | 4 | crowded |
| Accountability | 5 | 0 | 5 | moderate |
| Eroom's law / R&D productivity | 5 | 0 | 5 | moderate |
| Protocol libraries | 4 | 2 | 2 | moderate |
| Dexterity | 3 | 0 | 3 | thin |
| DOE — Design of experiments | 3 | 2 | 1 | thin |
| Trust | 2 | 0 | 2 | thin |
| VLA / mimicking scientists | 1 | 1 | 0 | very thin |
