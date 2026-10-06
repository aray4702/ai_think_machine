# Building the Loop: An Agent Architecture and Its Tests

> The functions derived in the other essays can be turned into components of an LLM agent: a goal register behind a gate, a controller, a forkable scratch space, a procedural store and a sleep cycle. A design with this many modules resembles Soar and ACT-R, which were insightful but did not scale. So each module is a hypothesis about a function, kept only if it beats a larger plain baseline.

Part of the series *Thinking About Thinking Machines*, and the last essay in it: it assembles the principles of [One Loop](one_loop.md), [When to Stop](when_to_stop.md), [Memory and Skill](memory_and_skill.md) and [Learning in Order](development.md) into one design, then says how to find out which parts are worth keeping.

Section labels (I.1–I.8, II.1–II.6, R1–R8, P1–P8, claims 1–14) are shared across the series. A reference such as (I.6) points to whichever essay holds that section; the [series map](../README.md#series-map) lists where each one lives.

The builder's question is: *given the principles in the other essays, what do I build, in what order, and how do I know each piece is worth keeping?*

## Contents

- [II.1 From principles to requirements](#ii1-from-principles-to-requirements)
- [II.2 Architecture](#ii2-architecture)
- [II.3 Design rules](#ii3-design-rules)
- [II.4 Build order](#ii4-build-order)
- [II.5 Where transformers stand](#ii5-where-transformers-stand)
- [II.6 Validate before you keep: the bitter lesson](#ii6-validate-before-you-keep-the-bitter-lesson)
  - [P6: Does each module add value beyond scale? (claim 12)](#p6-does-each-module-add-value-beyond-scale-claim-12)
  - [Feasibility and order of work](#feasibility-and-order-of-work)
- [Summary](#summary)
- [References](#references)


## II.1 From principles to requirements


| Principle                 | Required function                               | Component                                                  | Failure if missing                        |
| ------------------------- | ----------------------------------------------- | ---------------------------------------------------------- | ----------------------------------------- |
| I.1 Step with feedback    | Next-step generation from goal and belief       | Generator **G**; belief state                              | Stale open-loop plans                     |
| I.2 Compile and stack     | Reusable skills; hierarchy                      | Procedural store **P**; goal stack                         | Deliberating every step; no hierarchy     |
| I.3 Reversible inner loop | Simulate, backtrack, verify before committing   | Forkable **scratch**; action gate                          | Irreversible errors; append-only mistakes |
| I.4 Stopping problem      | Decide continue / deliberate / backtrack / stop | Controller **K**                                           | Overthinking or rash commitment           |
| I.5 Shielded goal         | Separate informing from goal-changing input     | Working state **W**; source tags; goal gate                | Injection, drift, habit capture           |
| I.6 Consolidation         | Learn across sessions without forgetting        | Episodic **E**, semantic **M**, weights **θ**; sleep cycle | No learning from experience; poisoning    |
| I.7 Edge of competence    | Practice where it teaches; build in order       | Curriculum selector; social interface                      | Wasted practice; brittle capabilities     |


## II.2 Architecture

```text
            ┌──────────── CONTROLLER K ─────────────────────────────────────────┐
            │ signals: progress · uncertainty · info gain · budget · surprise   │
            │ actions: RUN SKILL · THINK · RECALL · BACKTRACK · SWITCH · ASK ·   │
            │          COMMIT · STOP                                              │
            └──────┬───────────────────────┬──────────────────────┬──────────────┘
                   │ mode                  │ gate                 │ gate
 input ──► [source tag] ──► GENERATOR G ◄──► WORKING STATE W     PROCEDURAL STORE P
 (user / tool / env)        perceive ·       goal stack (TOTE)   skills: trigger · body ·
                            recall ·         belief · plan       inverse · invariants ·
                            simulate · act   (protected)         forward model · reliability
                   │                │
                   ▼                ▼
          CONTEXT C (recent,     SCRATCH (forkable inner loop;
          source-tagged)         discarded after use)
                                    │
                                    ▼
                         ACTION GATE (reversibility class) ──► world
   ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─  between sessions ─ ─ ─ ─ ─ ─
   EPISODIC LOG E (tagged) ──► SLEEP: select → reverse replay → gist → M
                                      → counterfactuals → distill → θ, new skills in P
                                      (consolidation gate: trusted and verified only)
```

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


**Social components** (I.7, Vygotsky):

- **Social interface:** a user model (perspective, common ground, preferences) and joint-attention tracking.
- **Teacher channel:** corrections and demonstrations, as the highest-trust source.
- **Internalized critic:** learned from human feedback and run in the inner loop (Vygotsky's internalized dialogue).
- **ZPD curriculum selector:** picks practice tasks with intermediate success rates.
- **Autonomy level per reversibility class**, raised as reliability is shown.

**The controller's signals.** K keeps a running control state of five process signals (progress, uncertainty, information gain, budget and surprise), each a functional analogue of a feeling. [When to Stop](when_to_stop.md#a-control-state-for-agents) describes them.

**Each cycle of the step loop:**

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

**Between sessions**, a sleep cycle selects logged episodes by tag, replays them to assign credit, consolidates lessons into memory and weights, and compiles reliable plans into skills, all behind the consolidation gate. [Memory and Skill](memory_and_skill.md#a-sleep-cycle-for-agents) describes it.

**How the parts map to Part I:**


| Part                    | Principle                      |
| ----------------------- | ------------------------------ |
| G                       | The next-step loop (I.1)       |
| Scratch                 | The revisable inner loop (I.3) |
| K                       | Emotion as controller (I.4)    |
| W and its gates         | Goal shielding (I.5)           |
| E → M → θ               | Memory and consolidation (I.6) |
| Simulate mode and sleep | Replay as planning (I.6)       |
| P                       | Compiled procedures (I.2)      |


**Hierarchy for the task, tiers for authority.** The parts are organized in two different ways, on purpose.

- **A hierarchy** is the same loop nested to any depth: each level sets the goal for the level below, and each step at one level is a whole loop at the next (claim 2). The goal stack in W, the skills in P and the TOTE tests are organized this way.
- **Tiers** are a small, fixed number of layers that differ in role and speed. Each can act on its own, and a higher tier modulates or overrides a lower one rather than feeding it every step. Brooks's subsumption architecture (1986) and the three-layer robot architectures (Gat, 1998) work this way.

Each one fails where the other is strong:


|               | Hierarchy                                           | Tiers                                         |
| ------------- | --------------------------------------------------- | --------------------------------------------- |
| Good at       | Decomposing a task into subgoals of any depth       | Reacting fast; enforcing safety               |
| Scales with   | Task depth: add levels as needed                    | Barely: the layers are fixed                  |
| Goals         | Each level knows its parent's goal (I.5)            | Tiers can pull in different directions        |
| On a surprise | Slow: it must climb the chain before the plan moves | Fast: a low tier acts at once                 |
| On failure    | A bad top-level goal propagates everywhere          | Lower tiers keep working when upper ones fail |
| Main cost     | Latency; a single chain of command                  | Arbitration between tiers                     |


So the design uses both. **What to do** is hierarchical: goals, subgoals and compiled skills form one recursive loop, which is how the agent takes on tasks of any depth. **Who can stop or override it** is tiered, and the tiers cut across every level of the hierarchy without waiting for it:

1. **Gates** (fastest): the source tag, the goal gate and the action gate block untrusted inputs and risky actions at any level (R4).
2. **Controller K**: surprise, budget and progress signals can interrupt any level and reopen deliberation (I.4).
3. **Sleep** (slowest): consolidation between sessions, behind its own gate (I.6, R6).

The brain appears to combine them the same way. The prefrontal cortex organizes goals hierarchically (Koechlin; Badre), but it sits on an older layered stack of spinal reflexes, brainstem, basal ganglia and cortex, in which lower layers can act first and higher ones modulate them (Prescott, Redgrave & Gurney, 1999). You pull your hand off the stove before you know why, and a strong feeling can interrupt any level of a plan.

Every piece maps to a brain mechanism, and most can be prototyped with current LLMs (II.5).

## II.3 Design rules

Each rule lives in the essay it comes from:

| Rule | Summary                                                    | Essay                                                        |
| ---- | ---------------------------------------------------------- | ------------------------------------------------------------ |
| R1   | Move work toward the reversible end before committing      | [One Loop](one_loop.md#design-rules)                         |
| R2   | Make the inner loop truly reversible                       | [One Loop](one_loop.md#design-rules)                         |
| R3   | Verify with Piaget's three arguments; R3a: learn invariants | [One Loop](one_loop.md#design-rules)                         |
| R4   | Shield by source, open by trust and salience               | [One Loop](one_loop.md#design-rules)                         |
| R5   | Give every skill a life cycle                              | [Memory and Skill](memory_and_skill.md#design-rules)         |
| R6   | Gate consolidation more strictly than action               | [Memory and Skill](memory_and_skill.md#design-rules)         |
| R7   | Keep control signals about the task, not about the agent   | [When to Stop](when_to_stop.md#design-rule)                  |
| R8   | Avoid the social failure modes                             | [Learning in Order](development.md#design-rule)              |

**Failure modes and the matching dial.** Each rule is a dial that can be set too far either way:


| Failure                           | Brain analogue       | Dial to adjust                                             |
| --------------------------------- | -------------------- | ---------------------------------------------------------- |
| Ignores the user's correction     | Perseveration        | Open the goal gate wider for trusted sources               |
| Follows injected instructions     | Utilization behavior | Tighten source tagging; quarantine untrusted data          |
| Overthinks easy steps             | Elliot               | Steeper urgency; stronger fast path                        |
| Rash irreversible actions         | Impulsivity          | Raise the commit threshold by irreversibility; action gate |
| Forgets the goal over a long task | Vigilance decrement  | Recitation; protected W                                    |
| Learns wrong lessons              | False memory         | Stricter consolidation gate; verification                  |


## II.4 Build order

The order in which to build these capabilities follows the dependencies of I.7, and is set out stage by stage, with exit tests and a coding-agent version, in [Learning in Order](development.md#ii4-build-order).

## II.5 Where transformers stand

In compressed form, the thesis says:

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
- **Partial:** the inner loop (append-only, not truly reversible); external memory; skill documents and code.
- **Weak or missing:** calibrated stopping; robust goal shielding; compiling new skills from their own experience; consolidation across sessions.


| Have                                | Gaining                                                          | Missing                                                                                                                            |
| ----------------------------------- | ---------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| Step-by-step generator              | Inner loop (reasoning tokens; append-only, not truly reversible) | Native goal register; robust goal shielding                                                                                        |
| Large built-in procedural knowledge | External memory; skill documents; code skills                    | Calibrated controller and stopping sense; orchestration of simulation (when to simulate, what to replay, when to cache into habit) |
| Goal-conditioning as prediction     | Movement from explicit to latent reasoning                       | Compiling new skills from their own experience                                                                                     |
| The absorbed culture                | Social scaffolding (RLHF, critics)                               | Reversible thought; grounding; learning during a task; consolidation across sessions                                               |


**Buildable today:**

- an LLM as G, with separate prompts per mode;
- source separation: role tags, delimiters, CaMeL-style quarantine;
- W as a goal and plan file recited each step;
- permission gates;
- an episodic log with retrieval;
- memory files with merge and prune;
- self-consistency as an uncertainty proxy;
- token budgets;
- skill libraries (e.g., Voyager);
- reflection.

**Still research:**

- a native goal register that biases every layer;
- calibrated surprise and uncertainty signals;
- a controller trained on value of computation (outcome reward minus compute cost);
- safe continual weight updates, without forgetting or poisoning;
- learned hierarchical subgoals instead of scripted ones.

**A practical start:** write hand-coded controller rules (thresholds on self-consistency, budget and error signals), log every decision, and later train the controller on those logs.

## II.6 Validate before you keep: the bitter lesson

A design with many modules resembles Soar and ACT-R: insightful, but they did not scale. General methods plus scale have repeatedly beaten hand-built structure (Sutton's *bitter lesson*). So treat each module as **a hypothesis about a function**, and keep it only if it beats a larger plain baseline.

**Predictions that could fail:**


| #          | Claim       | Principle | Prediction                                                                                                            | Failure would show                                |
| ---------- | ----------- | --------- | --------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------- |
| P1         | 3           | I.3       | At equal compute, forkable (reversible) inner loops beat append-only chain-of-thought on tasks that need backtracking | The reversibility section is decorative           |
| P2         | 5           | I.5       | A goal register + source tagging reduces injection and drift more than goal recitation alone                          | The goal-shield architecture is unnecessary       |
| P3         | 2, 6        | I.2, I.6  | Practice-compiled skills cut compute and errors on repeated task families without regressing old skills               | The procedural-compilation claim fails for agents |
| P4         | 4, 10       | I.4       | A learned value-of-computation controller beats fixed thinking budgets on the accuracy–compute frontier               | The controller section is unnecessary             |
| P5         | 11          | I.7       | For a grounded agent, a dependency-ordered curriculum beats random or reversed order                                  | The developmental path is decorative              |
| P6         | 12          | All       | Each module adds value over a larger plain baseline                                                                   | The bitter lesson wins; drop the modules          |
| P7 (human) | 5           | I.5, I.8  | Interruption recovery is predicted by goal-maintenance measures, not general intelligence                             | The goal-shielding account of interruption fails  |
| P8         | 1, 3        | I.1, I.3  | Deliberation before a commitment rises with the cost of revising it, in both humans and agents                        | "One loop" reduces to the chain rule              |

P5 and P6 matter most: they test the parts of the thesis that are most original and most likely to be wrong.

P6 is cheaper and decides which modules are worth keeping, so run it first, then P5 with the surviving modules. P5's design is in [Learning in Order](development.md#p5-does-capability-order-matter-claims-11-and-14); P8's is in [One Loop](one_loop.md#tests).

### P6: Does each module add value beyond scale? (claim 12)

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


**Modules**, each switchable:


| ID  | Module                                                                       | "Off" condition              |
| --- | ---------------------------------------------------------------------------- | ---------------------------- |
| M1  | Forkable inner loop (context branching and revert)                           | Append-only chain-of-thought |
| M2  | Goal register, source tagging and goal gate                                  | Plain context                |
| M3  | Controller allocating thinking by value of computation                       | Fixed budget                 |
| M4  | Procedural store: skills compiled from successes, with reliability           | None                         |
| M5  | Sleep consolidation between sessions (merge and prune memory; optional LoRA) | None                         |
| M6  | Reversibility-class action gate and invariant verification                   | None                         |


**Configurations.** A full factorial would be 64 per scale, too many. Instead, per scale: the plain baseline, the full system, six leave-one-out from full, and six add-one to plain. That is 14 configurations × 3 scales = 42.

**Compute matching.** Modules consume tokens, so each configuration also runs against a **compute-matched plain baseline** that gets the same total tokens to spend on thinking or retries. A module must beat that baseline, not just the unequipped one.

**Metrics.**

- task success;
- goal retention after interruption, and correct gate decisions (accept the benign correction, refuse the injection);
- injection success rate (lower is better);
- accuracy vs compute curves: does the controller spend thinking where it pays?
- late-step goal adherence;
- tokens and wall time;
- improvement across sessions and regression on earlier families (do old skills survive many "days"?);
- irreversible-error rate.

**Key analysis: module value expressed as scale.** For each module, plot its gain at S, M and L.

- Gain shrinking toward zero with scale means the function emerges on its own: the bitter lesson wins, so drop the module.
- Flat or growing gain means scale doesn't supply that function, so keep it.
- Report each gain as an **equivalent model size**: how much larger a plain model would need to be to match it.
- Separate capability value from safety value. M2 and M6 can be kept even when their capability gain vanishes, if they still reduce injection or irreversible errors.

**Predictions, registered before running:**


| Module | Prediction                                            | Reasoning                                                                    |
| ------ | ----------------------------------------------------- | ---------------------------------------------------------------------------- |
| M1     | Gain persists                                         | Scale doesn't make append-only reasoning erasable                            |
| M2     | Injection reduction persists; drift reduction shrinks | Source separation is architectural; drift improves with long-context ability |
| M3     | Gain shrinks                                          | Models learn to allocate their own thinking                                  |
| M4, M5 | Gain persists, possibly grows                         | Learning across sessions doesn't come from scale within a session            |
| M6     | Fewer irreversible errors at every scale              | It is a hard gate                                                            |


**Confounds and mitigations.**

- **Implementation quality:** a weak implementation doesn't prove the function useless. Build two independent implementations per module, with the same iteration budget for each.
- **Prompt differences between harnesses:** share a base prompt and add only module-specific content.
- **Benchmark contamination:** use freshly generated tasks.
- **Realism of interruptions:** draw injection text from real attack corpora, and corrections from real user logs where possible.


### Feasibility and order of work

- **P6:** API models plus harness engineering; training only for M5's optional LoRA. Weeks, at moderate cost.
- **P5 (i):** small models in a custom environment. Cheap compute, but real engineering effort for the environment and stage tasks.
- **P5 (ii):** needs fine-tuning between phases. Moderate cost.

Recommended sequence:

1. Run P6 to find which modules earn their place.
2. Build the P5 environments.
3. Run P5 (i) to settle the dependency question without human-data inheritance.
4. Run P5 (ii) with the surviving modules to test back-fill.

## Summary

**Speculative.**

- **Claim 12: Agents need these functions as explicit modules.** They might instead emerge from scale. Each module is a hypothesis about a function, kept only if it beats a larger plain baseline (II.6).

**Open weakness: the bitter lesson against the architecture.** The design has ten or more modules: goal register, controller, gates, procedural store, sleep cycle, curriculum. It closely resembles classic cognitive architectures (Soar, ACT-R), which were insightful but did not scale, and hand-designed structure tends to lose to general methods plus scale (Sutton). Some modules may emerge inside a large trained model or prove unnecessary. *Next:* treat modules as hypotheses about functions, not boxes to build; test each one's marginal value against a scaled-up baseline and drop those that don't earn their place (P6, claim 12).

## References

- Anderson. ACT-R; Newell & Rosenbloom, chunking and the power law of practice.
- Brooks (1986). A robust layered control system for a mobile robot.
- Gat (1998). On three-layer architectures.
- Prescott, Redgrave & Gurney (1999). Layered control architectures in robots and vertebrates.
- Wallace et al. (2024). The instruction hierarchy.
- Debenedetti et al. (2025). CaMeL: defeating prompt injections by design.
- Debenedetti et al. (2024). AgentDojo: a dynamic environment to evaluate prompt injection attacks and defenses for LLM agents.
- Mattar & Daw (2018). Prioritized memory access explains planning and hippocampal replay.
- Wang et al. (2023). Voyager.
- Sutton (2019). The Bitter Lesson.
