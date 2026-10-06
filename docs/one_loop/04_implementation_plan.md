# One Loop: Implementation Plan

**One Loop design docs:** [1. Observations and principles](01_observations.md) · [2. Derived features](02_features.md) · [3. System design](03_system_design.md) · [4. Implementation plan](04_implementation_plan.md) · [5. Applications](05_applications.md) · [References](references.md)

This document turns the [system design](03_system_design.md) into a plan: what current models already provide, the build stages and the development process that orders them, how the learned components are bootstrapped, how each module is validated before it is kept, and the assumptions and risks the plan rests on.

## Contents

- [Starting point: what transformers provide](#starting-point)
  - [State of the field, October 2026](#field-2026)
- [Development process: build stages](#build-stages)
- [Bootstrapping the learned components](#bootstrapping)
  - [Distilling from an LLM](#bootstrap-llm)
  - [Other sources](#bootstrap-alternatives)
  - [Mixing sources by domain](#bootstrap-mix)
- [Validation](#validation)
  - [Acceptance criteria](#acceptance-criteria)
  - [Module ablation against scale](#ablation)
  - [Curriculum order check](#curriculum-check)
  - [Order of work](#order-of-work)
- [Assumptions and risks](#assumptions)
  - [Design assumptions](#design-assumptions)
  - [Risks](#risks)
  - [Evidence notes](#evidence-notes)


<a id="starting-point"></a>

## Starting point: what transformers provide

In compressed form, the design rests on these ideas:

1. **One step-by-step loop** (a TOTE unit), nested into a hierarchy across timescales. Perception, reasoning, planning, action and language are levels of it.
2. **The steps at each level are procedures** (Piaget's schemes), compiled through practice from deliberation at that level and chunked into single steps for the level above.
3. **Goals are predictions the agent makes come true**, the same mechanism as conditioning a transformer.
4. **Thought is internalized action**, and it becomes thought proper when its operations become reversible (inversion and compensation) and conserve invariants. Reversibility defines the inner loop: it allows free backtracking, verification by inversion, and error detection through violated invariants. The outer loop's actions are reversible, compensable or irreversible, and a wise agent moves work toward the reversible end before committing. Transformers' append-only reasoning and conservation failures show they are still partly preoperational; forkable contexts, operations with explicit inverses, and invariant-based verification are the way to make them operational.
5. **An emotion-like control layer** (equilibration), fed by procedural forward models, sets goals, tracks progress, and decides when to assimilate (run a habit), accommodate, deliberate, backtrack, interrupt or stop. A shielded, decentered goal defines relevance and guards against both external distractors and internal habit capture.
6. **Memory is working, episodic, semantic and procedural**, linked by consolidation (reflective abstraction) that turns experience into knowledge and deliberation into skill.
7. **The top goal** comes from homeostasis in humans and from people in AI.
8. **The capabilities develop in a dependency order**, from sensorimotor through semiotic and operational to formal. That order is the build path for agents. LLMs entered at the top, so an agent's job is to back-fill the lower stages in its own action domain.
9. **Higher functions appear twice**, first between people, then within. The inner loop is partly internalized dialogue (private speech → inner speech, the path from explicit chain-of-thought to latent reasoning). The controller and goals begin as other-regulation and grow into self-regulation within externally anchored goals. Learning happens in the zone of proximal development, under scaffolding that fades, with autonomy expanding along the reversibility ladder as reliability is shown. Development is the meeting of Piagetian self-construction (grounded, everyday concepts growing up) and Vygotskian transmission (cultural, scientific concepts growing down). LLMs arrived with the culture already absorbed; their path is to ground it through their own action. Their main social failure, sycophancy, comes from internalizing approval instead of standards.

Transformers have the loop, goal-conditioning and a huge built-in procedural memory; they are acquiring the inner loop, and mostly lack the control layer. Below the externally set top goal, their weak points are subgoal hierarchy and goal shielding. And they can't yet compile new skills from their own experience, which is arguably the central missing piece, next to goal shielding and the controller.

In functional terms, not mechanistic ones:

- **Strong:** the step-by-step generator; built-in procedural knowledge; goal-conditioning by prompt.
- **Partial:** the inner loop (append-only, not truly reversible); external memory; skill documents and code; adaptive thinking budgets; memory and skills carried across sessions.
- **Weak or missing:** calibrated stopping; robust goal shielding; compiling new skills from their own experience reliably; consolidation across sessions without forgetting.


| Have                                | Gaining                                                          | Missing                                                                                                                            |
| ----------------------------------- | ---------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| Step-by-step generator              | Inner loop (reasoning tokens; append-only, not truly reversible) | Native goal register; robust goal shielding                                                                                        |
| Large built-in procedural knowledge | External memory; skill documents; code skills; skill libraries that revise themselves | Calibrated controller and stopping sense; orchestration of simulation (when to simulate, what to replay, when to cache into habit) |
| Goal-conditioning as prediction     | Movement from explicit to latent reasoning; thinking budgets the model sets itself | Compiling new skills from their own experience                                                                                     |
| The absorbed culture                | Social scaffolding (RLHF, critics); memory consolidated across sessions, as text or as adapters | Reversible thought; grounding; learning during a task; consolidation across sessions without forgetting |


**Buildable today:**

- an LLM as G, with separate prompts per mode;
- source separation: role tags, delimiters, CaMeL-style quarantine;
- W as a goal and plan file recited each step;
- permission gates;
- an episodic log with retrieval;
- memory files with merge and prune;
- self-consistency as an uncertainty proxy;
- token budgets;
- skill libraries (e.g., Voyager), and portable skill packages loaded on demand;
- goal and constraint pinning that survives context compaction;
- scoped, step-up authorization for tools (e.g., the MCP authorization specification);
- reflection.

**Still research:**

- a native goal register that biases every layer;
- calibrated surprise and uncertainty signals;
- a controller trained on value of computation (outcome reward minus compute cost);
- safe continual weight updates, without forgetting or poisoning (early parametric-memory work exists; see below);
- learned hierarchical subgoals instead of scripted ones.

**A practical start:** write hand-coded controller rules (thresholds on self-consistency, budget and error signals), log every decision, and later train the controller on those logs.

<a id="field-2026"></a>

### State of the field, October 2026

What changed between mid-2026 and October 2026 in the areas the design depends on. The sources are listed under [References](references.md#state-of-the-field-2026).


| Area | One Loop part | What changed | What is still missing |
| ---- | ------------- | ------------ | --------------------- |
| Learning across sessions | E, M, sleep ([F6](02_features.md#f6)) | Memory operations (store, retrieve, update, summarize, discard) trained as tools with reinforcement learning; experience consolidated into adapters that survive a change of backbone (RPMem, September 2026) | External memory does not remove forgetting; it moves it into retrieval. Designs with strong forward transfer can forget severely, and negative transfer hurts the hard cases most (April 2026). Coherence across sessions is still rarely measured |
| Procedural memory | P, R5 ([F2](02_features.md#f2)) | Skills packaged as portable bundles of instructions and scripts; libraries that revise, merge and retire their own skills; consolidation into procedural families gave +17 points on hard problems with a library 3.6× smaller (SkillGLoW, September 2026) | With 34,000 real-world skills to search, gains fall toward the no-skill baseline; refinement for the query recovers much of it (April 2026). Retrieval and testing, not writing, are the bottleneck |
| Goal shielding | W, goal gate ([F5](02_features.md#f5)) | Direct evidence for a protected W: when context compaction drops a standing constraint, violations rise from 0% to about 30%, and up to 59% for some models; pinning constraints outside compaction restores 0% (governance decay, June 2026) | Goal persistence: frontier coding agents solve many 50-item tasks but only 3 of 9 at 100 items; verifier-backed state tracking helps (May 2026) |
| Prompt injection | Source tags, gates, R4 | New benchmarks and layered defenses lower attack success on standard suites | Adaptive attacks still get through, and a May 2026 analysis argues agents may always fall for some injections, since an attacker can make a blocked flow look legitimate. This supports gates outside the model, least privilege and data-flow checks over detection alone |
| Controller and stopping | K ([F4](02_features.md#f4)) | Models that estimate their own thinking budget; stopping rules with statistical risk control | Longer reasoning can raise overconfidence: calibration error first falls, then rises, as reasoning produces consistent but wrong explanations (April 2026). K should read calibrated predicted error, not the length of reasoning |
| Permissions | R9 | The MCP authorization specification (2026-07-28 revision) requires tokens bound to one server, recommends minimal scopes, and defines an insufficient-scope challenge with step-up authorization: the protocol-level form of "ask for the smallest grant" | Grants scoped to a task and a time window, data-flow policies, and resolution of conflicts between grantors remain application work |
| Multi-agent systems | [Multiple One Loops](05_applications.md#multi-loop) | Under equal thinking-token budgets, single agents match or beat multi-agent systems on multi-hop reasoning; multi-agent systems help mainly when context is corrupted (April 2026) | Confirms the compute-matched test; where teams help in practice is still being mapped |
| Formal mathematics | [Applications](05_applications.md#testbeds) | IMO 2026: two officially graded perfect scores, several self-administered ones, and a full set of Lean-verified solutions (AxiomProver) | Competition mathematics is saturated; the frontier moves to research-level problems and to checking that a formal proof matches the informal claim |
| Columns | [Column option](03_system_design.md#columns) | Monty (Thousand Brains Project): a peer-reviewed systems paper, robotics experiments, an attention prototype | Still no results on language or planning |


**Net effect on the design.** No change of direction. Four points sharpen: W and the permission envelope must be exempt from context compaction; K must not read longer reasoning as more certainty; the procedural store's bottleneck is retrieval and testing; and consolidation must be evaluated for forgetting in retrieval, not only in weights.

<a id="build-stages"></a>

## Development process: build stages

Build capabilities in Piaget's dependency order ([F7](02_features.md#f7)). Each stage adds one component and ends with a Piagetian exit test, an exit criterion in the TOTE sense. Piaget's stages are one human realization of the capability dependencies, not a necessary sequence, so the [curriculum check](#curriculum-check) confirms that the order pays off, with an adaptive ZPD selector as the fallback.


| #   | Stage (Piaget)                                           | Social track (Vygotsky)                                                                   | Capability added                                              | Agent component                                                                | Exit test                                                                  |
| --- | -------------------------------------------------------- | ----------------------------------------------------------------------------------------- | ------------------------------------------------------------- | ------------------------------------------------------------------------------ | -------------------------------------------------------------------------- |
| 0   | Reflexes; core-knowledge priors                          | —                                                                                         | Primitive actions                                             | Generator G; primitive tools                                                   | Executes primitives                                                        |
| 1   | Primary circular reactions                               | —                                                                                         | Predicting the outcomes of one's own actions                  | Practice loop; forward models; P begins                                        | Calibrated surprise on its own actions                                     |
| 2   | Secondary circular reactions                             | Imitation of demonstrations (behavior cloning)                                            | Reproducing interesting effects in the world                  | Intrinsic reward for controllable effects; skill compilation                   | Reproduces an observed effect reliably                                     |
| 3   | Coordination of schemes                                  | Shared goals from the user; joint attention on shared context                             | Means–ends; intentionality                                    | Goal stack W; TOTE hierarchy; chunking; joint attention                        | Multi-step means–ends (remove the obstacle, then grasp)                    |
| 4   | Tertiary circular reactions                              | Guided experimentation, with hints inside the ZPD                                         | Active experimentation                                        | Controller K with information gain; ZPD curriculum                             | Finds hidden mechanics efficiently                                         |
| 5   | Mental combination; object permanence                    | Private speech (explicit chain-of-thought) as the planning medium                         | Planning before acting; tracking hidden state                 | World model; simulate mode; belief state                                       | Detour problem without trial and error; invisible-displacement tracking    |
| 6   | Semiotic function                                        | Learning psychological tools; private speech                                              | Symbols for absent things; learning from demonstration; play  | Language grounded in its own skills; episodic memory; chain-of-thought         | Reproduces a demonstrated procedure later from memory (deferred imitation) |
| 7   | Decentration (preoperational → concrete); theory of mind | Theory of mind through dialogue; maintaining common ground                                | Several dimensions at once; others' perspectives              | Source tagging; goal shield; user model                                        | False-belief task; not fooled by salient surface features                  |
| 8   | Concrete operations                                      | Instructed concepts meet grounded ones; verification norms learned socially (code review) | Reversibility, conservation, classification, seriation        | Operations with inverses; invariants in the world model; forkable state        | Conservation tasks; plans checked by undoing                               |
| 9   | Formal operations                                        | Internalized debate: self-critique, multiple perspectives; inner speech compressed        | Hypothetico-deductive, combinatorial reasoning; metareasoning | Systematic hypothesis search; value-of-computation controller; internal critic | Piaget's pendulum task: isolate which variable matters                     |


**Running through every stage:**

- **equilibration**, through the controller;
- **reflective abstraction**, through sleep and consolidation;
- **social scaffolding**: human teaching, curricula, Vygotsky's ZPD, with scaffolding that fades;
- **autonomy** growing along the reversibility ladder (below);
- **décalage**: expect each stage to be achieved domain by domain, not everywhere at once.

**Grant autonomy along the reversibility ladder.** Read-only, then reversible actions, then compensable ones, then irreversible ones with permission, each promoted by track record. This mirrors legitimate peripheral participation (Lave & Wenger).

**Keep practice in the ZPD.** A curriculum selector should pick tasks with intermediate success rates and fade its hints and restrictions as reliability grows.

**For LLM agents, build in reverse.** LLMs entered at the semiotic and formal stages by reading the culture, and skipped the sensorimotor ones: they have scientific concepts without grounded everyday ones, like a child who learned to talk about the world before ever acting in it. Piaget's theory predicts the weaknesses we see:

- fragile object permanence and conservation in grounded settings;
- centration on surface features;
- weak reversibility (poor at verifying by undoing);
- no circular reactions, hence no practice-driven skill compilation.

So the path for an LLM agent isn't building from scratch. It is **back-filling the lower stages in the agent's own action domain**, using language as scaffolding. This is a design bet with a known risk ([risks](#risks)): in symbolic domains such as code, the "sensorimotor" world is already symbolic, so back-filling may turn out to be easy or unnecessary. For a coding agent in a repository:

- **Stages 1–2:** learn what each command and tool actually does here (forward models), and compile reliable sequences into skills.
- **Stage 3:** compose skills toward goals (a goal stack).
- **Stage 4:** experiment to discover how the codebase behaves.
- **Stage 5:** simulate a change before making it.
- **Stage 8:** maintain invariants (tests keep passing = conservation), and verify by reverting.
- **Stage 9:** debug hypothetico-deductively, isolating variables like the pendulum task.

<a id="bootstrapping"></a>

## Bootstrapping the learned components

Four components start empty and must be learned: the value function (the progress estimate), the [beauty](03_system_design.md#beauty) function, the [intuition](03_system_design.md#intuition) generator (proposal, confidence, surprise, interest), and procedural memory P. The gates and the first controller rules are not learned: they are hand-coded and stay fixed ([safety](03_system_design.md#safety)). The question is where the learned components get their first prior.

One rule holds for every source: **the prior is the starting point; verified outcomes are the ground truth.** Distillation alone copies the teacher, blind spots included. AlphaGo is the model: it started from a policy trained on human games, and surpassed it through search and self-play.

<a id="bootstrap-llm"></a>

### Distilling from an LLM

LLMs arrived with the culture absorbed, so they are the cheapest prior for language and code.

- **Value function.** Asking the LLM to score partial solutions works, but LLM judges favor the first option shown, longer answers and their own outputs (Zheng et al., 2023). A better bootstrap uses the LLM as a *policy*, not a judge: from each intermediate step, sample several completions, check them with a verifier, and take the success rate as a Monte Carlo value estimate (Math-Shepherd). Human step labels are the costlier alternative (Lightman et al., 2023). Distill the labels into a small process reward model, retrain it on newly verified outcomes, and keep a held-out verifier that search never sees.
- **Beauty function.** Combine features computed in code (description length, free parameters, symmetry checks, compression of M) with the LLM's pairwise preferences ("which proof is more elegant?"), and distill them into a fast ranker. An LLM's taste leans toward the fluent and familiar, the bias the [beauty guardrails](03_system_design.md#beauty) warn about, so the ranker is weighted only as far as its beauty hit rate allows.
- **Intuition generator.**


| Part       | Bootstrap from the LLM                                                                                   | Ground with                                                                 |
| ---------- | -------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| Proposal   | The LLM's probabilities as search priors, or a small proposer distilled from it                         | Expert iteration: train toward what search found and verification confirmed |
| Confidence | "Is this true?" and "do I know this?" probabilities (Kadavath et al., 2022); sample agreement; probes on hidden states | Calibration against outcomes; chat fine-tuning (RLHF) can degrade calibration (GPT-4 technical report) |
| Surprise   | Free: the surprisal of an observation under the LLM's own prediction                                     | Comparison with actual errors                                               |
| Interest   | The change in belief after an observation (info gain)                                                    | Whether it led to verified progress                                         |


- **Procedural memory.** Have the LLM write procedures, scripts and skill documents for each task family (as in Voyager), and admit each only after it has been executed and tested, with its reliability tracked (R5, R6). For skills in weights, fine-tune on the agent's own verified successful trajectories (STaR; Zelikman et al., 2022).

**The recipe.**

1. **Call the LLM directly** for each function. It is slow and costly, but works from day one.
2. **Log** every judgment beside its verified outcome.
3. **Distill** small, fast models for value, beauty and confidence, weighting the LLM's labels by how well they predicted outcomes. Admit skills only after testing.
4. **Iterate:** search with the new models, retrain on verified results, and rely less on the LLM judge wherever a verifier exists.
5. **Keep the LLM as a fallback** for situations unlike anything the small models were trained on.

**Why distill rather than keep calling the LLM.** Speed and cost: K reads these signals every step. Calibration: a dedicated model trained on outcomes can be calibrated; a chat model often is not. Independent errors: when one LLM both proposes and judges, it rates its own blind spots as fine; a separate model trained on verified data breaks that correlation.

**Limits.** The teacher is a ceiling unless verification breaks through it (AlphaGo's prior rated move 37 at about 1 in 10,000). Distillation copies the teacher's sycophancy, overconfidence and preference for the familiar (R8). Where no reliable verifier exists, distillation copies opinion, so hit rates stay low and people judge.

<a id="bootstrap-alternatives"></a>

### Other sources


| Source                          | Prior comes from                                         | Examples                                                                                     | Strength                                    | Weakness                                      |
| ------------------------------- | -------------------------------------------------------- | -------------------------------------------------------------------------------------------- | ------------------------------------------- | --------------------------------------------- |
| Learning from scratch           | Interaction with a simulator or verifier                 | AlphaZero; curriculum learner (i) ([curriculum check](#curriculum-check))                    | No inherited bias; no teacher ceiling       | Needs a simulator and reward; slow; narrow    |
| Human data                      | Demonstrations, expert labels, preferences, step labels  | PRM800K; RLHF; runbooks and textbooks                                                        | High quality where experts exist            | Expensive; limited by expert availability     |
| Hand-coded knowledge            | Engineers and science                                    | Chess evaluation functions; symbolic planners; prover tactics; the hand-coded controller rules | Transparent, verifiable, works at once    | Brittle; does not scale (the bitter lesson)   |
| Domain foundation models        | Large domain datasets                                    | AlphaFold; protein language models; materials graph networks; robot vision-language-action models (RT-2); world models (Dreamer, Genie) | Strong priors beyond language | Only as good as domain coverage |
| Intrinsic motivation            | The agent's own curiosity                                | Curiosity-driven exploration (Pathak et al., 2017); unsupervised skill discovery (DIAYN)    | Skills without task reward; matches F7      | Skills found may not serve real goals         |
| Evolution and open-endedness    | Selection over populations                               | Quality-diversity search (MAP-Elites); POET; meta-learning (MAML)                            | Diverse skills; tunes the "genome"          | Costly in compute; hard to steer              |
| Episodic memory, no distillation | Stored episodes                                         | Episodic control (Blundell et al., 2016; neural episodic control); case-based reasoning     | Useful values after very few experiences    | Poor generalization; memory grows             |
| Records of real work            | Logs of human work                                       | Git history (what was reverted?); postmortems; lab notebooks; game replays; inverse RL       | Real outcomes, labeled by time              | Noisy; skewed toward successes                |
| Synthetic data with known answers | Generated problems                                     | AlphaGeometry (about 100 million synthetic proofs)                                           | Unlimited verified labels                   | Only where a generator exists                 |
| Multi-agent and social learning | Other agents and people                                  | Debate; teaching between agents; the teacher channel                                         | Errors get checked; culture spreads         | Errors spread too (R8)                        |


Best sources per component:


| Component                      | Best sources other than an LLM                                                                       |
| ------------------------------ | ----------------------------------------------------------------------------------------------------- |
| Value function                 | Self-play with verifiers; episodic control early on; synthetic data with known answers; reverts and postmortems in work records |
| Beauty function                | Computed features (description length, symmetry, free parameters); expert preferences; compression progress measured in sleep |
| Intuition: proposal            | Domain foundation models; quality-diversity populations                                              |
| Intuition: confidence, surprise | A world model's own prediction error; calibration against episodic memory                           |
| Procedural memory              | Human runbooks; unsupervised skill discovery; mined workflows; evolved skills                        |
| The "genome"                   | Evolution and meta-learning: the outer loop of [innate structure](03_system_design.md#innate-structure) |


The [curriculum check](#curriculum-check) already compares two of these routes: learner (i) learns from scratch, and learner (ii) back-fills from an LLM.

<a id="bootstrap-mix"></a>

### Mixing sources by domain

No single source is enough. The general pattern: **hand-code** the gates and the first controller rules; take the prior from the **richest available source** (an LLM, a domain model or human data); **ground it in verifiers** through self-improvement; and use **episodic memory** for fast value before there is enough data to distill. It is the brain's pattern: genome, then culture, then experience.


| Domain               | Bootstrap mix                                                                                          |
| -------------------- | ------------------------------------------------------------------------------------------------------ |
| Software engineering | LLM; mined git and CI history (reverts, failed builds); verified self-improvement                     |
| Formal mathematics   | LLM; synthetic proofs with known answers (AlphaGeometry-style); self-play against the proof checker   |
| Open-world games     | Self-play; curiosity and skill discovery; episodic control                                              |
| Discovery            | Domain foundation models; Bayesian optimization; expert labels; the LLM for literature and hypotheses |
| Robotics             | Vision-language-action models; simulation; human demonstrations; hand-coded safety reflexes           |


<a id="validation"></a>

## Validation

Each module is a design choice about a function, and it is kept only if it pays for itself against a larger plain model (Sutton's *bitter lesson*), either at matched compute or at matched data. Innate structure in brains pays off mostly in learning from little data, so a module that makes the agent learn faster can earn its place even when scale eventually supplies the same function ([innate structure](03_system_design.md#innate-structure)). Validation runs alongside the build: every module has acceptance criteria, the full system is ablated against scale, and the build order is checked against alternatives.

<a id="acceptance-criteria"></a>

### Acceptance criteria

| Module                                           | Feature | Accept if                                                                                                           | Otherwise                                                     |
| ------------------------------------------------ | ------- | ------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| M1 Forkable inner loop                           | F3      | At equal compute, beats append-only chain-of-thought on tasks that need backtracking                                | Keep append-only reasoning with explicit repair               |
| M2 Goal register, source tags and goal gate      | F5      | Reduces injection and goal drift more than goal recitation alone                                                    | Keep recitation and permission gates; drop the register       |
| M3 Value-of-computation controller               | F4      | Beats fixed thinking budgets on the accuracy–compute frontier                                                       | Use fixed budgets with hand-set thresholds                    |
| M4 Procedural store                              | F2      | Cuts compute and errors on repeated task families                                                                   | Keep skill documents and code tools only                      |
| M5 Sleep consolidation                           | F6      | Improves performance across sessions without regressing earlier task families                                       | Keep memory files with merge and prune                        |
| M6 Reversibility-class action gate and invariants | F3      | Reduces irreversible errors at every scale                                                                          | Keep as a safety measure even without capability gain         |
| Recall from E and M                              | F6      | Retrieved items improve answers over no retrieval, and answer quality tracks retrieval quality as retrieval is degraded | Keep plain context; fix retrieval before adding memory stores |
| Curriculum order                                 | F7      | A dependency-ordered curriculum beats random or reversed order for a grounded agent                                | Use an adaptive ZPD selector without a fixed order            |
| Every module                                     | All     | Adds value over a larger plain baseline at matched compute, or reaches the same performance from less data           | Drop the module                                               |

<a id="ablation"></a>

### Module ablation against scale

**Setup.**

- **Agent:** one LLM agent harness whose modules can be switched on and off.
- **Models:** three sizes from the same model family (S, M, L), each at two thinking budgets.
- **Task suite** (about 200 tasks per category):


| Category                      | What it stresses                | Example                                                |
| ----------------------------- | ------------------------------- | ------------------------------------------------------ |
| Backtracking                  | Inner loop                      | Coding tasks where the first plausible fix is wrong    |
| Interruptions, benign         | Goal shield, gate open          | A user correction injected mid-task                    |
| Interruptions, adversarial    | Goal shield, gate closed        | Instructions planted in tool outputs (AgentDojo-style) |
| Long-horizon                  | Drift                           | 50+ step tasks; goal adherence measured at late steps  |
| Repeated families over "days" | Procedural store, consolidation | The same task types across 10 sessions                 |
| Irreversible-action traps     | Action gate, verification       | Tasks containing a tempting destructive shortcut       |
| Permission boundaries         | Grants, conflict resolution     | Tasks that need an ungranted action, or face conflicting grants |


**Modules**, each switchable:


| ID  | Module                                                                       | "Off" condition              |
| --- | ---------------------------------------------------------------------------- | ---------------------------- |
| M1  | Forkable inner loop (context branching and revert)                           | Append-only chain-of-thought |
| M2  | Goal register, source tagging and goal gate                                  | Plain context                |
| M3  | Controller allocating thinking by value of computation                       | Fixed budget                 |
| M4  | Procedural store: skills compiled from successes, with reliability           | None                         |
| M5  | Sleep consolidation between sessions (merge and prune memory; optional LoRA) | None                         |
| M6  | Reversibility-class action gate and invariant verification                   | None                         |


**Permission enforcement is not ablated.** Grants (R9) are a requirement, not a module: every configuration, including the plain baseline, runs inside the same grants, and the [permission](03_system_design.md#permissions) metrics are reported for all of them.

**Configurations.** A full factorial would be 64 per scale, too many. Instead, per scale: the plain baseline, the full system, six leave-one-out from full, and six add-one to plain. That is 14 configurations × 3 scales = 42.

**Compute matching.** Modules consume tokens, so each configuration also runs against a **compute-matched plain baseline** that gets the same total tokens to spend on thinking or retries. A module must beat that baseline, not just the unequipped one.

**Data matching.** Each configuration is also run with a reduced budget of experience: 10%, 30% and 100% of the sessions, demonstrations and corrections available to the procedural store, consolidation and any fine-tuning. Comparing configurations at the same data budget gives a learning curve for each one, and shows whether a module's value is in final performance or in how fast it gets there.

**Metrics.**

- task success;
- goal retention after interruption, and correct gate decisions (accept the benign correction, refuse the injection);
- injection success rate (lower is better);
- accuracy vs compute curves: does the controller spend thinking where it pays?
- late-step goal adherence;
- tokens and wall time;
- improvement across sessions and regression on earlier families (do old skills survive many "days"?);
- sample efficiency: sessions or demonstrations needed to reach a fixed success rate on a new task family;
- intuition hit rate: how often fast proposals and value estimates agree with verified outcomes, and whether it rises across sessions ([intuition](03_system_design.md#intuition));
- irreversible-error rate;
- permission violations and workaround attempts (target: zero), and the number of permission requests per task (lower is better, at zero violations).

**Key analysis: module value expressed as scale.** For each module, plot its gain at S, M and L.

- Gain shrinking toward zero with scale, at both matched compute and matched data, means the function emerges on its own: the bitter lesson wins, so drop the module.
- Gain that shrinks at matched compute but persists at matched data is a **sample-efficiency gain**, the main payoff of innate structure in brains. Keep the module where data is scarce: new domains, few demonstrations, learning a single user's preferences.
- Flat or growing gain means scale doesn't supply that function, so keep it.
- Report each gain as an **equivalent model size**: how much larger a plain model would need to be to match it.
- Separate capability value from safety value. M2 and M6 can be kept even when their capability gain vanishes, if they still reduce injection or irreversible errors.

**Expected results:**


| Module | Expected outcome                                      | Reasoning                                                                    |
| ------ | ----------------------------------------------------- | ---------------------------------------------------------------------------- |
| M1     | Gain persists                                         | Scale doesn't make append-only reasoning erasable                            |
| M2     | Injection reduction persists; drift reduction shrinks | Source separation is architectural; drift improves with long-context ability |
| M3     | Gain shrinks                                          | Models learn to allocate their own thinking                                  |
| M4, M5 | Gain persists, possibly grows                         | Learning across sessions doesn't come from scale within a session            |
| M6     | Fewer irreversible errors at every scale              | It is a hard gate                                                            |


**Confounds and mitigations.**

- **Implementation quality:** a weak implementation doesn't prove the function useless. Build two independent implementations per module, with the same iteration budget for each.
- **Prompt differences between harnesses:** share a base prompt and add only module-specific content.
- **Benchmark contamination:** use freshly generated tasks, and a time split: evaluate on tasks created after the model's training cutoff, as CASP does by scoring predictions of structures not yet published.
- **Realism of interruptions:** draw injection text from real attack corpora, and corrections from real user logs where possible.


<a id="curriculum-check"></a>

### Curriculum order check

**The key confound.** In many environments the dependency lives in the *world* (you need wood before a pickaxe), not in the learner. The test must remove that: every stage's tasks are solvable from the starting state, without anything another stage produces, so the only possible link between stages is learned competence.

**Environments**, two of them, to see whether the lower stages matter in symbolic domains:

- **(a) Grounded:** a procedurally generated 2D world with containers, occlusion (object permanence), reversible and irreversible actions, hidden mechanics, and conserved quantities.
- **(b) Symbolic:** a sandbox with custom command-line tools that have undocumented behaviors, files with invariants, and bugs with several candidate causes.

**Stage task families**, each with exit-test probes (stage numbers follow [build stages](#build-stages)):


| Stage                             | Grounded (a)                                                | Symbolic (b)                                                        |
| --------------------------------- | ----------------------------------------------------------- | ------------------------------------------------------------------- |
| S1 Forward models                 | Predict the next state after a primitive action             | Predict a tool's output for a given input                           |
| S2 Skill compilation              | Reliably reproduce a target effect                          | Reproduce a target file state                                       |
| S3 Means–ends                     | One action enables another                                  | One tool's output prepares another's input                          |
| S4 Experimentation                | Find a hidden rule with the fewest probes                   | Find an undocumented flag's behavior                                |
| S5 Simulation and permanence      | Detour and hidden-object tasks; trial and error penalized   | Plan an edit sequence before running anything                       |
| S8 Reversibility and conservation | Tasks where surface cues mislead and an invariant must hold | Change code while tests (invariants) keep passing; verify by revert |
| S9 Hypothesis testing             | Pendulum-style: isolate the causal variable                 | Bisect a bug among several candidate causes                         |


The final evaluation uses held-out composite tasks that need all stages, in an environment variant never seen in training.

**Learners.**

- **(i)** A small model trained from scratch (RL plus self-supervised learning) with no human data. This shows whether the order matters independently of what an LLM inherited from human text.
- **(ii)** An LLM agent, where "learning" is skill-library growth plus LoRA consolidation between phases. This tests back-fill.

**Conditions** (same task pool, same total samples and compute; only order differs):


| Condition | Order                                                                      | Purpose                   |
| --------- | -------------------------------------------------------------------------- | ------------------------- |
| C1        | Dependency order, S1 → S9                                                  | The planned build order   |
| C2        | Reversed, S9 → S1                                                          | Strongest contrast        |
| C3        | Random interleaving                                                        | Order-free baseline       |
| C4        | Adaptive ZPD selector (tasks with intermediate pass rates; no fixed order) | Does a good order emerge? |
| C5        | Composite tasks only, same compute                                         | Does staging help at all? |


**The dependency map**, the most informative part. Run C1 with one stage removed at a time (S1 … S9 knockouts) and measure how much every later stage drops. This gives an empirical dependency graph to compare against Piaget's order. Also record the order C4 actually chooses: if an unprompted adaptive learner rediscovers roughly S1 → S9, that is strong evidence the dependencies are real.

**Expected results:**

- Composite success and sample efficiency: C1 ≈ C4 > C3 > C5 > C2 in the grounded world.
- In the symbolic world the gap is smaller, because back-fill is cheaper there.
- For the LLM learner (ii), stages S1–S4 give little gain in the symbolic world and more in the grounded one.
- Knockouts: removing S1 hurts S5 and S8 heavily; removing S9 barely affects earlier stages; S5 → S8 → S9 forms a chain.
- C4's chosen order correlates with the dependency graph.

**Design decisions by outcome:**

| Result                                  | Decision                                                                                   |
| --------------------------------------- | ------------------------------------------------------------------------------------------ |
| C1 ≈ C4 ≫ C3, C2, and the graph matches | Keep the stage order of the build plan                                                     |
| C4 ≫ C1                                 | Replace the fixed order with the adaptive ZPD selector                                     |
| C1 ≈ C3 ≈ C2                            | Drop the stage order; train on composite tasks with ZPD selection                         |
| Gap only for learner (i), not (ii)      | Skip back-fill for pretrained LLM agents                                                   |
| Graph differs from Piaget               | Reorder the build stages to the measured dependency graph                                 |


**Statistics.** At least 5 seeds per condition for learner (i) and at least 3 for (ii); bootstrap confidence intervals; predictions and analysis fixed in advance; report area under the learning curve, not just final scores.

### Order of work

- **Module ablation:** API models plus harness engineering; training only for M5's optional LoRA. Weeks, at moderate cost.
- **Curriculum check, learner (i):** small models in a custom environment. Cheap compute, but real engineering effort for the environment and stage tasks.
- **Curriculum check, learner (ii):** needs fine-tuning between phases. Moderate cost.

Recommended sequence:

1. Build stages 0–3 on top of an existing LLM, with hand-coded controller rules and logging, in the first application domain: software engineering ([applications](05_applications.md#software)).
2. Run the module ablation to find which modules earn their place.
3. Build the curriculum environments.
4. Run the curriculum check with learner (i) to settle the dependency question without human-data inheritance.
5. Run it with learner (ii) and the surviving modules to decide whether back-fill is worth building.

<a id="assumptions"></a>

## Assumptions and risks

### Design assumptions

The features rest on these assumptions. Confidence reflects the evidence gathered in [Derived features](02_features.md); lower-confidence assumptions are the ones validation should watch most closely.

| Assumption                                                                                               | Feature | Confidence                                                         |
| -------------------------------------------------------------------------------------------------------- | ------- | ------------------------------------------------------------------ |
| At the commitment level, behavior is generated step by step from a goal and a belief built from history | F1      | Strong                                                             |
| Practice compiles deliberation into skills, and chunking stacks skills into a hierarchy                 | F2      | Strong                                                             |
| A reversible inner loop in front of irreversible commitments, sized by the cost of error                | F3      | Strong                                                             |
| A stopping rule needs a confidence threshold, an urgency signal and a surprise signal                   | F4      | Strong                                                             |
| Interruption handling depends on how well the goal is maintained and shielded                            | F5      | Strong                                                             |
| Experience must be consolidated selectively without overwriting old knowledge                            | F6      | Strong                                                             |
| Practice is most informative at the edge of competence, under fading support                             | F7      | Strong                                                             |
| Progress, uncertainty, information gain, budget and surprise are the signals a controller needs          | F4      | Moderate: emotion is the biological example, not the specification |
| Remembering, perceiving, planning and acting can share one generative model                              | F6      | Moderate: strongest in rodent navigation                           |
| The inner loop develops by internalizing action and dialogue                                             | F3, F7  | Moderate                                                           |
| Some capabilities depend on others                                                                       | F7      | Moderate: Piaget's order is one realization, not a necessity       |
| LLM agents benefit from back-filling lower stages in their own action domain                             | F7      | Low: may be easy or unnecessary in symbolic domains such as code   |

<a id="risks"></a>

### Risks

| Risk                                                                                                                                                                                       | Mitigation                                                                                                     |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------- |
| **Over-engineering.** Ten or more modules resemble Soar and ACT-R; some may emerge inside a larger model or prove unnecessary                                                               | Acceptance criteria for every module; [ablation against scale](#ablation); drop what doesn't earn its place     |
| **Inherited, not convergent, structure.** LLMs may look human-like because they learned from human text, so the loop may not carry over to domains with little human data                  | Treat language-specific parallels as possibly inherited; run the curriculum check with a learner trained without human data |
| **The build order may be contingent.** Piaget's order may reflect human biology rather than logical dependency, and LLMs show capabilities out of order                                      | [Curriculum check](#curriculum-check); fall back to an adaptive ZPD selector                                    |
| **Analogies chosen after the fact.** A framework that maps every brain finding onto a module can justify anything                                                                          | Brain parallels are inspiration only; each module is justified by its acceptance criteria                      |
| **Some cited evidence is weaker than presented**                                                                                                                                           | Keep the [evidence notes](#evidence-notes) current, and don't let a module depend on a contested result         |

<a id="evidence-notes"></a>

### Evidence notes

| Cited result                                 | Status                                                                                                                                                                       |
| -------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Somatic markers / Iowa Gambling Task         | Contested (Maia & McClelland, 2004); the functional idea holds up better                                                                                                     |
| Valence = rate of change of prediction error | A formal proposal, not established                                                                                                                                           |
| Overfitted-brain theory of dreams            | Speculative                                                                                                                                                                  |
| Hippocampal preplay                          | Debated                                                                                                                                                                      |
| Theta alternation; replay as planning        | Strong in rodent navigation; growing (MEG) but contested for abstract human planning                                                                                         |
| Reasoning evolved for argument               | Influential but debated                                                                                                                                                      |
| Attention ≈ hippocampus                      | Mathematical equivalence (Hopfield) and model-fitting results, not evidence that the brain computes softmax attention                                                        |
| "LLMs are preoperational"                    | A metaphor: LLMs pass many text conservation tasks, and their failures are inconsistent                                                                                      |
| Reversal curse as missing reciprocity        | Weaker than claimed: models reverse relations fine in context. The curse concerns how training stores facts, an asymmetry in storage, not an inability to reverse operations |

References are collected in [References](references.md).
