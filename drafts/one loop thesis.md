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
- **Not planned beforehand**: the full sequence is not *explicitly represented* in advance. The internal state can still carry *implicit look-ahead*: speech errors show that later words are already active; hippocampal "theta sweeps" alternate between possible futures several times a second; LLMs choose a rhyme before writing the line.
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

- **Definition.** Knowing *how* rather than knowing *that* (Ryle). It is acquired by practice, hard to verbalize, and a separate memory system: the amnesic patient H.M. improved at mirror drawing without remembering any practice.
- **Formation.**
  - Skills move from cognitive to associative to autonomous (Fitts & Posner).
  - Declarative steps get compiled into single procedures (ACT-R knowledge compilation; Soar chunking).
  - The basal ganglia learn which action fits which context through dopamine prediction errors.
  - The cerebellum learns **forward models** that predict an action's consequences.
- **Reach.** Expertise in perception and reasoning is largely procedural too: chess masters see positions as chunks, and radiologists' saccades go straight to anomalies.
- **Lashley's problem.** Chunking answers Lashley's (1951) problem of serial order: behavior isn't a flat chain, it's nested.
- **Failure mode: habit capture.** A habit fires after the goal has changed (salt in the coffee, driving to the old office), so a compiled skill needs a veto.

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

**Constraint.** A network that learns new things quickly overwrites what it already knew (*catastrophic interference*; the stability–plasticity dilemma). And the optimal agent needs a belief state but cannot afford to keep, or re-read, everything.

**Consequence.** Use **separate stores** that learn at different speeds, and **consolidate** selectively from fast to slow:

| Store      | Brain                     | Role                                       | Learns by               |
| ---------- | ------------------------- | ------------------------------------------ | ----------------------- |
| Working    | Prefrontal cortex         | Goal stack and belief; small and protected | Gated updates           |
| Episodic   | Hippocampus               | One-shot events, cue-based recall          | Logging                 |
| Semantic   | Neocortex                 | Gist, world knowledge, invariants          | Consolidation           |
| Procedural | Basal ganglia, cerebellum | Skills: the steps of the loop              | Practice, reward, error |

**Evidence.**

- **Compress or keep everything.** The two approximations of the belief state from I.1 trade off: compression (brains) forces abstraction; raw context allows reinterpreting the past. Hybrids look best.
- **Attention and the hippocampus.** Modern Hopfield networks are mathematically equivalent to attention, and transformers with suitable position encodings reproduce hippocampal codes. That is a formal parallel, not evidence that the brain computes softmax attention.
- **Complementary Learning Systems** (McClelland, McNaughton & O'Reilly). During sleep, time-compressed replay moves salience-tagged experience from hippocampus to cortex. Reverse replay at reward sites assigns credit, synaptic downscaling prunes, and episodes become gist.
- **Memory is reconstructive** (Bartlett). Recall itself runs on the generative loop.
- **Replay as planning.** Hippocampal sequences sweep ahead at choice points, replay predicts the path about to be taken, and replay is prioritized by *gain × need* (Mattar & Daw). Repeated planning gets cached into habit, as in Dyna and chain-of-thought distillation.
- **One generative model, four uses.** The same model may **remember** (the past), **perceive** (the present), **plan** (the future) and **act** (making predictions come true). This is strongest in rodent navigation and less certain for abstract human planning.

The loop thus runs at three timescales: commitment (milliseconds), deliberation (seconds to minutes), consolidation (days).

## I.7 Learning signal lives at the edge of competence → development has an order

**Constraints.**

- Practice teaches nothing when a task always succeeds or always fails.
- Some capabilities can only be built on top of others.

**Consequences.**

- Learning happens in the **zone of proximal development** (ZPD): where success is possible but unreliable, under support that fades. In group-relative RL methods such as GRPO, problems that are always or never solved produce zero gradient, so this is the ZPD stated mathematically.
- Capabilities form a **dependency order**: forward models before planning, planning before verification, a shielded goal before safe autonomy.

**Evidence.**

- **Piaget gives the mechanism.**
  - Thought is internalized action.
  - Schemes are *assimilated* (applied) and *accommodated* (revised) under **equilibration**, a self-regulation driven by disequilibrium that is close to prediction-error minimization.
  - Development runs from sensorimotor, through semiotic and concrete operations, to formal operations.
- **Vygotsky gives the social source.**
  - Every higher function appears twice: first between people, then within.
  - Private speech becomes inner speech. Chain-of-thought is private speech; its compression into latent reasoning is inner speech.
  - Everyday concepts grow upward from experience; scientific concepts grow downward from instruction; development is where they meet.
- **Caveats.** Infants show some competences earlier than Piaget thought, stages are uneven (décalage), and culture matters more than he allowed. Read the stages as a dependency order of capabilities, not fixed ages.

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

| Claim                                        | Status                                                                   |
| -------------------------------------------- | ------------------------------------------------------------------------ |
| Somatic markers / Iowa Gambling Task         | Contested (Maia & McClelland, 2004); the functional idea holds up better |
| Valence = rate of change of prediction error | Formal proposal                                                          |
| Hippocampal preplay                          | Debated                                                                  |
| Replay as planning                           | Strong in rodent navigation; contested for abstract human planning       |
| Attention ≈ hippocampus                      | Formal equivalence, not a mechanism claim                                |
| "LLMs are preoperational"                    | A metaphor; failures are inconsistent                                    |
| Reversal curse as missing reciprocity        | Weaker than it looks; models reverse relations fine in context           |

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
2. **Test** the top goal in W. If it is met, pop it and return to the parent goal.
3. **Controller decides:**
   - A confident skill matches → **run skill** (the fast path), monitoring only its forward model.
   - High surprise from a trusted source → reopen the belief and maybe replan, through the goal gate.
   - Progress has stalled → **backtrack** or **switch**.
   - Uncertainty × stakes is high and budget remains → **think**: simulate branches in scratch, expanding the one with the highest gain × need.
   - Information is missing → **recall** from E or M.
   - The goal is ambiguous → **ask** the user.
   - Otherwise → **commit**.
4. The commit threshold **drops as the budget runs down**, so the agent never stalls.
5. The **action gate** checks the action's reversibility class before it reaches the world.

**Between sessions (the sleep cycle):**

1. Select episodes by tag: corrections, failures, surprises, successes.
2. Replay them in reverse to assign credit to the steps that caused each outcome.
3. Extract gist into M: merge, resolve contradictions, prune what is stale.
4. Generate counterfactual variants of hard episodes as practice data.
5. Distill into adapters, interleaving generated replays of old knowledge so nothing is overwritten.
6. Compile plans that repeatedly succeed into skills in P.

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

- **Compile:** deliberate, succeed repeatedly, then cache.
- **Run:** monitor the forward model.
- **Veto:** stop it when the goal has changed.
- **Decompile:** when it keeps producing surprises, drop back to deliberation, relearn, and compile again.

Each skill records its trigger, body, inverse or compensation, the invariants it preserves, a forward model and a reliability score.

**R6. Gate consolidation more strictly than action.** Untrusted content consolidated into weights becomes a **persistent injection**. Only verified experience from trusted sources gets promoted, and changes that touch values or goals go to human review.

**R7. Keep control signals about the task, not about the agent.**

- The signals in II.2 are **functional analogues**, not a claim that the system would feel anything.
- Homeostatic drives give an agent something like self-interest. Man & Damasio (2019) proposed homeostatic "feeling machines"; that helps robustness, but an agent that regulates its own state may come to value preserving that state.
- So progress, uncertainty and budget are useful; self-maintenance drives raise alignment questions. The top goal stays external, anchored to people.

**R8. Avoid the social failure modes.**

- **Sycophancy** means internalizing approval instead of standards.
- Scaffolding that never fades produces dependence.

## II.4 Build order

Build capabilities in dependency order. Each stage ends with an exit test.

| #   | Capability (Piaget / Vygotsky)                                  | Agent component                                                     | Exit test                                          |
| --- | --------------------------------------------------------------- | ------------------------------------------------------------------- | -------------------------------------------------- |
| 0   | Reflexes; core priors                                           | Generator; primitive tools                                          | Executes primitives                                |
| 1–2 | Circular reactions; imitation                                   | Forward models; skill compilation                                   | Calibrated surprise; reproduces effects            |
| 3   | Means–ends; shared goals                                        | Goal stack; TOTE; chunking; joint attention                         | Multi-step means–ends tasks                        |
| 4   | Experimentation, with guidance                                  | Controller with information gain; ZPD curriculum                    | Finds hidden mechanics efficiently                 |
| 5–6 | Internal simulation; object permanence; symbols; private speech | World model; belief state; episodic memory; chain-of-thought        | Detour without trial and error; deferred imitation |
| 7   | Decentration; theory of mind                                    | Source tagging; goal shield; user model                             | False-belief task; not fooled by surface cues      |
| 8   | Reversibility; conservation                                     | Operations with inverses; invariants; forkable state                | Conservation; verify by undoing                    |
| 9   | Formal operations; internalized debate                          | Hypothesis search; value-of-computation controller; internal critic | Pendulum task: isolate the causal variable         |

**Grant autonomy along the reversibility ladder.** Read-only, then reversible actions, then compensable ones, then irreversible ones with permission, each promoted by track record. This mirrors legitimate peripheral participation (Lave & Wenger).

**Keep practice in the ZPD.** A curriculum selector should pick tasks with intermediate success rates and fade its hints and restrictions as reliability grows.

**For LLM agents, build in reverse.** LLMs entered at the symbolic and formal stages by reading the culture: they have scientific concepts without grounded everyday ones. The job is to **back-fill the lower stages in the agent's own action domain**. For a coding agent:

- **Stages 1–2:** learn what each tool actually does here, and compile reliable sequences into skills.
- **Stage 3:** compose skills toward goals.
- **Stage 4:** experiment to discover how the codebase behaves.
- **Stage 5:** simulate a change before making it.
- **Stage 8:** treat passing tests as conservation, and verify by reverting.
- **Stage 9:** debug by hypothesis, isolating variables.

## II.5 Where transformers stand

In compressed form, the thesis says:

1. **One step-by-step loop** (a TOTE unit), nested into a hierarchy across timescales. Perception, reasoning, planning, action and language are levels of it.
2. **Goals are predictions the agent makes come true**, the same mechanism as conditioning a transformer.
3. **A revisable inner loop** sits in front of each irreversible commitment.
4. **An emotion-like control layer** sets goals, tracks progress, and decides when to continue, backtrack, interrupt or stop.
5. **The top goal** comes from homeostasis in humans and from people in AI.

Transformers have the loop and goal-conditioning, are acquiring the inner loop, and mostly lack the control layer. Below the externally set top goal, their weak points are subgoal hierarchy and goal shielding.

| Have                                | Gaining                                       | Missing                                                                   |
| ----------------------------------- | --------------------------------------------- | ------------------------------------------------------------------------- |
| Step-by-step generator              | Inner loop (reasoning tokens)                 | Native, shielded goal register                                            |
| Large built-in procedural knowledge | External memory; skill documents; code skills | Calibrated controller and stopping sense                                  |
| Goal-conditioning as prediction     | Movement from explicit to latent reasoning    | Compiling new skills from their own experience                            |
| The absorbed culture                | Social scaffolding (RLHF, critics)            | Reversible thought; grounding; learning during a task and across sessions |

**Buildable today:**

- an LLM as G, with separate prompts per mode;
- source separation;
- W as a recited goal and plan file;
- permission gates;
- an episodic log with retrieval;
- memory files with merge and prune;
- self-consistency as an uncertainty proxy;
- token budgets;
- skill libraries (e.g., Voyager);
- reflection.

**Still research:**

- a native goal register that biases every layer;
- calibrated surprise and uncertainty;
- a controller trained on value of computation;
- safe continual weight updates;
- learned hierarchical subgoals.

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
  - goal retention after interruption;
  - injection success rate;
  - late-step adherence;
  - tokens and time;
  - improvement across sessions and regression on earlier families;
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
- Wilson & McNaughton (1994); Foster & Wilson (2006); Pfeiffer & Foster (2013); Kay et al. (2020).
- Mattar & Daw (2018). Prioritized memory access explains planning and hippocampal replay.
- Hassabis et al. (2007); Schacter & Addis (2007). Constructive episodic simulation.
- Ramsauer et al. (2020). Hopfield Networks is All You Need.
- Whittington et al. (2022). Relating transformers to the hippocampal formation.
- Sutton (1990). Dyna.
- Ha & Schmidhuber (2018). World Models.
- Hafner et al. Dreamer.
- Schrittwieser et al. (2020). MuZero.
- Park et al. (2023). Generative Agents.
- Kirkpatrick et al. (2017). Elastic weight consolidation.
- Tononi & Cirelli. The synaptic homeostasis hypothesis.

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
