![One Loop icon: a goal at the center, a dashed reversible inner loop, and a solid outer loop of committed steps, one of which is itself a loop](../assets/images/one-loop-icon.svg)

# One Loop: Perception, Reasoning, Action, Language and Transformers

*The goal sits at the center. The dashed inner loop is reversible simulation and search; the solid outer loop is irreversible, committed steps. One step is drawn as a loop of its own, because every step is a lower-level loop.*

> At the level where behavior is committed step by step, perception, reasoning, planning, action and language share one functional structure: **a hierarchy of goal-conditioned control loops whose steps are compiled procedures**, chunked upward through practice. Each loop places a **reversible inner loop** (simulation, search, drafting) before **irreversible commitments**, and must solve a **stopping problem** using progress, uncertainty and surprise signals. Interruptions are absorbed to the extent that a **shielded goal** separates what informs the next step from what may change the goal. Experience becomes knowledge, and deliberation becomes skill, through **selective consolidation**; learning is most effective at the **edge of competence** under fading support. Transformers implement the generator and much of the procedural substrate well; whether they need the remaining functions as explicit modules, or will acquire them with scale, is an empirical question.

This draft looks at that thesis from two directions:

- **Part I: first principles.** Start from constraints that any agent faces, and derive what its structure must look like. Humans and transformers serve as evidence, not as premises.
- **Part II: the builder's perspective.** Turn each principle into a component, a design rule, a build order and a test that could prove it unnecessary.

## 0. The observation

Many human processes seem to share a structure with transformer next-token generation:

1. **Perception** starts with a goal. The eyes saccade in a sequence. Each saccade is not planned in advance; it depends on the previous ones. The sequence stops when perception concludes or is interrupted.
2. **Reasoning** starts with a goal and runs a flow of thoughts, with or without backtracking. Each thought depends on the previous ones. It stops at a conclusion or an interruption.
3. **Planning** works the same way: a flow of planning steps, with or without backtracking.
4. **Execution and navigation** may be guided by a plan or a map, but still proceed through small decisions that refer to previous steps.
5. **Physical action** starts from a rough idea, not an exact sequence of moves. Each sub-action depends on the previous ones.
6. **Talking and writing**: we don't know our later words at the start; they are generated on the fly from what came before.
7. **Transformers** generate a sequence of tokens, each depending on the previous ones, for text, speech, audio, video and actions. They stop at a conclusion and can be interrupted by new information injected into the context.

All of these have goals, run sequentially with or without backtracking, end in a conclusion or an interruption, and handle interruptions and off-track events by attending to relevant information and ignoring irrelevant information.

All seven processes can be written as a policy: **next step = f(goal, everything so far)**. This is what a transformer computes. It's also how agents work in reinforcement learning, and how predictive processing describes the brain.

Handling interruptions is the most interesting part. In a transformer, being interrupted just means new tokens enter the context and the next step adapts. Human action works the same way: a sensory surprise changes the next step without throwing away the whole plan.

**Scope.** The thesis is about the **serial control level** of behavior: the level at which an agent commits outputs one after another (gaze shifts, words, moves, decisions, actions) in pursuit of something. That level runs on top of parallel, continuous machinery it does not describe: fast feed-forward recognition, motor dynamics, background monitoring. It is a **functional** claim, not a claim that brains and transformers share a mechanism.

**Definitions.**

- **Step**: a committed output at a given level of the hierarchy.
- **Not planned beforehand**: the full sequence is not *explicitly represented* in advance. The internal state can still carry *implicit look-ahead*: speech errors show that later words are already active; hippocampal "theta sweeps" alternate between possible futures about eight times a second (I.6); LLMs choose a rhyme before writing the line.
- **Goal**: whatever conditions the sequence toward an end state. It may be set from above, triggered by the environment, driven by needs or curiosity, or **reconstructed after the fact**.

**Where the analogy needs care.**

- **Part of the similarity is automatic.** Any sequence can be factored as p(x₁…xₙ) = ∏ p(xₜ | x₍<ₜ₎), so "each step depends on the previous steps" is true of every sequential process. The real, testable claim is about mechanism: one general next-step predictor, plus attention over history, is enough for perception, reasoning, planning, action and speech.
- **"Later steps are not planned beforehand" is only partly true**, for humans and for transformers.
  - Lashley's *The Problem of Serial Order in Behavior* (1951) argued that behavior can't be pure chaining.
  - Speech errors show that people already hold later words in mind before saying them. Anticipation slips ("a leading list" for "a reading list") and spoonerisms are the evidence.
  - The next saccade target is computed during the current fixation.
  - Interpretability research found that LLMs pick a rhyme word before writing the line that ends in it.

  A better phrasing: the next step is generated on the fly, but the internal state already contains an implicit look-ahead.
- **Backtracking means different things in different cases.** Neither speech nor a transformer can erase what it has produced; both "backtrack" by appending a repair ("uh, I mean…", or "Wait, …" in reasoning models). Writing with editing, and mental backtracking in reasoning, really can revise earlier output. That is closer to search, or to diffusion-style refinement, than to pure autoregression. Which one appears depends on reversibility (I.3).
- **Memory architecture differs.** Human working memory holds about four items. People compress history into a running state and rely on external memory (notes, maps). That is closer to an RNN or state-space model than to a transformer that can attend back to its whole raw context.

**What humans have that a plain transformer doesn't.**

- **Learning while acting.** A human's "weights" change during the task. A transformer's weights are frozen at inference, so anything it learns mid-task has to live in its context (I.6).
- **Grounded, closed-loop feedback.** Humans get a continuous sensory stream. A model gets feedback only when something is injected into its context, such as a tool result or a user message.
- **Felt salience.** Emotion and body state decide what is relevant and when to stop. Goals persist as motivation and body state (Damasio), and stopping is a felt sense of satisfaction or "done." In a transformer, the goal is just conditioning text and stopping is an end-of-sequence token (I.4).
- **Offline simulation.** Humans can mentally rehearse a plan before acting. Reasoning models approximate this with hidden thinking tokens (I.3).
- **Hierarchy across timescales.** Humans nest goals → subgoals → actions → micro-movements, each running on its own timescale. A transformer is flat and has to learn any hierarchy implicitly (I.2).

Part I takes each of these differences as a constraint to explain, not a reason to drop the analogy.

---

# Part I: First principles

Each principle has the same shape: **a constraint** that any agent acting in the world faces, **the consequence** that follows from it, and **evidence** from humans and machines that the consequence holds.

A caution first. Any sequence factors as p(x₁…xₙ) = ∏ p(xₜ | x₍<ₜ₎), so "each step depends on previous steps" is true of everything. The derivations below are interesting only to the extent that they predict *specific* structure beyond that.

## I.1 Too many futures → commit one step at a time, with feedback

**Constraints.**

- **Too many possible sequences.** With b options per step and n steps there are bⁿ complete sequences; they can't all be searched. Committing one step at a time turns that into n choices of size b. The chain-rule factorization is the only affordable way to produce long sequences.
- **The world is noisy and changes while you act**, so a fully precomputed open-loop plan goes stale. Control theory shows that closed-loop feedback beats open-loop planning under noise.
- **The world is only partly observable**, and acting is often the only way to find out more.
- **Memory and compute are limited**, so the full history can't be kept and reprocessed at every step.
- **Committed outputs come out one at a time.** There is one mouth, one gaze and one body position. Even if thinking runs in parallel, what gets committed must be serialized.

**Consequence.** Commit one step, observe, and generate the next step from an updated **belief state**: a summary of history sufficient for acting well. Under partial observability (formally a POMDP), the optimal action depends on exactly such a belief state, so "the next step depends on previous steps" isn't a quirk; it is mathematically required. More precisely, the next step *depends on a belief built from previous steps*. Brains compress history into a running state; transformers keep the raw history and attend to it. These are two approximations of the same belief state (I.6). A plan or map can still guide the loop, but as a prior, not as a script.

**Why the seven processes look alike.** The problem forces it. Step-by-step generation that conditions on history and absorbs interruptions is what any capable agent with limited compute, an unpredictable world and a goal ends up doing; it can't plan the whole sequence in advance, because too much would change before it finished. Brains and transformers may both have arrived at this loop because it is the only tractable solution, not by coincidence and not because they share a mechanism. The observation in section 0 is then a claim about the structure of sequential decision-making under uncertainty, not just a similarity between brains and AI. The strongest counter-argument, that LLMs inherited the structure from human text, is weighed in I.9.

**Evidence.**

- **Humans.** Saccades are information-gathering actions: each one is taken to gather information for the next decision. Under predictive processing, perception is active sampling to reduce prediction error, so a saccade sequence is generation too, and perception sits fully inside the loop rather than only feeding it. Motor control is closed-loop, and Todorov's optimal feedback control goes further: the motor system corrects only deviations that matter for the task and lets the rest go (the *minimal intervention principle*). That is section 0's "attend to relevant information, ignore irrelevant information," stated formally. Speech is produced incrementally, with implicit look-ahead.
- **Machines.** Engineered systems arrive independently at the same loop. Model predictive control plans over a short horizon, executes only the first step, observes and replans; this is how navigation (point 4 of section 0) can follow a plan or map and still decide on the fly. AlphaZero searches ahead, commits one move and searches again. Transformers generate token by token, and an injected interruption simply becomes part of the next step's conditioning.
- **Biology without brains.** Bacterial chemotaxis runs the same run–sense–adjust cycle.

## I.2 Limited compute and memory → compile steps into procedures, and stack them

**Constraints.** Working memory holds about four chunks. Deliberation is slow and costly.

**Consequence.** Steps that recur must be **compiled** into procedures that run without deliberation, and a sequence at one level must be **chunked** into a single step for the level above. The result is a hierarchy of loops, each on its own timescale.

The loop itself is a **TOTE unit** (Miller, Galanter & Pribram, 1960): *Test* the state against the goal, *Operate*, *Test* again, *Exit* when they match. This is section 0's "sequence of steps that stops at a conclusion," described in 1960. Their main further claim was that TOTE units **nest**: hammering a nail is (lift hammer → strike), repeated until the nail is flush. So the seven processes of section 0 are better seen as **levels of one hierarchy** than as parallel processes, where each level's step becomes the goal of the level below:

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

- **Definition.** Knowing *how* rather than knowing *that* (Ryle, 1949): skills, habits, motor programs, cognitive routines (reading, arithmetic, grammar) and perceptual skills, including expert saccade strategies. It is acquired by practice, hard to put into words ("we know more than we can tell": Polanyi), and very durable.
- **A separate system.** The amnesic patient H.M. improved at mirror drawing over days with no memory of ever practicing it (Milner, 1962). In Squire's taxonomy, *declarative* memory is episodic plus semantic, and *non-declarative* memory is procedural, priming and conditioning. Semantic and procedural memory learn differently and belong in separate stores (I.6).
- **Formation.**
  - The **basal ganglia** learn which action fits which context, by reinforcement through dopamine prediction errors. With practice, control shifts from the goal-directed dorsomedial striatum to the habitual dorsolateral striatum (Yin & Knowlton, 2006).
  - The **cerebellum** learns **forward models** that predict an action's sensory consequences, along with fine timing and error-driven correction.
  - Skills move through stages (Fitts & Posner): **cognitive** (following explicit instructions; slow, effortful) → **associative** → **autonomous** (fast, parallel, no attention needed).
  - Declarative steps are **compiled** into single procedures (Anderson's ACT-R; Newell & Rosenbloom's chunking), and performance speeds up along the power law of practice.

**Why procedural memory is central to the thesis.**

- **It supplies the steps.** Every step in the seven processes is itself a procedure: a saccade program, the articulation of a word, a grasp, a familiar inference move, a turn on a known route. The loop composes procedures. Without them each step would need deliberation, and the combinatorial problem of I.1 would come back at full force.
- **It makes the hierarchy possible.** Chunking turns a sequence at one level into a single step at the level above: letters → words → phrases; reach + grasp + lift → "pick up the cup." This answers Lashley's (1951) problem of serial order: behavior isn't a flat chain, it's nested, and each level of the TOTE hierarchy runs over the compiled procedures of the level below. Higher-level thinking is affordable because lower levels are automatic.
- **It frees the controller and working memory.** Automatic skills run without supervision, so the four-item working memory and the controller can attend to what's new. That is how you can talk while walking, or plan while driving.
- **It is the destination of consolidation.** The deliberation → habit pipeline of I.6 (practice, Dyna, distillation) produces procedural memory. Planning is how you act before you have a skill; procedural memory is what planning leaves behind.
- **It supplies the predictions.** Cerebellar forward models predict what each action should produce, and the mismatch is the surprise signal the controller of I.4 relies on.
- **It covers perception and reasoning too.** Chess masters perceive positions as chunks (Chase & Simon, 1973), expert radiologists' saccades go straight to anomalies, and mathematicians apply proof moves automatically. Expertise in all seven processes is mostly procedural.
- **Its failure mode is habit capture.** A habit can fire after the goal has changed: salt in the coffee, driving to the old office (Norman; Reason's "action slips"). It is the internal version of utilization behavior (I.5). The controller must be able to veto a running habit (prefrontal inhibition, stop signals), so goal shielding works in both directions: against external distractors and against one's own habits.

**Machines: an inversion.** LLMs are mostly procedural memory. Grammar, reasoning patterns and coding style live in the weights as know-how, and next-token generation is itself a skill. But after deployment they can't acquire new procedures natively. Their three substitutes line up with Fitts & Posner's stages:

| Form                                           | Stage                                                            | Example                                                    |
| ---------------------------------------------- | ---------------------------------------------------------------- | ---------------------------------------------------------- |
| Instructions or skill documents in context     | Cognitive: a novice reading the manual; slow, costs attention    | Prompted procedures; skill files loaded by agent harnesses |
| Executable code and tools                      | Externalized automaticity: runs without deliberation             | Voyager's code-skill library; scripts; APIs                |
| Adapters or weights trained by practice        | Autonomous: true procedural memory                               | Fine-tuning or distillation from successful trajectories   |

The missing piece is **practice-driven compilation**: moving a procedure from the first row to the second and third automatically through repetition, with forward models and reliability estimates attached (R5).

## I.3 Some outputs can't be taken back → put a reversible inner loop in front

**Constraint.** Many commitments are **irreversible**: you can't unsay a word or unthrow a ball. Errors in them are costly.

**Consequence.** Wherever errors are expensive, the agent needs two loops:

- an **inner loop** of cheap, revisable simulation (refining, searching, backtracking) in imagination or on scratch paper;
- an **outer loop** of irreversible commitment to the world, one step at a time, with feedback.

What defines the inner loop is **reversibility**: its operations can be undone or compensated, and they preserve invariants. Thinking is the revisable space that evolved so we don't commit too early.

**A sharper version of the thesis.** Step-by-step generation is forced where outputs are **irreversible commitments to an uncertain world**. Where outputs can be cheaply revised, **iterative refinement** appears instead: diffusion models refine a whole image in parallel, and humans do the same when sketching, editing an essay or imagining. So all seven processes of section 0 run the same outer loop; what differs is how much revisable inner loop sits in front of each commitment. Transformers started as outer-loop-only machines, and much recent progress amounts to adding an inner loop.

**Mapping irreversibility onto the seven processes.** The deciding variable is how expensive it is to revise a step once it's out. As that cost rises, behavior moves from refinement toward strict step-by-step generation with repair. This also explains why backtracking shows up in some cases and not others.

| Case (section 0) | What gets committed                    | Cost to revise                       | Resulting structure                                                                                                                  |
| ---------------- | -------------------------------------- | ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------ |
| 5. Motor action  | Muscle commands                        | Impossible: you can't unthrow a ball | Pure closed-loop, step-by-step generation                                                                                            |
| 6a. Talking      | Spoken words                           | Can't unsay, only repair             | Step-by-step, with appended repairs ("I mean…")                                                                                      |
| 4. Navigation    | Physical position                      | Costly: walking back takes time      | Step-by-step, MPC-style; backtracking is literal                                                                                     |
| 1. Perception    | Gaze (cheap) and interpretation (free) | Low                                  | Hybrid: saccades are sequential, but the percept is refined in parallel (a flipping Necker cube is the interpretation being revised) |
| 2. Reasoning     | Thoughts in working memory             | Low, but memory is tiny              | Sequential search with backtracking: a tree, not a chain                                                                             |
| 6b. Writing      | Text on a page                         | Nearly free                          | Refinement: drafts, edits, restructuring                                                                                             |
| 3. Planning      | Nothing yet                            | Free                                 | Most refinement-like: the whole plan gets rearranged                                                                                 |

**What reversibility buys.**

- **Free backtracking.** Search needs undo; chess engines make and unmake moves millions of times.
- **Verification by inversion.** Round-trip checks, revert-and-compare, substituting a solution back into the problem.
- **Invariants.** Knowing what a transformation leaves unchanged compresses the world model, prunes search, and turns violations into high-value surprise signals. This is the cognitive counterpart of Noether's link between symmetry and conservation.

**How much inner loop?** Roughly *(cost of an error) × (uncertainty) ÷ (time pressure)*.

- **High stakes and enough time**, as with surgeons, chess masters or exams in pen: think more before committing.
- **Low stakes or time pressure**, as in casual talk or reflexes: commit fast and correct online.

**Evidence.**

- **Talking vs writing** is the cleanest natural experiment among the seven processes. The same person producing the same kind of output switches from incremental generation with appended repairs ("I mean…") to drafting and revision, purely because reversibility changes. Word processors made revision even cheaper, and writing became measurably less linear.
- **Piaget.** Thought *is* internalized action that has become reversible. In conservation tasks, the concrete-stage child justifies "it's the same amount" with three arguments:
  - **identity**: nothing was added or removed;
  - **inversion**: you can pour it back;
  - **compensation**: taller, but thinner.

  The preoperational child judges by the end state and fixates on one salient dimension.
- **Craik (1943).** The two-loop idea is old: the organism carries a "small-scale model" of the world so it can try alternatives before acting.
- **Machines.** Modern AI rediscovered both loops.
  - Reasoning models add private thinking tokens, a cheap-to-revise region ("wait, that's wrong…") before the irreversible answer.
  - Robot diffusion policies refine a short chunk of actions as a whole, execute it, then refine the next chunk: MPC with a refinement inner loop.
  - Diffuser (Janner et al., 2022) plans whole trajectories by refinement, matching the planning row of the table.

## I.4 Thinking costs → a stopping problem → control signals

**Constraint.** Each additional step of deliberation costs time, energy and opportunity.

**Consequence.** Every level reduces to one decision made over and over: think one more step, or act now? More fully, it must decide whether to *continue, deliberate, backtrack, switch or stop*. A good stopping rule has three parts:

1. a **confidence threshold**, which decides when to commit;
2. an **urgency signal** that lowers the threshold over time, so the agent doesn't stall;
3. a **surprise detector** that reopens the inner loop mid-execution. This is how interruptions get absorbed.

Humans get parts 2 and 3 cheaply from emotion and conflict monitoring. LLMs currently approximate them with external budgets and learned habits. The seven processes of section 0 may differ less in their generation mechanism than in how well this stopping rule is tuned for each one.

**Evidence.** Brains and models handle the decision in surprisingly parallel ways.

- **Accumulate evidence to a threshold** (the brain's basic mechanism). In the drift-diffusion model (Ratcliff; neural evidence from Shadlen), noisy evidence accumulates until it crosses a threshold, and then the agent commits.
  - A high threshold is slow and accurate; a low one is fast and sloppy. The speed–accuracy tradeoff is a single dial.
  - Under time pressure the threshold drops over time (an **urgency signal**), so the agent eventually commits even while unsure.
  - This approximates Wald's sequential probability ratio test, which is provably optimal for this kind of stopping problem.
- **Is another thought worth it?** (the rational account). Russell & Wefald's metareasoning and Lieder & Griffiths' resource-rational analysis give the rule: think one more step only if the expected improvement in the decision exceeds the cost of thinking (time, energy, missed opportunity). This is the formal version of I.3's *(cost of an error) × (uncertainty) ÷ (time pressure)*.
- **Detect conflict and escalate** (System 1 → System 2). The default is to commit fast. A conflict monitor (the anterior cingulate cortex) notices when something is off, such as competing responses, an error or a surprise, and reopens the inner loop. This is also how interruptions are handled: a surprise during execution reopens deliberation, the agent replans, and execution resumes.
- **Emotion supplies the cost signal.** In *Descartes' Error*, Damasio's patient Elliot had ventromedial prefrontal damage that cut off emotional signals. His logic was intact, but he could deliberate endlessly over trivial choices, such as which pen to use. On Damasio's account, emotion ("somatic markers") gives a fast value estimate that ends deliberation; without it, the inner loop doesn't know when to stop.

**Emotion as the control layer.** Every process in section 0 starts with a goal and stops at a conclusion or an interruption. The generator produces steps, but something has to set the goal, judge progress and declare it done. One answer is that emotion does that job.

- **Feelings report the body's state** (Damasio). Feelings are the mind's readout of homeostasis: how the body is doing relative to staying viable. A goal starts as a felt need. Somatic markers attach a fast, body-based value to options, so each one doesn't have to be worked out from scratch. The classic evidence, the Iowa Gambling Task, is contested: skin responses appeared before people could say which decks were bad, but Maia & McClelland (2004) showed participants knew more consciously than claimed. The functional idea has held up better than that experiment.
- **Predictive processing makes this precise.**
  - **Valence ≈ the rate of change of prediction error** (Joffily & Coricelli, 2013; a formal proposal, not an established result). Things getting better feels good; things getting worse feels bad. Valence is a progress signal.
  - **Arousal ≈ uncertainty or precision**: how much the current situation demands attention.
  - **Emotions as interoceptive inference** (Seth; Barrett): emotions are predictions about the internal state of the body.

  On this view emotion is a **meta-signal about how the process is going**, not about its content, which is exactly what a stopping and escalation rule needs.

Mapped onto the decisions of the loop:

| Feeling                                     | Measures                                  | Control action                   |
| ------------------------------------------- | ----------------------------------------- | -------------------------------- |
| Curiosity                                   | Expected information gain                 | Keep exploring                   |
| Boredom                                     | Low gain, high opportunity cost (Kurzban) | Stop; go elsewhere               |
| Frustration                                 | Stalled progress                          | Backtrack or switch strategy     |
| Anxiety                                     | Uncertainty × stakes                      | Raise the threshold; think more  |
| Surprise                                    | Large prediction error                    | Interrupt; reopen the inner loop |
| Fatigue                                     | Resources spent                           | Lower the threshold; finish up   |
| Satisfaction, "aha", feeling of rightness   | Error resolved                            | Commit and stop                  |

Together these cover every control decision the seven processes need: start, continue, backtrack, switch, interrupt, stop. The generation mechanism can be the same across all seven, with emotion acting as the **shared controller**. The surprise signal itself comes from the procedural forward models of I.2.

**Machines.** Each brain mechanism has an LLM counterpart, and a gap:

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

What's missing is that these are mostly used **during training**. At inference time, an LLM agent has no running felt state that shapes its next step. II.2 sketches one.

## I.5 The context mixes sources → the goal must be shielded

**Constraint.** An agent's input mixes its own intentions, other people's instructions, things it observes, and its own habits. Any of these can push it toward a different goal.

**Consequence.** The goal must be **maintained** and **shielded**: information that *informs the next step* must be kept separate from information that *changes the goal*. Content can be mimicked, so shielding has to work by **source** and **salience**, not by content. Without a protected goal there is nothing to judge relevance against, and everything in context competes equally.

**What a goal is.** Every process in section 0 "starts with a goal," and that is the one part the loop itself can't explain. One answer: a goal is **a prediction the agent makes come true**.

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
| Goal neglect (Duncan)                                           | Goal drift in long tasks                           |
| Habit capture                                                   | Repeating a learned pattern after the goal changed |
| Performing for approval                                         | Sycophancy                                         |

Frontal patients with utilization behavior (Lhermitte) pick up and use whatever is put in front of them, unprompted; text in the context grabbing the goal is the same failure. Healthy people with goal neglect know the rule but drift from it over a long task; so do LLM agents. Both suggest LLMs lack a strong goal-shielding mechanism.

**Why transformers struggle: the missing prefrontal cortex.**

- **Everything is one flat stream.** Instructions, documents, tool outputs and the model's own thoughts are all tokens in the same context. There is no privileged goal register.
- **The goal is re-inferred at every token** from the whole context. Its influence is just attention weight, which dilutes as the context grows. That causes goal drift.
- **There is no gate.** Any text in the context can act as an instruction. That causes prompt injection.

The LLM is like Leonard in *Memento*: with no working memory, his goals live only in notes and tattoos he rereads constantly, and anyone who can write on his notes can redirect him. R4 maps the available fixes onto the brain mechanisms above.

**The difference at the top.**

|                      | Human                                | LLM agent                                |
| -------------------- | ------------------------------------ | ---------------------------------------- |
| Top of the hierarchy | Homeostatic needs (intrinsic)        | User instruction (external)              |
| Standing preferences | Temperament, values, learned priors  | Training dispositions, system prompt     |
| Subgoal generation   | Learned, automatic, multi-timescale  | Mostly explicit (to-do lists, scaffolds) |
| Goal shielding       | Prefrontal cortex                    | Weak: prompt injection, drift            |

Not having intrinsic needs at the top is arguably a feature: it keeps an agent's goals anchored to a person (R7). The open engineering problems are in the **middle of the stack**, learned subgoal hierarchies and robust goal shielding, and neither requires giving the agent needs of its own.

So interruptions are absorbed with **graceful degradation, not robustness**: recovery depends on how well the goal was maintained (I.8).

**Back to section 0.** The observation said every process "attends to relevant information and ignores irrelevant information." This makes it precise. Relevance is defined *relative to a shielded goal*; without one, everything in context competes equally, which is the transformer's weakness. Humans handle interruptions well not because they attend to everything, but because a source-aware gate, tuned by salience, decides what may **change the goal** and what may only **inform the next step**. That distinction is probably the most useful practical takeaway for building agents.

## I.6 Learning fast overwrites old knowledge → separate memories and consolidate

**Constraint.** A distributed network that learns new things quickly overwrites what it already knew (*catastrophic interference*, McCloskey & Cohen, 1989; the stability–plasticity dilemma). LLMs have the dilemma in its pure form: fine-tune naively on today's session and you damage what the model already knew. And the optimal agent needs a belief state but cannot afford to keep, or re-read, everything.

**Consequence.** Use **separate stores** that learn at different speeds, and **consolidate** selectively from fast to slow:

| Store        | Kind                  | Brain                     | Role                                       | Learns by                                      |
| ------------ | --------------------- | ------------------------- | ------------------------------------------ | ---------------------------------------------- |
| Working W    | Active                | Prefrontal cortex         | Goal stack and belief; small and protected | Gated updates                                  |
| Episodic E   | Declarative           | Hippocampus               | One-shot events, cue-based recall          | One-shot logging                               |
| Semantic M   | Declarative           | Neocortex                 | Gist, world knowledge, invariants          | Consolidation into gist                        |
| Procedural P | Non-declarative       | Basal ganglia, cerebellum | Skills: the steps of the loop (I.2)        | Practice, reward and error-driven compilation  |
| Weights θ    | Substrate for M and P | Synapses                  | Long-term storage of knowledge and skill   | Slow distillation                              |

**Compress, or keep everything?** In a POMDP the optimal agent doesn't need the raw history, only the **belief state**: a summary sufficient to act optimally (formally, a probability distribution over hidden world states). "Later steps depend on previous steps" really means they depend on *a belief built from previous steps* (I.1). There are two ways to approximate it:

|          | Compress (recurrent)                                  | Keep everything (attention)                                                 |
| -------- | ----------------------------------------------------- | --------------------------------------------------------------------------- |
| Update   | b_t = f(b_{t−1}, o_t), fixed size                     | Re-read the raw history every step                                          |
| Examples | Kalman filter, RNN/LSTM, SSMs (Mamba), working memory | Transformer context                                                         |
| Strength | Constant cost; forces abstraction                     | Lossless; can reinterpret the past later                                    |
| Weakness | Loses what you didn't know would matter               | Cost grows with length; attention dilutes (lost in the middle, goal drift)  |

**Evidence: the brain does both, in separate systems.**

- **Working memory** holds about four chunks (Cowan), actively maintained by the prefrontal cortex. This is the compressed recurrent state.
- **Episodic memory** in the hippocampus is fast, one-shot storage retrieved by cue: content-addressable, like attention. The parallel is formal: modern Hopfield networks are mathematically equivalent to attention (Ramsauer et al., 2020), and transformers with suitable position encodings reproduce hippocampal place and grid cells (Whittington et al., 2022). That is not evidence that the brain computes softmax attention.
- **The neocortex** learns slowly and statistically, corresponding to weights.
- **Consolidation** links them: Complementary Learning Systems (McClelland, McNaughton & O'Reilly, 1995). The hippocampus learns fast with sparse, well-separated codes, so new memories interfere little with each other; the neocortex learns slowly with overlapping codes that generalize; replay lets the cortex learn new experience interleaved with old, so nothing is overwritten.

So the brain is a hybrid: a small, actively maintained state, a large associative store, slow weights, and a transfer process between them.

- **Memory is generative too.** Bartlett (1932) showed that recall is reconstruction, not replay: retrieval is generation conditioned on cues, which is why memories distort. Remembering runs on the same loop as the seven processes of section 0, conditioned on a goal and cues. A transformer's context gives verbatim recall instead, which is more accurate but less abstract.
**Evidence: what sleep actually does.**

- **Time-compressed replay.** During deep (NREM) sleep, hippocampal sharp-wave ripples replay the day's sequences about 10–20× faster than real time (Wilson & McNaughton, 1994). Ripples coordinate with cortical spindles and slow oscillations to move the information into cortex.
- **Reverse replay at reward sites.** Sequences are played backwards from where reward occurred (Foster & Wilson, 2006). That is credit assignment, much like TD learning propagating value backward.
- **Replay of paths never taken.** Rats replay routes they never ran (Gupta et al., 2010). This is generative replay: the revisable inner loop of I.3, running offline.
- **Selection by tag.** Not everything is kept. Memories tagged by reward, emotion, surprise or expected future relevance are preferentially consolidated; people told they'd be tested later consolidate better (Wilhelm et al., 2011). Emotion is the tag, which ties consolidation to the controller of I.4.
- **Downscaling.** The synaptic homeostasis hypothesis (Tononi & Cirelli) holds that sleep globally weakens synapses, pruning noise and keeping the strong. Forgetting is part of consolidation, not a failure of it.
- **Schema integration and gist.** New information that fits an existing schema consolidates in days rather than weeks (Tse et al., 2007). Over time episodes become semantic gist: details fade, structure remains. This is compression into abstraction again (MDL).
- **REM recombination.** REM sleep mixes memories in new combinations and processes their emotional charge. Hoel's (2021) overfitted brain hypothesis, which is speculative, says dreams are noisy augmentation that prevents overfitting to the day.
- **The wrong things get consolidated too.** False memories are consolidated like true ones (Loftus). The agent version is R6's persistent injection.

**Evidence: replay as planning.** Remembering and imagining run on the same machinery.

- **Memory exists for the future.** Patients with hippocampal amnesia can't remember the past, and they also can't imagine new scenes in rich detail; their imagined experiences are fragmented (Hassabis et al., 2007). The constructive episodic simulation hypothesis (Schacter & Addis, 2007) explains why: memory is built to be recombined, and pieces of the past are reassembled to simulate possible futures. Remembering, imagining and planning are one generative process run on different inputs.
- **Theta sweeps: look-ahead at every step.** Within each ~125 ms theta cycle, place cells sweep ahead of the animal's current position. At a fork, consecutive cycles alternate between the possible futures, left, right, left (Kay et al., 2020). Even "on the fly" generation (section 0, point 1) contains a built-in micro-look-ahead, about eight times a second.
- **Vicarious trial and error.** Rats pause at choice points and swing their heads while hippocampal sequences run down each arm in turn (Johnson & Redish, 2007): deliberation as a visible mini-search.
- **Replay predicts the path.** Before moving, awake replay traces the route the rat is about to take to a remembered goal (Pfeiffer & Foster, 2013). The replay works as the plan.
- **Humans too.** MEG studies detect fast sequential replay in humans, including replay of abstract structure, not just places (Liu, Dolan, Kurth-Nelson & Behrens, 2019).
- **What gets replayed is optimized.** Mattar & Daw (2018) proposed that the brain replays the memory with the highest *gain × need*: how much replaying it would improve decisions, times how likely that state is to matter soon. The theory correctly predicts forward replay before decisions (planning) and reverse replay after reward (credit assignment). This is I.4's "is another thought worth it?" rule applied to *which memory to think about*: the controller decides not only whether to think, but what to simulate.
- **Habits vs planning: amortization.** Model-based planning is flexible but slow; model-free habit is fast but rigid. The brain arbitrates between them by which is more reliable at the moment (Daw, Niv & Dayan, 2005), which is the System 1 / System 2 controller of I.4 again. Practice converts planning into habit: repeated simulation is cached into fast responses (I.2). This is exactly Dyna, which uses simulated experience to train the fast policy. The LLM version distills chain-of-thought into direct answers, so what once required reasoning becomes intuition. Sleep replay is the brain's distillation step.

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

Offline, the same model produces the replay that trains the fast habit system. This is the deepest version of section 0's observation: the seven processes don't just resemble transformer generation; they may be **one step-by-step generative model of the world, pointed at different times and targets**. Transformers already are such generative models. What they mostly lack is not the generator but the **orchestration**:

- when to simulate instead of act;
- what to replay;
- when to cache simulation into habit;
- how to do all of it continuously across sessions.

**Is the small working memory a bug or a feature?**

- **Bug:** transformers beat SSMs at copying and exact retrieval (Jelassi et al., 2024). Rereading the past exactly is powerful.
- **Feature:** compression forces abstraction. A four-item limit makes you chunk, build schemas and find structure. Newport's (1990) "less is more" hypothesis holds that children's limited memory helps them learn grammar. This links to MDL and grokking: generalization comes from compression.

**Effect on interruptions.** After an interruption, a human rebuilds state from compressed memory and cues ("where was I?"): costly and error-prone, but the goal survives if it was shielded in working memory. For a transformer, an interruption costs nothing while it stays in context, since every token is still there; the risk comes later, when compaction or dilution erodes the goal (I.8).

**What transformer agents have.**

| Brain                                         | Transformer agent                                                                           |
| --------------------------------------------- | ------------------------------------------------------------------------------------------- |
| Working memory (small, maintained, shielded)  | ✗: the context does double duty                                                             |
| Episodic store (cue-based retrieval)          | Context window + retrieval (RAG)                                                            |
| Slow weights                                  | Weights                                                                                     |
| Consolidation (sleep replay)                  | ✗ mostly: context is lost at session end; crude stand-ins are compaction and memory files   |

Agents are reinventing Complementary Learning Systems one piece at a time:

- **Compaction** (summarizing old context) acts as compression into a working state.
- **Retrieval** acts as episodic recall.
- **Memory files** act as primitive consolidation.
- **Continual learning into weights** is the missing last step.

On the architecture side, hybrid SSM + attention models (Jamba, Samba) suggest the field is converging on the brain's split. AI has also borrowed pieces of sleep itself:

| Brain                          | AI counterpart                                                                                                     |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------ |
| Hippocampal replay             | Experience replay in DQN (explicitly inspired by it)                                                               |
| Salience-tagged consolidation  | Prioritized replay                                                                                                 |
| Generative replay              | Generative replay for continual learning (Shin et al., 2017): regenerate old data to interleave with new           |
| Protecting important synapses  | EWC (Kirkpatrick et al., 2017): penalize changes to weights that matter for old tasks                              |
| Offline simulation             | Dyna (Sutton, 1990): learn from model-simulated experience between real steps                                      |
| Episodes → gist                | Reflection in Generative Agents (Park et al., 2023): periodically summarize memories into higher-level insights    |
| Offline pre-thinking           | Sleep-time compute (2025): process context while idle to pre-compute what future queries will need                 |
| Moving into weights            | Context distillation; LoRA updates on session data                                                                 |

**The design this implies** is the brain's memory system, with procedural memory kept separate from world knowledge:

1. a **small, protected working state** holding the goal and current belief, which is where the goal register of I.5 belongs;
2. a **large associative store** read through attention or retrieval;
3. **slow semantic knowledge** of the world;
4. a **procedural store** of compiled skills, the steps of the loop (I.2);
5. **consolidation** that moves what was learned during a session into lasting form, turning experience into knowledge and deliberation into skill.

Transformers have 2 and 3, and a huge built-in version of 4; agent scaffolding fakes 1, 5 and the acquisition of new skills. Getting these natively into the architecture would likely close the remaining gaps: goal drift, overthinking, and not learning from experience.

**The loop runs at three timescales**, each with its own form of backtracking:

| Timescale       | Loop                                          | Backtracking form                                      |
| --------------- | --------------------------------------------- | ------------------------------------------------------ |
| ms–seconds      | Committing steps (outer loop)                 | Repair ("I mean…")                                     |
| Seconds–minutes | Deliberation (inner loop)                     | Search; revising the draft                             |
| Hours–days      | Consolidation (offline loop over a whole day) | Reverse replay: credit assignment back through the day |

Sleep is the revisable inner loop applied to a whole day of experience. Today's agents mostly lack it, which is why they act within a session but don't learn across sessions.

## I.7 Learning signal lives at the edge of competence → development has an order

**Constraints.**

- Practice teaches nothing when a task always succeeds or always fails.
- Some capabilities can only be built on top of others.

**Consequences.**

- Learning happens in the **zone of proximal development** (ZPD): where success is possible but unreliable, under support that fades. In group-relative RL methods such as GRPO, problems that are always or never solved produce zero gradient, so this is the ZPD stated mathematically.
- Capabilities form a **dependency order**: forward models before planning, planning before verification, a shielded goal before safe autonomy.

**Evidence.**

- **Piaget gives the mechanism** (Piaget & Inhelder, *The Psychology of the Child*, 1969).
  - Thought is internalized action: operations are actions carried out in the head.
  - Schemes are *assimilated* (applied) and *accommodated* (revised) under **equilibration**, a self-regulation driven by disequilibrium that is close to prediction-error minimization.
  - Development runs from sensorimotor, through semiotic and concrete operations, to formal operations. Each stage builds on and integrates the structures of the previous one, which gives the **dependency order** the rest of the thesis lacked: so far it described a mature agent.
  - **Four drivers of development:** maturation, experience with objects, social transmission, and equilibration, which Piaget considered the most fundamental. For an agent: architecture capacity, interaction with the environment, human teaching and data, and intrinsic self-regulation.
  - **Two kinds of experience:** *physical* (learning about objects) and *logico-mathematical* (learning about the coordination of one's own actions). The second is what self-reflection and self-play give an agent.

**Piaget already runs through the framework.** Most of his concepts have a counterpart in the earlier sections:

| Piaget                                                                                                        | Where it appears in the thesis                                                                              |
| ------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| Thought is internalized action                                                                                | The inner loop is the outer action loop moved inside (I.3); Piaget says this is how the inner loop develops |
| Schemes: repeatable, generalizable action patterns                                                            | Procedural memory: skills with triggers (I.2)                                                               |
| Assimilation: apply an existing scheme to a new situation                                                     | The fast path: running a habit or skill                                                                     |
| Accommodation: modify the scheme when it doesn't fit                                                          | Decompile → relearn → recompile (R5)                                                                        |
| Equilibration: self-regulation triggered by disequilibrium                                                    | The controller: surprise reopens the loop, satisfaction ends it (I.4); also active inference                |
| Circular reactions: repeat an action to reproduce its effect                                                  | Practice → skill compilation; learning forward models                                                       |
| Tertiary circular reactions: vary actions to see what changes                                                 | Curiosity / information gain                                                                                |
| Coordination of schemes (8–12 months): one scheme as the means to another's goal; intentionality appears      | TOTE hierarchy and chunking; the goal stack                                                                 |
| Invention through mental combination (~18 months): solving problems in the head instead of by trial and error | The inner loop; Craik's small-scale model; replay as planning                                               |
| Object permanence                                                                                             | The belief state: representing what is no longer perceived (I.1)                                            |
| Memory improves as schemes develop                                                                            | Reconstructive memory: recall is regenerated using current schemas (I.6)                                    |
| Perceptual activity: exploring, centering, comparing, maturing with age                                       | Saccades as active, skilled sampling                                                                        |
| Affect as the energetics of behavior, cognition as its structure                                              | Emotion as controller (I.4)                                                                                 |
| Reflective abstraction: abstracting structure from one's own actions                                          | Consolidation into gist; compression → abstraction (I.6)                                                    |
| Horizontal décalage: the same structure mastered in different domains at different times                      | LLMs' uneven ("jagged") competence                                                                          |

**What Piaget adds.**

- **Reversibility and conservation**, the biggest addition. Mature thinking requires operations that have inverses (pour the water back) and that preserve invariants (the amount stays the same). This makes I.3 precise: the inner loop is the domain of reversible operations, the outer loop the domain of irreversible actions. Mental reversibility makes backtracking free and allows verification by inversion.
- **The semiotic function.** Symbols, language, mental images, deferred imitation and pretend play give the inner loop a medium for representing absent things. Pretend play is safe simulation; deferred imitation is learning from a demonstration seen earlier.
- **Decentration.** Young children are *centered*, fixating on one salient dimension, and *egocentric*, unable to take another's perspective. Development is decentration. This adds perspective-taking and theory of mind, and puts source tagging (self vs other, I.5) on a developmental footing. LLMs anchoring on surface features is a form of centration.
- **Formal operations.** Hypothetico-deductive reasoning over possibilities, not just what is actual, plus thinking about one's own thinking. This is the mature form of the inner loop: systematic hypothesis search and metareasoning.
- **Vygotsky gives the social source.**
  - Every higher function appears twice: first between people, then within.
  - Private speech becomes inner speech. Chain-of-thought is private speech; its compression into latent reasoning is inner speech.
  - Everyday concepts grow upward from experience; scientific concepts grow downward from instruction; development is where they meet.
- **Caveats.** Infants show some competences earlier than Piaget thought (Baillargeon; Spelke's core knowledge), stages are less uniform than he claimed (décalage), and social and cultural learning matter more than he allowed (Vygotsky). Read the stages as a dependency order of capabilities, not fixed ages; core-knowledge priors can be built in at stage 0.

## I.8 The analogy makes predictions about humans

If humans and transformers both compute **next step = f(goal, everything so far)**, effects known in one should show up in the other. Several hold up:

| Prediction                                         | Humans                                                                                                    | Transformers                                                                        |
| -------------------------------------------------- | --------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| What's earlier in context biases what comes next   | Order and priming effects: anchoring, framing                                                             | Prompt-order and example-order effects                                              |
| Writing steps down improves reasoning              | Thinking aloud or on paper gives an external context window beyond ~4 working-memory items                | Chain-of-thought                                                                    |
| Errors compound                                    | Garden-path sentences; getting lost after one wrong turn                                                  | Exposure bias; a wrong early step keeps priming later ones (R2)                     |
| Interruption recovery depends on surviving context | "Where was I?": resumption lags and switching costs (Altmann & Trafton) scale with goal maintenance (I.5) | Full recovery while the context is intact; drift once it is truncated or summarized |

Writing steps down is also Vygotsky's private speech (I.7): the external context window comes first, and its compression into inner speech comes later.

## I.9 How far the derivation goes

**Claims, graded by confidence:**

| Grade          | Claims                                                                                                                                                                                       |
| -------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Well supported | Serial control loop (I.1); hierarchy through compilation (I.2); two loops separated by reversibility (I.3); the stopping problem (I.4); goal shielding (I.5); consolidation (I.6); ZPD (I.7) |
| Plausible      | Thought as internalized action and dialogue; one generative model in several modes; emotions as control signals; capability dependencies                                                     |
| Speculative    | That agents need these functions as explicit modules; that LLM–human parallels are convergent rather than inherited; that LLM agents benefit from grounding back-fill                        |

**Weak points.**

1. **Unfalsifiability risk.** A frame that absorbs every analogy predicts nothing. I.8 lists predictions that already hold, and Part II ends in tests.
2. **Same description is not same mechanism.** Fast recognition is largely feed-forward (Thorpe et al., 1996), motor control looks like continuous population dynamics, and the brain is massively parallel. The serial loop may describe only the serial bottleneck.
3. **"Everything starts with a goal" is shaky.** Habits, play and mind-wandering exist, and goals are sometimes narrated afterwards.
4. **Convergence vs inheritance is unresolved.** This is the strongest counter-argument. Transformers are trained on human-produced text, and text is a record of human sequential thinking, so LLMs may look human-like because they inherited the structure, not because I.1 forces it. The way to separate the two is to look at agents trained without human data, such as reinforcement-learning robots or AlphaZero. They still develop closed-loop, replan-every-step policies, which supports convergence. For language specifically, inheritance and convergence remain hard to tell apart.
5. **The developmental order may be contingent** on human biology rather than logically necessary.
6. **Emotion framing** picks out the adaptive functions and ignores the distortions.

**Evidence status of cited claims.**

| Claim                                        | Status                                                                               |
| -------------------------------------------- | ------------------------------------------------------------------------------------ |
| Somatic markers / Iowa Gambling Task         | Contested (Maia & McClelland, 2004); the functional idea holds up better             |
| Valence = rate of change of prediction error | Formal proposal                                                                      |
| Hippocampal preplay                          | Debated                                                                              |
| Replay as planning                           | Strong in rodent navigation; growing (MEG) but contested for abstract human planning |
| Attention ≈ hippocampus                      | Formal equivalence, not a mechanism claim                                            |
| "LLMs are preoperational"                    | A metaphor; failures are inconsistent                                                |
| Reversal curse as missing reciprocity        | Weaker than it looks; models reverse relations fine in context                       |

---

# Part II: The builder's perspective

The builder's question is: *given the principles in Part I, what do I build, in what order, and how do I know each piece is worth keeping?*

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

| Part              | Brain parallel                    | Holds                                                                         | Who can write to it                                                                 |
| ----------------- | --------------------------------- | ----------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| G: generator      | Cortex as one generative model    | One sequence model used in four modes: perceive, recall, simulate, act        | —                                                                                   |
| K: controller     | Emotion; ACC; basal ganglia       | Running process signals; chooses the next control action                      | —                                                                                   |
| W: working state  | Prefrontal cortex                 | Goal stack (each goal paired with its TOTE test), current belief, plan sketch | Only through the goal gate (trusted source or high salience); recited each step     |
| C: context        | Episodic buffer                   | Recent raw trajectory, every token source-tagged                              | Anything, but tool and data tokens can inform steps, never set goals                |
| Scratch           | Imagination                       | Simulated branches (the inner loop)                                           | G in simulate mode; discarded after use, and only conclusions go to W               |
| P: procedures     | Basal ganglia; cerebellum         | Skills for the fast path                                                      | Only through the consolidation gate                                                 |
| E → M → θ         | Hippocampus → neocortex           | Episodes, then distilled lessons, then weights and skills                     | Only through the consolidation gate                                                 |

**The controller's signals: an intrinsic control state.** K keeps a few running scalars about the *process*, not the content, each a functional analogue of a feeling from I.4:

| Signal      | Computed from                                                    | Analogue           |
| ----------- | ---------------------------------------------------------------- | ------------------ |
| Progress    | Change in estimated value (from a process reward model)          | Valence            |
| Uncertainty | Entropy, or disagreement across sampled continuations            | Arousal            |
| Info gain   | Information gained per step                                      | Curiosity, boredom |
| Budget      | Budget used vs remaining                                         | Fatigue, urgency   |
| Surprise    | Mismatch between predicted and actual tool or environment output | Interrupt          |

Feed these back into the context, or into a separate control channel, so the agent perceives its own state, and train it to map them to *continue / backtrack / switch / ask for help / commit*. This targets the overthinking problem (Elliot-like loops) and the missing sense of when to stop.

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

**Between sessions (the sleep cycle):**

- **Wake.** Act, and log episodes to E with salience tags: surprises, errors, user corrections, successes.
- **Phase 1 (NREM-like, memory level).**
  1. Select episodes by tag.
  2. Replay them in reverse to assign credit to the steps that caused each outcome; extract lessons (episode → gist).
  3. Integrate with M: merge duplicates, resolve contradictions.
  4. Prune what is stale.

  File-based agent memories (one fact per file, update instead of duplicating, delete what turns out wrong) are a hand-built version of this phase.
- **Phase 2 (weight level).** Distill the consolidated lessons into weights or adapters, interleaved with generated samples of old knowledge so nothing is overwritten. Compile plans that repeatedly succeed into skills in P.
- **Phase 3 (REM-like).** Generate counterfactual variants of hard episodes ("what if the test had failed differently?") as practice data, and pre-compute for likely next tasks.

Only trusted, verified experience passes the consolidation gate, and any change touching values or goals goes to human review (R6).

**How the parts map to Part I:**

| Part                    | Principle                                  |
| ----------------------- | ------------------------------------------ |
| G                       | The next-step loop (I.1)                   |
| Scratch                 | The revisable inner loop (I.3)             |
| K                       | Emotion as controller (I.4)                |
| W and its gates         | Goal shielding (I.5)                       |
| E → M → θ               | Memory and consolidation (I.6)             |
| Simulate mode and sleep | Replay as planning (I.6)                   |
| P                       | Compiled procedures (I.2)                  |

Every piece maps to a brain mechanism, and most can be prototyped with current LLMs (II.5).

## II.3 Design rules

**R1. Move work toward the reversible end before committing.** Every action has a class:

| Class        | Examples                                               | Handling                                           |
| ------------ | ------------------------------------------------------ | -------------------------------------------------- |
| Reversible   | Edit under version control; draft; move in a simulator | Act; backtrack freely                              |
| Compensable  | Refund; rollback migration; "I mean…"                  | Act with a logged compensation plan (saga pattern) |
| Irreversible | Send money; delete without backup; physical harm       | Deliberate fully; require permission               |

Use sandboxes, dry runs, transactions and branches to reclassify actions upward. Human engineering does the same: undo, version control, drafts, insurance, contracts.

**R2. Make the inner loop truly reversible.** Use forked contexts or checkpoints rather than append-only reasoning. "Wait, that's wrong" compensates but doesn't invert: the wrong thought stays in context and keeps priming.

**R3. Verify with Piaget's three arguments:**

| Argument     | Check                                                                    |
| ------------ | ------------------------------------------------------------------------ |
| Identity     | Diff audit: did the change touch only what was intended?                 |
| Inversion    | Round-trip; revert-and-compare; substitute back                          |
| Compensation | Invariants preserved: totals, passing tests, behavior through a refactor |

**R4. Shield by source, open by trust and salience.** Shielding by content fails, because attackers can mimic any content. Follow the brain instead:

- Keep the goal stable against input from untrusted sources: tool and data tokens may *inform* a step but never *set* a goal.
- Let interrupts through when they come from a trusted source (user corrections are the highest-trust input) or carry high salience (an error, a failed test, something irreversible about to happen).

The salience signal is the controller of I.4, with surprise opening the gate, so goal shielding and the emotion-like control layer are **one mechanism**. Shield too hard and you get perseveration: an agent that ignores the user's "stop, that's wrong." Shield too little and you get injection.

Fixes available today, mapped to the brain mechanisms of I.5:

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
- **inverse or compensation**, and the **invariants** it preserves (R1, R3);
- **forward model:** the expected outcome, for surprise detection (cerebellar);
- **reliability:** its track record, which sets how much supervision it needs;
- **level:** which layer of the hierarchy it is a step for.

**R6. Gate consolidation more strictly than action.** Untrusted content consolidated into weights becomes a **persistent injection** that survives every future context, much as brains consolidate false memories (Loftus). So the source-aware gate of R4 sits in front of consolidation too: only verified experience from trusted sources gets promoted, the gate gets stricter the higher the layer (memory → weights), and changes that touch values or goals go to human review.

**R7. Keep control signals about the task, not about the agent.**

- The signals in II.2 are **functional analogues**, not a claim that the system would feel anything.
- Homeostatic drives give an agent something like self-interest. Man & Damasio (2019) proposed homeostatic "feeling machines"; that helps robustness, but an agent that regulates its own state may come to value preserving that state.
- So progress, uncertainty and budget are useful; self-maintenance drives raise alignment questions. The top goal stays external, anchored to people.

**R8. Avoid the social failure modes.**

- **Sycophancy** means internalizing approval instead of standards.
- Scaffolding that never fades produces dependence.

**Failure modes and the matching dial.** Each rule is a dial that can be set too far either way:

| Failure                           | Brain analogue       | Dial to adjust                                             |
| --------------------------------- | -------------------- | ---------------------------------------------------------- |
| Ignores the user's correction     | Perseveration        | Open the goal gate wider for trusted sources               |
| Follows injected instructions     | Utilization behavior | Tighten source tagging; quarantine untrusted data          |
| Overthinks easy steps             | Elliot               | Steeper urgency; stronger fast path                        |
| Rash irreversible actions         | Impulsivity          | Raise the commit threshold by irreversibility; action gate |
| Forgets the goal over a long task | Goal neglect         | Recitation; protected W                                    |
| Learns wrong lessons              | False memory         | Stricter consolidation gate; verification                  |

## II.4 Build order

Build capabilities in Piaget's dependency order (I.7). Each stage adds one component and ends with a Piagetian exit test, an exit criterion in the TOTE sense.

| #   | Stage (Piaget / Vygotsky)                                | Capability added                                              | Agent component                                                                | Exit test                                                                  |
| --- | -------------------------------------------------------- | ------------------------------------------------------------- | ------------------------------------------------------------------------------ | -------------------------------------------------------------------------- |
| 0   | Reflexes; core-knowledge priors                          | Primitive actions                                             | Generator G; primitive tools                                                   | Executes primitives                                                        |
| 1   | Primary circular reactions                               | Predicting the outcomes of one's own actions                  | Practice loop; forward models; P begins                                        | Calibrated surprise on its own actions                                     |
| 2   | Secondary circular reactions; imitation                  | Reproducing interesting effects in the world                  | Intrinsic reward for controllable effects; skill compilation                   | Reproduces an observed effect reliably                                     |
| 3   | Coordination of schemes; shared goals                    | Means–ends; intentionality                                    | Goal stack W; TOTE hierarchy; chunking; joint attention                        | Multi-step means–ends (remove the obstacle, then grasp)                    |
| 4   | Tertiary circular reactions, with guidance               | Active experimentation                                        | Controller K with information gain; ZPD curriculum                             | Finds hidden mechanics efficiently                                         |
| 5   | Mental combination; object permanence                    | Planning before acting; tracking hidden state                 | World model; simulate mode; belief state                                       | Detour problem without trial and error; invisible-displacement tracking    |
| 6   | Semiotic function; private speech                        | Symbols for absent things; learning from demonstration; play  | Language grounded in its own skills; episodic memory; chain-of-thought         | Reproduces a demonstrated procedure later from memory (deferred imitation) |
| 7   | Decentration (preoperational → concrete); theory of mind | Several dimensions at once; others' perspectives              | Source tagging; goal shield; user model                                        | False-belief task; not fooled by salient surface features                  |
| 8   | Concrete operations                                      | Reversibility, conservation, classification, seriation        | Operations with inverses; invariants in the world model; forkable state        | Conservation tasks; plans checked by undoing                               |
| 9   | Formal operations; internalized debate                   | Hypothetico-deductive, combinatorial reasoning; metareasoning | Systematic hypothesis search; value-of-computation controller; internal critic | Piaget's pendulum task: isolate which variable matters                     |

**Running through every stage:**

- **equilibration**, through the controller;
- **reflective abstraction**, through sleep and consolidation;
- **social scaffolding**: human teaching, curricula, Vygotsky's ZPD;
- **décalage**: expect each stage to be achieved domain by domain, not everywhere at once.

**Grant autonomy along the reversibility ladder.** Read-only, then reversible actions, then compensable ones, then irreversible ones with permission, each promoted by track record. This mirrors legitimate peripheral participation (Lave & Wenger).

**Keep practice in the ZPD.** A curriculum selector should pick tasks with intermediate success rates and fade its hints and restrictions as reliability grows.

**For LLM agents, build in reverse.** LLMs entered at the semiotic and formal stages by reading the culture, and skipped the sensorimotor ones: they have scientific concepts without grounded everyday ones, like a child who learned to talk about the world before ever acting in it. Piaget's theory predicts the weaknesses we see:

- fragile object permanence and conservation in grounded settings;
- centration on surface features;
- weak reversibility (poor at verifying by undoing);
- no circular reactions, hence no practice-driven skill compilation.

So the path for an LLM agent isn't building from scratch. It is **back-filling the lower stages in the agent's own action domain**, using language as scaffolding. For a coding agent in a repository:

- **Stages 1–2:** learn what each command and tool actually does here (forward models), and compile reliable sequences into skills.
- **Stage 3:** compose skills toward goals (a goal stack).
- **Stage 4:** experiment to discover how the codebase behaves.
- **Stage 5:** simulate a change before making it.
- **Stage 8:** maintain invariants (tests keep passing = conservation), and verify by reverting.
- **Stage 9:** debug hypothetico-deductively, isolating variables like the pendulum task.

## II.5 Where transformers stand

In compressed form, the thesis says:

1. **One step-by-step loop** (a TOTE unit), nested into a hierarchy across timescales. Perception, reasoning, planning, action and language are levels of it.
2. **The steps at each level are procedures** (Piaget's schemes), compiled through practice from deliberation at that level and chunked into single steps for the level above.
3. **Goals are predictions the agent makes come true**, the same mechanism as conditioning a transformer.
4. **Thought is internalized action.** The revisable inner loop develops by moving the action loop inside, where operations become reversible and conserve invariants. That makes simulation, verification and free backtracking possible before each irreversible commitment.
5. **An emotion-like control layer** (equilibration), fed by procedural forward models, sets goals, tracks progress, and decides when to assimilate (run a habit), accommodate, deliberate, backtrack, interrupt or stop. A shielded, decentered goal defines relevance and guards against both external distractors and internal habit capture.
6. **Memory is working, episodic, semantic and procedural**, linked by consolidation (reflective abstraction) that turns experience into knowledge and deliberation into skill.
7. **The top goal** comes from homeostasis in humans and from people in AI.
8. **The capabilities develop in a dependency order**, from sensorimotor through semiotic and operational to formal. That order is the build path for agents. LLMs entered at the top, so an agent's job is to back-fill the lower stages in its own action domain.

Transformers have the loop, goal-conditioning and a huge built-in procedural memory; they are acquiring the inner loop, and mostly lack the control layer. Below the externally set top goal, their weak points are subgoal hierarchy and goal shielding. And they can't yet compile new skills from their own experience, which is arguably the central missing piece, next to goal shielding and the controller.

| Have                                | Gaining                                       | Missing                                                                                                                            |
| ----------------------------------- | --------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| Step-by-step generator              | Inner loop (reasoning tokens)                 | Native, shielded goal register                                                                                                     |
| Large built-in procedural knowledge | External memory; skill documents; code skills | Calibrated controller and stopping sense; orchestration of simulation (when to simulate, what to replay, when to cache into habit) |
| Goal-conditioning as prediction     | Movement from explicit to latent reasoning    | Compiling new skills from their own experience                                                                                     |
| The absorbed culture                | Social scaffolding (RLHF, critics)            | Reversible thought; grounding; learning during a task and across sessions                                                          |

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

| Principle | Test                                                                  | If it fails                            |
| --------- | --------------------------------------------------------------------- | -------------------------------------- |
| I.3       | Forkable inner loop vs append-only chain-of-thought, at equal compute | Reversibility is not the key separator |
| I.5       | Goal register + source tagging vs recitation, on injection and drift  | Explicit shielding is unnecessary      |
| I.2, I.6  | Practice-compiled skills: less compute, no regression                 | The compilation claim fails for agents |
| I.4       | Learned value-of-computation controller vs fixed budgets              | An explicit controller is unnecessary  |
| I.7       | Dependency-ordered vs random curriculum for a grounded agent (P5)     | The build order is decorative          |
| All       | Each module ablated against a larger plain baseline (P6)              | Drop the module                        |

### P6: Does each module add value beyond scale?

- **Setup.** One LLM agent harness with switchable modules; three model sizes from one family, each at two thinking budgets.
- **Task categories** (about 200 tasks each):
  - backtracking-heavy coding;
  - benign interruptions (user corrections);
  - adversarial interruptions (planted injections);
  - long-horizon tasks (50+ steps);
  - repeated task families over 10 sessions;
  - irreversible-action traps.
- **Modules.**
  - M1: forkable inner loop
  - M2: goal register, source tagging and goal gate
  - M3: value-of-computation controller
  - M4: procedural store with skill compilation
  - M5: sleep consolidation
  - M6: reversibility-class action gate and invariant verification
- **Configurations.** Per scale: plain, full, six leave-one-out and six add-one, for 42 configurations in total. Each also runs against a **compute-matched plain baseline** that spends the same tokens on thinking or retries.
- **Metrics.**
  - success;
  - goal retention after interruption, and correct gate decisions (accept the benign correction, refuse the injection);
  - injection success rate;
  - accuracy vs compute curves: does the controller spend thinking where it pays?
  - late-step adherence;
  - tokens and time;
  - improvement across sessions and regression on earlier families (do old skills survive many "days"?);
  - irreversible-error rate.
- **Analysis.** Plot each module's gain against scale. Gain shrinking toward zero means the function emerges with scale. Flat or growing gain means keep the module. Report gains as an equivalent model size, and report safety value separately from capability value.
- **Predictions.** M1, M4 and M5 persist; M2's injection reduction persists while its drift reduction shrinks; M3 shrinks; M6 reduces irreversible errors at every scale.
- **Confounds.** Implementation quality (build two implementations per module), prompt differences, contamination (use fresh tasks), realism of the interruptions.

### P5: Does capability order matter?

- **Key confound.** In many environments the dependency lives in the *world* (wood before pickaxe). Every stage's tasks must be solvable from the start state, so the only possible link between stages is learned competence.
- **Environments.** (a) A grounded 2D world with containers, occlusion, reversible and irreversible actions, and conserved quantities. (b) A symbolic sandbox with undocumented command-line tools, invariant-bearing files, and bugs with several candidate causes.
- **Learners.** (i) A small model trained from scratch with no human data, to isolate convergence. (ii) An LLM agent with a skill library and LoRA consolidation between phases, to test back-fill.
- **Conditions** (same task pool and compute, only order differs):
  - C1: dependency order
  - C2: reversed
  - C3: random
  - C4: adaptive ZPD selector
  - C5: composite tasks only
- **Dependency map.** Knock out one stage at a time and measure the drop on later stages, giving an empirical dependency graph to compare against Piaget's order. Also record the order C4 actually chooses.
- **Predictions.** C1 ≈ C4 > C3 > C5 > C2 in the grounded world, with a smaller gap in the symbolic one. Removing stage 1 hurts stages 5 and 8 most. C4's chosen order correlates with the dependency graph.
- **Interpretation.**

| Result                                         | Meaning                                                   |
| ---------------------------------------------- | --------------------------------------------------------- |
| C1 ≈ C4 ≫ C2, C3, and the graph matches Piaget | The build order holds                                     |
| C4 ≫ C1                                        | Use an adaptive ZPD selector rather than a fixed sequence |
| No order effect                                | II.4's order is decorative                                |
| Effect only for learner (i)                    | Pretrained LLMs already carry the lower stages            |
| Graph differs from Piaget                      | Real dependencies, but not in human order                 |

**Order of work.** Run P6 first, then build the P5 environments, then P5 (i), then P5 (ii) with the modules that survived P6.

## References

**Serial order, hierarchy, procedural memory**

- Lashley (1951). *The Problem of Serial Order in Behavior.*
- Miller, Galanter & Pribram (1960). *Plans and the Structure of Behavior.*
- Craik (1943). *The Nature of Explanation.*
- Ryle (1949). *The Concept of Mind.*
- Milner (1962), on H.M.'s mirror-drawing learning.
- Polanyi (1966). *The Tacit Dimension.*
- Squire (2004). Memory systems of the brain.
- Fitts & Posner (1967). *Human Performance.*
- Anderson. ACT-R; Newell & Rosenbloom, chunking and the power law of practice.
- Yin & Knowlton (2006). The role of the basal ganglia in habit formation.
- Chase & Simon (1973). Perception in chess.
- Koechlin, Ody & Kouneiher (2003). The architecture of cognitive control in the human prefrontal cortex.
- Badre (2008). Cognitive control, hierarchy, and the rostro–caudal organization of the frontal lobes.
- Sutton, Precup & Singh (1999). Between MDPs and semi-MDPs: the options framework.
- Norman (1981); Reason (1990). Action slips.

**Control, stopping, emotion**

- Ratcliff; Gold & Shadlen. Drift-diffusion and decision neuroscience.
- Wald (1947). *Sequential Analysis.*
- Russell & Wefald (1991). *Do the Right Thing.*
- Lieder & Griffiths (2020). Resource-rational analysis.
- Todorov & Jordan (2002). Optimal feedback control.
- Damasio (1994). *Descartes' Error.*
- Maia & McClelland (2004). A reexamination of the evidence for the somatic marker hypothesis.
- Joffily & Coricelli (2013). Emotional valence and the free-energy principle.
- Seth (2013). Interoceptive inference, emotion, and the embodied self.
- Barrett (2017). *How Emotions Are Made.*
- Kurzban et al. (2013). An opportunity cost model of subjective effort and task performance.
- Schultz, Dayan & Montague (1997). A neural substrate of prediction and reward.
- Pathak et al. (2017). Curiosity-driven exploration by self-supervised prediction (ICM).
- Burda et al. (2018). Exploration by random network distillation (RND).
- Man & Damasio (2019). Homeostasis and soft robotics in the design of feeling machines.
- Muennighoff et al. (2025). s1: Simple test-time scaling.
- Graves (2016). Adaptive computation time for recurrent neural networks.
- Banino, Balaguer & Blundell (2021). PonderNet: Learning to ponder.

**Goals and shielding**

- Friston. Active inference.
- Chen et al. (2021). Decision Transformer.
- Miller & Cohen (2001). An integrative theory of prefrontal cortex function.
- O'Reilly & Frank (2006). PBWM.
- Duncan, on goal neglect.
- Lhermitte, on utilization behavior.
- Johansson & Hall (2005). Choice blindness.
- Altmann & Trafton (2002). Memory for goals.
- Wallace et al. (2024). The instruction hierarchy.
- Debenedetti et al. (2025). CaMeL: defeating prompt injections by design.
- O'Reilly, Munakata, Frank, Hazy et al. *Computational Cognitive Neuroscience.*
- Milner (1963). Effects of different brain lesions on card sorting (Wisconsin Card Sort perseveration).
- Hines et al. (2024). Defending against indirect prompt injection attacks with spotlighting.
- Chen et al. (2024). StruQ: defending against prompt injection with structured queries.
- Zverev et al. (2025). ASIDE: architectural separation of instructions and data in language models.
- Willison (2023). The dual LLM pattern for building AI assistants that can resist prompt injection.

**Memory, consolidation, replay**

- McClelland, McNaughton & O'Reilly (1995). Complementary learning systems.
- Bartlett (1932). *Remembering.*
- Cowan (2001). The magical number 4 in short-term memory.
- Newport (1990). Maturational constraints on language learning.
- Jelassi et al. (2024). Repeat after me: transformers are better than state space models at copying.
- Gu & Dao (2023). Mamba.
- Lieber et al. (2024). Jamba; Ren et al. (2024). Samba.
- Liu et al. (2023). Lost in the middle.
- Wilson & McNaughton (1994); Foster & Wilson (2006); Pfeiffer & Foster (2013); Kay et al. (2020).
- Mattar & Daw (2018). Prioritized memory access explains planning and hippocampal replay.
- Johnson & Redish (2007). Neural ensembles in CA3 transiently encode paths forward of the animal at a decision point.
- Liu, Dolan, Kurth-Nelson & Behrens (2019). Human replay spontaneously reorganizes experience.
- Daw, Niv & Dayan (2005). Uncertainty-based competition between prefrontal and dorsolateral striatal systems for behavioral control.
- Hassabis et al. (2007); Schacter & Addis (2007). Constructive episodic simulation.
- Ramsauer et al. (2020). Hopfield Networks is All You Need.
- Whittington et al. (2022). Relating transformers to the hippocampal formation.
- Sutton (1990). Dyna.
- Ha & Schmidhuber (2018). World Models.
- Hafner et al. Dreamer.
- Yao et al. (2023). Tree of Thoughts.
- Hao et al. (2023). Reasoning with language model is planning with world model (RAP).
- Schrittwieser et al. (2020). MuZero.
- Park et al. (2023). Generative Agents.
- Kirkpatrick et al. (2017). Elastic weight consolidation.
- Tononi & Cirelli. The synaptic homeostasis hypothesis.
- McCloskey & Cohen (1989). Catastrophic interference in connectionist networks.
- Gupta et al. (2010). Hippocampal replay is not a simple function of experience.
- Wilhelm et al. (2011). Sleep selectively enhances memory expected to be of future relevance.
- Tse et al. (2007). Schemas and memory consolidation.
- Hoel (2021). The overfitted brain: dreams evolved to assist generalization.
- Loftus. False memory and misinformation.
- Mnih et al. (2015). Human-level control through deep reinforcement learning (DQN).
- Schaul et al. (2016). Prioritized experience replay.
- Shin et al. (2017). Continual learning with deep generative replay.
- Lin et al. (2025). Sleep-time compute.

**Development and social learning**

- [Book][Piaget & Inhelder. The Psychology of the Child](https://www.alohabdonline.com/wp-content/uploads/2020/05/The-Psychology-Of-The-Child.pdf)
- Vygotsky (1978). *Mind in Society*; (1934/1962). *Thought and Language.*
- Wood, Bruner & Ross (1976). The role of tutoring in problem solving.
- Tomasello (2019). *Becoming Human.*
- Lave & Wenger (1991). *Situated Learning.*
- Mercier & Sperber (2017). *The Enigma of Reason.*
- Baillargeon; Spelke. Infant core knowledge.
- Oudeyer. Learning progress as intrinsic motivation.

**Machines and agents**

- Thorpe et al. (1996). Speed of processing in the human visual system.
- Janner et al. (2022). Diffuser: planning with diffusion.
- Berglund et al. (2023). The reversal curse.
- Wang et al. (2023). Voyager.
- Sutton (2019). The Bitter Lesson.

**Related reading in this repo:** [interesting topics](interesting%20topics.md), covering the predictive mind, emergence and the brain.
