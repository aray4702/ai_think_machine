# ![One Loop icon: a goal at the center, a dashed reversible inner loop, and a solid outer loop of committed steps, one of which is itself a loop](../assets/images/one-loop-icon.svg) One Loop: Minds and Transformers

*About the logo: the goal sits at the center. The dashed inner loop is reversible simulation and search; the solid outer loop is irreversible, committed steps. One step is drawn as a loop of its own, because every step is a lower-level loop.*

> At the level where behavior is committed step by step, minds and LLM agents run the same loop: choose the next step from the goal and what has happened so far, commit it, observe. The loop itself is cheap. What makes it work is control, and two decisions matter most: **how much reversible deliberation goes before a commitment**, which should scale with how costly that commitment is to undo, and **which inputs may change the goal rather than only inform the next step**. Transformers supply the generator. LLM agents (a model plus its harness) handle both decisions poorly, for architectural reasons rather than ones inherited from human text. Four tests could show this is wrong.

This essay begins with an observation, derives the loop and its two control decisions from constraints that any agent faces, and ends with tests that could prove it wrong. Humans and transformers serve as evidence, not as premises.

It is the first essay in the series *Thinking About Thinking Machines*. The rest of the framework has its own essays:

- [When to Stop](when_to_stop.md): the stopping problem and control signals (I.4).
- [Memory and Skill](memory_and_skill.md): compiled procedures, separate memory stores and consolidation (I.2, I.6).
- [Learning in Order](development.md): the edge of competence, development, teaching and imitation (I.7).
- [Building the Loop](architecture.md): an agent architecture assembled from all of them, and a test of whether its modules beat scale (II).

Section labels (I.1–I.8, II.1–II.6, R1–R8, P1–P8, claims 1–14) are shared across the series. A reference such as (I.6) points to whichever essay holds that section; the [series map](../README.md#series-map) lists where each one lives.

## Contents

- [The observation](#the-observation)
- [Scope](#scope)
- [I.1 Too many futures to plan in advance → commit one step at a time and use feedback](#i1-too-many-futures-to-plan-in-advance--commit-one-step-at-a-time-and-use-feedback)
- [I.3 Some outputs can't be taken back → put a reversible inner loop in front](#i3-some-outputs-cant-be-taken-back--put-a-reversible-inner-loop-in-front)
- [I.5 The context mixes sources → the goal must be shielded](#i5-the-context-mixes-sources--the-goal-must-be-shielded)
- [I.8 The analogy makes predictions about humans](#i8-the-analogy-makes-predictions-about-humans)
- [Design rules](#design-rules)
- [Tests](#tests)
- [Summary and open questions](#summary-and-open-questions)
  - [Summary](#summary)
  - [Open questions](#open-questions)
- [References](#references)


## The observation

Many human processes seem to share a structure with transformer next-token generation:

1. **Perception** unfolds through successive observations, guided by what we are trying to find out. Our eyes make rapid shifts called saccades; each shift draws on what we have seen so far. We stop looking when we have enough information or something interrupts us.
2. **Reasoning** develops thought by thought toward an answer. Each thought builds on earlier ones, sometimes revisiting or correcting them, until we reach a conclusion or are interrupted.
3. **Planning** develops a course of action step by step. Each choice shapes the next, and later considerations may lead us to revise earlier choices.
4. **Execution and navigation** turn intentions into successive decisions. A plan or map provides direction, while each next step responds to our current situation and what happened before.
5. **Physical action** often begins with an intended outcome rather than a fully specified sequence of movements. Each movement adjusts to the effects of preceding movements and incoming sensory feedback.
6. **Talking and writing** unfold word by word. We may know what we want to express without having chosen every word; the wording develops as we proceed, with opportunities for correction and revision.
7. **Transformers** generate outputs token by token, conditioned on the available context and previously generated tokens. These outputs can represent text, speech, audio, video, or actions. Generation ends when a stopping condition is met, and new information added to the context can redirect subsequent output.

All of these have goals, run sequentially with or without backtracking, end in a conclusion or an interruption, and handle interruptions and off-track events by attending to relevant information and ignoring irrelevant information.

All seven processes can be written as a policy:

$$
\text{next step} = f(\text{goal}, \text{everything so far})
$$

This is what a transformer computes. It's also how agents work in reinforcement learning, and how predictive processing describes the brain.

Handling interruptions is the most interesting part. In a transformer, being interrupted just means new tokens enter the context and the next step adapts. Human action works the same way: a sensory surprise changes the next step without throwing away the whole plan.

##### **Comparisons between minds and transformers**

- **Goal**: whatever conditions the sequence toward an end state. It may be set from above, triggered by the environment, driven by needs or curiosity, or **reconstructed after the fact**.
- **Step**: a committed output at a given level of the hierarchy. For perception, reasoning, planning, action and speech, any sequence can be factored as p(x₁…xₙ) = ∏ p(xₜ | x₍<ₜ₎), and the shared mechanism works as general next-step predictor, plus attention over history.
- **Step is not planned beforehand**: the full sequence is not *explicitly represented* in advance. The internal state can still carry *implicit look-ahead*: speech errors show that later words are already active; hippocampal "theta sweeps" alternate between possible futures about eight times a second (I.6); LLMs choose a rhyme before writing the line. So the two are compatible: steps are generated on the fly, but the state looks ahead.
  - Lashley's *The Problem of Serial Order in Behavior* (1951) argued that behavior can't be pure chaining.
  - Speech errors show that people already hold later words in mind before saying them. Anticipation slips ("a leading list" for "a reading list") and spoonerisms are the evidence.
  - The next saccade target is computed during the current fixation.
  - Interpretability research found that LLMs pick a rhyme word before writing the line that ends in it.
- **Backtracking means different things in different cases.** Neither speech nor a transformer can erase what it has produced; both "backtrack" by appending a repair ("uh, I mean…", or "Wait, …" in reasoning models). Writing with editing, and mental backtracking in reasoning, really can revise earlier output. That is closer to search, or to diffusion-style refinement, than to pure autoregression. Which one appears depends on reversibility (I.3).


##### **Contrasts between minds and transformers**

- **Memory architectures differ.** Human working memory holds about four items. People compress history into a running state and rely on external memory (notes, maps). That is closer to an RNN or state-space model than to a transformer that can attend back to its whole raw context.
- **Learning while acting.** A human's "weights" change during the task. A transformer's weights are frozen at inference, so anything it learns mid-task has to live in its context (I.6).
- **Grounded, closed-loop feedback.** Humans get a continuous sensory stream. A model gets feedback only when something is injected into its context, such as a tool result or a user message.
- **Felt salience.** Emotion and body state decide what is relevant and when to stop. Goals persist as motivation and body state (Damasio), and stopping is a felt sense of satisfaction or "done." In a transformer, the goal is just conditioning text and stopping is an end-of-sequence token (I.4).
- **Offline simulation.** Humans can mentally rehearse a plan before acting. Reasoning models approximate this with hidden thinking tokens (I.3).
- **Hierarchy across timescales.** Humans nest goals → subgoals → actions → micro-movements, each running on its own timescale. A transformer is flat and has to learn any hierarchy implicitly (I.2).


## Scope

![Scope of the One Loop thesis: shared supporting functions coordinate domain-specific knowledge and skills; underlying mechanisms implement the supporting functions.](../assets/images/one-loop-scope.svg)

The series examines the **supporting functions** that organize intelligent activity across domains: committing one step at a time using feedback, compiling steps into nested procedures, simulating and revising before committing, deciding when to continue or stop, maintaining and shielding the goal, consolidating learning selectively, and learning at the edge of competence (I.1–I.7). Domains such as language, spatial reasoning, and social or emotional understanding supply specialized knowledge, representations and skills; the supporting functions coordinate when and how those resources are used, revised and learned. For example, composing a sentence and navigating a route require different knowledge and skills, but both involve maintaining a goal, evaluating possible next steps and adjusting to feedback. Capable behavior depends on their interaction: a shared control structure alone does not explain competence in a particular domain. An operating system is a useful analogy: the supporting functions are the **kernel** (scheduling steps, handling interrupts, managing memory), the domains are **services** that run on it, and the underlying mechanisms are the **hardware**, which services reach only through the kernel. The analogy is about roles, not components: a kernel is one separate body of code, whereas whether these functions need explicit modules is left open (II.6). This essay covers three of the seven: the step-by-step loop itself (I.1), the reversible inner loop (I.3) and the shielded goal (I.5).

The series focuses on the **serial control level** of behavior: the level at which an agent commits outputs one after another (gaze shifts, words, moves, decisions, actions) in pursuit of something. Domain-specific capabilities serve as examples, rather than subjects of a complete theory. This level runs on top of parallel, continuous machinery the document does not describe: fast feed-forward recognition, motor dynamics, background monitoring. It is a **functional** claim, not a claim that brains and transformers share a mechanism.

---

Each section below follows the same pattern. It starts with a **constraint** that every agent acting in the world faces, derives the **consequence** that follows from it, and gives **evidence** from humans and machines that the consequence holds.

Any sequence can be factored as p(x₁…xₙ) = ∏ p(xₜ | x₍<ₜ₎), so step-by-step dependence alone is not the claim. The derivations below predict *specific* structure beyond that: structure an arbitrary sequence would not have.

## I.1 Too many futures to plan in advance → commit one step at a time and use feedback

**Constraints:**

- **Too many possible sequences.** With b options per step and n steps there are bⁿ complete sequences; they can't all be searched. Committing one step at a time turns that into n choices of size b. For outputs that can't be revised once out, that is the affordable way to produce long sequences; where revision is cheap, refinement is an alternative (I.3).
- **The world is noisy and changes while you act**, so a fully precomputed open-loop plan goes stale. Control theory shows that closed-loop feedback beats open-loop planning under noise.
- **The world is only partly observable**, and acting is often the only way to find out more.
- **Memory and compute are limited**, so the full history can't be kept and reprocessed at every step.
- **Committed outputs come out one at a time.** There is one mouth, one gaze and one body position. Even if thinking runs in parallel, what gets committed must be serialized.

**Consequence:** Commit one step, observe, and generate the next step from an updated **belief state**: a summary of history sufficient for acting well. Under partial observability (formally a POMDP), the optimal action depends on exactly such a belief state. Formally, the next step depends not on the raw history but on *a belief built from previous steps*. Brains compress history into a running state; transformers keep the raw history and attend to it. These are two approximations of the same belief state (I.6). A plan or map can still guide the loop, but as a prior, not as a script.

![I.1: planning the whole sequence first means searching bⁿ futures and running one as a script that goes stale; the closed loop instead chooses one step from a belief state and the goal, commits it, observes the outcome and updates the belief.](../assets/images/one-loop-i1-step-feedback.svg)

**Why the processes of minds and transformers look alike.** The problem forces it. Step-by-step generation that conditions on history and absorbs interruptions is what any capable agent with limited compute, an unpredictable world and a goal ends up doing for outputs it can't take back; it can't plan the whole sequence in advance, because too much would change before it finished. Brains and transformers may both have arrived at this loop because it is the standard tractable solution for irreversible commitments under uncertainty, not by coincidence and not because they share a mechanism. The observation in the observation section is then a claim about the structure of sequential decision-making under uncertainty, not just a similarity between brains and AI. The strongest counter-argument, that LLMs inherited the structure from human text, is weighed in the [Summary](#summary).

**Evidence:**

- **Humans:** Saccades are information-gathering actions: each one is taken to gather information for the next decision. Under predictive processing, perception is active sampling to reduce prediction error, so a saccade sequence is generation too, and perception sits fully inside the loop rather than only feeding it. Motor control is closed-loop, and Todorov's optimal feedback control goes further: the motor system corrects only deviations that matter for the task and lets the rest go (the *minimal intervention principle*). Speech is produced incrementally, with implicit look-ahead.
- **Machines:** Engineered systems arrive independently at the same loop. Model predictive control plans over a short horizon, executes only the first step, observes and replans; this is how navigation (point 4 in Observation section) can follow a plan or map and still decide on the fly. AlphaZero searches ahead, commits one move and searches again. Transformers generate token by token, and an injected interruption simply becomes part of the next step's conditioning.
- **Biology without brains:** Bacterial chemotaxis runs the same run–sense–adjust cycle.


## I.3 Some outputs can't be taken back → put a reversible inner loop in front

**Constraint:** Many commitments are **irreversible**: you can't unsay a word or unthrow a ball. Errors in them are costly.

**Consequence:** Wherever errors are expensive, the agent needs two loops:

- an **inner loop** of cheap, revisable simulation (refining, searching, backtracking) in imagination or on scratch paper;
- an **outer loop** of irreversible commitment to the world, one step at a time, with feedback.

What defines the inner loop is **reversibility**: its operations can be undone or compensated, and they preserve invariants. Thinking is the revisable space that evolved so we don't commit too early.

Step-by-step generation is forced where outputs are **irreversible commitments to an uncertain world**. Where outputs can be cheaply revised, **iterative refinement** appears instead: diffusion models refine a whole image in parallel, and humans do the same when sketching, editing an essay or imagining. So all seven processes in the Observation section run the same outer loop; what differs is how much revisable inner loop sits in front of each commitment. Transformers started as outer-loop-only machines, and much recent progress amounts to adding an inner loop.

![I.3: a reversible inner loop (propose, check, revise or undo) passes its result through a one-way commit into the outer loop of irreversible steps in the world, and feedback returns to the inner loop. How much inner loop sits in front depends on the cost of revising a committed step, from planning (free) to motor action (impossible).](../assets/images/one-loop-i3-two-loops.svg)

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
- **The reversal curse** (Berglund et al., 2023). Models trained on "A is B" often fail at "B is A," which looks like a failure of reciprocity in learned knowledge. The reading is weaker than it seems, though: models reverse relations fine when both are in context (see [Summary](#summary)).
- **Conservation failures.** Entity and state tracking breaks down over long sequences of operations; video generators make objects appear, vanish or change count; counting fails after a transformation. These are classic preoperational errors: judging by surface state instead of tracking the transformation.
- **Verification by inversion helps.** Substituting a solution back into the original equation, or round-tripping a transformation, catches many LLM errors. It is an underused form of self-checking.


## I.5 The context mixes sources → the goal must be shielded

**Constraint.** An agent's input mixes its own intentions, other people's instructions, things it observes, and its own habits. Any of these can push it toward a different goal.

**Consequence.** The goal must be **maintained** and **shielded**: information that *informs the next step* must be kept separate from information that *changes the goal*. Content can be mimicked, so shielding has to work by **source** and **salience**, not by content. Without a protected goal there is nothing to judge relevance against, and everything in context competes equally.

![I.5: inputs arrive tagged by source; a gate lets a trusted source or a high-salience event change the shielded goal, while everything else, including instructions found in a web page, may only inform the next step. Without a gate, a transformer's context is one flat stream in which injected text can act as an instruction. Shielding is a dial between distractibility (prompt injection) and perseveration.](../assets/images/one-loop-i5-goal-gate.svg)

**What a goal is.** Every process in the Observation section "starts with a goal," and that is the one part the loop itself can't explain. One answer: a goal is **a prediction the agent makes come true**.

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

So interruptions are absorbed with **graceful degradation, not robustness**: recovery depends on how well the goal was maintained (I.8).

**Back to the Observation section.** Every case there "attends to relevant information and ignores irrelevant information." The shielded goal is what makes that possible. Relevance exists only relative to a goal: without a protected goal, nothing in the context has priority over anything else, which is the transformer's weakness. Humans cope with interruptions as well as they do not by attending to everything, but because a gate checks where each input came from and how salient it is, then decides whether it may **change the goal** or only **inform the next step**. That distinction is probably the most useful practical lesson for building agents.

## I.8 The analogy makes predictions about humans

The sections above, with the companion essays, derived the shared structure from constraints; this section puts it to use and asks what it predicts. If humans and transformers both compute **next step = f(goal, everything so far)**, effects known in one should show up in the other. Several hold up:


| Prediction                                         | Humans                                                                                                    | Transformers                                                                        |
| -------------------------------------------------- | --------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| What's earlier in context biases what comes next   | Order and priming effects: anchoring, framing                                                             | Prompt-order and example-order effects                                              |
| Writing steps down improves reasoning              | Thinking aloud or on paper gives an external context window beyond ~4 working-memory items                | Chain-of-thought                                                                    |
| Errors compound                                    | Garden-path sentences; getting lost after one wrong turn                                                  | Exposure bias; a wrong early step keeps priming later ones (R2)                     |
| Interruption recovery depends on surviving context | "Where was I?": resumption lags and switching costs (Altmann & Trafton) scale with goal maintenance (I.5) | Full recovery while the context is intact; drift once it is truncated or summarized |


Writing steps down is also Vygotsky's private speech (I.7): the external context window comes first, and its compression into inner speech comes later.

## Design rules

Turned into rules for building agents, I.3 and I.5 give the first four design rules. R5–R8 belong to the companion essays, and [Building the Loop](architecture.md) collects all of them.

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

The salience signal is the controller of I.4, with surprise opening the gate, so goal shielding and the emotion-like control layer are **one mechanism**. Shield too hard and you get perseveration: an agent that ignores the user's "stop, that's wrong." Shield too little and you get injection.

Fixes available today, mapped to the brain mechanisms of I.5:


| Brain mechanism                 | AI approach                                                                                                                                                                          | Status                                                        |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------- |
| Source tagging                  | Instruction hierarchy (trained system > user > tool priority); delimiting and datamarking (spotlighting); role embeddings that mark data tokens in the representation (StruQ, ASIDE) | Deployed or research; reduces but doesn't eliminate injection |
| Gate that blocks distractors    | Dual-LLM / CaMeL: a privileged planner sees only trusted input and writes the control flow; a quarantined model reads untrusted data but can't choose actions                        | Strongest guarantees; costs flexibility                       |
| Active maintenance by rehearsal | Goal recitation: keep a to-do or plan file and restate it near the end of the context, in the high-attention region                                                                  | Common in agent harnesses; cheap; works well against drift    |
| Gating the action stage         | Permission systems: tool calls need approval or an allowlist, whatever the context says                                                                                              | Defense in depth                                              |
| Persistent top-down bias        | A goal vector outside the token stream that steers every layer, like goal-conditioned activation steering                                                                            | Mostly a research idea                                        |


## Tests

Each claim comes with a prediction that could fail. P1, P2 and P7 test parts of the loop; P8 tests the unification itself.

| #          | Claim       | Principle | Prediction                                                                                                            | Failure would show                                |
| ---------- | ----------- | --------- | --------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------- |
| P1         | 3           | I.3       | At equal compute, forkable (reversible) inner loops beat append-only chain-of-thought on tasks that need backtracking | The reversibility section is decorative           |
| P2         | 5           | I.5       | A goal register + source tagging reduces injection and drift more than goal recitation alone                          | The goal-shield architecture is unnecessary       |
| P7 (human) | 5           | I.5, I.8  | Interruption recovery is predicted by goal-maintenance measures, not general intelligence                             | The goal-shielding account of interruption fails  |
| P8 (unification) | 1, 3 | I.1, I.3 | With task difficulty held fixed, the amount of deliberation before a commitment rises with the cost of revising it, in humans (speaking vs writing; pen vs keyboard) and in agents (the same task against a sandbox vs a live system) | Minds and agents share a description but not its control; "one loop" reduces to the chain rule |

P8 matters most for this essay. P1, P2 and P7 test components that could each be true on its own. P8 tests whether the same variable governs the loop in both minds and agents, which is what makes the shared description more than the chain rule. It needs two controls: difficulty must be matched across conditions, and the agent's instructions must not mention the cost of mistakes, so any effect comes from the agent's own reading of the situation rather than from being told.

The remaining predictions (P3–P6) belong to the companion essays, and [Building the Loop](architecture.md#ii6-validate-before-you-keep-the-bitter-lesson) gives the full experimental design for testing each module against scale.

## Summary and open questions

### Summary

**The derivation at a glance.**

| Section | Constraint                                | Consequence                                |
| ------- | ----------------------------------------- | ------------------------------------------ |
| I.1     | Too many futures to plan in advance       | Commit one step at a time and use feedback |
| I.3     | Some outputs can't be taken back          | Put a reversible inner loop in front       |
| I.5     | The context mixes sources                 | Shield the goal by source and salience     |

Put together: a loop that commits one step at a time from a belief about the world, with a reversible inner loop sized by the cost of undoing each commitment, and a goal gate that decides whether an input may change the goal or only inform the next step. I.8 showed that known effects (priming, thinking on paper, compounding errors, interruption recovery) line up in humans and transformers, as a shared structure would lead one to expect.

The other four constraints, and what follows from them, are derived in the companion essays: limited compute and memory in [Memory and Skill](memory_and_skill.md) (I.2), the cost of thinking in [When to Stop](when_to_stop.md) (I.4), fast learning overwriting old knowledge in [Memory and Skill](memory_and_skill.md) (I.6), and the edge of competence in [Learning in Order](development.md) (I.7).

**What is supported, and what isn't.** Each claim below is well supported *in its own field*: POMDPs and control theory for claim 1, search and Piaget for claim 3, prefrontal gating for claim 5. What this essay adds is that one structure, with the same two control variables, governs both minds and LLM agents. That unification is not established by the evidence above; P8 tests it.

**Well supported.**

- **Claim 1: Serial control loop (I.1).** At the commitment level, perception (gaze), reasoning, planning, action and language each generate the next step conditioned on a goal and a belief built from history. For irreversible commitments, committing one step at a time with feedback is the tractable solution under huge option spaces, noise, partial observability and limited memory, which is why engineered systems (MPC, game search) arrive at it too.
- **Claim 3: Two loops, separated by reversibility (I.3).** A revisable inner loop (simulation, search, drafting) sits in front of an irreversible outer loop (commit, then feedback). Inner-loop operations can be undone or compensated and preserve invariants, which allows cheap backtracking and verification before commitment. How much inner loop precedes a commitment scales with the cost of error, uncertainty and time available.
- **Claim 5: Goal maintenance determines interruption handling (I.5).** Interruptions are handled with graceful degradation, not robustness: recovery depends on how well the goal was maintained and shielded. Shielding must separate information that informs the next step from information that changes the goal, using source and salience rather than content.

**Speculative.**

- **Claim 13: Convergence vs inheritance.** Some parallels between LLMs and human cognition may be inherited from human text rather than convergent. Claim 1's generality rests on evidence from agents trained without human data, not on LLM resemblance.

**How the claims were narrowed.** Several first-draft claims overreached. The forms above are the narrowed ones:

- **Serial control level, not all of cognition.** Several processes aren't naturally discrete or serial. Fast object recognition takes about 100 ms through a mostly feed-forward sweep with no saccade sequence (Thorpe et al., 1996); motor control looks like continuous neural population dynamics (Shenoy; Churchland); and walking, talking and monitoring run at once. The loop describes the serial bottleneck (conscious access and committed outputs, as in Global Workspace theory), which sits on top of parallel, continuous machinery (Scope). Same description is not same mechanism.
- **Goals are one source of conditioning among several.** Much behavior isn't goal-initiated: habits, exploration, play, mind-wandering. Goals are often constructed after the fact: in choice blindness people defend choices they never made (Johansson & Hall, 2005), and Gazzaniga's split-brain "interpreter" invents reasons for actions it didn't cause. Goals can be set from above, triggered by affordances, driven by needs or curiosity, or inferred afterwards (the definition of goal in the Observation section; I.5).
- **Graceful degradation, not robustness.** Humans are bad at interruptions: there is a measurable resumption lag, switching costs, and errors after interruption (Altmann & Trafton's memory-for-goals model), and LLM agents degrade too. Both can recover, at a cost that depends on how well the goal was maintained (claim 5).
- **"Not planned beforehand" allows look-ahead.** Steps are generated on the fly, yet the state carries look-ahead (theta sweeps, rhyme planning, MPC). The two are compatible because "planned" means *explicitly represented as a full sequence*, which is how the Observation section defines it.

### Open questions

**Open weaknesses, most serious first.** Each comes with what it costs the thesis and how it will be tested.

1. **Unfalsifiability risk.** "One step-by-step loop" fits any sequential process, by the chain rule. A frame that absorbs everything predicts nothing, and I.8 shows that known effects line up, which is consistent with the thesis but not a test of it. This essay's answer is to narrow the claim to two control decisions and commit to predictions that could fail: P1, P2, P7 and especially P8.
2. **Convergence vs inheritance is unresolved, and it matters.** Transformers are trained on human-produced text, a record of human sequential thinking, so LLMs may look human-like because they inherited the structure, not because I.1 forces it; then their similarity to human cognition says little about whether the loop is a general solution. Much of the AI side of the thesis quietly assumes convergence. Agents trained without human data, such as reinforcement-learning robots or AlphaZero, still develop closed-loop, replan-every-step policies, which supports convergence. *Next:* label the language-specific parallels as possibly inherited, and test the loop in agents trained without human data (claim 13; learner (i) of P5 in [Learning in Order](development.md#p5-does-capability-order-matter-claims-11-and-14)).

Two further objections belong to the companion essays: the bitter lesson against an architecture of many modules ([Building the Loop](architecture.md#summary)), and whether the developmental order is necessary ([Learning in Order](development.md#summary)).

**Evidence status.**

| Claim                                        | Status                                                                                                                                                                       |
| -------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Reversal curse as missing reciprocity        | Weaker than claimed: models reverse relations fine in context. The curse concerns how training stores facts, an asymmetry in storage, not an inability to reverse operations |

## References

**Serial order and closed-loop control**

- Lashley (1951). *The Problem of Serial Order in Behavior.*
- Miller, Galanter & Pribram (1960). *Plans and the Structure of Behavior.*
- Craik (1943). *The Nature of Explanation.*
- Todorov & Jordan (2002). Optimal feedback control.

**Goals and shielding**

- Friston. Active inference.
- Chen et al. (2021). Decision Transformer.
- Miller & Cohen (2001). An integrative theory of prefrontal cortex function.
- O'Reilly & Frank (2006). PBWM.
- Duncan, Emslie, Williams, Johnson & Freer (1996). Intelligence and the frontal lobe: the organization of goal-directed behavior.
- Lhermitte (1983). "Utilization behaviour" and its relation to lesions of the frontal lobes.
- Johansson & Hall (2005). Choice blindness.
- Altmann & Trafton (2002). Memory for goals.
- Wallace et al. (2024). The instruction hierarchy.
- Debenedetti et al. (2025). CaMeL: defeating prompt injections by design.
- Debenedetti et al. (2024). AgentDojo: a dynamic environment to evaluate prompt injection attacks and defenses for LLM agents.
- O'Reilly, Munakata, Frank, Hazy et al. *Computational Cognitive Neuroscience.*
- Milner (1963). Effects of different brain lesions on card sorting (Wisconsin Card Sort perseveration).
- Hines et al. (2024). Defending against indirect prompt injection attacks with spotlighting.
- Chen et al. (2024). StruQ: defending against prompt injection with structured queries.
- Zverev et al. (2025). ASIDE: architectural separation of instructions and data in language models.
- Willison (2023). The dual LLM pattern for building AI assistants that can resist prompt injection.

**Reversibility**

- [Book][Piaget & Inhelder. The Psychology of the Child](https://www.alohabdonline.com/wp-content/uploads/2020/05/The-Psychology-Of-The-Child.pdf)
- Janner et al. (2022). Diffuser: planning with diffusion.
- Berglund et al. (2023). The reversal curse.
- Ernst et al. (2007). The Daikon system for dynamic detection of likely invariants.
- Garcia-Molina & Salem (1987). Sagas.

**Scope**

- Thorpe et al. (1996). Speed of processing in the human visual system.
- Churchland, Shenoy et al. (2012). Neural population dynamics during reaching.
- Baars (1988). *A Cognitive Theory of Consciousness* (Global Workspace theory).
