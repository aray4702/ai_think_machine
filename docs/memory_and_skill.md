# Memory and Skill: How Experience Becomes Knowledge

> An agent with limited compute must compile recurring steps into procedures and stack them into a hierarchy, and an agent that learns while acting must keep fast learning from overwriting what it already knows. Minds solve both with separate stores that learn at different speeds, a small protected working state, and selective consolidation that turns experience into knowledge and deliberation into skill. LLMs carry a huge built-in procedural memory, but they cannot compile new skills from their own experience or consolidate across sessions; agent harnesses are rebuilding complementary learning systems one piece at a time.

Part of the series *Thinking About Thinking Machines*. [One Loop](one_loop.md) derives the step-by-step loop; this essay is about where its steps come from (I.2) and how what it learns is kept (I.6).

Section labels (I.1–I.8, II.1–II.6, R1–R8, P1–P8, claims 1–14) are shared across the series. A reference such as (I.6) points to whichever essay holds that section; the [series map](../README.md#series-map) lists where each one lives.

Each section below follows the same pattern. It starts with a **constraint** that every agent acting in the world faces, derives the **consequence** that follows from it, and gives **evidence** from humans and machines that the consequence holds.

Any sequence can be factored as p(x₁…xₙ) = ∏ p(xₜ | x₍<ₜ₎), so step-by-step dependence alone is not the claim. The derivations below predict *specific* structure beyond that: structure an arbitrary sequence would not have.

## Contents

- [I.2 Limited compute and memory → compile steps into procedures, and stack them](#i2-limited-compute-and-memory--compile-steps-into-procedures-and-stack-them)
- [I.6 Learning fast overwrites old knowledge → separate memories and consolidate](#i6-learning-fast-overwrites-old-knowledge--separate-memories-and-consolidate)
- [A sleep cycle for agents](#a-sleep-cycle-for-agents)
- [Design rules](#design-rules)
- [Test](#test)
- [Summary](#summary)
- [References](#references)


## I.2 Limited compute and memory → compile steps into procedures, and stack them

**Constraints:** Human working memory holds about four chunks. Deliberation is slow and costly.

**Consequence:** Steps that recur must be **compiled** into procedures that run without deliberation, and a sequence at one level must be **chunked** into a single step for the level above. The result is a hierarchy of loops, each on its own timescale.

![I.2: practice compiles reach, grasp and pull into one step, "open the door", freeing working memory; stacked, each step at one level (plan, action, perception) is a whole loop at the level below.](../assets/images/one-loop-i2-compile-stack.svg)

The loop itself is a **TOTE unit** (Miller, Galanter & Pribram, 1960): *Test* the state against the goal, *Operate*, *Test* again, *Exit* when they match. Their main further claim was that TOTE units **nest**: hammering a nail is (lift hammer → strike), repeated until the nail is flush. So the seven processes of the observation section are better seen as **levels of one hierarchy** than as parallel processes, where each level's step becomes the goal of the level below:

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
- **Procedural memory is a separate system:** The amnesic patient H.M. improved at mirror drawing over days with no memory of ever practicing it (Milner, 1962). In Squire's taxonomy, *declarative* memory is episodic plus semantic, and *non-declarative* memory is procedural, priming and conditioning. Semantic and procedural memory learn differently and belong in separate stores (I.6).
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


| Form                                       | Stage                                                         | Example                                                    |
| ------------------------------------------ | ------------------------------------------------------------- | ---------------------------------------------------------- |
| Instructions or skill documents in context | Cognitive: a novice reading the manual; slow, costs attention | Prompted procedures; skill files loaded by agent harnesses |
| Executable code and tools                  | Externalized automaticity: runs without deliberation          | Voyager's code-skill library; scripts; APIs                |
| Adapters or weights trained by practice    | Autonomous: true procedural memory                            | Fine-tuning or distillation from successful trajectories   |


The missing piece in LLMs is **practice-driven compilation**: moving a procedure from the first row to the second and third automatically through repetition, with forward models and reliability estimates attached (R5).

## I.6 Learning fast overwrites old knowledge → separate memories and consolidate

**Constraint.** A distributed network that learns new things quickly overwrites what it already knew (*catastrophic interference*, McCloskey & Cohen, 1989; the stability–plasticity dilemma). LLMs have the dilemma in its pure form: fine-tune naively on today's session and you damage what the model already knew. And the optimal agent needs a belief state but cannot afford to keep, or re-read, everything.

**Consequence.** Use **separate stores** that learn at different speeds, and **consolidate** selectively from fast to slow:


| Store        | Kind                  | Brain                     | Role                                       | Learns by                                     |
| ------------ | --------------------- | ------------------------- | ------------------------------------------ | --------------------------------------------- |
| Working W    | Active                | Prefrontal cortex         | Goal stack and belief; small and protected | Gated updates                                 |
| Episodic E   | Declarative           | Hippocampus               | One-shot events, cue-based recall          | One-shot logging                              |
| Semantic M   | Declarative           | Neocortex                 | Gist, world knowledge, invariants          | Consolidation into gist                       |
| Procedural P | Non-declarative       | Basal ganglia, cerebellum | Skills: the steps of the loop (I.2)        | Practice, reward and error-driven compilation |
| Weights θ    | Substrate for M and P | Synapses                  | Long-term storage of knowledge and skill   | Slow distillation                             |


![I.6: one network learning fast overwrites old skills (catastrophic interference). The brain instead uses separate stores that learn at different speeds: working memory (seconds), episodic memory (one shot), and slow semantic and procedural stores, with consolidation in sleep keeping only what is tagged by reward, surprise or emotion. Transformer agents lack working memory and mostly lack consolidation.](../assets/images/one-loop-i6-memory-stores.svg)

**Compress, or keep everything?** In a POMDP the optimal agent doesn't need the raw history, only the **belief state**: a summary sufficient to act optimally (formally, a probability distribution over hidden world states). "Later steps depend on previous steps" really means they depend on *a belief built from previous steps* (I.1). There are two ways to approximate it:


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

- **Memory is generative too.** Bartlett (1932) showed that recall is reconstruction, not replay: retrieval is generation conditioned on cues, which is why memories distort. Remembering runs on the same loop as the seven processes of the Observation section, conditioned on a goal and cues. A transformer's context gives verbatim recall instead, which is more accurate but less abstract. **Evidence: what sleep actually does.**
- **Time-compressed replay.** During deep (NREM) sleep, hippocampal sharp-wave ripples replay the day's sequences about 10–20× faster than real time (Wilson & McNaughton, 1994). Ripples coordinate with cortical spindles and slow oscillations to move the information into cortex.
- **Reverse replay at reward sites.** Sequences are played backwards from where reward occurred (Foster & Wilson, 2006). That is credit assignment, much like TD learning propagating value backward.
- **Replay of paths never taken.** Rats replay routes they never ran (Gupta et al., 2010). This is generative replay: the revisable inner loop of I.3, running offline.
- **Selection by tag.** Not everything is kept. Memories tagged by reward, emotion, surprise or expected future relevance are preferentially consolidated; people told they'd be tested later consolidate better (Wilhelm et al., 2011). Emotion is the tag, which ties consolidation to the controller of I.4.
- **Downscaling.** The synaptic homeostasis hypothesis (Tononi & Cirelli) holds that sleep globally weakens synapses, pruning noise and keeping the strong. Forgetting is part of consolidation, not a failure of it.
- **Schema integration and gist.** New information that fits an existing schema consolidates in days rather than weeks (Tse et al., 2007). Over time episodes become semantic gist: details fade, structure remains. This is compression into abstraction again (MDL).
- **REM recombination.** REM sleep mixes memories in new combinations and processes their emotional charge. Hoel's (2021) overfitted brain hypothesis, which is speculative, says dreams are noisy augmentation that prevents overfitting to the day.
- **The wrong things get consolidated too.** False memories are consolidated like true ones (Loftus). The agent version is R6's persistent injection.

**Is the small working memory a bug or a feature?**

- **Bug:** transformers beat SSMs at copying and exact retrieval (Jelassi et al., 2024). Rereading the past exactly is powerful.
- **Feature:** compression forces abstraction. A four-item limit makes you chunk, build schemas and find structure. Newport's (1990) "less is more" hypothesis holds that children's limited memory helps them learn grammar. This links to MDL and grokking: generalization comes from compression.

**Effect on interruptions.** After an interruption, a human rebuilds state from compressed memory and cues ("where was I?"): costly and error-prone, but the goal survives if it was shielded in working memory. For a transformer, an interruption costs nothing while it stays in context, since every token is still there; the risk comes later, when compaction or dilution erodes the goal (I.8).

**Evidence: replay as planning.** Remembering and imagining run on the same machinery.

- **Memory exists for the future.** Patients with hippocampal amnesia can't remember the past, and they also can't imagine new scenes in rich detail; their imagined experiences are fragmented (Hassabis et al., 2007). The constructive episodic simulation hypothesis (Schacter & Addis, 2007) explains why: memory is built to be recombined, and pieces of the past are reassembled to simulate possible futures. Remembering, imagining and planning are one generative process run on different inputs.
- **Theta sweeps: look-ahead at every step.** Within each ~125 ms theta cycle, place cells sweep ahead of the animal's current position. At a fork, consecutive cycles alternate between the possible futures, left, right, left (Kay et al., 2020). Even "on the fly" generation (Observation section, point 1) contains a built-in micro-look-ahead, about eight times a second.
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
- **Continual learning into weights** is the missing last step.

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


**Learning from one example.** Everything above is about *keeping* what was learned. The harder question is how one example can teach anything general at all.

- **Humans do it routinely.** A child learns a new word from a single use (*fast mapping*, Carey & Bartlett, 1978). Adults can recognize and draw a new handwritten character after seeing it once, where standard neural networks needed thousands of examples (Lake, Salakhutdinov & Tenenbaum, 2015).
- **The prior does most of the work.** One example can't define a concept; it can only *choose* among hypotheses the learner already favors. Children assume a new word names a whole object and extend it by shape (the shape bias, Landau, Smith & Jones, 1988). Bayesian models of word learning show how a few examples rapidly narrow a hypothesis space the learner already has (Xu & Tenenbaum, 2007). Characters are learned from one example because they are parsed into strokes the learner already knows how to compose. Analogy does the same at a higher level: map the new case onto a familiar structure (Gentner, 1983).
- **Transformers do it in context.** Put one or a few examples in the prompt and the model generalizes from them with no weight change (Brown et al., 2020). This is the same mechanism as goal-conditioning and interruption: the example enters the context, and the next step is conditioned on it. Pretraining builds the prior; the context selects from it. In-context learning behaves like implicit Bayesian inference (Xie et al., 2022), can implement gradient-descent-like updates inside the forward pass (von Oswald et al., 2023), and relies on circuits such as induction heads that copy patterns from earlier in the context (Olsson et al., 2022).


So one-shot learning splits across the two speeds of this section:

1. **Fast: use the example now.** Hold it in the fast store (hippocampus; the context window) and generalize by attending to it. This works only as far as the prior already contains the right hypotheses.
2. **Slow: decide whether to keep it.** What an LLM learns in context disappears at the end of the session unless it is consolidated. Humans keep one-shot learning when it fits an existing schema, which is also when consolidation is fastest (Tse et al., 2007, above).

Where the two differ:

- **Humans learn from explanations, not just examples.** People ask *why* the example works and generalize the reason, not the surface (explanation-based learning). In-context learning often keys on surface format: models can still do well when the labels in the examples are randomized (Min et al., 2022), and results shift with example order (I.8).
- **Humans tag single events for keeping.** A surprising, rewarded or emotional one-off is stored and consolidated preferentially (selection by tag, above). LLMs weigh every token in context alike and have no mechanism for marking one example as worth keeping.
- **A correction is the most valuable one-shot lesson** (I.7). But one example is also the easiest way to learn the wrong lesson: a single misleading case, or an injected one, generalizes just as readily.

For an agent this suggests a pipeline: log the example verbatim in E; extract the rule it implies as an explicit *hypothesis*; check that hypothesis on the next cases where it applies; and let it through the consolidation gate (R6) into M or P only once it has held up. One example is enough to *act* on, and the inner loop can test it cheaply; it is rarely enough to *keep*.

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

## A sleep cycle for agents

I.6 described what sleep does in the brain. For an agent, the same steps can run between sessions:

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

## Design rules

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

## Test

| #          | Claim       | Principle | Prediction                                                                                                            | Failure would show                                |
| ---------- | ----------- | --------- | --------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------- |
| P3         | 2, 6        | I.2, I.6  | Practice-compiled skills cut compute and errors on repeated task families without regressing old skills               | The procedural-compilation claim fails for agents |

Modules M4 (procedural store) and M5 (sleep consolidation) in [Building the Loop](architecture.md#p6-does-each-module-add-value-beyond-scale-claim-12) measure this across ten simulated "days", including regression on earlier task families. Unlike most modules, their gain is predicted to persist or grow with scale, because learning across sessions doesn't come from scale within a session.

## Summary

**Well supported.**

- **Claim 2: Hierarchy through procedural compilation (I.2).** Steps at each level are compiled procedures. Practice turns deliberation into skill, and chunking turns a sequence at one level into a single step for the level above. That makes deep hierarchies affordable and frees working memory and control.
- **Claim 6: Consolidation (I.6).** Experience must be moved selectively from fast episodic storage into slow semantic and procedural knowledge without overwriting old knowledge, through replay, gist extraction and practice-driven compilation.

**Plausible, needs testing.**

- **Claim 9: One generative model, several uses (I.6).** Remembering, perceiving, planning and acting may share one generative world model run in different modes. This is strongest in rodent navigation and less certain for abstract human planning.

**Evidence status.**

| Claim                                        | Status                                                                                                                                                                       |
| -------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Overfitted-brain theory of dreams            | Speculative                                                                                                                                                                  |
| Hippocampal preplay                          | Debated                                                                                                                                                                      |
| Theta alternation; replay as planning        | Strong in rodent navigation; growing (MEG) but contested for abstract human planning                                                                                         |
| Attention ≈ hippocampus                      | Mathematical equivalence (Hopfield) and model-fitting results, not evidence that the brain computes softmax attention                                                        |

## References

**Procedural memory and hierarchy**

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

**Learning from one example**

- Carey & Bartlett (1978). Acquiring a single new word.
- Landau, Smith & Jones (1988). The importance of shape in early lexical learning.
- Gentner (1983). Structure-mapping: a theoretical framework for analogy.
- Xu & Tenenbaum (2007). Word learning as Bayesian inference.
- Lake, Salakhutdinov & Tenenbaum (2015). Human-level concept learning through probabilistic program induction.
- Brown et al. (2020). Language models are few-shot learners.
- Xie et al. (2022). An explanation of in-context learning as implicit Bayesian inference.
- Olsson et al. (2022). In-context learning and induction heads.
- Min et al. (2022). Rethinking the role of demonstrations: what makes in-context learning work?
- von Oswald et al. (2023). Transformers learn in-context by gradient descent.

**World models, replay and continual learning**

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
- Wang et al. (2023). Voyager.
