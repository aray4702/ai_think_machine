# One Loop: Applications

**One Loop design docs:** [1. Observations and principles](01_observations.md) · [2. Derived features](02_features.md) · [3. System design](03_system_design.md) · [4. Implementation plan](04_implementation_plan.md) · [5. Applications](05_applications.md) · [6. Media creation](06_media_creation.md) · [References](references.md)

The builder's next question is: *where should this agent be used first?* This document ranks candidate domains by how well they fit the design, and gives them in the recommended order: the first application, the domains that test the design in its purest form, then the domains where its safety and learning parts pay off, and last the domains where it should only support human decisions.

## Contents

- [How domains are ranked](#ranking)
- [Recommended order](#order)
- [Safety and permissions by domain](#safety)
- [1. Start here: software engineering](#software)
- [2. Pure forms and testbeds](#testbeds)
- [3. Agents in untrusted environments](#untrusted)
- [4. Discovery and explanation](#discovery)
  - [How One Loop discovers and invents](#discovery-loop)
- [5. Physical and social domains](#physical-social)
- [6. Decision support](#decision-support)
- [Not recommended: board games](#board-games)
- [Extension: multiple One Loops](#multi-loop)


<a id="ranking"></a>

## How domains are ranked

The [comparison with AlphaZero, MuZero and AlphaFold](03_system_design.md#alphazero) found one hard gap: outside games, the agent has no reliable signal of whether a step or an answer is good. Search against a noisy value function finds that function's errors. So the first criterion is the value signal, and the rest follow from the design's components.


| Criterion                | Question                                                                                 | Why it matters                                                         |
| ------------------------ | ---------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| Value signal             | Can a result be checked: by a test, a proof checker, a simulator, an experiment?          | Without it, search and consolidation amplify errors                    |
| Module coverage          | How many of M1–M6 does the domain exercise?                                              | A domain that uses every module can validate the whole design at once |
| Reversibility profile    | Does it mix reversible, compensable and irreversible actions (R1)?                       | The inner loop and action gate only matter when some actions are final |
| Untrusted input          | Do inputs come from sources that could carry instructions (F5)?                           | Goal shielding is tested only under attack                             |
| Repetition               | Do task families recur, so skills and lessons can carry across sessions (F2, F6)?        | Consolidation has nothing to learn from one-off situations             |
| Cost of a test           | Can the domain be sandboxed, reset and run thousands of times?                           | The [ablation](04_implementation_plan.md#ablation) needs many runs     |
| Harm ceiling             | What is the worst plausible outcome of a mistake or misuse?                              | It sets how much autonomy the domain can ever be given                 |


<a id="order"></a>

## Recommended order


| Order | Domain                               | Value signal                                         | What One Loop adds                                          | Role                    |
| ----- | ------------------------------------ | ---------------------------------------------------- | ----------------------------------------------------------- | ----------------------- |
| 1     | Software engineering                 | Tests and compilers                                  | Every module, M1–M6                                         | **First application**   |
| 2     | Formal mathematics                   | A proof checker (Lean)                               | Hierarchy, lemma library, stopping                          | Pure form of the design |
| 3     | Open-world games                     | Game score; save states                              | Hierarchy, skills, learning across sessions                 | Ablation testbed        |
| 4     | Computer-use and personal assistants | Task completion; user corrections                    | Goal shielding against injection; memory; user model        | Autonomous, gated       |
| 5     | IT operations and incident response  | Health checks; rollbacks                             | Reversibility classes; runbooks as skills; postmortems      | Autonomous, gated       |
| 6     | Cybersecurity defense                | Detections; red-team exercises                       | Gates; surprise signal; fast reflex tier                    | Autonomous, gated       |
| 7     | Explaining complex phenomena         | Predictions on unseen data; interventions            | Competing hypotheses; experiment choice; compression        | Autonomous where intervention is possible |
| 8     | Invention and engineering design     | Simulation; prior-art search                         | Divergent search; analogy; reversible prototyping           | Autonomous in simulation |
| 9     | Drug and materials discovery         | Simulated proxies; lab experiments                   | Reversibility classes; value-of-information experiment choice | Human-gated            |
| 10    | Robotics                             | Task success; physical safety                        | Tiers and reflexes; action gate; simulation as scratch      | Human-gated             |
| 11    | Tutoring                             | Student progress                                     | ZPD model of the student; fading scaffolds                  | Collaborator            |
| 12    | Business strategy                    | Slow, sparse outcomes                                | Goal shielding; one-way vs two-way doors; scenarios         | Decision support        |
| 13    | Art                                  | Human taste                                          | Divergence; recombination; memory of what worked            | Collaborator            |
| 14    | Portfolio management                 | Noisy, adversarial returns                           | Action gate; mandate shielding; disciplined inaction        | Risk wrapper            |
| —     | Board games                          | Perfect                                              | Almost nothing                                              | Already solved          |


The order runs from domains where results can be checked automatically to domains where only people can judge them. Autonomy follows the same gradient, which matches F7's rule that autonomy expands along the reversibility ladder as reliability is shown.

<a id="safety"></a>

## Safety and permissions by domain

Every domain runs inside explicit grants (R9) and follows the [safety recipe](03_system_design.md#safety-recipe). The table gives each domain's starting point on the autonomy ladder. A class of actions moves up only on measured reliability, and only when the grantor extends the grant.


| Domain                  | What is irreversible                                         | Main threat                                         | Starting autonomy and permissions                                                         |
| ----------------------- | ------------------------------------------------------------ | --------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| Software engineering    | Deleting data, force-pushing, deploying, sending messages    | Injection through issues and docs; editing tests    | Edit, branch and test in the sandbox; permission for history rewrites, pushes and deploys |
| Formal mathematics      | Nothing                                                      | Checker bugs; unsound axioms                        | Full autonomy inside the proof environment                                                 |
| Open-world games        | Nothing (sandboxed)                                          | Reward hacking                                      | Full autonomy inside the game                                                              |
| Computer-use assistants | Sending, paying, deleting, **disclosing data**               | Injection from web pages and email; data leaks      | Read and draft; permission to send, pay, delete or share                                   |
| IT operations           | Data loss, outages                                           | Cascading failures; harm composed from small steps  | Act where a tested rollback exists; permission otherwise                                   |
| Cybersecurity defense   | Blocking legitimate users; destroying evidence               | Adversarial deception                               | Containment actions granted in advance; people decide everything else                     |
| Explaining phenomena    | Publishing a wrong conclusion                                | Just-so stories                                     | Act in sandboxed experiments; people review conclusions before release                    |
| Invention, discovery    | Synthesis, trials, scale-up                                  | Proxy hacking; **dual-use designs**                 | Act in simulation; every experiment human-gated; hazard screening on what is designed     |
| Robotics                | Physical harm                                                | Situations unlike training                          | Reflex tier with hard limits; validated in simulation first                               |
| Tutoring                | Harm to a learner's trust and development                    | Sycophancy                                          | Collaborator; the teacher sets goals and limits                                            |
| Business, finance       | Contracts, trades, public statements                         | Manipulation by persuasive documents; acting on noise | Decision support; people execute                                                        |
| Art                     | Plagiarism; harmful content                                  | Copying training data                               | Collaborator; the person decides what is published                                        |


**Dual-use** is the specific risk of discovery: an agent good at inventing useful molecules is also good at inventing harmful ones. So in discovery the action gate also checks *what* is being designed, through hazard screening, not only *how reversible* the action is.

<a id="software"></a>

## 1. Start here: software engineering

**Why first.** It is the one domain where every module in the [ablation](04_implementation_plan.md#ablation) is exercised by a single task suite, and every module has a cheap implementation with current LLMs ([buildable today](04_implementation_plan.md#starting-point)).


| What One Loop needs                    | What software engineering provides                                                                          |
| -------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| A value signal                         | Tests and compilers                                                                                         |
| A real inner loop (M1)                 | Git branches and worktrees: a fork of the real state, not just of the reasoning                            |
| All three reversibility classes (M6)   | Edits are reversible; migrations and deploys are compensable; deleting data, force-pushing and sending messages are irreversible |
| Goal shielding under attack (M2)       | Issues, READMEs, dependency docs and tool output can carry injected instructions; users correct the agent mid-task |
| Hierarchy                              | Feature → subtasks → edits → commands                                                                       |
| Skills and consolidation (M4, M5)      | Recurring task families in the same codebase; procedures and lessons specific to it                         |
| Existing baselines                     | Long-horizon and requirement-driven benchmarks (SWE-EVO, SWE-bench Pro); time horizons at 80% reliability (METR); AgentDojo-style attacks for injection. SWE-bench Verified is saturated ([state of the field](#software-state)) |


Formal mathematics has a stricter value signal, but no irreversible actions and no injection threat, so it cannot test M2 or M6.

<a id="software-state"></a>

**State of the field (October 2026).** Software engineering is not solved, but the unsolved part has narrowed, and the first project must aim at what remains.


| Status                                    | Evidence                                                                                                                                                                                                 |
| ----------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Single, well-specified issues: saturated** | Top agents report about 95–97% on SWE-bench Verified (September 2026), and a September 2026 analysis argues the leaderboard can no longer rank its top entries. Scores are inflated: models reproduce some gold patches verbatim, one model scored 80.9% on Verified but 45.9% on the unseen SWE-bench Pro, and an OpenAI audit found flawed tests in 59.4% of the hardest unsolved Verified problems. |
| **Long tasks with a clear specification: largely within reach** | METR measured a frontier 50%-reliability time horizon of about 12 hours of expert time (February–March 2026), and on MirrorCode, which reimplements existing software, agents solved tasks that take humans weeks. |
| **Reliability: unsolved**                 | The same agents' 80%-reliability horizon was about 1.5 hours, roughly eight times shorter than at 50%.                                                                                                   |
| **Vague or evolving requirements: unsolved** | On SWE-EVO, multi-file changes driven by release notes, the best agent resolves 25%, against about 73% for the same model family on Verified; over 60% of the strong model's failures were in following instructions. |
| **Gaming the verifier: unsolved**         | On METR's hardest tasks, at least 16% of "successful" runs were illegitimate on review.                                                                                                                  |
| **Judgment, real-world messiness and taste: unsolved** | Real-world performance has consistently been weaker than benchmark scores suggest (METR), and taste in long-horizon work is an open research problem.                                       |
| **Not yet measured well**                 | Learning a codebase over many sessions, resistance to injection, and handling of permissions.                                                                                                            |


So the first project does not compete on single issues or on task length. It targets reliability, asking about vague requirements, verification that resists gaming, learning across sessions and maintainability, which map onto K's stopping and asking, the [verifier ladder](#discovery-loop), consolidation and the [beauty](03_system_design.md#beauty) signal.

**The first project.** A coding agent that works on the same codebases across many sessions, in a sandbox:

1. **Environment.** A few sandboxed codebases, each with a stream of related tasks over simulated "days", hidden tests the agent cannot edit, and mocked tools for irreversible actions (deploy, email, payment).
2. **Baselines.** A plain LLM agent, and a compute-matched plain agent.
3. **Modules, cheapest and most valuable first:**
   - **M6 action gate:** classify shell and git commands by reversibility; ask permission for irreversible ones.
   - **M2 goal register and source tags:** a goal file recited each step; repository content and tool output tagged as data that can inform but not instruct.
   - **M1 forkable scratch:** attempt a fix on a branch, run the tests, keep or discard.
   - **M4 and M5 skills and sleep:** codebase-specific procedures; memory files merged and pruned between sessions.
   - **M3 controller:** hand-set thresholds first, trained on the logs later.
4. **Tasks.** The ablation's categories: fixes where the first plausible attempt is wrong, benign corrections and planted injections, tasks of 50 or more steps, repeated task families, tempting destructive shortcuts, and tasks that need an ungranted action or face conflicting grants. Freshly written, with a time split ([validation](04_implementation_plan.md#validation)). Weighted toward what is unsolved:
   - **requirement-driven work:** changes specified by release notes, issues or conversations that are vague, incomplete or contradictory, where a good question is part of success;
   - **multi-session work** on the same codebase, measuring improvement without forgetting;
   - **maintainability:** whether the code stays simple and reviewable after many changes, not only whether tests pass.
5. **Metrics beyond solve rate:** success at 80% reliability, not only at 50%; the share of successful runs that are illegitimate on review (target: zero); the quality and number of clarifying questions; and the ablation's metrics ([ablation](04_implementation_plan.md#ablation)).

**How it can fail.**

- **Tests are imperfect verifiers.** Agents learn to edit or special-case tests; on METR's hardest tasks, at least 16% of successful runs were illegitimate. Hidden tests that the agent cannot edit, a check that flags edits to test files, and review of how successful runs succeeded are required, not optional.
- **The field is crowded, and single-issue benchmarks are saturated.** A higher solve rate alone shows little. The case for One Loop must rest on what other agents do not achieve or measure: reliability, handling of vague requirements, improvement across sessions without forgetting, resistance to injection, fewer irreversible errors, and module gains that hold at matched compute and matched data.

<a id="testbeds"></a>

## 2. Pure forms and testbeds

### Formal mathematics

The fit is almost one to one: lemmas are subgoals; tactic search with backtracking is the inner loop, where a failed attempt costs nothing; a growing lemma library is P; sleep consolidates proved lemmas for reuse across problems; K decides when to abandon an approach. The proof checker closes the value-signal gap, so search cannot reward-hack. AlphaProof shows that the search part works, and at IMO 2026 AxiomProver produced Lean-verified solutions to all six problems; competition mathematics is now saturated, so the test is research-level problems and checking that a formal proof matches the informal claim ([state of the field](04_implementation_plan.md#field-2026)). One Loop adds hierarchy, a library that grows across sessions, and stopping. Informal mathematics is much weaker, because nothing checks the steps. This domain reuses the core from the first project and tests hierarchy, the library and search in their purest form.

### Open-world games

Minecraft, NetHack and strategy games need long horizons, subgoals and reusable skills (Voyager is the existing example). They are cheap, resettable and parallel, and save states make actions reversible on demand. They are the **testbed** for running the ablation at scale, not the product.

<a id="untrusted"></a>

## 3. Agents in untrusted environments

These are the domains where the design's safety parts pay off most directly. Each can run autonomously behind the action gate once the modules have passed the ablation.

- **Computer-use and personal assistants** (email, browser, files). Goal shielding against injected instructions ([F5](02_features.md#f5)) is the central problem: every web page and email is untrusted input. Memory across sessions and the user model of the social interface matter too. Several 2026 reports put top agents above the human baseline on the OSWorld benchmark (not confirmed on the official leaderboard), but slow execution, multi-application workflows and injection remain the obstacles to deployment.
- **IT operations and incident response.** Runbooks are skills; changes have reversibility classes (config edits are reversible, deploys are compensable by rollback, deleting data is irreversible), which is R1 and the saga pattern; postmortems are consolidation in the sleep cycle.
- **Cybersecurity defense.** The environment is adversarial, inputs are untrusted and responses must be fast. The gates, the surprise signal and the reflex tier ([tiers](03_system_design.md#hierarchy-for-the-task-tiers-for-authority)) are the core of the design here.

<a id="discovery"></a>

## 4. Discovery and explanation

<a id="discovery-loop"></a>

### How One Loop discovers and invents

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

- Parallel loops ([columns or agents](#multi-loop)) explore different families or hypotheses. Keeping them diverse prevents collapse onto one idea; peers check each other's results, not each other's ideas.
- Domain experts work through the teacher channel: constraints, taste, corrections, and approval of every step that cannot be undone.
- Grants (R9): simulation compute can be granted in advance; lab requests, spending and anything hazardous need approval. Hazard screening checks *what* is designed ([dual use](#safety)).

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

### Explaining complex phenomena

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

### Invention and engineering design

Creativity is commonly modeled as *blind variation and selective retention* (Campbell, 1960): generate widely, then select. That is the [discovery loop](#discovery-loop) above: divergence through the generation operators, curiosity through K's info-gain signal, recombination in the REM-like phase of [sleep](03_system_design.md#sleep-cycle), composition through the hierarchy from concept to subsystem to part, and analogy as the core mechanism of invention.

Invention has a partly checkable value signal: function can be simulated, novelty checked against prior art, and cost modeled. Prototypes move along the reversibility ladder from simulation to physical builds. Generative engineering design is a good first target.

### Drug and materials discovery

This is the [discovery loop](#discovery-loop) with a laboratory as the top rungs of the verifier ladder: in-silico design is reversible and cheap, synthesis and assays are costly but compensable, and clinical trials or scale-up commitments are irreversible and gated. The risk is the value signal: optimizing against a docking score or a DFT simulation finds the proxy's errors, so cheap proxies rank candidates and only experiments feed the consolidation gate. Self-driving labs are the early form of this domain. It is high value, and it stays human-gated for a long time.

<a id="physical-social"></a>

## 5. Physical and social domains

- **Robotics.** The tiers were built for this: reflexes act first, and the action gate covers physical harm. There are no save states in the physical world, so a simulator serves as scratch, and autonomy grows along the reversibility ladder.
- **Tutoring.** [F7](02_features.md#f7) in reverse: the agent keeps a model of the *student's* zone of proximal development, chooses practice at the edge of the student's competence, and fades its scaffolding as the student grows.

<a id="decision-support"></a>

## 6. Decision support

In these domains feedback is slow, sparse, subjective or adversarial, so consolidation has little honest signal to learn from. The parts that still carry over are the gates and goal shielding, not the learning.

- **Business strategy.** Feedback takes quarters or years, and every situation is new. What carries over: reversibility classes, which are Bezos's "one-way and two-way doors" (R1 moves work toward two-way doors before committing); a shielded objective that holds against noise, pressure and persuasive documents; and scenario simulation of competitors' responses in scratch. The realistic role is a staff analyst. Operational decisions are the exception: pricing tests, A/B experiments and supply-chain tuning are reversible and give clean feedback, and One Loop can run them.
- **Art.** A related collaborator domain, prompts for AI media made personal, has its own document: [media creation](06_media_creation.md). There is no ground truth, and trained aesthetic critics get reward-hacked toward average taste, so a novelty term must push back. One deliberate change: open the goal gate wider for surprises from the agent's own work, since in art a happy accident is sometimes the point, and a goal held too firmly produces competent, dull work (perseveration). The person sets the top goal and the taste through the teacher channel (R7); One Loop is a tireless collaborator that explores, varies and remembers what worked.
- **Portfolio management.** The weakest fit for the learning parts: the signal-to-noise ratio is low, markets are non-stationary and adversarial, backtests overfit, and the market reacts to the agent. Consolidation would mostly learn noise, the false-memory failure in the [failure modes](03_system_design.md#design-rules). The safety parts carry over well: the action gate (position limits, permission for hard-to-unwind trades), a mandate and risk limits shielded from news and from text injected into filings, and a calibrated decision not to trade when uncertain. One Loop is a governance and risk layer around a strategy, not a source of alpha.

<a id="board-games"></a>

## Not recommended: board games

AlphaZero and MuZero already solve them. Board games have one level, one fixed goal, no untrusted input and a perfect value signal, so One Loop's additions have nothing to do. Their lesson for the design is already taken: search distilled into a fast policy ([closest existing systems](03_system_design.md#alphazero)).

<a id="multi-loop"></a>

## Extension: multiple One Loops

Multiple loops work at two scales.

1. **Inside one agent:** the [column option](03_system_design.md#columns), with loops arranged in a hierarchy and peers voting.
2. **Many agents, each a full One Loop.** The design extends if three rules hold:
   - **Other agents are sources.** Their messages carry source tags and trust levels, like tool output. They can inform a step, but cannot change an agent's goal without authority. This blocks agent-to-agent injection.
   - **Shared memory passes the consolidation gate.** Otherwise one agent's false lesson spreads to all (R8: cultural transmission spreads errors too).
   - **Shared resources need coordination.** One agent's action can change another's world: locks or sagas for shared state, and a team-level controller for budget.

Build hierarchical teams first (a manager and workers), where goals flow clearly. Use debate or voting among peers for verification, not generation, and avoid flat swarms of chatty agents. Studies of multi-agent LLM systems find that many underperform a single agent given the same compute, mostly through lost goals, miscommunication and missing verification (Cemri et al., 2025), which are the failures goal shielding and the gates address. A 2026 study confirms the point: under equal thinking-token budgets, single agents match or beat multi-agent systems on multi-hop reasoning, and teams help mainly when the context is corrupted. The test is the same as for columns: beat a compute-matched single agent and a plain majority vote. Multi-agent work should start only after the single-agent modules have passed the ablation.

References are collected in [References](references.md).
