# One Loop: Derived Features

**One Loop design docs:** [1. Observations and principles](01_observations.md) · [2. Derived features](02_features.md) · [3. System design](03_system_design.md) · [4. Implementation plan](04_implementation_plan.md) · [5. Applications](05_applications.md) · [6. Media creation](06_media_creation.md) · [7. Companion](07_companion.md) · [8. Discovery and invention](08_discovery_invention.md) · [9. Robotics](09_robotics.md) · [References](references.md)

Each section below derives one feature of the agent. It starts with a **constraint** that every agent acting in the world faces, derives the **consequence** that follows from it, gathers **evidence** from humans and machines on how the consequence can be met, and ends with the **feature** it adds to the design. Components named in the feature boxes (G, K, W, P and the rest) are specified in [System design](03_system_design.md); rules R1–R9 are in its [design rules](03_system_design.md#design-rules).

## Contents

- [F1. Too many futures to plan in advance → commit one step at a time and use feedback](#f1)
- [F2. Limited compute and memory → compile steps into procedures, and stack them](#f2)
- [F3. Some outputs can't be taken back → put a reversible inner loop in front](#f3)
- [F4. Thinking has a cost → use control signals to decide when to stop](#f4)
- [F5. The context mixes sources → the goal must be shielded](#f5)
- [F6. Learning fast overwrites old knowledge → separate memories and consolidate](#f6)
- [F7. Learning signal lives at the edge of competence → development has an order](#f7)
- [Behaviors the design should expect](#behaviors)


<a id="f1"></a>

## F1. Too many futures to plan in advance → commit one step at a time and use feedback

**Constraints:**

- **Too many possible sequences.** With b options per step and n steps there are bⁿ complete sequences; they can't all be searched. Committing one step at a time turns that into n choices of size b. For outputs that can't be revised once out, that is the affordable way to produce long sequences; where revision is cheap, refinement is an alternative (F3).
- **The world is noisy and changes while you act**, so a fully precomputed open-loop plan goes stale. Control theory shows that closed-loop feedback beats open-loop planning under noise.
- **The world is only partly observable**, and acting is often the only way to find out more.
- **Memory and compute are limited**, so the full history can't be kept and reprocessed at every step.
- **Committed outputs come out one at a time.** There is one mouth, one gaze and one body position. Even if thinking runs in parallel, what gets committed must be serialized.

**Consequence:** Commit one step, observe, and generate the next step from an updated **belief state**: a summary of history sufficient for acting well. Under partial observability (formally a POMDP), the optimal action depends on exactly such a belief state. Formally, the next step depends not on the raw history but on *a belief built from previous steps*. Brains compress history into a running state; transformers keep the raw history and attend to it. These are two approximations of the same belief state (F6). A plan or map can still guide the loop, but as a prior, not as a script.

![Planning the whole sequence first means searching bⁿ futures and running one as a script that goes stale; the closed loop instead chooses one step from a belief state and the goal, commits it, observes the outcome and updates the belief.](../../assets/images/one-loop-i1-step-feedback.svg)

**Why the processes of minds and transformers look alike.** The problem forces it. Step-by-step generation that conditions on history and absorbs interruptions is what any capable agent with limited compute, an unpredictable world and a goal ends up doing for outputs it can't take back; it can't plan the whole sequence in advance, because too much would change before it finished. Brains and transformers may both have arrived at this loop because it is the standard tractable solution for irreversible commitments under uncertainty, not by coincidence and not because they share a mechanism. That makes the loop a sound basis for an agent design, not just a similarity between brains and AI. The main caveat, that LLMs may have inherited the structure from human text, is tracked as a design risk ([risks](04_implementation_plan.md#risks)).

**Evidence:**

- **Humans:** Saccades are information-gathering actions: each one is taken to gather information for the next decision. Under predictive processing, perception is active sampling to reduce prediction error, so a saccade sequence is generation too, and perception sits fully inside the loop rather than only feeding it. Motor control is closed-loop, and Todorov's optimal feedback control goes further: the motor system corrects only deviations that matter for the task and lets the rest go (the *minimal intervention principle*). Speech is produced incrementally, with implicit look-ahead.
- **Machines:** Engineered systems arrive independently at the same loop. Model predictive control plans over a short horizon, executes only the first step, observes and replans; this is how navigation (point 4 in the [observation](01_observations.md#observation)) can follow a plan or map and still decide on the fly. AlphaZero searches ahead, commits one move and searches again. Transformers generate token by token, and an injected interruption simply becomes part of the next step's conditioning.
- **Biology without brains:** Bacterial chemotaxis runs the same run–sense–adjust cycle.

**Feature F1: the step loop.** Every level of the agent runs one loop: generate the next step from the goal and a belief state, commit it, observe the result, and update the belief. A plan or map guides the loop as a prior, not a script. *Components:* generator G; belief state in the working state W ([architecture](03_system_design.md#architecture)).

<a id="f2"></a>

## F2. Limited compute and memory → compile steps into procedures, and stack them

**Constraints:** Human working memory holds about four chunks. Deliberation is slow and costly.

**Consequence:** Steps that recur must be **compiled** into procedures that run without deliberation, and a sequence at one level must be **chunked** into a single step for the level above. The result is a hierarchy of loops, each on its own timescale.

![Practice compiles reach, grasp and pull into one step, "open the door", freeing working memory; stacked, each step at one level (plan, action, perception) is a whole loop at the level below.](../../assets/images/one-loop-i2-compile-stack.svg)

The loop itself is a **TOTE unit** (Miller, Galanter & Pribram, 1960): *Test* the state against the goal, *Operate*, *Test* again, *Exit* when they match. Their main further claim was that TOTE units **nest**: hammering a nail is (lift hammer → strike), repeated until the nail is flush. So the seven processes of the [observation](01_observations.md#observation) are better seen as **levels of one hierarchy** than as parallel processes, where each level's step becomes the goal of the level below:

```text
need (hunger)                         homeostasis, hours
 └ goal (get lunch)
    └ plan (go to the café)           planning, minutes
       └ navigation (turn left)       execution, seconds
          └ action (reach, grasp)     motor, ~100s of ms
             └ saccade (find handle)  perception, ~200 ms
   (talking and reasoning attach at any level)
```

Each level runs its own step-by-step loop on its own timescale. The brain has a matching layout: the prefrontal cortex runs from abstract goals at the front to concrete actions at the back (Koechlin; Badre). In AI terms this is hierarchical reinforcement learning, or the options framework (Sutton, Precup & Singh, 1999).

**Evidence: procedural memory.**

- **Definition:** Knowing *how* rather than knowing *that* (Ryle, 1949): skills, habits, motor programs, cognitive routines (reading, arithmetic, grammar) and perceptual skills, including expert saccade strategies. It is acquired by practice, hard to put into words ("we know more than we can tell": Polanyi), and very durable.
- **Procedural memory is a separate system:** The amnesic patient H.M. improved at mirror drawing over days with no memory of ever practicing it (Milner, 1962). In Squire's taxonomy, *declarative* memory is episodic plus semantic, and *non-declarative* memory is procedural, priming and conditioning. Semantic and procedural memory learn differently and belong in separate stores (F6).
- **Formation.**
  - The **basal ganglia** learn which action fits which context, by reinforcement through dopamine prediction errors. With practice, control shifts from the goal-directed dorsomedial striatum to the habitual dorsolateral striatum (Yin & Knowlton, 2006).
  - The **cerebellum** learns **forward models** that predict an action's sensory consequences, along with fine timing and error-driven correction.
  - Skills move through stages (Fitts & Posner): **cognitive** (following explicit instructions; slow, effortful) → **associative** → **autonomous** (fast, parallel, no attention needed).
  - Declarative steps are **compiled** into single procedures (Anderson's ACT-R; Newell & Rosenbloom's chunking), and performance speeds up along the power law of practice.

**Why procedural memory is central to the design.**

- **It supplies the steps.** Every step in the seven processes is itself a procedure: a saccade program, the articulation of a word, a grasp, a familiar inference move, a turn on a known route. The loop composes procedures. Without them each step would need deliberation, and the combinatorial problem of F1 would come back at full force.
- **It makes the hierarchy possible.** Chunking turns a sequence at one level into a single step at the level above: letters → words → phrases; reach + grasp + lift → "pick up the cup." This answers Lashley's (1951) problem of serial order: behavior isn't a flat chain, it's nested, and each level of the TOTE hierarchy runs over the compiled procedures of the level below. Higher-level thinking is affordable because lower levels are automatic.
- **It frees the controller and working memory.** Automatic skills run without supervision, so the four-item working memory and the controller can attend to what's new. That is how you can talk while walking, or plan while driving.
- **It is the destination of consolidation.** The deliberation → habit pipeline of F6 (practice, Dyna, distillation) produces procedural memory. Planning is how you act before you have a skill; procedural memory is what planning leaves behind.
- **It supplies the predictions.** Cerebellar forward models predict what each action should produce, and the mismatch is the surprise signal the controller of F4 relies on.
- **It covers perception and reasoning too.** Chess masters perceive positions as chunks (Chase & Simon, 1973), expert radiologists' saccades go straight to anomalies, and mathematicians apply proof moves automatically. Expertise in all seven processes is mostly procedural.
- **Its failure mode is habit capture.** A habit can fire after the goal has changed: salt in the coffee, driving to the old office (Norman; Reason's "action slips"). It is the internal version of utilization behavior (F5). The controller must be able to veto a running habit (prefrontal inhibition, stop signals), so goal shielding works in both directions: against external distractors and against one's own habits.

**Machines: an inversion.** LLMs are mostly procedural memory. Grammar, reasoning patterns and coding style live in the weights as know-how, and next-token generation is itself a skill. But after deployment they can't acquire new procedures natively. Their three substitutes line up with Fitts & Posner's stages:


| Form                                       | Stage                                                         | Example                                                    |
| ------------------------------------------ | ------------------------------------------------------------- | ---------------------------------------------------------- |
| Instructions or skill documents in context | Cognitive: a novice reading the manual; slow, costs attention | Prompted procedures; skill files loaded by agent harnesses |
| Executable code and tools                  | Externalized automaticity: runs without deliberation          | Voyager's code-skill library; scripts; APIs                |
| Adapters or weights trained by practice    | Autonomous: true procedural memory                            | Fine-tuning or distillation from successful trajectories   |


The missing piece in LLMs is **practice-driven compilation**: moving a procedure from the first row to the second and third automatically through repetition, with forward models and reliability estimates attached (R5). Self-revising skill libraries appeared in 2026, but retrieving and testing the right skill remains the bottleneck ([state of the field](04_implementation_plan.md#field-2026)).

**Feature F2: compiled skills, stacked into a hierarchy.** Sequences that repeatedly succeed are compiled into skills, and a skill at one level becomes a single step for the level above. Each skill carries a forward model, so running it yields predictions the controller can check, and the controller can veto a skill whose goal no longer applies. *Components:* procedural store P; goal stack in W; the skill life cycle (R5).

<a id="f3"></a>

## F3. Some outputs can't be taken back → put a reversible inner loop in front

**Constraint:** Many commitments are **irreversible**: you can't unsay a word or unthrow a ball. Errors in them are costly.

**Consequence:** Wherever errors are expensive, the agent needs two loops:

- an **inner loop** of cheap, revisable simulation (refining, searching, backtracking) in imagination or on scratch paper;
- an **outer loop** of irreversible commitment to the world, one step at a time, with feedback.

What defines the inner loop is **reversibility**: its operations can be undone or compensated, and they preserve invariants. Thinking is the revisable space that evolved so we don't commit too early.

Step-by-step generation is forced where outputs are **irreversible commitments to an uncertain world**. Where outputs can be cheaply revised, **iterative refinement** appears instead: diffusion models refine a whole image in parallel, and humans do the same when sketching, editing an essay or imagining. So all seven processes in the [observation](01_observations.md#observation) run the same outer loop; what differs is how much revisable inner loop sits in front of each commitment. Transformers started as outer-loop-only machines, and much recent progress amounts to adding an inner loop.

![A reversible inner loop (propose, check, revise or undo) passes its result through a one-way commit into the outer loop of irreversible steps in the world, and feedback returns to the inner loop. How much inner loop sits in front depends on the cost of revising a committed step, from planning (free) to motor action (impossible).](../../assets/images/one-loop-i3-two-loops.svg)

**Mapping irreversibility onto the seven processes.** The deciding variable is how expensive it is to revise a step once it's out. As that cost rises, behavior moves from refinement toward strict step-by-step generation with repair. This also explains why backtracking shows up in some cases and not others.


| Case (Observation section) | What gets committed                    | Cost to revise                       | Resulting structure                                                                                                                  |
| -------------------------- | -------------------------------------- | ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------ |
| 5. Motor action            | Muscle commands                        | Impossible: you can't unthrow a ball | Pure closed-loop, step-by-step generation                                                                                            |
| 6a. Talking                | Spoken words                           | Can't unsay, only repair             | Step-by-step, with appended repairs ("I mean…")                                                                                      |
| 4. Navigation              | Physical position                      | Costly: walking back takes time      | Step-by-step, MPC-style; backtracking is literal                                                                                     |
| 1. Perception              | Gaze (cheap) and interpretation (free) | Low                                  | Hybrid: saccades are sequential, but the percept is refined in parallel (a flipping Necker cube is the interpretation being revised) |
| 2. Reasoning               | Thoughts in working memory             | Low, but memory is tiny              | Sequential search with backtracking: a tree, not a chain                                                                             |
| 6b. Writing                | Text on a page                         | Nearly free                          | Refinement: drafts, edits, restructuring                                                                                             |
| 3. Planning                | Nothing yet                            | Free                                 | Most refinement-like: the whole plan gets rearranged                                                                                 |


**Advantages of reversibility:**

- **Free backtracking.** Search needs undo; chess engines make and unmake moves millions of times. The inner loop is cheap because its operations are reversible.
- **Verification by inversion.** Check addition with subtraction, decode(encode(x)) = x, round-trip tests, back-translation, cycle consistency, substituting a solution back into the problem. Undoing is often easier to check than doing.
- **Invariants.** Knowing what a transformation leaves unchanged compresses the world model, prunes search, and turns violations into high-value surprise signals: a violated invariant means a bug or a wrong belief. This is the cognitive counterpart of Noether's link between symmetry and conservation.
- **Composability.** Reversible operations with an identity form a group-like structure: they can be composed, inverted and re-associated. That is the basis of systematic generalization.

**How much inner loop?** Roughly *(cost of an error) × (uncertainty) ÷ (time pressure)*.

- **High stakes and enough time**, as with surgeons, chess masters or exams in pen: think more before committing.
- **Low stakes or time pressure**, as in casual talk or reflexes: commit fast and correct online.

**Evidence:**

- **Talking vs writing** is the cleanest natural experiment among the seven processes. The same person producing the same kind of output switches from incremental generation with appended repairs ("I mean…") to drafting and revision, purely because reversibility changes. Word processors made revision even cheaper, and writing became measurably less linear.
- **Piaget.** Thought *is* internalized action, and it becomes thought proper when its operations become reversible. He described two forms of reversibility:
  - **inversion** (negation): undo the operation; +A − A = 0; pour the water back;
  - **reciprocity** (compensation): a change in one dimension offset by another; taller but thinner; A < B ⇔ B > A.
  - At the concrete stage these work separately; at the formal stage they combine into a single system, the **INRC group** (Identity, Negation, Reciprocal, Correlative). Conservation tasks reveal the shift. Water is poured from a wide glass into a tall, thin one:
    - The **preoperational** child says "more now, it's higher." It judges by the end state (*figurative* knowledge) and fixates on one dimension (centration).
    - The **concrete** child says "the same," with three justifications: **identity** (nothing was added or taken away), **inversion** (you can pour it back) and **compensation** (taller, but thinner). It reasons about the transformation, not just the states (*operative* knowledge).
  - Each justification is also a way for an agent to check its own work: identity becomes a diff audit, inversion a round-trip test, and compensation a conservation check (R3).
- **How reversibility develops.** Piaget traced it from action to thought:
  - **Sensorimotor, practical reversibility:** the infant can physically return to a starting point and take detours (the "practical group of displacements").
  - **Concrete operations:** reversibility is internalized; undoing is done mentally, on concrete things.
  - **Formal operations:** inversion and reciprocity are unified (INRC) and applied to hypotheses, as in reasoning with contrapositives and controlling variables in the balance and pendulum tasks.
  - The agent version follows the same path: learn undo as an action (git revert, rollback), then as internal simulation (forked contexts, invariant checks), then as formal reasoning over hypotheses ("if this fix is right, reverting it must bring the failure back").
- **Craik (1943).** The two-loop idea is old: the organism carries a "small-scale model" of the world so it can try alternatives before acting.
- **Machines.** Modern AI rediscovered both loops.
  - Reasoning models add private thinking tokens, a cheap-to-revise region ("wait, that's wrong…") before the irreversible answer.
  - Robot diffusion policies refine a short chunk of actions as a whole, execute it, then refine the next chunk: MPC with a refinement inner loop.
  - Diffuser (Janner et al., 2022) plans whole trajectories by refinement, matching the planning row of the table.


**Where transformers lack reversibility.** They are still partly preoperational.

- **Append-only thinking.** A reasoning model can't delete a wrong thought. "Wait, that's wrong" leaves the error in context, where it still primes later tokens. This is compensation, not inversion. Real inversion requires forking or rolling back the context, which tree-search harnesses provide (R2).
- **The reversal curse** (Berglund et al., 2023). Models trained on "A is B" often fail at "B is A," which looks like a failure of reciprocity in learned knowledge. The reading is weaker than it seems, though: models reverse relations fine when both are in context ([evidence notes](04_implementation_plan.md#evidence-notes)).
- **Conservation failures.** Entity and state tracking breaks down over long sequences of operations; video generators make objects appear, vanish or change count; counting fails after a transformation. These are classic preoperational errors: judging by surface state instead of tracking the transformation.
- **Verification by inversion helps.** Substituting a solution back into the original equation, or round-tripping a transformation, catches many LLM errors. It is an underused form of self-checking.

**Feature F3: a reversible inner loop.** Before each commitment, the agent may simulate, search and revise in a forkable scratch space. How much it does scales with the cost of undoing the commitment, the uncertainty and the time available, so every action carries a reversibility class. Verification uses inversion, identity and conservation checks. *Components:* scratch; action gate; rules R1–R3a.

<a id="f4"></a>

## F4. Thinking has a cost → use control signals to decide when to stop

**Constraint:** Each additional step of deliberation costs time, energy and opportunity.

**Consequence:** Every level reduces to one decision made over and over: think one more step, or act now? More fully, it must decide whether to *continue, deliberate, backtrack, switch or stop*. A good stopping rule has three parts:

1. a **confidence threshold**, which decides when to commit;
2. an **urgency signal** that lowers the threshold over time, so the agent doesn't stall;
3. a **surprise detector** that reopens the inner loop mid-execution. This is how interruptions get absorbed.

Humans get parts 2 and 3 cheaply from emotion and conflict monitoring. LLMs currently approximate them with external budgets and learned habits. The seven processes in the [observation](01_observations.md#observation) may differ less in their generation mechanism than in how well this stopping rule is tuned for each one.

![Noisy evidence accumulates until it crosses a confidence threshold, and the agent commits; urgency lowers the threshold over time; a surprise during execution reopens deliberation. Emotion acts as the controller, mapping feelings such as curiosity, frustration, anxiety, surprise, fatigue and satisfaction to control actions.](../../assets/images/one-loop-i4-stopping.svg)

**Evidence.** Brains and models handle the decision in surprisingly parallel ways.

- **Accumulate evidence to a threshold** (the brain's basic mechanism). In the drift-diffusion model (Ratcliff; neural evidence from Shadlen), noisy evidence accumulates until it crosses a threshold, and then the agent commits.
  - A high threshold is slow and accurate; a low one is fast and sloppy. The speed–accuracy tradeoff is a single dial.
  - Under time pressure the threshold drops over time (an **urgency signal**), so the agent eventually commits even while unsure.
  - This approximates Wald's sequential probability ratio test, which is provably optimal for this kind of stopping problem.
- **Is another thought worth it?** (the rational account). Russell & Wefald's metareasoning and Lieder & Griffiths' resource-rational analysis give the rule: think one more step only if the expected improvement in the decision exceeds the cost of thinking (time, energy, missed opportunity). This is the formal version of F3's *(cost of an error) × (uncertainty) ÷ (time pressure)*.
- **Detect conflict and escalate** (System 1 → System 2). The default is to commit fast. A conflict monitor (the anterior cingulate cortex) notices when something is off, such as competing responses, an error or a surprise, and reopens the inner loop. This is also how interruptions are handled: a surprise during execution reopens deliberation, the agent replans, and execution resumes.
- **Emotion supplies the cost signal.** In *Descartes' Error*, Damasio's patient Elliot had ventromedial prefrontal damage that cut off emotional signals. His logic was intact, but he could deliberate endlessly over trivial choices, such as which pen to use. On Damasio's account, emotion ("somatic markers") gives a fast value estimate that ends deliberation; without it, the inner loop doesn't know when to stop.

**Emotion as the control layer.** Every process in the [observation](01_observations.md#observation) starts with a goal and stops at a conclusion or an interruption. The **generator** (the part that produces each next step: next-token prediction in a transformer, the cortex's generative model in a brain) produces steps, but something has to set the goal, judge progress and declare it done. One answer is that emotion does that job.

- **Feelings report the body's state** (Damasio). Feelings are the mind's readout of homeostasis: how the body is doing relative to staying viable. A goal starts as a felt need. Somatic markers attach a fast, body-based value to options, so each one doesn't have to be worked out from scratch. The classic evidence, the Iowa Gambling Task, is contested: skin responses appeared before people could say which decks were bad, but Maia & McClelland (2004) showed participants knew more consciously than claimed. The functional idea has held up better than that experiment.
- **Predictive processing makes this precise.**
  - **Valence ≈ the rate of change of prediction error** (Joffily & Coricelli, 2013; a formal proposal, not an established result). Things getting better feels good; things getting worse feels bad. Valence is a progress signal.
  - **Arousal ≈ uncertainty or precision**: how much the current situation demands attention.
  - **Emotions as interoceptive inference** (Seth; Barrett): emotions are predictions about the internal state of the body.
  - On this view emotion is a **meta-signal about how the process is going**, not about its content, which is exactly what a stopping and escalation rule needs.

Mapped onto the decisions of the loop:


| Feeling                                   | Measures                                  | Control action                   |
| ----------------------------------------- | ----------------------------------------- | -------------------------------- |
| Curiosity                                 | Expected information gain                 | Keep exploring                   |
| Boredom                                   | Low gain, high opportunity cost (Kurzban) | Stop; go elsewhere               |
| Frustration                               | Stalled progress                          | Backtrack or switch strategy     |
| Anxiety                                   | Uncertainty × stakes                      | Raise the threshold; think more  |
| Surprise                                  | Large prediction error                    | Interrupt; reopen the inner loop |
| Fatigue                                   | Resources spent                           | Lower the threshold; finish up   |
| Satisfaction, "aha", feeling of rightness | Error resolved                            | Commit and stop                  |


Together these cover every control decision the seven processes need: start, continue, backtrack, switch, interrupt, stop. The generation mechanism can be the same across all seven, with emotion acting as the **shared controller**. The surprise signal itself comes from the procedural forward models of F2.

**Machines:** Each brain mechanism has an LLM counterpart, and a gap:


| Brain mechanism                       | LLM counterpart                                                                 | Gap                                              |
| ------------------------------------- | ------------------------------------------------------------------------------- | ------------------------------------------------ |
| Threshold on accumulated evidence     | Token entropy or confidence; self-consistency voting                            | Models are often poorly calibrated               |
| Urgency signal                        | Thinking-token budgets; length penalties in reinforcement learning              | Imposed from outside, not felt                   |
| Conflict monitor reopens deliberation | "Wait, …" self-correction learned in reasoning RL                               | Emergent and unreliable                          |
| Somatic markers end deliberation      | Nothing intrinsic                                                               | Overthinking on easy problems, a lot like Elliot |
| Variable thought per step             | Fixed compute per token; adaptive computation (Graves 2016, PonderNet) is niche | Architecture limitation                          |


A telling result: in the *s1* paper (2025), suppressing the end-of-thinking token and appending "Wait" made models think longer and improved accuracy. That is essentially an external "are you sure?". The model had no internal sense of when it was done.

**What AI already has of the control layer:**

- **Dopamine ≈ reward prediction error** (Schultz, 1997), which is the TD error of reinforcement learning. This is the closest established match.
- **Curiosity bonuses** (ICM, RND) and **learning progress as intrinsic reward** (Oudeyer). Learning progress is almost exactly Joffily's valence.
- **Process reward models and value heads** score intermediate reasoning steps, a kind of progress signal.


What's missing is that these are mostly used **during training**. At inference time, an LLM agent has no running felt state that shapes its next step. The [controller signals](03_system_design.md#controller-signals) of the system design provide one.

**Feature F4: a controller that decides when to stop.** A controller keeps a running state of process signals (progress, uncertainty, information gain, budget, surprise) and chooses among run skill, think, recall, backtrack, switch, ask, commit and stop. The commit threshold drops as the budget runs out, and surprise reopens deliberation. *Components:* controller K ([controller signals](03_system_design.md#controller-signals)); rule R7.

<a id="f5"></a>

## F5. The context mixes sources → the goal must be shielded

**Constraint.** An agent's input mixes its own intentions, other people's instructions, things it observes, and its own habits. Any of these can push it toward a different goal.

**Consequence.** The goal must be **maintained** and **shielded**: information that *informs the next step* must be kept separate from information that *changes the goal*. Content can be mimicked, so shielding has to work by **source** and **salience**, not by content. Without a protected goal there is nothing to judge relevance against, and everything in context competes equally.

![Inputs arrive tagged by source; a gate lets a trusted source or a high-salience event change the shielded goal, while everything else, including instructions found in a web page, may only inform the next step. Without a gate, a transformer's context is one flat stream in which injected text can act as an instruction. Shielding is a dial between distractibility (prompt injection) and perseveration.](../../assets/images/one-loop-i5-goal-gate.svg)

**What a goal is.** Every process in the [observation](01_observations.md#observation) "starts with a goal," and that is the one part the loop itself can't explain. One answer: a goal is **a prediction the agent makes come true**.

- **Active inference.** Goals are prior preferences: the organism expects to be in viable states ("I'll be fed"). When reality doesn't match, the error can be resolved two ways: change the belief (perception), or change the world so the prediction comes true (action). Goals and beliefs are the same kind of object, distinguished only by **which side yields**.
- **Transformers work this way literally.** A prompt like "Here is a correct proof:" is a conditioning prefix, and the model generates a continuation in which the goal is achieved. The Decision Transformer (Chen et al., 2021) makes it explicit: condition on a desired future reward, and the model predicts the actions that would produce it. Goal-conditioning as prediction may be the deepest point of contact between the seven processes and the transformer.

**Goals also come from the bottom up.** Not every goal starts with a need. The environment suggests goals: you see a cup and want to pick it up (an **affordance**). Goals are also sometimes constructed after the fact (choice blindness; Gazzaniga's interpreter). Bottom-up goals are exactly what the prefrontal cortex has to shield the top-down ones from.

**Evidence: how the brain shields goals.**

- **Active maintenance with top-down bias.** The prefrontal cortex doesn't just store the goal: it holds it in sustained activity and continuously biases all other processing toward goal-relevant pathways ("biased competition"; Miller & Cohen, 2001).
- **A learned gate.** In the PBWM model (O'Reilly & Frank, 2006), the basal ganglia gate working memory. While the gate is closed, distractors can't overwrite the goal; it opens only when updating is warranted. Maintaining a goal and updating it are separate operations, controlled by a learned gate. O'Reilly's *Computational Cognitive Neuroscience* covers this in detail.
- **Source tagging.** The brain keeps track of where information came from: my intention, someone's instruction, something I saw. When source monitoring fails, as in some psychosis, inner speech is experienced as external voices.
- **A tunable tradeoff.** Too much shielding causes perseveration: frontal patients keep applying an old rule on the Wisconsin Card Sort after it stops working. Too little causes distractibility and utilization behavior. The setting moves with context: a fire alarm always gets through.

**When shielding fails, humans and agents fail the same ways:**


| Human failure                                                   | Agent failure                                      |
| --------------------------------------------------------------- | -------------------------------------------------- |
| Utilization behavior (frontal patients use any object they see) | Prompt injection                                   |
| Goal neglect (Duncan): a known rule ignored as rules pile up    | Dropping one instruction among many                |
| Losing the goal over time (vigilance decrement)                 | Goal drift in long tasks                           |
| Habit capture                                                   | Repeating a learned pattern after the goal changed |
| Performing for approval                                         | Sycophancy                                         |


Frontal patients with utilization behavior (Lhermitte, 1983) pick up and use whatever is put in front of them, unprompted; text in the context taking over the goal looks like the same failure. Goal neglect shows that even intact shielding is fragile: healthy people can state a task rule yet fail to act on it, more often as the number of rules grows (Duncan et al., 1996), and LLMs likewise drop one instruction among many in a complex prompt. The first suggests LLMs lack a dedicated goal-shielding mechanism; the second, that even one would need support as task demands grow.

**Why transformers struggle: the missing prefrontal cortex.**

- **Everything is one flat stream.** Instructions, documents, tool outputs and the model's own thoughts are all tokens in the same context. There is no privileged goal register.
- **The goal is re-inferred at every token** from the whole context. Its influence is just attention weight, which dilutes as the context grows. That causes goal drift.
- **There is no gate.** Any text in the context can act as an instruction. That causes prompt injection.

The LLM is like Leonard in *Memento*: with no working memory, his goals live only in notes and tattoos he rereads constantly, and anyone who can write on his notes can redirect him. R4 maps the available fixes onto the brain mechanisms above.

**The difference at the top.**


|                      | Human                               | LLM agent                                |
| -------------------- | ----------------------------------- | ---------------------------------------- |
| Top of the hierarchy | Homeostatic needs (intrinsic)       | User instruction (external)              |
| Standing preferences | Temperament, values, learned priors | Training dispositions, system prompt     |
| Subgoal generation   | Learned, automatic, multi-timescale | Mostly explicit (to-do lists, scaffolds) |
| Goal shielding       | Prefrontal cortex                   | Weak: prompt injection, drift            |


Not having intrinsic needs at the top is arguably a feature: it keeps an agent's goals anchored to a person (R7). The open engineering problems are in the **middle of the stack**, learned subgoal hierarchies and robust goal shielding, and neither requires giving the agent needs of its own.

So interruptions are absorbed with **graceful degradation, not robustness**: recovery depends on how well the goal was maintained ([expected behaviors](#behaviors)).

**Back to the [observation](01_observations.md#observation).** Every case there "attends to relevant information and ignores irrelevant information." The shielded goal is what makes that possible. Relevance exists only relative to a goal: without a protected goal, nothing in the context has priority over anything else, which is the transformer's weakness. Humans cope with interruptions as well as they do not by attending to everything, but because a gate checks where each input came from and how salient it is, then decides whether it may **change the goal** or only **inform the next step**. That distinction is probably the most useful practical lesson for building agents.

**Feature F5: a shielded goal.** The goal lives in a protected register. Every input is tagged by source: a trusted source or a high-salience event may change the goal, and everything else may only inform the next step. The same gate lets the controller veto a habit that no longer fits. *Components:* working state W; source tags; goal gate; rule R4.

<a id="f6"></a>

## F6. Learning fast overwrites old knowledge → separate memories and consolidate

**Constraint.** A distributed network that learns new things quickly overwrites what it already knew (*catastrophic interference*, McCloskey & Cohen, 1989; the stability–plasticity dilemma). LLMs have the dilemma in its pure form: fine-tune naively on today's session and you damage what the model already knew. And the optimal agent needs a belief state but cannot afford to keep, or re-read, everything.

**Consequence.** Use **separate stores** that learn at different speeds, and **consolidate** selectively from fast to slow:


| Store        | Kind                  | Brain                     | Role                                       | Learns by                                     |
| ------------ | --------------------- | ------------------------- | ------------------------------------------ | --------------------------------------------- |
| Working W    | Active                | Prefrontal cortex         | Goal stack and belief; small and protected | Gated updates                                 |
| Episodic E   | Declarative           | Hippocampus               | One-shot events, cue-based recall          | One-shot logging                              |
| Semantic M   | Declarative           | Neocortex                 | Gist, world knowledge, invariants          | Consolidation into gist                       |
| Procedural P | Non-declarative       | Basal ganglia, cerebellum | Skills: the steps of the loop (F2)        | Practice, reward and error-driven compilation |
| Weights θ    | Substrate for M and P | Synapses                  | Long-term storage of knowledge and skill   | Slow distillation                             |


![One network learning fast overwrites old skills (catastrophic interference). The brain instead uses separate stores that learn at different speeds: working memory (seconds), episodic memory (one shot), and slow semantic and procedural stores, with consolidation in sleep keeping only what is tagged by reward, surprise or emotion. Transformer agents lack working memory and mostly lack consolidation.](../../assets/images/one-loop-i6-memory-stores.svg)

**Compress, or keep everything?** In a POMDP the optimal agent doesn't need the raw history, only the **belief state**: a summary sufficient to act optimally (formally, a probability distribution over hidden world states). "Later steps depend on previous steps" really means they depend on *a belief built from previous steps* (F1). There are two ways to approximate it:


|          | Compress (recurrent)                                  | Keep everything (attention)                                                |
| -------- | ----------------------------------------------------- | -------------------------------------------------------------------------- |
| Update   | bₜ = f(bₜ₋₁, oₜ), fixed size                          | Re-read the raw history every step                                         |
| Examples | Kalman filter, RNN/LSTM, SSMs (Mamba), working memory | Transformer context                                                        |
| Strength | Constant cost; forces abstraction                     | Lossless; can reinterpret the past later                                   |
| Weakness | Loses what you didn't know would matter               | Cost grows with length; attention dilutes (lost in the middle, goal drift) |


**Evidence: the brain does both, in separate systems.**

- **Working memory** holds about four chunks (Cowan), actively maintained by the prefrontal cortex. This is the compressed recurrent state.
- **Episodic memory** in the hippocampus is fast, one-shot storage retrieved by cue: content-addressable, like attention. The parallel is formal: modern Hopfield networks are mathematically equivalent to attention (Ramsauer et al., 2020), and transformers with suitable position encodings reproduce hippocampal place and grid cells (Whittington et al., 2022). That is not evidence that the brain computes softmax attention.
- **The neocortex** learns slowly and statistically, corresponding to weights.
- **Consolidation** links them: Complementary Learning Systems (McClelland, McNaughton & O'Reilly, 1995). The hippocampus learns fast with sparse, well-separated codes, so new memories interfere little with each other; the neocortex learns slowly with overlapping codes that generalize; replay lets the cortex learn new experience interleaved with old, so nothing is overwritten.

So the brain is a hybrid: a small, actively maintained state, a large associative store, slow weights, and a transfer process between them.

- **Memory is generative too.** Bartlett (1932) showed that recall is reconstruction, not replay: retrieval is generation conditioned on cues, which is why memories distort. Remembering runs on the same loop as the seven processes of the [observation](01_observations.md#observation), conditioned on a goal and cues. A transformer's context gives verbatim recall instead, which is more accurate but less abstract. **Evidence: what sleep actually does.**
- **Time-compressed replay.** During deep (NREM) sleep, hippocampal sharp-wave ripples replay the day's sequences about 10–20× faster than real time (Wilson & McNaughton, 1994). Ripples coordinate with cortical spindles and slow oscillations to move the information into cortex.
- **Reverse replay at reward sites.** Sequences are played backwards from where reward occurred (Foster & Wilson, 2006). That is credit assignment, much like TD learning propagating value backward.
- **Replay of paths never taken.** Rats replay routes they never ran (Gupta et al., 2010). This is generative replay: the revisable inner loop of F3, running offline.
- **Selection by tag.** Not everything is kept. Memories tagged by reward, emotion, surprise or expected future relevance are preferentially consolidated; people told they'd be tested later consolidate better (Wilhelm et al., 2011). Emotion is the tag, which ties consolidation to the controller of F4.
- **Downscaling.** The synaptic homeostasis hypothesis (Tononi & Cirelli) holds that sleep globally weakens synapses, pruning noise and keeping the strong. Forgetting is part of consolidation, not a failure of it.
- **Schema integration and gist.** New information that fits an existing schema consolidates in days rather than weeks (Tse et al., 2007). Over time episodes become semantic gist: details fade, structure remains. This is compression into abstraction again (MDL).
- **REM recombination.** REM sleep mixes memories in new combinations and processes their emotional charge. Hoel's (2021) overfitted brain hypothesis, which is speculative, says dreams are noisy augmentation that prevents overfitting to the day.
- **The wrong things get consolidated too.** False memories are consolidated like true ones (Loftus). The agent version is R6's persistent injection.

**Is the small working memory a bug or a feature?**

- **Bug:** transformers beat SSMs at copying and exact retrieval (Jelassi et al., 2024). Rereading the past exactly is powerful.
- **Feature:** compression forces abstraction. A four-item limit makes you chunk, build schemas and find structure. Newport's (1990) "less is more" hypothesis holds that children's limited memory helps them learn grammar. This links to MDL and grokking: generalization comes from compression.

**Effect on interruptions.** After an interruption, a human rebuilds state from compressed memory and cues ("where was I?"): costly and error-prone, but the goal survives if it was shielded in working memory. For a transformer, an interruption costs nothing while it stays in context, since every token is still there; the risk comes later, when compaction or dilution erodes the goal ([expected behaviors](#behaviors)).

**Evidence: replay as planning.** Remembering and imagining run on the same machinery.

- **Memory exists for the future.** Patients with hippocampal amnesia can't remember the past, and they also can't imagine new scenes in rich detail; their imagined experiences are fragmented (Hassabis et al., 2007). The constructive episodic simulation hypothesis (Schacter & Addis, 2007) explains why: memory is built to be recombined, and pieces of the past are reassembled to simulate possible futures. Remembering, imagining and planning are one generative process run on different inputs.
- **Theta sweeps: look-ahead at every step.** Within each ~125 ms theta cycle, place cells sweep ahead of the animal's current position. At a fork, consecutive cycles alternate between the possible futures, left, right, left (Kay et al., 2020). Even "on the fly" generation (Observation section, point 1) contains a built-in micro-look-ahead, about eight times a second.
- **Vicarious trial and error.** Rats pause at choice points and swing their heads while hippocampal sequences run down each arm in turn (Johnson & Redish, 2007): deliberation as a visible mini-search.
- **Replay predicts the path.** Before moving, awake replay traces the route the rat is about to take to a remembered goal (Pfeiffer & Foster, 2013). The replay works as the plan.
- **Humans too.** MEG studies detect fast sequential replay in humans, including replay of abstract structure, not just places (Liu, Dolan, Kurth-Nelson & Behrens, 2019).
- **What gets replayed is optimized.** Mattar & Daw (2018) proposed that the brain replays the memory with the highest *gain × need*: how much replaying it would improve decisions, times how likely that state is to matter soon. The theory correctly predicts forward replay before decisions (planning) and reverse replay after reward (credit assignment). This is F4's "is another thought worth it?" rule applied to *which memory to think about*: the controller decides not only whether to think, but what to simulate.
- **Habits vs planning: amortization.** Model-based planning is flexible but slow; model-free habit is fast but rigid. The brain arbitrates between them by which is more reliable at the moment (Daw, Niv & Dayan, 2005), which is the System 1 / System 2 controller of F4 again. Practice converts planning into habit: repeated simulation is cached into fast responses (F2). This is exactly Dyna, which uses simulated experience to train the fast policy. The LLM version distills chain-of-thought into direct answers, so what once required reasoning becomes intuition. Sleep replay is the brain's distillation step.


AI counterparts:


| Brain                                   | AI                                                                                                                     |
| --------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| Replay trains habits from a model       | Dyna (Sutton, 1990)                                                                                                    |
| Simulating futures in a learned model   | World models (Ha & Schmidhuber, 2018: "learning inside the dream"); Dreamer (a policy trained entirely in imagination) |
| Look-ahead at choice points             | MuZero: a learned model plus tree search, without being given the rules                                                |
| Theta-sweep alternation between options | Sampling several candidate continuations; tree-of-thought                                                              |
| Verbal simulation of outcomes           | LLM-as-world-model planning (e.g., RAP, 2023); reasoning tokens                                                        |
| Planning → intuition                    | Distilling reasoning traces into direct-answer models                                                                  |


A caveat: the hippocampus-as-planner evidence is strongest for spatial navigation in rodents. For abstract human planning it is growing but contested, and the prefrontal cortex clearly plays a large role too.

**One generative model, four uses.**


| Applied to           | It is called                                  |
| -------------------- | --------------------------------------------- |
| The past             | Remembering (reconstruction)                  |
| The present          | Perceiving (prediction plus saccade sampling) |
| The future           | Planning (simulation, theta sweeps, replay)   |
| Oneself in the world | Acting (predictions made true)                |


Offline, the same model produces the replay that trains the fast habit system. This is the deepest version of the observation: the seven processes don't just resemble transformer generation; they may be **one step-by-step generative model of the world, pointed at different times and targets**. Transformers already are such generative models. What they mostly lack is not the generator but the **orchestration**:

- when to simulate instead of act;
- what to replay;
- when to cache simulation into habit;
- how to do all of it continuously across sessions.

**What transformer agents have.**


| Brain                                        | Transformer agent                                                                         |
| -------------------------------------------- | ----------------------------------------------------------------------------------------- |
| Working memory (small, maintained, shielded) | ✗: the context does double duty                                                           |
| Episodic store (cue-based retrieval)         | Context window + retrieval (RAG)                                                          |
| Slow weights                                 | Weights                                                                                   |
| Consolidation (sleep replay)                 | ✗ mostly: context is lost at session end; crude stand-ins are compaction and memory files |


Agents are reinventing Complementary Learning Systems one piece at a time:

- **Compaction** (summarizing old context) acts as compression into a working state.
- **Retrieval** acts as episodic recall.
- **Memory files** act as primitive consolidation.
- **Continual learning into weights** is the missing last step. Early parametric-memory systems in 2026 consolidate sessions into adapters, but forgetting is not solved ([state of the field](04_implementation_plan.md#field-2026)).

On the architecture side, hybrid SSM + attention models (Jamba, Samba) suggest the field is converging on the brain's split. AI has also borrowed pieces of sleep itself:


| Brain                         | AI counterpart                                                                                                  |
| ----------------------------- | --------------------------------------------------------------------------------------------------------------- |
| Hippocampal replay            | Experience replay in DQN (explicitly inspired by it)                                                            |
| Salience-tagged consolidation | Prioritized replay                                                                                              |
| Generative replay             | Generative replay for continual learning (Shin et al., 2017): regenerate old data to interleave with new        |
| Protecting important synapses | EWC (Kirkpatrick et al., 2017): penalize changes to weights that matter for old tasks                           |
| Offline simulation            | Dyna (Sutton, 1990): learn from model-simulated experience between real steps                                   |
| Episodes → gist               | Reflection in Generative Agents (Park et al., 2023): periodically summarize memories into higher-level insights |
| Offline pre-thinking          | Sleep-time compute (2025): process context while idle to pre-compute what future queries will need              |
| Moving into weights           | Context distillation; LoRA updates on session data                                                              |

**Consolidating by rewriting has its own failure mode.** When a model maintains its memory by rewriting it after each episode, the memory degrades in two ways: entries drift toward short, generic advice (*brevity bias*), and one rewrite can drop most of the accumulated detail at once (*context collapse*). ACE (Zhang et al., 2025) avoids both by treating memory as a playbook of itemized entries: one role generates trajectories, a second reflects on them to extract lessons, and a third curates them into small changes to single entries, merged by fixed rules. Brains do something similar: schema integration adds to existing structure instead of rebuilding it (Tse et al., above). The [sleep cycle](03_system_design.md#sleep-cycle) follows this, applying lessons as itemized changes.


**Learning from one example.** Everything above is about *keeping* what was learned. The harder question is how one example can teach anything general at all.

- **Humans do it routinely.** A child learns a new word from a single use (*fast mapping*, Carey & Bartlett, 1978). Adults can recognize and draw a new handwritten character after seeing it once, where standard neural networks needed thousands of examples (Lake, Salakhutdinov & Tenenbaum, 2015).
- **The prior does most of the work.** One example can't define a concept; it can only *choose* among hypotheses the learner already favors. Children assume a new word names a whole object and extend it by shape (the shape bias, Landau, Smith & Jones, 1988). Bayesian models of word learning show how a few examples rapidly narrow a hypothesis space the learner already has (Xu & Tenenbaum, 2007). Characters are learned from one example because they are parsed into strokes the learner already knows how to compose. Analogy does the same at a higher level: map the new case onto a familiar structure (Gentner, 1983).
- **Transformers do it in context.** Put one or a few examples in the prompt and the model generalizes from them with no weight change (Brown et al., 2020). This is the same mechanism as goal-conditioning and interruption: the example enters the context, and the next step is conditioned on it. Pretraining builds the prior; the context selects from it. In-context learning behaves like implicit Bayesian inference (Xie et al., 2022), can implement gradient-descent-like updates inside the forward pass (von Oswald et al., 2023), and relies on circuits such as induction heads that copy patterns from earlier in the context (Olsson et al., 2022).


So one-shot learning splits across the two speeds of this section:

1. **Fast: use the example now.** Hold it in the fast store (hippocampus; the context window) and generalize by attending to it. This works only as far as the prior already contains the right hypotheses.
2. **Slow: decide whether to keep it.** What an LLM learns in context disappears at the end of the session unless it is consolidated. Humans keep one-shot learning when it fits an existing schema, which is also when consolidation is fastest (Tse et al., 2007, above).

Where the two differ:

- **Humans learn from explanations, not just examples.** People ask *why* the example works and generalize the reason, not the surface (explanation-based learning). In-context learning often keys on surface format: models can still do well when the labels in the examples are randomized (Min et al., 2022), and results shift with example order ([expected behaviors](#behaviors)).
- **Humans tag single events for keeping.** A surprising, rewarded or emotional one-off is stored and consolidated preferentially (selection by tag, above). LLMs weigh every token in context alike and have no mechanism for marking one example as worth keeping.
- **A correction is the most valuable one-shot lesson** (F7). But one example is also the easiest way to learn the wrong lesson: a single misleading case, or an injected one, generalizes just as readily.

For an agent this suggests a pipeline: log the example verbatim in E; extract the rule it implies as an explicit *hypothesis*; check that hypothesis on the next cases where it applies; and let it through the consolidation gate (R6) into M or P only once it has held up. One example is enough to *act* on, and the inner loop can test it cheaply; it is rarely enough to *keep*.

**The design this implies** is the brain's memory system, with procedural memory kept separate from world knowledge:

1. a **small, protected working state** holding the goal and current belief, which is where the goal register of F5 belongs;
2. a **large associative store** read through attention or retrieval;
3. **slow semantic knowledge** of the world;
4. a **procedural store** of compiled skills, the steps of the loop (F2);
5. **consolidation** that moves what was learned during a session into lasting form, turning experience into knowledge and deliberation into skill.

Transformers have 2 and 3, and a huge built-in version of 4; agent scaffolding fakes 1, 5 and the acquisition of new skills. Getting these natively into the architecture would likely close the remaining gaps: goal drift, overthinking, and not learning from experience.

**The loop runs at three timescales**, each with its own form of backtracking:


| Timescale       | Loop                                          | Backtracking form                                      |
| --------------- | --------------------------------------------- | ------------------------------------------------------ |
| ms–seconds      | Committing steps (outer loop)                 | Repair ("I mean…")                                     |
| Seconds–minutes | Deliberation (inner loop)                     | Search; revising the draft                             |
| Hours–days      | Consolidation (offline loop over a whole day) | Reverse replay: credit assignment back through the day |


Sleep is the revisable inner loop applied to a whole day of experience. Today's agents mostly lack it, which is why they act within a session but don't learn across sessions. Memory tools and skill libraries are partial versions of it as of 2026.

**Feature F6: separate memories, joined by consolidation.** A small protected working state, an episodic log, slow semantic knowledge and a procedural store, linked by a between-session sleep cycle that consolidates only trusted, verified experience into memory, skills and weights. *Components:* W, E, M, P, θ; the [sleep cycle](03_system_design.md#sleep-cycle); rule R6.

<a id="f7"></a>

## F7. Learning signal lives at the edge of competence → development has an order

**Constraints.**

- Practice teaches nothing when a task always succeeds or always fails.
- Some capabilities can only be built on top of others.

**Consequences.**

- Learning happens in the **zone of proximal development** (ZPD): where success is possible but unreliable, under support that fades. In group-relative RL methods such as GRPO, problems that are always or never solved produce zero gradient, so this is the ZPD stated mathematically.
- Capabilities form a **dependency order**: forward models before planning, planning before verification, a shielded goal before safe autonomy. Piaget's stages, below, are one human realization of these dependencies, not a necessary order (see [risks](04_implementation_plan.md#risks)).

![Learning signal is zero when a task always fails or always succeeds and peaks in the zone of proximal development; scaffolding pulls a too-hard task into the zone and fades as competence grows. Capabilities build in order, from forward models to planning, verification, and hypotheses with metareasoning; learning happens one step above what is mastered.](../../assets/images/one-loop-i7-edge-of-competence.svg)

**Evidence.**

- **Piaget gives the mechanism** (Piaget & Inhelder, *The Psychology of the Child*, 1969).
  - Thought is internalized action: operations are actions carried out in the head.
  - Schemes are *assimilated* (applied) and *accommodated* (revised) under **equilibration**, a self-regulation driven by disequilibrium that is close to prediction-error minimization.
  - Development runs from sensorimotor, through semiotic and concrete operations, to formal operations. Each stage builds on and integrates the structures of the previous one, which gives the **dependency order** the rest of the design lacked: so far it described a mature agent.
  - **Four drivers of development:** maturation, experience with objects, social transmission, and equilibration, which Piaget considered the most fundamental. For an agent: architecture capacity, interaction with the environment, human teaching and data, and intrinsic self-regulation.
  - **Two kinds of experience:** *physical* (learning about objects) and *logico-mathematical* (learning about the coordination of one's own actions). The second is what self-reflection and self-play give an agent.

**Piaget already runs through the framework.** Most of his concepts have a counterpart in the earlier sections:


| Piaget                                                                                                        | Where it appears in the design                                                                              |
| ------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| Thought is internalized action                                                                                | The inner loop is the outer action loop moved inside (F3); Piaget says this is how the inner loop develops |
| Schemes: repeatable, generalizable action patterns                                                            | Procedural memory: skills with triggers (F2)                                                               |
| Assimilation: apply an existing scheme to a new situation                                                     | The fast path: running a habit or skill                                                                     |
| Accommodation: modify the scheme when it doesn't fit                                                          | Decompile → relearn → recompile (R5)                                                                        |
| Equilibration: self-regulation triggered by disequilibrium                                                    | The controller: surprise reopens the loop, satisfaction ends it (F4); also active inference                |
| Circular reactions: repeat an action to reproduce its effect                                                  | Practice → skill compilation; learning forward models                                                       |
| Tertiary circular reactions: vary actions to see what changes                                                 | Curiosity / information gain                                                                                |
| Coordination of schemes (8–12 months): one scheme as the means to another's goal; intentionality appears      | TOTE hierarchy and chunking; the goal stack                                                                 |
| Invention through mental combination (~18 months): solving problems in the head instead of by trial and error | The inner loop; Craik's small-scale model; replay as planning                                               |
| Object permanence                                                                                             | The belief state: representing what is no longer perceived (F1)                                            |
| Memory improves as schemes develop                                                                            | Reconstructive memory: recall is regenerated using current schemas (F6)                                    |
| Perceptual activity: exploring, centering, comparing, maturing with age                                       | Saccades as active, skilled sampling                                                                        |
| Affect as the energetics of behavior, cognition as its structure                                              | Emotion as controller (F4)                                                                                 |
| Reflective abstraction: abstracting structure from one's own actions                                          | Consolidation into gist; compression → abstraction (F6)                                                    |
| Horizontal décalage: the same structure mastered in different domains at different times                      | LLMs' uneven ("jagged") competence                                                                          |


**What Piaget adds.**

- **Reversibility and conservation**, the biggest addition. Mature thinking requires operations that have inverses (pour the water back) and that preserve invariants (the amount stays the same). This makes F3 precise: the inner loop is the domain of reversible operations, the outer loop the domain of irreversible actions. Mental reversibility makes backtracking free and allows verification by inversion.
- **The semiotic function.** Symbols, language, mental images, deferred imitation and pretend play give the inner loop a medium for representing absent things. Pretend play is safe simulation; deferred imitation is learning from a demonstration seen earlier.
- **Decentration.** Young children are *centered*, fixating on one salient dimension, and *egocentric*, unable to take another's perspective. Development is decentration. This adds perspective-taking and theory of mind, and puts source tagging (self vs other, F5) on a developmental footing. LLMs anchoring on surface features is a form of centration.
- **Formal operations.** Hypothetico-deductive reasoning over possibilities, not just what is actual, plus thinking about one's own thinking. This is the mature form of the inner loop: systematic hypothesis search and metareasoning.
- **Caveats.** Infants show some competences earlier than Piaget thought (Baillargeon; Spelke's core knowledge), stages are less uniform than he claimed (décalage), and social and cultural learning matter more than he allowed (Vygotsky). Read the stages as a dependency order of capabilities, not fixed ages; core-knowledge priors can be built in at stage 0.

**Vygotsky gives the social source.** Piaget explains how the agent constructs its structures from its own action. Vygotsky explains where much of the content, the tools and the pace come from: other people.

- **Every higher function appears twice:** first between people, then inside the child. Attention, memory, planning and self-control all start as regulation by others and become self-regulation.
- **Mediation by tools and signs.** Language, numbers, writing, maps and mnemonics are psychological tools that transform the mental function itself: memory with a written note is a different function from memory without one.
- **Zone of proximal development:** the gap between what a learner can do alone and what they can do with help. Learning happens in that gap.
- **Scaffolding** (Wood, Bruner & Ross, 1976): support adapted to the learner's level and faded as competence grows.
- **From social speech to inner speech:** social speech → private speech (talking aloud to oneself) → inner speech (silent, abbreviated, condensed). Private speech increases with task difficulty.
- **Everyday vs scientific concepts.** Everyday concepts grow upward from experience; scientific concepts are systematic and grow downward from instruction. Development is where they meet.
- **Play creates its own ZPD:** in play, a child is "a head taller than himself."
- **Later work** extends this: shared intentionality and the cultural ratchet (Tomasello), legitimate peripheral participation (Lave & Wenger), and reasoning as evolved for argument (Mercier & Sperber).


**Vygotsky already runs through the framework:**


| Vygotsky                                                                                        | Where it appears in the design                                                                                                                                            |
| ----------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Private speech grows with difficulty, then goes underground                                     | Chain-of-thought: reasoning models think longer on harder problems. Distilling reasoning into direct answers, or latent "continuous thought," is speech going underground |
| Piaget vs Vygotsky on "egocentric speech": a symptom of egocentrism, or a self-regulation tool? | The same debate about whether chain-of-thought is real reasoning or decoration. The evidence favors Vygotsky: it regulates the process                                    |
| Functions move from social to individual                                                        | Thought as internalized action (F3), but the source is dialogue: the inner loop is partly internalized argument, as in self-critique and multi-agent debate              |
| Other-regulation → self-regulation                                                              | The controller and goals start external: a parent's instruction, a user's goal. Self-regulation grows within those goals (F5)                                            |
| Psychological tools                                                                             | External memory and scaffolding: notes, scratchpads, memory files, tools. Writing as an external context window ([expected behaviors](#behaviors))                                                     |
| Culture passes on compiled procedures (long division, reading)                                  | Procedural memory transmitted, not discovered: the cultural ratchet (F2)                                                                                                 |
| Imitation works only within the ZPD                                                             | Piaget's deferred imitation, plus a limit on what can be imitated                                                                                                         |


**What Vygotsky adds.**

- **The ZPD is a formal training principle.** In group-relative RL methods such as GRPO, problems the model always or never solves give zero learning signal; only intermediate pass rates produce gradient. Oudeyer's learning-progress curiosity is an agent choosing its own ZPD.
- **A ZPD can be generated, within limits.** Autodata (Kulikov et al., 2026) has a challenger write problems that a strong solver passes and a weak solver fails, which places them in the weak solver's ZPD by construction. The weak solver improves; the strong one does not, so this is closer to distillation than to self-improvement. Self-generated curricula raise a learner toward its teacher, not past it; past that point the signal must come from verifiers and the world.
- **Scaffolding fades.** Hints, partial plans, demonstrations, restricted tool sets and human approvals are support, and should fade as reliability grows. This ties directly to the reliability record of each skill in P (R5).
- **Scientific concepts meet everyday ones.** LLMs have the scientific concepts (systematic, verbal, from reading) without the everyday ones (grounded in their own action). Pretraining supplied the downward growth; Piaget's back-fill ([build stages](04_implementation_plan.md#build-stages)) is the upward growth; grounding is where they meet.
- **Shared intentionality** (Tomasello): joint attention, common ground, we-goals, teaching by pointing. For agents: track what both parties are attending to (the open file, the selected code), maintain common ground (what has been agreed), and plan *with* the user, not just for them. This requires the decentration and theory of mind of the Piaget stages.
- **Legitimate peripheral participation.** Newcomers start with low-risk peripheral tasks and earn responsibility. For agents, autonomy expands along the reversibility ladder ([build stages](04_implementation_plan.md#build-stages)), and scaffolding fades class by class.
- **A teacher's corrections are privileged signals.** A user's correction is the most valuable kind of interruption: it gets top trust at the goal gate (R4), top salience at the consolidation gate (R6), and becomes a lesson.

**Piaget and Vygotsky together:**


|                   | Piaget                                        | Vygotsky                                             |
| ----------------- | --------------------------------------------- | ---------------------------------------------------- |
| Learner as        | Scientist                                     | Apprentice                                           |
| Engine            | Action + equilibration                        | Social interaction + tools                           |
| Explains          | How structure is built                        | Where content, tools and pace come from              |
| Direction         | Development enables learning                  | Learning leads development                           |
| Agent counterpart | Self-practice, experimentation, consolidation | Demonstrations, feedback, curricula, cultural priors |


An agent needs both: self-construction for grounding and structure, social scaffolding for content and speed.

**Learning by watching: imitation.** Piaget and Vygotsky both mention imitation in passing, but it may be the main channel through which humans and LLMs acquire their content.

- **Pretraining is imitation.** Next-token prediction on human text is behavior cloning on the written record of human sequential behavior: speech, argument, worked solutions, thinking set down on paper. The generator of this design was learned largely by imitating people. This matters for the design: if LLMs learned by copying humans, their resemblance to humans is the expected outcome, and the design can't assume the loop will carry over unchanged to domains with little human data ([risks](04_implementation_plan.md#risks)).
- **Good imitation copies the goal, not the movements.** Eighteen-month-olds who watch an adult *fail* to pull a toy apart still pull it apart: they reproduce the intended act, not the observed one (Meltzoff, 1995). Infants who see an adult switch on a light with her forehead copy the odd action when her hands were free, but use their hands when hers were wrapped in a blanket: they infer *why* she did it that way (rational imitation, Gergely, Bekkering & Király, 2002). Imitation is goal inference followed by one's own steps toward the goal, which ties it to the goal machinery of F5.
- **Faithful copying has a price.** When a causal mechanism is hidden, children copy even the demonstrator's useless steps, which chimpanzees skip (overimitation, Horner & Whiten, 2005). High-fidelity copying of steps one doesn't understand is what lets cultures pass on procedures nobody could reinvent (the cultural ratchet, Tomasello), and it is also how quirks and errors get passed along. LLMs show both sides: they inherit compiled human procedures, and also human filler, biases and mistakes.
- **Imitation alone compounds errors.** A cloned policy has seen only the states the expert visited. One mistake takes it somewhere the demonstrations never went, and errors grow with the length of the task (Ross, Gordon & Bagnell, 2011). This is the exposure bias of [expected behaviors](#behaviors) and R2. The fix is to close the loop: DAgger has the expert label the states the *learner* actually reaches, and RL on a model's own outputs (RLHF, verifiable rewards) trains on its own trajectories. Humans learn the same way: watch a demonstration, then practice while a coach corrects your attempts, not the coach's. Imitation supplies the prior, and feedback on one's own steps repairs it.
- **Imitation is bounded by the ZPD.** You can imitate only what you can almost do already (Vygotsky). A few-shot prompt is imitation in the fast store: the demonstration sits in context and the model follows it (F6, learning from one example).

The human forms of imitation each have a machine counterpart:


| Human                                              | Machine                                                                      |
| -------------------------------------------------- | ---------------------------------------------------------------------------- |
| Copy the movements (mimicry)                       | Behavior cloning; next-token pretraining                                     |
| Copy the outcome by any means (emulation)          | Goal-conditioned imitation; hindsight relabeling (Andrychowicz et al., 2017) |
| Infer the intention, then act (rational imitation) | Inverse RL (Ng & Russell, 2000); apprenticeship learning (Abbeel & Ng, 2004) |
| Copy steps whose purpose is opaque (overimitation) | Inheriting human quirks, biases and errors from training data                |
| Practice while a coach corrects your own attempts  | DAgger; RL on the model's own outputs                                        |


For an agent:

1. **Treat a demonstration as evidence about a goal.** Infer what the demonstrator was trying to achieve, then plan toward it; copy the exact steps only where the agent can't yet tell which ones matter.
2. **Follow imitation with corrected practice.** Let the agent attempt the task and have the user fix *its* attempts. Corrections on states the agent actually reaches are worth more than further demonstrations.
3. **Keep only what holds up.** A demonstrated procedure enters P as a skill through the consolidation gate (R6), like any other lesson, once the agent's own runs confirm it.

**Feature F7: learning at the edge of competence.** Practice tasks are chosen where success is possible but unreliable, support fades as reliability grows, capabilities are built in dependency order, demonstrations are treated as evidence about goals, and autonomy expands along the reversibility ladder. *Components:* curriculum selector; teacher channel; social interface; rule R8; the [build stages](04_implementation_plan.md#build-stages).

<a id="behaviors"></a>

## Behaviors the design should expect

If humans and transformers both compute **next step = f(goal, everything so far)**, effects known in one show up in the other, and the agent should expect them in itself. Several are well documented on both sides:


| Behavior                                           | Humans                                                                                                    | Transformers                                                                        |
| -------------------------------------------------- | --------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| What's earlier in context biases what comes next   | Order and priming effects: anchoring, framing                                                             | Prompt-order and example-order effects                                              |
| Writing steps down improves reasoning              | Thinking aloud or on paper gives an external context window beyond ~4 working-memory items                | Chain-of-thought                                                                    |
| Errors compound                                    | Garden-path sentences; getting lost after one wrong turn                                                  | Exposure bias; a wrong early step keeps priming later ones (R2)                     |
| Interruption recovery depends on surviving context | "Where was I?": resumption lags and switching costs (Altmann & Trafton) scale with goal maintenance (F5) | Full recovery while the context is intact; drift once it is truncated or summarized |


Writing steps down is also Vygotsky's private speech (F7): the external context window comes first, and its compression into inner speech comes later.

Each row is a design input. Priming argues for clean, source-tagged contexts (F5); the benefit of writing steps down argues for scratch space and memory files (F3, F6); compounding errors argue for forkable inner loops that discard wrong branches (R2); and recovery after interruption argues for a protected goal register (F5).

References are collected in [References](references.md).
