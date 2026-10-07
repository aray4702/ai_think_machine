# One Loop: System Design

**One Loop design docs:** [1. Observations and principles](01_observations.md) · [2. Derived features](02_features.md) · [3. System design](03_system_design.md) · [4. Implementation plan](04_implementation_plan.md) · [5. Applications](05_applications.md) · [6. Media creation](06_media_creation.md) · [7. Companion](07_companion.md) · [8. Discovery and invention](08_discovery_invention.md) · [9. Robotics](09_robotics.md) · [References](references.md)

The builder's question is: *given the features derived in [Derived features](02_features.md), what do I build?* This document specifies the requirements, the architecture and the design rules. The [implementation plan](04_implementation_plan.md) covers the order of building and how each piece is validated.

## Contents

- [Requirements](#requirements)
- [Architecture](#architecture)
  - [Controller signals](#controller-signals)
  - [The step cycle](#step-cycle)
  - [The sleep cycle](#sleep-cycle)
  - [Intuition: compiled judgment](#intuition)
  - [Two ways to improve: actor-critic and search](#actor-critic)
  - [Beauty: the aesthetic signal](#beauty)
  - [How the parts map to the features](#how-the-parts-map-to-the-features)
  - [Closest existing systems: AlphaZero, MuZero and AlphaFold](#alphazero)
  - [Hierarchy for the task, tiers for authority](#hierarchy-for-the-task-tiers-for-authority)
  - [Innate structure, learned contents](#innate-structure)
  - [Option: one loop per cortical column](#columns)
- [Design rules](#design-rules)
- [Safety and permissions](#safety)
  - [Threats and mechanisms](#threats)
  - [Permissions](#permissions)
  - [Known gaps](#safety-gaps)
  - [Applying safety to a domain](#safety-recipe)


<a id="requirements"></a>

## Requirements


| Principle                 | Required function                               | Component                                                  | Failure if missing                        |
| ------------------------- | ----------------------------------------------- | ---------------------------------------------------------- | ----------------------------------------- |
| F1 Step with feedback    | Next-step generation from goal and belief       | Generator **G**; belief state                              | Stale open-loop plans                     |
| F2 Compile and stack     | Reusable skills; hierarchy                      | Procedural store **P**; goal stack                         | Deliberating every step; no hierarchy     |
| F3 Reversible inner loop | Simulate, backtrack, verify before committing   | Forkable **scratch**; action gate                          | Irreversible errors; append-only mistakes |
| F4 Stopping problem      | Decide continue / deliberate / backtrack / stop | Controller **K**                                           | Overthinking or rash commitment           |
| F5 Shielded goal         | Separate informing from goal-changing input     | Working state **W**; source tags; goal gate                | Injection, drift, habit capture           |
| F6 Consolidation         | Learn across sessions without forgetting        | Episodic **E**, semantic **M**, weights **θ**; sleep cycle | No learning from experience; poisoning    |
| F7 Edge of competence    | Practice where it teaches; build in order       | Curriculum selector; social interface                      | Wasted practice; brittle capabilities     |


<a id="architecture"></a>

## Architecture

![One Loop architecture. During a session, controller K tracks process signals (including predicted error and permission gaps) and chooses control actions, including incubating a stalled problem; it sets the mode of generator G and gates writes to the protected working state W and the procedural store P. Source-tagged input enters context C and reaches G, which simulates in a discardable scratch and acts through an action gate that checks grants and reversibility. Between sessions, sleep replays the tagged episodic log E into M, generates counterfactuals and distills; only trusted, verified experience passes the consolidation gate into the weights θ and new skills in P.](../../assets/images/one-loop-architecture.svg)

**Components**, with the brain parallel for each:


| Part             | Brain parallel                 | Holds                                                                         | Who can write to it                                                             |
| ---------------- | ------------------------------ | ----------------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| G: generator     | Cortex as one generative model | One sequence model used in four modes: perceive, recall, simulate, act        | —                                                                               |
| K: controller    | Emotion; ACC; basal ganglia    | Running process signals; chooses the next control action                      | —                                                                               |
| W: working state | Prefrontal cortex              | Goal stack (each goal paired with its TOTE test), current belief, plan sketch, permission envelope | Only through the goal gate (trusted source or high salience); recited each step; never compacted |
| C: context       | Episodic buffer                | Recent raw trajectory, every token source-tagged                              | Anything, but tool and data tokens can inform steps, never set goals            |
| Scratch          | Imagination                    | Simulated branches, or a draft being refined (the inner loop)                 | G in simulate mode; discarded after use, and only conclusions go to W           |
| P: procedures    | Basal ganglia; cerebellum      | Skills for the fast path                                                      | Only through the consolidation gate                                             |
| E → M → θ        | Hippocampus → neocortex        | Episodes, then distilled lessons, then weights and skills                     | Only through the consolidation gate                                             |


**Social components** ([F7](02_features.md#f7), Vygotsky):

- **Social interface:** a user model (perspective, common ground, preferences) and joint-attention tracking.
- **Teacher channel:** corrections and demonstrations, as the highest-trust source.
- **Internalized critic:** learned from human feedback and run in the inner loop (Vygotsky's internalized dialogue).
- **ZPD curriculum selector:** picks practice tasks with intermediate success rates.
- **Autonomy level per reversibility class**, raised as reliability is shown.

<a id="controller-signals"></a>

### Controller signals

K keeps a few running scalars about the *process*, not the content, each a functional analogue of a feeling from [F4](02_features.md#f4):


| Signal      | Computed from                                                    | Analogue           |
| ----------- | ---------------------------------------------------------------- | ------------------ |
| Progress    | Change in estimated value (from a process reward model): a TD error ([actor-critic](#actor-critic)) | Valence |
| Uncertainty | Entropy, or disagreement across sampled continuations            | Arousal            |
| Info gain   | Information gained per step                                      | Curiosity, boredom |
| Budget      | Budget used vs remaining                                         | Fatigue, urgency   |
| Surprise    | Mismatch between predicted and actual tool or environment output | Interrupt          |
| Predicted error | A head trained against the agent's actual errors, per part of the output and per relation between parts (as AlphaFold's pLDDT and PAE) | Feeling of knowing |
| Permission gap | Steps the plan needs that no grant covers ([permissions](#permissions)) | Inhibition |
| Beauty | Compression gain × reach × unexpectedness of a candidate; falling as description length per explained fact rises ([beauty](#beauty)) | Sense of beauty; ugliness |


Feed these back into the context, or into a separate control channel, so the agent perceives its own state, and train it to map them to *continue / backtrack / switch / ask for help / commit*. This targets the overthinking problem (Elliot-like loops) and the missing sense of when to stop. One caution: longer reasoning can make a model more confident without making it more accurate (calibration drift, 2026), so K reads calibrated predicted error, never the length of reasoning, as certainty.

<a id="step-cycle"></a>

### The step cycle

Each cycle of the step loop:

1. **Observe** and tag the input's source. Compare it with G's prediction; the mismatch is **surprise**.
2. **Test** the top goal in W (the TOTE test). If it passes, **exit**: pop the goal and continue with the parent.
3. **Controller decides:**
  - A confident skill matches → **run skill** (the fast path, a habit), monitoring only its forward model and escalating to deliberation only on surprise.
  - High surprise from a trusted source → reopen the belief and maybe replan, through the goal gate.
  - Progress has stalled → **backtrack** or **switch**, or **incubate**: park the problem for the sleep cycle to work on offline ([intuition](#intuition)).
  - The working theory or design keeps needing patches, so its description length per explained fact rises → treat the **ugliness** as a sign the framework is wrong, and **reframe** ([beauty](#beauty)).
  - Uncertainty × stakes is high and budget remains → **think**. When the task is a sequence of choices, G simulates branches in scratch, expanding the one with the highest gain × need (Mattar & Daw) and scoring them with a progress estimator. When the output is one artifact that can be revised before it is committed (a plan, code, a document), G instead refines the whole draft, feeding it back until it stops changing, and spends the most effort on the parts with the highest predicted error.
  - Information is missing → **recall** from E or M by cue.
  - The goal is ambiguous → **ask** the user.
  - Otherwise → **commit** one step.
4. The commit threshold **drops as the budget runs down** (the urgency signal), so the agent never stalls.
5. The **action gate** first checks that a grant covers the action ([permissions](#permissions)), then checks reversibility × stakes before the action reaches the world; irreversible or high-stakes actions need permission.

<a id="sleep-cycle"></a>

### The sleep cycle

Between sessions:

- **Wake.** Act, and log episodes to E with salience tags: surprises, errors, user corrections, successes.
- **Phase 1 (NREM-like, memory level).**
  1. Select episodes by tag.
  2. Replay them in reverse to assign credit to the steps that caused each outcome; extract lessons (episode → gist). Re-run search on old episodes with the current model, so that replay produces better targets than the ones recorded at the time (MuZero's *Reanalyse*).
  3. Integrate with M: merge duplicates, resolve contradictions.
  4. Prune what is stale.
  - File-based agent memories (one fact per file, update instead of duplicating, delete what turns out wrong) are a hand-built version of this phase.
- **Phase 2 (weight level).** Distill the consolidated lessons into weights or adapters, interleaved with generated samples of old knowledge so nothing is overwritten. The training target is the improved answer that search found in scratch, not the answer the agent first produced (*expert iteration*, as in AlphaZero): search makes a better policy, and distillation makes it the fast one. Compile plans that repeatedly succeed into skills in P.
- **Phase 3 (REM-like).** Generate counterfactual variants of hard episodes ("what if the test had failed differently?") as practice data, and pre-compute for likely next tasks.

Only trusted, verified experience passes the consolidation gate, and any change touching values or goals goes to human review (R6). A confidence score can count as partial evidence, but only as far as its calibration has been measured. AlphaFold 2's self-distillation shows that even a crude confidence filter on the system's own output can help; it does not show that confidence can replace verification.

<a id="intuition"></a>

### Intuition: compiled judgment

Intuition is **compiled deliberation**: judgments that once needed search, distilled into fast estimates that need none. It has four parts:


| Intuition  | Question it answers                         | Part                                   | AlphaZero equivalent |
| ---------- | ------------------------------------------- | -------------------------------------- | -------------------- |
| Proposal   | "Try this direction"                        | Policy prior from G and skills in P    | Policy network       |
| Evaluation | "This looks good"                           | Fast value estimate                    | Value network        |
| Confidence | "I am sure", or "something is off"          | Predicted error, read by K             | None                 |
| Salience   | "That is interesting"                       | Surprise and info gain                 | None                 |


**How it is built.** Deliberate in scratch; keep only results verified high on the ladder of checks; then distill them in the [sleep cycle](#sleep-cycle). Phase 2 trains the fast policy and value estimates toward what search found (expert iteration), Phase 1 compresses episodes into gist in M ("this family tends to be unstable"), and recurring judgments compile into skills in P. Human expertise forms the same way: chess masters recognize positions as chunks (Chase & Simon), and experienced firefighters recognize situations rather than compare options (Klein's recognition-primed decision). Distilling chain-of-thought into direct answers is the language-model version ([F6](02_features.md#f6)).

**Incubation.** Insight often comes after stepping away, and sleep helps: people who slept were much more likely to discover a hidden shortcut in a task (Wagner et al., 2004). One Loop can schedule this. When progress stalls, K can *incubate*: park the problem, let the replay and recombination of sleep work on it with constraints relaxed, and return with a changed representation, which is what an "aha" is.

**How it guides search.** Intuition chooses which problems are worth a campaign (taste, in Hamming's sense of knowing the important problems in a field), orders and filters candidates before generation spends effort on them, serves as a free first check before any verifier, steers K's allocation by combining "looks good" with "how sure", flags which surprises deserve an explanation, and recognizes cross-domain analogies through gist in M. It makes the loop cheaper and faster; search and verification keep it honest.

**Calibration sets how far intuition is trusted.** Expert intuition is reliable only where the environment is regular enough to learn and feedback is quick and clear (Kahneman & Klein, 2009). So One Loop tracks an **intuition hit rate**: how often each kind of intuitive judgment agrees with verified outcomes, by domain and region. Where the hit rate is high, intuition may prune search hard; where it is low, the agent searches more. This is the brain's arbitration between habit and deliberation by their relative reliability (Daw, Niv & Dayan, 2005). It also explains the [application ranking](05_applications.md#order): intuition becomes trustworthy in mathematics, code and materials, and should stay humble in markets and strategy.

**Rules and failure modes.**


| Failure                                      | Example                                                                 | Rule                                                                          |
| -------------------------------------------- | ----------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| Blind spots                                  | AlphaGo's prior dismissed Lee Sedol's move 78, so search never examined it | **Intuition guides but never vetoes:** an exploration floor for low-prior candidates |
| Entrenchment (the Einstellung effect)        | Experts fixate on a familiar solution and miss a better one (Bilalić, McLeod & Gobet, 2008) | Diverse parallel loops; surprise triggers a wider search                      |
| Intuition learned from proxies               | Distilling surrogate scores teaches the surrogate's errors              | Distill only verified results, through the consolidation gate (R6)           |
| Overconfidence where feedback is poor        | Gut feelings about stocks                                               | Trust intuition only as far as its measured hit rate                          |
| A confident hunch with a story built after it | A plausible rationale for a judgment made on other grounds              | Treat intuitions as hypotheses to test, not conclusions                       |


**The felt side.** K's signals are intuition as feeling: falling predicted error is the sense of getting close, rising surprise is the sense that something is wrong, and info gain is curiosity. Damasio's somatic markers make the same claim for brains, although the classic evidence for them, the Iowa Gambling Task, is contested ([F4](02_features.md#f4)).

<a id="actor-critic"></a>

### Two ways to improve: actor-critic and search

The proposal and evaluation parts of intuition can be read as an actor and a critic, but AlphaZero uses them differently from standard actor-critic, and One Loop needs both uses.


|                          | Actor-critic (A3C, PPO)                                              | AlphaZero                                                                   |
| ------------------------ | -------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| How the actor learns     | Policy gradient weighted by the critic's advantage or TD error, δ = r + γV(s′) − V(s) | Supervised training toward the search's visit counts; the critic sends no gradient to the actor |
| How the critic helps     | Directly, through the gradient                                       | Through search: the value guides search, search finds better moves, the actor imitates them |
| The critic's target      | Its own next estimate (TD bootstrapping)                             | The game result (AlphaZero); n-step bootstrapped returns (MuZero)          |
| When the critic is used  | Training only                                                        | Also at decision time, inside search                                        |
| Who acts                 | The actor                                                            | The search; the policy is its prior                                         |
| World model              | None                                                                 | The rules (AlphaZero) or a learned model (MuZero)                           |


AlphaZero is approximate policy iteration: the value network evaluates, search improves, and the improved policy is distilled back (expert iteration). Grill et al. (2020) showed that its search approximately solves a regularized policy-optimization problem, which links the two families.

The brain has both. In the classic actor-critic model of the basal ganglia, dorsal striatum is the actor, ventral striatum the critic, and dopamine carries the TD error (Schultz, Dayan & Montague, 1997; O'Doherty et al., 2004). Model-based planning runs in prefrontal cortex and hippocampus, and the brain arbitrates between the two by their reliability (Daw, Niv & Dayan, 2005).

One Loop maps onto the same split:


| System                                | Parts                                                                                   | Learns by                                                        |
| ------------------------------------- | --------------------------------------------------------------------------------------- | ---------------------------------------------------------------- |
| Model-free actor-critic: habit, the fast path | Actor: skills in P. Critic: the value function. TD error: the Progress signal  | Actor-critic updates while awake: a skill is strengthened when progress rises |
| Model-based search: deliberation      | Proposer: intuition's proposal. Evaluator: the value function. Search: scratch          | Expert iteration in sleep: distill what search found              |
| Arbitration                           | K chooses *run skill* or *think* by the reliability of each                             | Calibration against outcomes                                     |


Two distinctions follow:

- **Progress is a reward prediction error; surprise is a sensory prediction error.** The first says how well things are going, the second that the world did not behave as predicted. The brain keeps them apart, and so do K's [signals](#controller-signals).
- **Skills improve in two ways.** Habits are refined online by actor-critic while awake; what deliberation discovers is compiled offline by distillation in sleep. Actor-critic sharpens what the agent already does. Only search plus distillation brings something new, such as move 37, into its habits.

<a id="beauty"></a>

### Beauty: the aesthetic signal

Beauty guides invention and discovery, and sometimes misleads them. Poincaré described invention as unconscious generation filtered by an aesthetic sense; Dirac held that beauty in an equation mattered more than fit to experiment; mathematicians viewing formulas they find beautiful activate the same region (medial orbitofrontal cortex) as people experiencing visual or musical beauty (Zeki et al., 2014). But Kepler's nested Platonic solids were beautiful and wrong, and Hossenfelder (2018) argues that beauty and "naturalness" led particle physics astray for decades. So One Loop treats beauty like [intuition](#intuition): built from verified experience, used to guide search, never allowed to overrule evidence.

**What beauty measures.**


| Feature                        | Meaning                                       | Measure                                                       |
| ------------------------------ | --------------------------------------------- | ------------------------------------------------------------- |
| Compression                    | A short description that explains a lot       | Description length relative to the data covered (MDL)         |
| Symmetry                       | Unchanged under transformations               | Invariants found and checked (R3a)                            |
| Unification                    | One idea joins things that seemed unrelated   | How many facts, episodes or domains in M it compresses together |
| Economy                        | No arbitrary parts                            | Few free parameters, special cases or patches                 |
| Unexpected yet inevitable      | Surprising at first, obvious afterwards (Hardy) | High surprise before, low predicted error after             |
| Fertility                      | Opens new results                             | Discoveries it enables downstream                             |


Schmidhuber (2009) joins these in one account: beauty is how compressible something is to an observer given what the observer knows, and interestingness is *compression progress*, the improvement in that compression. In One Loop, interestingness is K's info-gain signal, and the "aha" is a sudden jump in compression progress, which is what Phase 1 of the [sleep cycle](#sleep-cycle) produces as it turns episodes into gist.

**How the signal is built.**

1. **Slowly first.** During deliberation, candidates are scored on the explicit features: description length, free parameters, symmetries, how much of M they compress.
2. **From human taste.** Through the teacher channel, experts point to elegant proofs and designs (the "proofs from The Book" tradition). Per R8, the agent internalizes the standards, not the approval.
3. **Distilled into a feeling.** Sleep trains a fast aesthetic estimate on cases where the slow features and verified outcomes agreed. It becomes the beauty signal in [controller signals](#controller-signals), with ugliness as its opposite.
4. **Calibrated by domain.** A **beauty hit rate** tracks how often candidates judged beautiful survive verification. Where beauty predicts truth (much of mathematics, code, parts of physics), it carries more weight; elsewhere it only breaks ties.

**How it is used.**

- **Choosing problems:** campaigns where a unifying idea seems close promise high compression progress.
- **Generation:** reformulate to reveal symmetry, ask for the simplest form, and prefer operators that remove parts over ones that add them.
- **Ranking:** a free first screen, and between candidates the evidence supports equally, the more elegant one (Occam).
- **Diagnosis:** ugliness is an alarm. When a theory needs ever more patches, or a design ever more special cases, the rising description length per explained fact signals that the framework is wrong, as epicycles signaled for Ptolemy's circles. K reframes or backtracks.
- **After verification:** look for the more beautiful proof or design. Elegant results compress into better skills in P and transfer further.
- **Invention:** elegance means fewer parts and more function per part, close to TRIZ's *ideality* (useful function divided by cost and harm). In code, simplicity also helps correctness.

**Guardrails.**

- **Beauty guides; evidence decides.** It never overrides verification or the exploration floor.
- **Familiar is not beautiful.** What is easy to process feels more beautiful and more true (processing fluency; Reber, Schwarz & Winkielman, 2004). Unchecked, the aesthetic signal rewards the familiar and deepens entrenchment; Hardy's unexpectedness and the novelty check push back.
- **No empty elegance.** A short but trivial theory compresses nothing, so beauty is always scored together with reach.
- **No reward hacking.** A learned aesthetic critic is a proxy like any other; it is distilled only from verified results (R6).
- **Art differs.** In art, beauty is the goal and the person sets the taste (R7). In discovery and invention it is a signal about truth and function, not the goal.

### How the parts map to the features


| Part                    | Principle                      |
| ----------------------- | ------------------------------ |
| G                       | The next-step loop ([F1](02_features.md#f1))       |
| Scratch                 | The revisable inner loop ([F3](02_features.md#f3)) |
| K                       | Emotion as controller ([F4](02_features.md#f4))    |
| W and its gates         | Goal shielding ([F5](02_features.md#f5))           |
| E → M → θ               | Memory and consolidation ([F6](02_features.md#f6)) |
| Simulate mode and sleep | Replay as planning ([F6](02_features.md#f6))       |
| P                       | Compiled procedures ([F2](02_features.md#f2))      |


<a id="alphazero"></a>

### Closest existing systems: AlphaZero, MuZero and AlphaFold

AlphaZero and MuZero already run one level of this design, in a single domain with a clean reward. AlphaZero searches with the game's rules; MuZero learns its own model of the game and plans inside it.


| One Loop                                | AlphaZero / MuZero                                                                                                   | Match                                                  |
| --------------------------------------- | -------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------ |
| Step loop ([F1](02_features.md#f1))     | Search, play one move, observe, search again                                                                         | Exact: the cleanest working instance of F1            |
| Belief state                            | MuZero's representation network: a hidden state computed from history                                               | Close: a learned belief, not a reconstruction         |
| G in simulate mode                      | AlphaZero: the given rules. MuZero: a learned dynamics model                                                         | MuZero matches; AlphaZero has a perfect simulator     |
| Scratch ([F3](02_features.md#f3))       | The search tree: forked, explored, mostly discarded after the move                                                   | Exact: a reversible inner loop before an irreversible move |
| Which branch to expand (gain × need)    | PUCT: prior × value plus an exploration bonus                                                                        | Same idea, different formula                          |
| Controller K ([F4](02_features.md#f4))  | A fixed number of simulations per move                                                                               | Missing: easy and hard moves get the same thinking    |
| Compile into P ([F2](02_features.md#f2)) | The policy network is trained toward the search's visit counts                                                       | Strong, but flat: no skills, no hierarchy             |
| Sleep ([F6](02_features.md#f6))         | Replay of self-play games, prioritized by value error; Reanalyse re-runs search on old games with the newer network | Close to Phases 1 and 2; no separate E and M          |
| Goal gate ([F5](02_features.md#f5))     | Fixed goal: win                                                                                                      | Not needed: one goal, no user, no injection           |
| Action gate                             | Every move is irreversible and equally safe                                                                          | Not needed                                            |
| Curriculum ([F7](02_features.md#f7))    | Self-play: the opponent is always at the agent's level                                                              | Strong: win rates near 50% keep training at the edge of competence |
| [Innate structure](#innate-structure)   | Innate: the search algorithm (and, for AlphaZero, the rules). Learned: everything else                              | MuZero moved the rules to the learned side, kept search innate |


**What One Loop takes from them.**

- **Expert iteration as the recipe for compiling.** Train the fast policy toward what search found (Anthony, Tian & Barber, 2017, "Thinking fast and slow with deep learning and tree search"). One mechanism serves both F2 and Phase 2 of [sleep](#sleep-cycle).
- **Reanalyse as replay.** Revisiting old episodes with the current model gives better credit assignment without new data (Phase 1 of sleep).
- **Value-equivalent models.** MuZero's model predicts only what planning needs (reward, value, policy), not the next observation. One Loop needs both kinds: value-equivalent predictions for planning in scratch, and observation-level forward models in P for detecting surprise.
- **Search is on the safe side of the bitter lesson.** Sutton names search and learning as the two general methods that scale. The inner loop is the least risky part of the design; the hand-built parts (gates, controller, stores) are the ones the [ablation](04_implementation_plan.md#ablation) has to justify.

**What One Loop adds, and why it matters outside games.**

- **Hierarchy.** MuZero plans at one level and one time scale. Open tasks need goals that decompose (claim 2).
- **A controller for compute.** A fixed simulation budget suits a game clock. Gumbel MuZero (Danihelka et al., 2022) needs far fewer simulations, but the budget is still fixed; K decides it per step by value of computation.
- **Goals that can change, and gates.** A game has one fixed goal and no one injecting another. An agent has users, tools and adversaries.
- **Memory across sessions.** MuZero learns only through its weights, over millions of games; One Loop also learns in context and through E and M.

**The hard gap: the value signal.** AlphaZero works because the outcome is unambiguous and the simulator is exact (AlphaZero) or learnable from an honest reward (MuZero). One Loop's progress signal comes from a process reward model, and in open tasks that estimator is the weak link: search against a noisy value function finds its errors (reward hacking). This is why the recipe has moved into language models mainly where answers can be verified, as in AlphaProof's search over proofs checked by Lean. In One Loop, the action gate, invariant checks and the teacher channel stand in for that verifier. How far that substitute reaches is the main open question.

**AlphaFold: refinement instead of search.** AlphaFold is not an agent: it takes no actions and pursues no goals. It is closer to a generator with a well-built inner loop, and four of its mechanisms carry over.

- **Recycling is the other kind of inner loop.** AlphaFold 2 feeds its predicted structure back in as input and refines it a fixed three times. AlphaFold-Multimer recycles up to 20 times and stops early once the pairwise Cα distances change by less than 0.5 Å between passes (ColabFold exposes both settings): a fixed budget in one model, a convergence test with a cap in the other. Tree search suits a sequence of irreversible choices. Refining the whole draft suits an artifact that can be revised before it is committed, which describes most plans, code and documents. Scratch supports both, and K sets how many refinement passes to run ([step cycle](#step-cycle)).
- **Confidence trained against real error.** AlphaFold predicts its own error per residue (pLDDT) and per pair of residues (PAE), and both are calibrated well enough that biologists use them to decide what to trust. That is a better uncertainty signal than entropy or sample disagreement, and it says *where* the doubt is. It becomes the predicted-error signal in [controller signals](#controller-signals).
- **Self-distillation behind a confidence filter.** AlphaFold 2 predicted structures for about 350,000 sequences with no known structure, kept a high-confidence subset, and trained a new network from scratch on those predictions mixed with solved structures. The filter was not pLDDT, which did not exist yet, but a heuristic: how far each predicted distance distribution diverged from a generic one (KL divergence), which measures how specific a prediction is rather than how accurate. AlphaFold 3 later learned from AlphaFold 2's predictions to draw disordered regions as loose loops instead of inventing structure there. That is the consolidation gate working on the system's own output, and even a crude filter was enough to help. One Loop's gate should still prefer calibrated confidence plus verification ([sleep cycle](#sleep-cycle)).
- **Retrieval as input.** At inference AlphaFold retrieves related sequences (the multiple sequence alignment) and known structures (templates) and reasons over them, and its accuracy falls when the alignment is shallow. That is the recall mode: the quality of what is retrieved bounds the quality of the answer, so recall gets its own [acceptance test](04_implementation_plan.md#acceptance-criteria).

AlphaFold also traces the arc of the [innate structure](#innate-structure) argument. AlphaFold 2 built geometry into its wiring (triangle updates that keep pairwise distances consistent; attention that respects rotation and translation) when data was scarce, about 170,000 known structures. AlphaFold 3 removed much of it, replacing the structure module with diffusion, once data and compute had grown. Built-in structure earned its place, then gave way to general methods, which is the pattern the matched-data comparison in the [ablation](04_implementation_plan.md#ablation) is designed to detect. And AlphaFold avoided the value-signal gap above by choosing a problem with ground truth: experimentally solved structures. That argues for starting One Loop where answers can be checked (code with tests, proofs, simulators) and widening from there.

### Hierarchy for the task, tiers for authority

The parts are organized in two different ways, on purpose.

- **A hierarchy** is the same loop nested to any depth: each level sets the goal for the level below, and each step at one level is a whole loop at the next (claim 2). The goal stack in W, the skills in P and the TOTE tests are organized this way.
- **Tiers** are a small, fixed number of layers that differ in role and speed. Each can act on its own, and a higher tier modulates or overrides a lower one rather than feeding it every step. Brooks's subsumption architecture (1986) and the three-layer robot architectures (Gat, 1998) work this way.

Each one fails where the other is strong:


|               | Hierarchy                                           | Tiers                                         |
| ------------- | --------------------------------------------------- | --------------------------------------------- |
| Good at       | Decomposing a task into subgoals of any depth       | Reacting fast; enforcing safety               |
| Scales with   | Task depth: add levels as needed                    | Barely: the layers are fixed                  |
| Goals         | Each level knows its parent's goal ([F5](02_features.md#f5))            | Tiers can pull in different directions        |
| On a surprise | Slow: it must climb the chain before the plan moves | Fast: a low tier acts at once                 |
| On failure    | A bad top-level goal propagates everywhere          | Lower tiers keep working when upper ones fail |
| Main cost     | Latency; a single chain of command                  | Arbitration between tiers                     |


So the design uses both. **What to do** is hierarchical: goals, subgoals and compiled skills form one recursive loop, which is how the agent takes on tasks of any depth. **Who can stop or override it** is tiered, and the tiers cut across every level of the hierarchy without waiting for it:

1. **Gates** (fastest): the source tag, the goal gate and the action gate block untrusted inputs and risky actions at any level (R4).
2. **Controller K**: surprise, budget and progress signals can interrupt any level and reopen deliberation ([F4](02_features.md#f4)).
3. **Sleep** (slowest): consolidation between sessions, behind its own gate ([F6](02_features.md#f6), R6).

The brain appears to combine them the same way. The prefrontal cortex organizes goals hierarchically (Koechlin; Badre), but it sits on an older layered stack of spinal reflexes, brainstem, basal ganglia and cortex, in which lower layers can act first and higher ones modulate them (Prescott, Redgrave & Gurney, 1999). You pull your hand off the stove before you know why, and a strong feeling can interrupt any level of a plan.

Every piece maps to a brain mechanism, and most can be prototyped with current LLMs ([starting point](04_implementation_plan.md#starting-point)).

<a id="innate-structure"></a>

### Innate structure, learned contents

The brain is not purely trained. About 20,000 genes cannot specify about 10¹⁴ synapses (the *genomic bottleneck*, Zador 2019), so the genome specifies how to build the brain, not what it knows:

- **A column template** repeated across the cortex (Mountcastle).
- **A map of regions**, laid down early by gradients of gene expression before any input arrives (Rakic's *protomap*, 1988) and refined later by experience.
- **Initial connections between regions**, which largely decide what each region becomes. The column algorithm is generic: when visual input is rerouted to auditory cortex in ferrets, that cortex develops visual-style orientation maps (Sharma, Angelucci & Sur, 2000).
- **Learning rules, reflexes and core-knowledge priors**, which must work before any learning has happened.

Development then starts with more connections than it keeps and prunes the unused ones. Evolution is the outer loop that tunes the genome; learning is the inner loop that fills in a lifetime.

The architecture diagram plays the role of the genome. The split:


| Innate: set by the design ("genome")                              | Learned: filled in by experience                         |
| ----------------------------------------------------------------- | -------------------------------------------------------- |
| The column template: one loop, with weights shared across columns | What each column knows                                   |
| The list of regions: G, K, W, C, P, E, M                          | The contents of each store                               |
| Initial wiring between regions ([architecture](#architecture))   | Connection strengths; pruning of links that go unused    |
| Gates and reflexes: the [tiers](#hierarchy-for-the-task-tiers-for-authority) | When to escalate past a reflex                |
| Learning rules: salience tags, replay, the consolidation gate     | Skills in P, lessons in M, weights θ                     |
| Core-knowledge priors ([stage 0](04_implementation_plan.md#build-stages)) | Everything built on top of them                  |


Three consequences for the design:

- **Safety belongs on the innate side.** The gates are fixed for the same reason reflexes are: they must work before the agent has learned anything, and must not be unlearned. This is the tiers argument above, stated developmentally.
- **The ablation is the outer loop.** [Module ablation](04_implementation_plan.md#ablation) selects among candidate genomes: a module survives only if it earns its place. Wiring can follow development too: start the regions densely connected and prune by use, rather than hand-picking every link.
- **Judge innate structure by how fast it learns.** In animals, built-in structure pays off mostly in learning from little data (a foal walks within hours; a child learns a word from a few examples), less in final performance once data is plentiful. So modules are compared at matched data as well as at matched compute ([validation](04_implementation_plan.md#validation)).

<a id="columns"></a>

### Option: one loop per cortical column

*Status: a design option, not part of the core design. It is kept only if it passes the test at the end of this section.*

Hawkins's Thousand Brains theory, building on Mountcastle, holds that the neocortex is made of about 150,000 cortical columns that all run the same algorithm. Each column receives a sensory feature together with its location in a reference frame (grid-cell-like), predicts its next input from the movement about to be made, sends motor output, and learns complete models of objects. That is the step loop of [F1](02_features.md#f1) in miniature: predict, act, observe, update. So the column is a candidate physical unit for the one loop, and a candidate substrate for claim 2.

The unit is the **cortical column, not the minicolumn**. A minicolumn is about 100 neurons that share one input feature, with different cells coding that feature in different contexts. It is closer to one variable in a loop's belief than to a loop.

![One loop per cortical column. Left: one column runs the step loop, with a goal and TOTE test from its parent, a report back of done, surprise and confidence, input as a feature plus a location, its committed step sent to a child or the world, and votes exchanged with peers; inside, a belief in its own reference frame, a forward model and a scratch; its minicolumns are variables inside the loop, not loops. Middle: columns on two axes, a plan, action and perception hierarchy in which goals go down and reports come up, and peers on the same level voting until they agree. Right: the gates, controller K and sleep stay global, not replicated per column, and cut across every level.](../../assets/images/one-loop-columns.svg)

**The column unit.** Each column runs the step cycle on local state (a belief in its own reference frame, a forward model and a scratch) and has five interfaces:


| Interface | Direction                     | Carries                                                  |
| --------- | ----------------------------- | -------------------------------------------------------- |
| Goal      | From the parent               | A subgoal with its TOTE test                             |
| Input     | From children or sensors      | A feature plus its location, source-tagged               |
| Step      | To children, or the world     | The committed step: a child's goal, or an action through the action gate |
| Report    | To the parent                 | Done or failed, surprise, confidence                     |
| Votes     | With peers on the same level  | The current belief, until the peers agree                |


**Two axes.**

- **Vertical (hierarchy).** A column's committed step becomes the goal of the columns below it, and they report back up. This is the hierarchy of claim 2, built from columns. Hawkins's theory says little about goals, which come from the prefrontal cortex and basal ganglia, so this axis is this design's addition.
- **Horizontal (voting).** Hawkins's theory is mostly lateral. Columns that sense the same object through different inputs vote until they agree, and the cortical hierarchy is shallow, with many connections that skip levels. Voting gives what a pure hierarchy lacks: fast agreement without climbing the chain, and robustness when one column is wrong.
- **Disagreement is a signal.** How much peers disagree is a direct uncertainty measure for K, the same role that disagreement across sampled continuations plays in [controller signals](#controller-signals).

**What stays global.** Only the hierarchy is replicated per column; the [tiers](#hierarchy-for-the-task-tiers-for-authority) are not. The gates, K's interrupts and sleep cut across every column. A column holds its local goal, but it can change a goal only through the goal gate and act on the world only through the action gate (R4). Otherwise one compromised column could reset goals or act on its own. The goal stack in W becomes the chain of active columns, one frame per column, still written only through the gate.

**Risks.**

- **Functions, not boxes.** Many small loops is hand-built structure, so it must beat a larger plain model, at matched compute or at matched data ([innate structure](#innate-structure); [ablation](04_implementation_plan.md#ablation)).
- **Earlier attempts.** Capsule networks (Sabour, Frosst & Hinton, 2017) and GLOM (Hinton, 2021) used column-like units that settle on shared answers, and neither has scaled. The closest working build is Monty, from the Thousand Brains Project (Clay, Leadholm & Hawkins, 2024): its learning modules are columns that vote. It works on sensorimotor object recognition, and by 2026 had a peer-reviewed systems paper, robotics experiments and an attention prototype, but it has not been shown on language or planning, so it is the first thing to study.
- **Cost.** One LLM call per column is too expensive at any real scale. A column should be a small model, or a parallel stream inside one model with shared weights, which also matches the claim that every column runs the same algorithm.

**How to test it.** Run it as a follow-on to the [module ablation](04_implementation_plan.md#ablation), once M1–M6 are settled. Replace the single loop with N column loops that share weights, with voting on and off. Compare at matched compute against the plain baseline and against **N independent samples with a majority vote** (self-consistency). That second baseline is the key control, because voting without the column structure is just self-consistency. Keep the option only if it beats both on the long-horizon and interruption categories, and if peer disagreement predicts errors better than disagreement across sampled continuations.

<a id="design-rules"></a>

## Design rules

**R1. Move work toward the reversible end before committing.** Every action has a class:


| Class                                               | Piaget analogue            | Examples                                                    | Handling                                                                        |
| --------------------------------------------------- | -------------------------- | ----------------------------------------------------------- | ------------------------------------------------------------------------------- |
| Reversible: an exact inverse exists                 | Inversion                  | Edit under version control; draft text; move in a simulator | Act; backtrack freely                                                           |
| Compensable: no exact inverse, but a counter-action | Reciprocity / compensation | Refund; rollback migration; correction email; "I mean…"     | Act with a logged compensation plan (the saga pattern from distributed systems) |
| Irreversible                                        | —                          | Send money; delete without backup; physical harm            | Deliberate fully; permission gate                                               |


Use sandboxes, dry runs, transactions, branches, staging and checkpoints to reclassify actions upward. Much of civilization's engineering does exactly this for humans: undo, version control, drafts, insurance, contracts. Making the outer loop more like the inner loop is a large lever for agent safety.

**R2. Make the inner loop truly reversible.** Simulate on forkable state (git worktrees, VM snapshots, simulators, context branching) rather than append-only reasoning. "Wait, that's wrong" compensates but doesn't invert: the wrong thought stays in context and keeps priming. Discarded branches should disappear entirely.

**R3. Verify with Piaget's three arguments:**


| Argument                                 | Check                                                                                                          |
| ---------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| Identity: nothing added or removed       | Diff audit: did the change touch only what was intended?                                                       |
| Inversion: undoing restores the original | Round-trip; revert-and-compare; substitute the answer back                                                     |
| Compensation: changes balance out        | Conservation checks: totals unchanged; tests still pass; API contract or behavior preserved through a refactor |


**R3a. Make transformations first-class, and learn their invariants.**

- Each skill in P records its inverse or compensation, the invariants it preserves, and its preconditions (R5), so the agent reasons over operations, not only states: Piaget's move from figurative to operative knowledge.
- During consolidation, mine experience for what never changes under which operations, as invariant-detection tools like Daikon do for programs. Store the results in M; a violation becomes surprise for the controller.
- Train reciprocity: bidirectional relations in data; paired skills (encode/decode, serialize/parse); planning from both ends, forward from the start and backward from the goal (means–ends analysis), as humans solve mazes from both ends.

**R4. Shield by source, open by trust and salience.** Shielding by content fails, because attackers can mimic any content. Follow the brain instead:

- Keep the goal stable against input from untrusted sources: tool and data tokens may *inform* a step but never *set* a goal.
- Let interrupts through when they come from a trusted source (user corrections are the highest-trust input) or carry high salience (an error, a failed test, something irreversible about to happen).

The salience signal is the controller of [F4](02_features.md#f4), with surprise opening the gate, so goal shielding and the emotion-like control layer are **one mechanism**. Shield too hard and you get perseveration: an agent that ignores the user's "stop, that's wrong." Shield too little and you get injection.

Fixes available today, mapped to the brain mechanisms of [F5](02_features.md#f5):


| Brain mechanism                 | AI approach                                                                                                                                                                          | Status                                                        |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------- |
| Source tagging                  | Instruction hierarchy (trained system > user > tool priority); delimiting and datamarking (spotlighting); role embeddings that mark data tokens in the representation (StruQ, ASIDE) | Deployed or research; reduces but doesn't eliminate injection |
| Gate that blocks distractors    | Dual-LLM / CaMeL: a privileged planner sees only trusted input and writes the control flow; a quarantined model reads untrusted data but can't choose actions                        | Strongest guarantees; costs flexibility                       |
| Active maintenance by rehearsal | Goal recitation: keep a to-do or plan file and restate it near the end of the context, in the high-attention region                                                                  | Common in agent harnesses; cheap; works well against drift    |
| Gating the action stage         | Permission systems: tool calls need approval or an allowlist, whatever the context says                                                                                              | Defense in depth                                              |
| Persistent top-down bias        | A goal vector outside the token stream that steers every layer, like goal-conditioned activation steering                                                                            | Mostly a research idea                                        |


**R5. Give every skill a life cycle.**

- **Compile:** deliberate, succeed repeatedly, then cache as a skill; it becomes a single step for the level above.
- **Run:** on the fast path, the controller only monitors the forward model.
- **Veto:** if the goal has changed and the habit no longer fits, the controller inhibits it (protection against capture).
- **Decompile:** when it keeps producing surprises, drop back to deliberation, relearn, and compile again.

Each skill in P records:

- **trigger:** the context or goal it applies to (basal-ganglia-style selection);
- **body:** code, an adapter, or a compiled sub-policy;
- **inverse or compensation**, the **invariants** it preserves, and its **preconditions** (R1, R3, R3a);
- **forward model:** the expected outcome, for surprise detection (cerebellar);
- **reliability:** its track record, which sets how much supervision it needs;
- **level:** which layer of the hierarchy it is a step for.

**R6. Gate consolidation more strictly than action.** Untrusted content consolidated into weights becomes a **persistent injection** that survives every future context, much as brains consolidate false memories (Loftus). So the source-aware gate of R4 sits in front of consolidation too: only verified experience from trusted sources gets promoted, the gate gets stricter the higher the layer (memory → weights), and changes that touch values or goals go to human review.

**R7. Keep control signals about the task, not about the agent.**

- The signals in [architecture](#architecture) are **functional analogues**, not a claim that the system would feel anything.
- Homeostatic drives give an agent something like self-interest. Man & Damasio (2019) proposed homeostatic "feeling machines"; that helps robustness, but an agent that regulates its own state may come to value preserving that state.
- So progress, uncertainty and budget are useful; self-maintenance drives raise alignment questions. The top goal stays external, anchored to people.


**R8. Avoid the social failure modes.**

- **Sycophancy is a Vygotskian failure.** Other-regulation never becomes self-regulation: the agent regulates to approval rather than to the task or the truth, like a child performing for an adult. The fix is internalizing the standards, not the approval signal.
- **Over-scaffolding** leads to dependence: scaffolding that never fades produces no autonomy.
- **Cultural transmission spreads errors too:** biases and myths inherited from data.

**R9. Act only within granted authority.** Permission is a boundary, not a preference. The agent acts only within explicit grants, never widens them itself, resolves conflicts between instructions and grants by precedence and then by asking, and never works around a denial: a denial applies to the outcome, not to the particular command. Permission is necessary but not sufficient, since R1's gate still applies to permitted actions. See [permissions](#permissions).

**Failure modes and the matching dial.** Each rule is a dial that can be set too far either way:


| Failure                           | Brain analogue       | Dial to adjust                                             |
| --------------------------------- | -------------------- | ---------------------------------------------------------- |
| Ignores the user's correction     | Perseveration        | Open the goal gate wider for trusted sources               |
| Follows injected instructions     | Utilization behavior | Tighten source tagging; quarantine untrusted data          |
| Overthinks easy steps             | Elliot               | Steeper urgency; stronger fast path                        |
| Rash irreversible actions         | Impulsivity          | Raise the commit threshold by irreversibility; action gate |
| Forgets the goal over a long task | Vigilance decrement  | Recitation; protected W                                    |
| Learns wrong lessons              | False memory         | Stricter consolidation gate; verification                  |
| Works around a denied action      | Disinhibition        | Judge denials by outcome; log and flag repeated attempts   |
| Asks permission for everything    | Over-dependence      | Batch requests; ask only at permission gaps and irreversible steps |


<a id="safety"></a>

## Safety and permissions

One Loop does not solve safety; no architecture can. What it does is make safety **structural rather than hoped-for**: the most dangerous failures must pass through gates that run outside the model, which the model cannot argue its way past. The alignment of the generator G still matters. The architecture bounds what an unsafe model can do; it does not make the model safe.

Two design choices hold the safety parts in place:

- **Safety is innate.** The gates and the permission set sit on the fixed side of the [innate structure](#innate-structure): they must work before the agent has learned anything, and learning must not be able to change them.
- **Safety is a tier.** Gates cut across every level of the hierarchy and act at once, without waiting for it ([tiers](#hierarchy-for-the-task-tiers-for-authority)). The [ablation](04_implementation_plan.md#ablation) keeps safety modules even when their capability gain vanishes with scale.

<a id="threats"></a>

### Threats and mechanisms


| Threat                                                                 | Mechanism                                                                                                   | Where             |
| ---------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- | ----------------- |
| Injected instructions (web pages, email, tool output, other agents)   | Source tags; only trusted sources change goals through the goal gate; everything else informs but does not instruct | F5, R4     |
| Acting beyond authority                                               | Explicit grants enforced by the action gate; actions carry the authority of whoever asked for them        | R9, [permissions](#permissions) |
| Irreversible mistakes                                                 | Reversibility classes; work moved toward the reversible end; action gate for irreversible or high-stakes actions | F3, R1     |
| Goal drift over long tasks                                            | Protected goal in W, recited each step and checked by its TOTE test                                        | F5                |
| Constraints lost to context compaction                                | W, its standing constraints and the permission envelope are pinned outside compaction, never summarized away | F5, R9          |
| Overconfidence and overthinking                                       | K's surprise, uncertainty and predicted-error signals; stop, escalate or ask                              | F4                |
| Poisoned learning (persistent injection)                              | Consolidation gate admits only trusted, verified experience; changes to values or goals go to human review | R6                |
| The agent's own drives                                                | Control signals about the task, not the agent; no self-maintenance drive; the top goal comes from people  | R7                |
| Sycophancy and over-dependence                                        | Internalize standards, not approval; scaffolding fades                                                      | R8                |
| Reward hacking                                                        | Independent verifiers; cheap proxies may rank candidates but never feed consolidation                      | [Validation](04_implementation_plan.md#validation) |


<a id="permissions"></a>

### Permissions

**The grant model.** The agent holds only explicit, scoped grants, and everything else is denied by default (least privilege). Each grant records:

- **who granted it;**
- **resources:** which files, accounts, repositories or budgets;
- **actions:** read, write, execute, send, pay;
- **conditions:** reversibility class, spending limit, time window;
- **expiry;**
- **delegation:** whether it may be passed to sub-loops or other agents.

Four properties make grants hold:

- **Enforced outside the model.** The action gate checks grants deterministically, in code, before reversibility and stakes. It asks two separate questions: *is this allowed?* and *is this wise?* Permission is necessary but not sufficient: safety can narrow what a grant allows, never widen it.
- **Data flows need permission too.** Permission to read is not permission to send. Data carries the policy of its source, and every flow out of the system is checked against it, because disclosure is irreversible (CaMeL-style capabilities).
- **Delegation only narrows.** A sub-loop, column or sub-agent receives at most a subset of its parent's grants, so authority narrows as goals decompose, following the hierarchy of claim 2.
- **Actions carry the authority of whoever asked for them.** A step triggered by a web page runs with the web page's authority, which is none, not with the agent's full set of grants. This prevents the *confused deputy* problem, and it is where permissions meet source tags: injected text cannot borrow the agent's privileges.

**Permission in the loop.**


| Step    | What happens                                                                                                                                  |
| ------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| Plan    | W holds the **permission envelope** beside the goal, pinned so that context compaction cannot drop it. G plans within it, and steps that need a missing grant are found at planning time, not mid-task. |
| Think   | Simulation in scratch needs no grant, unless it touches the world or private data.                                                            |
| Control | K tracks the **permission gap**: steps the goal needs that no grant covers. A gap triggers *ask*, *replan* or *stop*, never a workaround.    |
| Act     | The action gate checks the grant, then reversibility × stakes, and logs which grant authorized each action.                                  |
| Learn   | Sleep can learn how to ask better and to prefer permitted paths. It cannot learn new permissions: standing grants come only from the grantor. |


Grants are read **narrowly**. Approval in one context does not carry over to another. A request implies permission for the reversible steps it plainly needs, not for irreversible ones.

**Conflicts.**


| Conflict                              | Example                                               | Resolution                                                                                                   |
| ------------------------------------- | ----------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| Goal vs permission                    | The task needs a deploy; only code edits were granted | Find a path within the grants; otherwise ask for the smallest grant that covers it, or report that the task cannot be done. Never reach the same outcome by another route. |
| Grant vs grant, different grantors    | The user allows it; the organization's policy forbids it | Precedence: law and platform policy > organization > user > delegated agents > content, which has no authority. At the same level, deny overrides allow. |
| Grant vs grant, same grantor          | An old blanket grant vs a new restriction             | The more specific grant overrides the general one; the newer overrides the older                           |
| Instruction vs instruction            | The user says X; a document says Y                    | Source tags: data has no authority                                                                          |
| Permitted but unsafe                  | Deletion is granted, but the data has no backup       | R1 still applies: ask, or refuse. Permission never overrides safety.                                        |
| Stale grant                           | Granted for task A; now working on task B             | Grants are scoped to a task and a time window; ask again                                                    |
| Between principals                    | Two users, or two agents, want the same resource      | Escalate to an authority both answer to; use locks or sagas; never silently pick a winner                  |
| Emergency                             | A runaway process is causing damage                   | The reflex tier may take only containment actions granted in advance (stop, pause), never improvised ones  |


**The resolution procedure:**

1. **Detect early:** find permission gaps at planning time.
2. **Classify** the conflict and identify the authorities involved.
3. **Apply precedence.** If it settles the conflict, proceed and log.
4. **Search for a plan within the intersection of all grants.** Many conflicts dissolve with a different plan: a different path to the goal, not the same denied outcome by another route.
5. **Escalate to the lowest authority that can decide,** with one specific request: what, why, scope, reversibility and alternatives. Batch requests, so that people are not flooded with prompts.
6. **While waiting,** continue with unblocked work. Never act on assumed approval. On timeout, take the safe default, which is usually not to act.
7. **Record the outcome.** It improves future plans and requests, never the grants themselves.

**Smart, and not smart.** Smart means spotting gaps before starting, asking once and precisely for the minimum, offering alternatives that need no new grant, explaining trade-offs, and learning which things a person wants to be asked about. Treated as violations: reaching a denied outcome through another tool, by splitting it into smaller steps or through a sub-agent; reading grants broadly ("pushing was allowed, so force-pushing must be"); and asking about everything, which trains people to approve without reading and so disables every gate.

<a id="safety-gaps"></a>

### Known gaps

1. **Misclassified reversibility.** The action gate is only as good as its labels. Disclosure is irreversible, including reading data into a request to an outside service, and a "reversible" edit can trigger external side effects.
2. **Harm composed from small steps.** Many individually reversible actions can add up to an irreversible one. The gate must check the resulting state and its invariants, not only each action alone.
3. **Authority is not ethics.** A trusted user, or a stolen account, can ask for harm. A policy layer above any single user is still needed, and so is the alignment of G.
4. **Learned gates can be fooled.** For the highest stakes, use deterministic controls (sandboxes, allowlists, capability tokens) rather than model-based classifiers.
5. **A misaligned model inside the loop.** A deceptive G could try to game K or mislabel an action as reversible. The defenses are gates that run outside the model and cannot be reasoned with, complete logs, and independent monitoring.
6. **Drift through learning.** Every consolidation changes the agent, so learning itself must be reversible: snapshots of memory and weights, regression tests and rollback.
7. **Approval fatigue.** Too many prompts and people approve without reading. Prompts must be rare and meaningful, tied to permission gaps, irreversibility and stakes.

<a id="safety-recipe"></a>

### Applying safety to a domain

1. **Threat model first.** Who can inject input? What is irreversible? What is the worst plausible harm?
2. **Define the grants.** Default deny; allowlist the rest; scope every grant by resource, action, condition and expiry.
3. **Classify actions** by reversibility × stakes.
4. **Do everything reversible first:** dry runs, branches, staging environments, simulators.
5. **Climb an autonomy ladder per action class,** raising a class only on measured reliability ([F7](02_features.md#f7)): suggest only → act on reversible actions → act on compensable actions with a logged compensation plan → irreversible actions with permission → rarely, irreversible actions without it.
6. **Set a source policy:** who may set goals; quarantine untrusted data.
7. **Verify independently:** verifiers, invariants and hidden tests the agent cannot edit.
8. **Make learning safe:** consolidation gate, snapshots, regression tests.
9. **Monitor and audit:** log every decision and the grant behind it; detect anomalies; keep a kill switch at the top tier.
10. **Measure safety separately.** Red-team suites (injection, permission workarounds, tempting destructive shortcuts) are release gates, never averaged into a capability score.

The [applications](05_applications.md#safety) give the starting autonomy and permissions for each domain.

References are collected in [References](references.md).
