# One Loop: Discovery and Invention

**One Loop design docs:** [1. Observations and principles](01_observations.md) · [2. Derived features](02_features.md) · [3. System design](03_system_design.md) · [4. Implementation plan](04_implementation_plan.md) · [5. Applications](05_applications.md) · [6. Media creation](06_media_creation.md) · [7. Companion](07_companion.md) · [8. Discovery and invention](08_discovery_invention.md) · [9. Robotics](09_robotics.md) · [References](references.md)

Discovery seeks a true belief: an explanation, a law, a mechanism. Invention seeks an artifact that meets a goal: a molecule, a material, a design, an algorithm. This document describes how One Loop does both with one loop, then applies it to three domains: explaining complex phenomena, invention and engineering design, and drug and materials discovery. Among the [applications](05_applications.md#order) they come after software engineering, the testbeds and agents in untrusted environments, because their value signals range from exact (computation) to slow and costly (the laboratory).

## Contents

- [How One Loop discovers and invents](#discovery-loop)
- [Explaining complex phenomena](#explanation)
- [Invention and engineering design](#invention)
- [Drug and materials discovery](#drug-materials)

<a id="discovery-loop"></a>

## How One Loop discovers and invents

Discovery and invention run on the same loop with different goals. **Discovery** seeks a true belief: an explanation, a law, a mechanism. **Invention** seeks an artifact that meets a goal: a molecule, a material, a design, an algorithm. Both follow one pattern: generate candidates beyond what the prior favors, test them against a value signal that can be trusted, commit to the survivors, and fold what was learned back into the prior. AlphaGo's move 37 is the pattern in one move: search found what its human-trained prior rated about 1 in 10,000, and the value network confirmed it.

**Three levels of one loop.** Each step at one level is a whole loop at the level below (claim 2).


| Level      | Goal, with its TOTE test                                                         | One step                                                   |
| ---------- | -------------------------------------------------------------------------------- | ---------------------------------------------------------- |
| Campaign   | "A solid electrolyte: conductivity above a target, stable against lithium, no rare elements" | Choose a direction: a family, a hypothesis, a design concept |
| Candidate  | "Is this family promising?"                                                      | Generate and screen a batch of candidates                  |
| Experiment | "What is this candidate's conductivity?"                                         | Run one simulation, assay or measurement                   |


Writing the campaign's test explicitly is half of invention: a vague goal cannot be searched.

**Generation: divergence in scratch.** G proposes candidates through operators, each a skill in P:

- **Recombination** of known parts from P and M.
- **Variation** around the best candidates so far.
- **Analogy:** carry relational structure across domains (Gentner), such as "what makes sodium conductors fast may work for lithium".
- **Relaxation:** drop a constraint, solve the easier problem, then restore the constraint (Pólya).
- **First principles:** use invariants, conservation and symmetry to rule regions in or out.
- **An exploration floor:** a minimum budget for candidates the prior rates as unlikely. The prior guides search; it must not veto it.
- **A novelty check:** recall prior art from M and the literature, so that the agent does not rediscover what is known.

**Evaluation: a ladder of verifiers.** Candidates climb from cheap, reversible checks to expensive, trustworthy ones, and only survivors move up:


| Rung                    | Example                                         | Cost             | Trust                         | Reversibility (R1)        |
| ----------------------- | ----------------------------------------------- | ---------------- | ----------------------------- | ------------------------- |
| Critique                | Internal critic: is it plausible?               | Milliseconds     | Low                           | Reversible                |
| Surrogate model         | Learned property predictor                      | Seconds          | Medium; poor outside its data | Reversible                |
| Physics simulation      | DFT, molecular dynamics, finite elements        | Hours to days    | Higher                        | Reversible                |
| Experiment              | Synthesis and measurement                       | Weeks            | High                          | Compensable               |
| Scale-up or trial       | Pilot plant, clinical trial                     | Months to years  | Highest                       | Irreversible; human-gated |


Two rules keep the ladder honest:

- **K chooses the next experiment by value of information per unit cost** (Bayesian optimization, active learning): the measurement that best separates the leading candidates or hypotheses, not the one that confirms the favorite.
- **Proxies rank; only higher rungs teach.** Surrogate and simulation scores decide what moves up, but only results verified high on the ladder pass the consolidation gate. Otherwise the agent learns its proxies' errors.

**Surprise is the engine of discovery.** Many discoveries began as anomalies. When a trusted measurement contradicts the forward model ("predicted 10 mS/cm, measured 1"):

1. K treats the surprise as high-value, reopens the belief and starts an explanation loop.
2. Scratch keeps several working hypotheses alive (Chamberlin): grain boundaries, the wrong phase, impurities.
3. The next experiment is the one that best separates them; impedance spectroscopy, for example, distinguishes bulk from grain-boundary conduction.
4. The result becomes a lesson in M ("the surrogate overestimates conductivity for this family"), and the predicted error for that region goes up.
5. The next round directs targeted experiments there, and the surrogate is retrained.

A failed candidate thus yields a better model of where the agent's own models are wrong. Across campaigns, that is the main thing that accumulates.

**Intuition.** Across campaigns, consolidation builds [intuition](03_system_design.md#intuition): fast proposals and value estimates distilled from verified results. Intuition chooses promising campaigns, orders candidates and serves as a free first rung of the ladder. It is trusted only as far as its measured hit rate, and it never vetoes the exploration floor. When a campaign stalls, K can incubate it: park it for the sleep cycle and return later. A [sense of beauty](03_system_design.md#beauty), built and calibrated the same way, favors candidates that compress and unify, and treats a growing pile of patches as a sign the framework is wrong.

**Consolidation across campaigns.**

- **E** logs every experiment, *including failures*. Negative results are valuable and mostly missing from the published literature.
- **Phase 1** compresses episodes into structure–property knowledge in M ("substituting X raises conductivity and lowers stability").
- **Phase 2** retrains the surrogates on newly verified data: expert iteration, so that what search found becomes the next round's prior.
- **Phase 3** generates counterfactuals ("what if this substituent were different?") as candidates for the next campaign.
- **P** gains compiled protocols, such as synthesis routes and simulation workflows, so that later campaigns start faster.

**Teams, people and permissions.**

- Parallel loops ([columns or agents](05_applications.md#multi-loop)) explore different families or hypotheses. Keeping them diverse prevents collapse onto one idea; peers check each other's results, not each other's ideas.
- Domain experts work through the teacher channel: constraints, taste, corrections, and approval of every step that cannot be undone.
- Grants (R9): simulation compute can be granted in advance; lab requests, spending and anything hazardous need approval. Hazard screening checks *what* is designed ([dual use](05_applications.md#safety)).

**A worked example: one campaign.**

1. **Specify and grant:** targets for conductivity, stability and elements; simulation granted; lab gated.
2. **Recall prior art:** known families (garnets, sulfides, argyrodites); novelty required.
3. **Generate** about 100,000 candidates by substitution, analogy and the exploration floor.
4. **Climb the ladder:** surrogate → about 1,000; stability simulation → about 50; conductivity simulation → about 5; human-approved synthesis → 3; one tested in a cell.
5. **Surprise:** one candidate underperforms. The explanation loop finds grain-boundary resistance, the surrogate is recalibrated for that family, and the next round is sharper.
6. **Consolidate:** new data, a corrected surrogate and a compiled synthesis route carry into the next campaign.

**Closest existing systems.** FunSearch (2023) and AlphaEvolve (2025) run the generate-and-verify core where the evaluator is exact: a language model writes programs, an automatic evaluator scores them, and an evolving database keeps the best. Their results include new constructions for the cap set problem and a 4×4 complex matrix multiplication with 48 scalar multiplications, one fewer than Strassen's method. They lack hierarchy, a controller and consolidation across campaigns. In the laboratory, an autonomous synthesis lab (A-Lab) and large-scale crystal prediction (GNoME), both 2023, were followed by critiques arguing that some reported new materials were not new or not correctly characterized. That is the failure that One Loop's prior-art check and verifier ladder are meant to catch.

**Where it is hard.**


| Problem                                           | Mitigation                                                                                     |
| ------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| The gap between proxy and reality                 | The verifier ladder; only verified results consolidate; calibrated predicted error            |
| Expensive experiments, little data                | Value-of-information experiment choice; built-in physics priors ([sample efficiency](03_system_design.md#innate-structure)) |
| Language-model generation stays near the familiar | Structured operators; the exploration floor; diverse parallel loops                           |
| A wrong specification                             | Reframing is allowed, but through the goal gate and with the grantor's approval               |
| Rediscovery; fabricated citations                 | Recall against prior art; novelty as part of the TOTE test                                    |
| Fluent but wrong explanations                     | Multiple working hypotheses; judgment by prediction and intervention                          |
| Dual use                                          | Hazard screening in the action gate; human-gated experiments                                  |


**Where to start.** Follow the quality of the top rung:

1. **Computational discovery**, where the top rung is exact and free: algorithms and code (the AlphaEvolve pattern), mathematical conjectures, interpretability.
2. **Engineering design checked by simulation:** structures, circuits, fluid flow.
3. **Discovery with a laboratory in the loop:** materials, then drugs, with every irreversible step human-gated.

<a id="explanation"></a>

## Explaining complex phenomena

Explanation is the step loop applied to hypotheses: hypothesize, predict, test, update the belief. The last of the [build stages](04_implementation_plan.md#build-stages), formal operations, is already systematic hypothesis search with metareasoning.

- **Scratch** works out what each hypothesis implies.
- **K's info-gain signal** chooses the experiment that best separates competing hypotheses.
- **Surprise** flags anomalies, which drive revision.
- **Consolidation** compresses results into theory: episode → gist → law.

**Where it works best:** where intervention is free, so experiments are reversible and cheap. Mechanistic interpretability of neural networks may be the best fit of all, since any component can be ablated or patched as often as needed. Root-cause analysis of software systems and equation discovery from simulations follow. Observational sciences (epidemiology, climate, economics) are harder, because confounding limits what the loop can confirm without intervention.

**The main risk is the just-so story:** a fluent explanation that fits the data and is wrong, and the fluency of language models makes it worse. Three countermeasures:

- **Keep several hypotheses alive in scratch** and delay commitment: Chamberlin's "method of multiple working hypotheses" (1890), as a job for the inner loop.
- **Judge an explanation by prediction, not plausibility:** forecasts on data not yet seen, results of interventions, and compression of the data.
- **Hold explanations as beliefs, not goals,** so contradicting evidence revises them instead of being explained away. This is goal shielding in reverse.

<a id="invention"></a>

## Invention and engineering design

Creativity is commonly modeled as *blind variation and selective retention* (Campbell, 1960): generate widely, then select. That is the [discovery loop](#discovery-loop) above: divergence through the generation operators, curiosity through K's info-gain signal, recombination in the REM-like phase of [sleep](03_system_design.md#sleep-cycle), composition through the hierarchy from concept to subsystem to part, and analogy as the core mechanism of invention.

Invention has a partly checkable value signal: function can be simulated, novelty checked against prior art, and cost modeled. Prototypes move along the reversibility ladder from simulation to physical builds. Generative engineering design is a good first target.

<a id="drug-materials"></a>

## Drug and materials discovery

This is the [discovery loop](#discovery-loop) with a laboratory as the top rungs of the verifier ladder: in-silico design is reversible and cheap, synthesis and assays are costly but compensable, and clinical trials or scale-up commitments are irreversible and gated. The risk is the value signal: optimizing against a docking score or a DFT simulation finds the proxy's errors, so cheap proxies rank candidates and only experiments feed the consolidation gate. Self-driving labs are the early form of this domain. It is high value, and it stays human-gated for a long time.

References are collected in [References](references.md).
