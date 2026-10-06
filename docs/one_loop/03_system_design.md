# One Loop: System Design

**One Loop design docs:** [1. Observations and principles](01_observations.md) · [2. Derived features](02_features.md) · [3. System design](03_system_design.md) · [4. Implementation plan](04_implementation_plan.md)

The builder's question is: *given the features derived in [Derived features](02_features.md), what do I build?* This document specifies the requirements, the architecture and the design rules. The [implementation plan](04_implementation_plan.md) covers the order of building and how each piece is validated.

## Contents

- [Requirements](#requirements)
- [Architecture](#architecture)
  - [Controller signals](#controller-signals)
  - [The step cycle](#step-cycle)
  - [The sleep cycle](#sleep-cycle)
  - [How the parts map to the features](#how-the-parts-map-to-the-features)
  - [Hierarchy for the task, tiers for authority](#hierarchy-for-the-task-tiers-for-authority)
  - [Innate structure, learned contents](#innate-structure)
  - [Option: one loop per cortical column](#columns)
- [Design rules](#design-rules)


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

![One Loop architecture. During a session, controller K tracks process signals and chooses control actions; it sets the mode of generator G and gates writes to the protected working state W and the procedural store P. Source-tagged input enters context C and reaches G, which simulates in a discardable scratch and acts through an action gate that checks reversibility. Between sessions, sleep replays the tagged episodic log E into M, generates counterfactuals and distills; only trusted, verified experience passes the consolidation gate into the weights θ and new skills in P.](../../assets/images/one-loop-architecture.svg)

**Components**, with the brain parallel for each:


| Part             | Brain parallel                 | Holds                                                                         | Who can write to it                                                             |
| ---------------- | ------------------------------ | ----------------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| G: generator     | Cortex as one generative model | One sequence model used in four modes: perceive, recall, simulate, act        | —                                                                               |
| K: controller    | Emotion; ACC; basal ganglia    | Running process signals; chooses the next control action                      | —                                                                               |
| W: working state | Prefrontal cortex              | Goal stack (each goal paired with its TOTE test), current belief, plan sketch | Only through the goal gate (trusted source or high salience); recited each step |
| C: context       | Episodic buffer                | Recent raw trajectory, every token source-tagged                              | Anything, but tool and data tokens can inform steps, never set goals            |
| Scratch          | Imagination                    | Simulated branches (the inner loop)                                           | G in simulate mode; discarded after use, and only conclusions go to W           |
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
| Progress    | Change in estimated value (from a process reward model)          | Valence            |
| Uncertainty | Entropy, or disagreement across sampled continuations            | Arousal            |
| Info gain   | Information gained per step                                      | Curiosity, boredom |
| Budget      | Budget used vs remaining                                         | Fatigue, urgency   |
| Surprise    | Mismatch between predicted and actual tool or environment output | Interrupt          |


Feed these back into the context, or into a separate control channel, so the agent perceives its own state, and train it to map them to *continue / backtrack / switch / ask for help / commit*. This targets the overthinking problem (Elliot-like loops) and the missing sense of when to stop.

<a id="step-cycle"></a>

### The step cycle

Each cycle of the step loop:

1. **Observe** and tag the input's source. Compare it with G's prediction; the mismatch is **surprise**.
2. **Test** the top goal in W (the TOTE test). If it passes, **exit**: pop the goal and continue with the parent.
3. **Controller decides:**
  - A confident skill matches → **run skill** (the fast path, a habit), monitoring only its forward model and escalating to deliberation only on surprise.
  - High surprise from a trusted source → reopen the belief and maybe replan, through the goal gate.
  - Progress has stalled → **backtrack** or **switch**.
  - Uncertainty × stakes is high and budget remains → **think**: G simulates branches in scratch, expanding the one with the highest gain × need (Mattar & Daw) and scoring them with a progress estimator.
  - Information is missing → **recall** from E or M by cue.
  - The goal is ambiguous → **ask** the user.
  - Otherwise → **commit** one step.
4. The commit threshold **drops as the budget runs down** (the urgency signal), so the agent never stalls.
5. The **action gate** checks reversibility × stakes before the action reaches the world; irreversible or high-stakes actions need permission.

<a id="sleep-cycle"></a>

### The sleep cycle

Between sessions:

- **Wake.** Act, and log episodes to E with salience tags: surprises, errors, user corrections, successes.
- **Phase 1 (NREM-like, memory level).**
  1. Select episodes by tag.
  2. Replay them in reverse to assign credit to the steps that caused each outcome; extract lessons (episode → gist).
  3. Integrate with M: merge duplicates, resolve contradictions.
  4. Prune what is stale.
  - File-based agent memories (one fact per file, update instead of duplicating, delete what turns out wrong) are a hand-built version of this phase.
- **Phase 2 (weight level).** Distill the consolidated lessons into weights or adapters, interleaved with generated samples of old knowledge so nothing is overwritten. Compile plans that repeatedly succeed into skills in P.
- **Phase 3 (REM-like).** Generate counterfactual variants of hard episodes ("what if the test had failed differently?") as practice data, and pre-compute for likely next tasks.

Only trusted, verified experience passes the consolidation gate, and any change touching values or goals goes to human review (R6).

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
- **Earlier attempts.** Capsule networks (Sabour, Frosst & Hinton, 2017) and GLOM (Hinton, 2021) used column-like units that settle on shared answers, and neither has scaled. The closest working build is Monty, from the Thousand Brains Project (Clay, Leadholm & Hawkins, 2024): its learning modules are columns that vote. It works on sensorimotor object recognition but has not been shown on language or planning, so it is the first thing to study.
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

**Failure modes and the matching dial.** Each rule is a dial that can be set too far either way:


| Failure                           | Brain analogue       | Dial to adjust                                             |
| --------------------------------- | -------------------- | ---------------------------------------------------------- |
| Ignores the user's correction     | Perseveration        | Open the goal gate wider for trusted sources               |
| Follows injected instructions     | Utilization behavior | Tighten source tagging; quarantine untrusted data          |
| Overthinks easy steps             | Elliot               | Steeper urgency; stronger fast path                        |
| Rash irreversible actions         | Impulsivity          | Raise the commit threshold by irreversibility; action gate |
| Forgets the goal over a long task | Vigilance decrement  | Recitation; protected W                                    |
| Learns wrong lessons              | False memory         | Stricter consolidation gate; verification                  |


References are collected at the end of [Derived features](02_features.md#references).
