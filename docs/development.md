# Learning in Order: Development, Teaching and Imitation

> Practice teaches only at the edge of competence, where success is possible but unreliable, under support that fades; and some capabilities can only be built on others. Piaget explains how an agent constructs structure from its own action, Vygotsky where its content, tools and pace come from, and imitation how both humans and LLMs acquire most of that content. LLMs entered the developmental order at the top, by reading the culture. Whether agents should back-fill the lower stages in their own action domain is an open question, and a testable one.

Part of the series *Thinking About Thinking Machines*. The other essays describe a mature agent; this one asks how it gets there.

Section labels (I.1–I.8, II.1–II.6, R1–R8, P1–P8, claims 1–14) are shared across the series. A reference such as (I.6) points to whichever essay holds that section; the [series map](../README.md#series-map) lists where each one lives.

Each section below follows the same pattern. It starts with a **constraint** that every agent acting in the world faces, derives the **consequence** that follows from it, and gives **evidence** from humans and machines that the consequence holds.

Any sequence can be factored as p(x₁…xₙ) = ∏ p(xₜ | x₍<ₜ₎), so step-by-step dependence alone is not the claim. The derivations below predict *specific* structure beyond that: structure an arbitrary sequence would not have.

## Contents

- [I.7 Learning signal lives at the edge of competence → development has an order](#i7-learning-signal-lives-at-the-edge-of-competence--development-has-an-order)
- [II.4 Build order](#ii4-build-order)
- [Design rule](#design-rule)
- [P5: Does capability order matter? (claims 11 and 14)](#p5-does-capability-order-matter-claims-11-and-14)
- [Summary](#summary)
- [References](#references)


## I.7 Learning signal lives at the edge of competence → development has an order

**Constraints.**

- Practice teaches nothing when a task always succeeds or always fails.
- Some capabilities can only be built on top of others.

**Consequences.**

- Learning happens in the **zone of proximal development** (ZPD): where success is possible but unreliable, under support that fades. In group-relative RL methods such as GRPO, problems that are always or never solved produce zero gradient, so this is the ZPD stated mathematically.
- Capabilities form a **dependency order**: forward models before planning, planning before verification, a shielded goal before safe autonomy. Piaget's stages, below, are one human realization of these dependencies, not a necessary order (see [Summary](#summary)).

![I.7: learning signal is zero when a task always fails or always succeeds and peaks in the zone of proximal development; scaffolding pulls a too-hard task into the zone and fades as competence grows. Capabilities build in order, from forward models to planning, verification, and hypotheses with metareasoning; learning happens one step above what is mastered.](../assets/images/one-loop-i7-edge-of-competence.svg)

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


| Vygotsky                                                                                        | Where it appears in the thesis                                                                                                                                            |
| ----------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Private speech grows with difficulty, then goes underground                                     | Chain-of-thought: reasoning models think longer on harder problems. Distilling reasoning into direct answers, or latent "continuous thought," is speech going underground |
| Piaget vs Vygotsky on "egocentric speech": a symptom of egocentrism, or a self-regulation tool? | The same debate about whether chain-of-thought is real reasoning or decoration. The evidence favors Vygotsky: it regulates the process                                    |
| Functions move from social to individual                                                        | Thought as internalized action (I.3), but the source is dialogue: the inner loop is partly internalized argument, as in self-critique and multi-agent debate              |
| Other-regulation → self-regulation                                                              | The controller and goals start external: a parent's instruction, a user's goal. Self-regulation grows within those goals (I.5)                                            |
| Psychological tools                                                                             | External memory and scaffolding: notes, scratchpads, memory files, tools. Writing as an external context window (I.8)                                                     |
| Culture passes on compiled procedures (long division, reading)                                  | Procedural memory transmitted, not discovered: the cultural ratchet (I.2)                                                                                                 |
| Imitation works only within the ZPD                                                             | Piaget's deferred imitation, plus a limit on what can be imitated                                                                                                         |


**What Vygotsky adds.**

- **The ZPD is a formal training principle.** In group-relative RL methods such as GRPO, problems the model always or never solves give zero learning signal; only intermediate pass rates produce gradient. Oudeyer's learning-progress curiosity is an agent choosing its own ZPD.
- **Scaffolding fades.** Hints, partial plans, demonstrations, restricted tool sets and human approvals are support, and should fade as reliability grows. This ties directly to the reliability record of each skill in P (R5).
- **Scientific concepts meet everyday ones.** LLMs have the scientific concepts (systematic, verbal, from reading) without the everyday ones (grounded in their own action). Pretraining supplied the downward growth; Piaget's back-fill (II.4) is the upward growth; grounding is where they meet.
- **Shared intentionality** (Tomasello): joint attention, common ground, we-goals, teaching by pointing. For agents: track what both parties are attending to (the open file, the selected code), maintain common ground (what has been agreed), and plan *with* the user, not just for them. This requires the decentration and theory of mind of the Piaget stages.
- **Legitimate peripheral participation.** Newcomers start with low-risk peripheral tasks and earn responsibility. For agents, autonomy expands along the reversibility ladder (II.4), and scaffolding fades class by class.
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

- **Pretraining is imitation.** Next-token prediction on human text is behavior cloning on the written record of human sequential behavior: speech, argument, worked solutions, thinking set down on paper. The generator of this thesis was learned largely by imitating people. That sharpens claim 13: if LLMs learned by copying humans, their resemblance to humans is the expected outcome and says little about whether the loop is a general solution.
- **Good imitation copies the goal, not the movements.** Eighteen-month-olds who watch an adult *fail* to pull a toy apart still pull it apart: they reproduce the intended act, not the observed one (Meltzoff, 1995). Infants who see an adult switch on a light with her forehead copy the odd action when her hands were free, but use their hands when hers were wrapped in a blanket: they infer *why* she did it that way (rational imitation, Gergely, Bekkering & Király, 2002). Imitation is goal inference followed by one's own steps toward the goal, which ties it to the goal machinery of I.5.
- **Faithful copying has a price.** When a causal mechanism is hidden, children copy even the demonstrator's useless steps, which chimpanzees skip (overimitation, Horner & Whiten, 2005). High-fidelity copying of steps one doesn't understand is what lets cultures pass on procedures nobody could reinvent (the cultural ratchet, Tomasello), and it is also how quirks and errors get passed along. LLMs show both sides: they inherit compiled human procedures, and also human filler, biases and mistakes.
- **Imitation alone compounds errors.** A cloned policy has seen only the states the expert visited. One mistake takes it somewhere the demonstrations never went, and errors grow with the length of the task (Ross, Gordon & Bagnell, 2011). This is the exposure bias of I.8 and R2. The fix is to close the loop: DAgger has the expert label the states the *learner* actually reaches, and RL on a model's own outputs (RLHF, verifiable rewards) trains on its own trajectories. Humans learn the same way: watch a demonstration, then practice while a coach corrects your attempts, not the coach's. Imitation supplies the prior, and feedback on one's own steps repairs it.
- **Imitation is bounded by the ZPD.** You can imitate only what you can almost do already (Vygotsky). A few-shot prompt is imitation in the fast store: the demonstration sits in context and the model follows it (I.6, learning from one example).

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


## II.4 Build order

Build capabilities in Piaget's dependency order (I.7). Each stage adds one component and ends with a Piagetian exit test, an exit criterion in the TOTE sense. Treat the order as a hypothesis: Piaget's stages are one human realization of the capability dependencies, not a necessary sequence, and P5 tests whether order matters at all.


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

So the path for an LLM agent isn't building from scratch. It is **back-filling the lower stages in the agent's own action domain**, using language as scaffolding. This is speculative (claim 14; see [Summary](#summary)): in symbolic domains such as code, the "sensorimotor" world is already symbolic, so back-filling may turn out to be easy or unnecessary. For a coding agent in a repository:

- **Stages 1–2:** learn what each command and tool actually does here (forward models), and compile reliable sequences into skills.
- **Stage 3:** compose skills toward goals (a goal stack).
- **Stage 4:** experiment to discover how the codebase behaves.
- **Stage 5:** simulate a change before making it.
- **Stage 8:** maintain invariants (tests keep passing = conservation), and verify by reverting.
- **Stage 9:** debug hypothetico-deductively, isolating variables like the pendulum task.

## Design rule

**R8. Avoid the social failure modes.**

- **Sycophancy is a Vygotskian failure.** Other-regulation never becomes self-regulation: the agent regulates to approval rather than to the task or the truth, like a child performing for an adult. The fix is internalizing the standards, not the approval signal.
- **Over-scaffolding** leads to dependence: scaffolding that never fades produces no autonomy.
- **Cultural transmission spreads errors too:** biases and myths inherited from data.

## P5: Does capability order matter? (claims 11 and 14)

**The key confound.** In many environments the dependency lives in the *world* (you need wood before a pickaxe), not in the learner. The test must remove that: every stage's tasks are solvable from the starting state, without anything another stage produces, so the only possible link between stages is learned competence.

**Environments**, two of them to test claim 14:

- **(a) Grounded:** a procedurally generated 2D world with containers, occlusion (object permanence), reversible and irreversible actions, hidden mechanics, and conserved quantities.
- **(b) Symbolic:** a sandbox with custom command-line tools that have undocumented behaviors, files with invariants, and bugs with several candidate causes.

**Stage task families**, each with exit-test probes (stage numbers follow II.4):


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

- **(i)** A small model trained from scratch (RL plus self-supervised learning) with no human data. This isolates convergence from inheritance (claim 13).
- **(ii)** An LLM agent, where "learning" is skill-library growth plus LoRA consolidation between phases. This tests back-fill.

**Conditions** (same task pool, same total samples and compute; only order differs):


| Condition | Order                                                                      | Purpose                   |
| --------- | -------------------------------------------------------------------------- | ------------------------- |
| C1        | Dependency order, S1 → S9                                                  | The hypothesis            |
| C2        | Reversed, S9 → S1                                                          | Strongest contrast        |
| C3        | Random interleaving                                                        | Order-free baseline       |
| C4        | Adaptive ZPD selector (tasks with intermediate pass rates; no fixed order) | Does a good order emerge? |
| C5        | Composite tasks only, same compute                                         | Does staging help at all? |


**The dependency map**, the most informative part. Run C1 with one stage removed at a time (S1 … S9 knockouts) and measure how much every later stage drops. This gives an empirical dependency graph to compare against Piaget's order. Also record the order C4 actually chooses: if an unprompted adaptive learner rediscovers roughly S1 → S9, that is strong evidence the dependencies are real.

**Predictions, registered before running:**

- Composite success and sample efficiency: C1 ≈ C4 > C3 > C5 > C2 in the grounded world.
- In the symbolic world the gap is smaller (claim 14: back-fill is cheaper there).
- For the LLM learner (ii), stages S1–S4 give little gain in the symbolic world and more in the grounded one.
- Knockouts: removing S1 hurts S5 and S8 heavily; removing S9 barely affects earlier stages; S5 → S8 → S9 forms a chain.
- C4's chosen order correlates with the dependency graph.

**Interpreting the outcomes:**


| Result                                  | Meaning                                                                                                               |
| --------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| C1 ≈ C4 ≫ C3, C2, and the graph matches | Dependencies are real; the developmental path holds                                                                   |
| C4 ≫ C1                                 | Dependencies exist, but an adaptive ZPD selector finds them better than a fixed order: use ZPD, not Piaget's sequence |
| C1 ≈ C3 ≈ C2                            | Order doesn't matter; the development section is decorative                                                           |
| Gap only for learner (i), not (ii)      | Pretrained LLMs already carry the lower stages; back-fill is unnecessary                                              |
| Graph differs from Piaget               | Dependencies are real but the order isn't human; build agents to the measured graph                                   |


**Statistics.** At least 5 seeds per condition for learner (i) and at least 3 for (ii); bootstrap confidence intervals; predictions and analysis fixed in advance; report area under the learning curve, not just final scores.

**Feasibility.**

- **P5 (i):** small models in a custom environment. Cheap compute, but real engineering effort for the environment and stage tasks.
- **P5 (ii):** needs fine-tuning between phases. Moderate cost.

P5 is best run after the module comparison in [Building the Loop](architecture.md#ii6-validate-before-you-keep-the-bitter-lesson), so that learner (ii) uses only the modules that earned their place.

## Summary

**Well supported.**

- **Claim 7: Learning at the edge of competence (I.7).** Practice is most informative where success is possible but unreliable, under support that fades.

**Plausible, needs testing.**

- **Claim 8: Thought is partly internalized action and dialogue (I.3, I.7).** The inner loop develops by moving action (Piaget) and dialogue (Vygotsky) inside. Chain-of-thought is private speech, and its compression into latent reasoning is inner speech.
- **Claim 11: Capability dependencies (I.7).** Some capabilities require others: forward models before planning, planning before verification, a shielded goal before safe autonomy. Piaget's stages are one human realization of these dependencies, not a necessary order.

**Speculative.**

- **Claim 14: Grounding back-fill.** LLM agents may benefit from building lower-level competences in their own action domain (tool forward models, compiled skills, invariant-based verification). In symbolic domains such as code, this may turn out to be easy or unnecessary.

**Open weakness: the order may be contingent, not necessary.** Piaget's order may reflect human biology (slow motor maturation, a body that comes first) rather than logical dependency. LLMs show capabilities out of order and still work. For a coding agent the "sensorimotor" world is already symbolic, so back-filling may be trivial or unnecessary. And Piaget's stages are contested in their own field (Baillargeon, Spelke; décalage). *Next:* claim only that some capabilities depend on others, and test whether curriculum order matters (P5, claims 11 and 14).

**Evidence status.**

| Claim                                        | Status                                                                                                                                                                       |
| -------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Reasoning evolved for argument               | Influential but debated                                                                                                                                                      |
| "LLMs are preoperational"                    | A metaphor: LLMs pass many text conservation tasks, and their failures are inconsistent                                                                                      |

## References

**Development and social learning**

- [Book][Piaget & Inhelder. The Psychology of the Child](https://www.alohabdonline.com/wp-content/uploads/2020/05/The-Psychology-Of-The-Child.pdf)
- Vygotsky (1978). *Mind in Society*; (1934/1962). *Thought and Language.*
- Wood, Bruner & Ross (1976). The role of tutoring in problem solving.
- Tomasello (2019). *Becoming Human.*
- Lave & Wenger (1991). *Situated Learning.*
- Mercier & Sperber (2017). *The Enigma of Reason.*
- Baillargeon; Spelke. Infant core knowledge.
- Oudeyer. Learning progress as intrinsic motivation.

**Imitation**

- Meltzoff (1995). Understanding the intentions of others: re-enactment of intended acts by 18-month-old children.
- Gergely, Bekkering & Király (2002). Rational imitation in preverbal infants.
- Horner & Whiten (2005). Causal knowledge and imitation/emulation switching in chimpanzees and children.
- Tomasello, Kruger & Ratner (1993). Cultural learning.
- Pomerleau (1989). ALVINN: an autonomous land vehicle in a neural network.
- Ng & Russell (2000). Algorithms for inverse reinforcement learning.
- Abbeel & Ng (2004). Apprenticeship learning via inverse reinforcement learning.
- Ross, Gordon & Bagnell (2011). A reduction of imitation learning and structured prediction to no-regret online learning.
- Andrychowicz et al. (2017). Hindsight experience replay.
