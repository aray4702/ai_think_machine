# ![One Loop icon: a goal at the center, a dashed reversible inner loop, and a solid outer loop of committed steps, one of which is itself a loop](../../assets/images/one-loop-icon.svg) One Loop: Observations and Design Principles

*About the logo: the goal sits at the center. The dashed inner loop is reversible simulation and search; the solid outer loop is irreversible, committed steps. One step is drawn as a loop of its own, because every step is a lower-level loop.*

> One Loop is the design of an agent built around a control structure that brains and transformers share: a hierarchy of goal-conditioned loops that commit one step at a time. From constraints every agent faces, and from what recent advances in AI and neuroscience show about meeting them, the design derives seven features: step-by-step commitment with feedback, compiled skills stacked into a hierarchy, a reversible inner loop in front of irreversible actions, a controller that decides when to stop, a shielded goal, separate memories joined by consolidation, and learning at the edge of competence. Transformers already supply the generator and much of the skill substrate. The design adds the rest around them, and keeps each added module only if it beats a stronger plain model.



**One Loop design docs:** [1. Observations and principles](01_observations.md) · [2. Derived features](02_features.md) · [3. System design](03_system_design.md) · [4. Implementation plan](04_implementation_plan.md) · [5. Applications](05_applications.md) · [6. Media creation](06_media_creation.md) · [7. Companion](07_companion.md) · [8. Discovery and invention](08_discovery_invention.md) · [References](references.md)

The design is written as eight documents, following the order of the design process:

1. **Observations and design principles** (this document): what was observed, what the design covers, and the constraints the features are derived from.
2. **[Derived features](02_features.md)**: one section per feature (F1–F7). Each starts from a constraint, derives what the agent must do about it, and gathers evidence from brains and machines on how it can be done.
3. **[System design](03_system_design.md)**: requirements, the architecture and its components, and the design rules (R1–R9).
4. **[Implementation plan](04_implementation_plan.md)**: where current models stand, the build stages and development process, validation of each module, and the design's assumptions and risks.
5. **[Applications](05_applications.md)**: candidate domains ranked by fit, in the recommended order, starting with software engineering.
6. **[Media creation](06_media_creation.md)**: One Loop as a director for AI media: personal intent, specialist agents for generation, tools for editing.
7. **[Companion](07_companion.md)**: One Loop as a personal companion that serves the person's flourishing, not engagement, and the lines it must not cross.
8. **[Discovery and invention](08_discovery_invention.md)**: how One Loop discovers and invents, applied to explaining phenomena, engineering design, and drug and materials discovery.



## Contents

- [The observation](#observation)
- [Scope](#scope)
- [From constraints to features](#from-constraints-to-features)
- [Design stance](#design-stance)



<a id="observation"></a>

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
- **Step is not planned beforehand**: the full sequence is not *explicitly represented* in advance. The internal state can still carry *implicit look-ahead*: speech errors show that later words are already active; hippocampal "theta sweeps" alternate between possible futures about eight times a second ([F6](02_features.md#f6)); LLMs choose a rhyme before writing the line. So the two are compatible: steps are generated on the fly, but the state looks ahead.
  - Lashley's *The Problem of Serial Order in Behavior* (1951) argued that behavior can't be pure chaining.
  - Speech errors show that people already hold later words in mind before saying them. Anticipation slips ("a leading list" for "a reading list") and spoonerisms are the evidence.
  - The next saccade target is computed during the current fixation.
  - Interpretability research found that LLMs pick a rhyme word before writing the line that ends in it.
- **Backtracking means different things in different cases.** Neither speech nor a transformer can erase what it has produced; both "backtrack" by appending a repair ("uh, I mean…", or "Wait, …" in reasoning models). Writing with editing, and mental backtracking in reasoning, really can revise earlier output. That is closer to search, or to diffusion-style refinement, than to pure autoregression. Which one appears depends on reversibility ([F3](02_features.md#f3)).



##### **Contrasts between minds and transformers**

- **Memory architectures differ.** Human working memory holds about four items. People compress history into a running state and rely on external memory (notes, maps). That is closer to an RNN or state-space model than to a transformer that can attend back to its whole raw context.
- **Learning while acting.** A human's "weights" change during the task. A transformer's weights are frozen at inference, so anything it learns mid-task has to live in its context ([F6](02_features.md#f6)).
- **Grounded, closed-loop feedback.** Humans get a continuous sensory stream. A model gets feedback only when something is injected into its context, such as a tool result or a user message.
- **Felt salience.** Emotion and body state decide what is relevant and when to stop. Goals persist as motivation and body state (Damasio), and stopping is a felt sense of satisfaction or "done." In a transformer, the goal is just conditioning text and stopping is an end-of-sequence token ([F4](02_features.md#f4)).
- **Offline simulation.** Humans can mentally rehearse a plan before acting. Reasoning models approximate this with hidden thinking tokens ([F3](02_features.md#f3)).
- **Hierarchy across timescales.** Humans nest goals → subgoals → actions → micro-movements, each running on its own timescale. A transformer is flat and has to learn any hierarchy implicitly ([F2](02_features.md#f2)).



## Scope

![Scope of the One Loop design: shared supporting functions coordinate domain-specific knowledge and skills; underlying mechanisms implement the supporting functions.](../../assets/images/one-loop-scope.svg)

The design is built around the **supporting functions** that organize intelligent activity across domains: committing one step at a time using feedback, compiling steps into nested procedures, simulating and revising before committing, deciding when to continue or stop, maintaining and shielding the goal, consolidating learning selectively, and learning at the edge of competence (F1–F7). Domains such as language, spatial reasoning, and social or emotional understanding supply specialized knowledge, representations and skills; the supporting functions coordinate when and how those resources are used, revised and learned. For example, composing a sentence and navigating a route require different knowledge and skills, but both involve maintaining a goal, evaluating possible next steps and adjusting to feedback. Capable behavior depends on their interaction: a shared control structure alone does not explain competence in a particular domain. An operating system is a useful analogy: the supporting functions are the **kernel** (scheduling steps, handling interrupts, managing memory), the domains are **services** that run on it, and the underlying mechanisms are the **hardware**, which services reach only through the kernel. The analogy is about roles, not components: a kernel is one separate body of code, whereas whether each function needs an explicit module is decided module by module during [validation](04_implementation_plan.md#validation).

The design focuses on the **serial control level** of behavior: the level at which an agent commits outputs one after another (gaze shifts, words, moves, decisions, actions) in pursuit of something. Domain-specific capabilities serve as examples, rather than subjects of a complete theory. This level runs on top of parallel, continuous machinery the document does not describe: fast feed-forward recognition, motor dynamics, background monitoring. The design borrows **functions**, not mechanisms: it does not assume that brains and transformers work the same way.

**What the design does not assume.** Several tempting readings of the observation go too far, and the design avoids them:

- **Serial control level, not all of cognition.** Several processes aren't naturally discrete or serial. Fast object recognition takes about 100 ms through a mostly feed-forward sweep with no saccade sequence (Thorpe et al., 1996); motor control looks like continuous neural population dynamics (Shenoy; Churchland); and walking, talking and monitoring run at once. The loop describes the serial bottleneck (conscious access and committed outputs, as in Global Workspace theory), which sits on top of parallel, continuous machinery. Same description is not same mechanism.
- **Goals are one source of conditioning among several.** Much behavior isn't goal-initiated: habits, exploration, play, mind-wandering. Goals are often constructed after the fact: in choice blindness people defend choices they never made (Johansson & Hall, 2005), and Gazzaniga's split-brain "interpreter" invents reasons for actions it didn't cause. Goals can be set from above, triggered by affordances, driven by needs or curiosity, or inferred afterwards (the definition of goal in the [observation](#observation); [F5](02_features.md#f5)).
- **Graceful degradation, not robustness.** Humans are bad at interruptions: there is a measurable resumption lag, switching costs, and errors after interruption (Altmann & Trafton's memory-for-goals model), and LLM agents degrade too. Both can recover, at a cost that depends on how well the goal was maintained (F5).
- **Control signals, with emotion as the biological example.** The mapping in [F4](02_features.md#f4) picked the adaptive functions of emotion. Real emotions also bias, distort and misfire: anxiety spirals, mood-congruent memory, loss aversion. The functional signals don't need the emotion framing, which also invites anthropomorphism (R7).
- **"Not planned beforehand" allows look-ahead.** Steps are generated on the fly, yet the state carries look-ahead (theta sweeps, rhyme planning, MPC). The two are compatible because "planned" means *explicitly represented as a full sequence*, which is how the [observation](#observation) defines it.



## From constraints to features

Each feature in [Derived features](02_features.md) follows the same pattern. It starts with a **constraint** that every agent acting in the world faces, derives the **consequence** that follows from it, gathers **evidence** from humans and machines on how the consequence can be met, and ends with the **feature** it adds to the agent.

Any sequence can be factored as p(x₁…xₙ) = ∏ p(xₜ | x₍<ₜ₎), so step-by-step generation alone says little about how to build an agent. The derivations yield *specific* structure beyond that: structure an arbitrary sequence model would not have, and that the agent therefore has to be given or has to learn.


| Feature | Constraint                                      | What the agent must do                                 | Main components                      |
| ------- | ----------------------------------------------- | ------------------------------------------------------ | ------------------------------------ |
| F1      | Too many futures to plan in advance             | Commit one step at a time and use feedback             | Generator G; belief state            |
| F2      | Limited compute and memory                      | Compile steps into skills, and stack them              | Procedural store P; goal stack       |
| F3      | Some outputs can't be taken back                | Put a reversible inner loop in front of commitments    | Scratch; action gate                 |
| F4      | Thinking has a cost                             | Use control signals to decide when to stop             | Controller K                         |
| F5      | The context mixes sources                       | Shield the goal by source and salience                 | Working state W; source tags; gate   |
| F6      | Learning fast overwrites old knowledge          | Separate fast and slow stores; consolidate selectively | Memories E, M, P, θ; sleep cycle     |
| F7      | Learning signal lives at the edge of competence | Learn where success is unreliable; build in order      | Curriculum selector; teacher channel |


Put together, the features give one structure: a hierarchy of goal-conditioned loops whose steps are compiled skills, each with a reversible inner loop in front of irreversible commitments, a stopping rule driven by control signals, a shielded goal, and consolidation that turns experience into knowledge and deliberation into skill.

## Design stance

- **Functions, not boxes.** A design with this many modules resembles classic cognitive architectures such as Soar and ACT-R, which were insightful but did not scale, and hand-built structure has repeatedly lost to general methods plus scale (Sutton's *bitter lesson*). Each module is therefore a design choice about a function. It is kept only if it beats a larger plain model, at matched compute or at matched data, and dropped if scale supplies the function on its own ([validation](04_implementation_plan.md#validation)).
- **Innate wiring, learned contents.** The brain is not a blank slate trained end to end. The genome is far too small to specify its synapses (the *genomic bottleneck*, Zador 2019), so it encodes rules instead: the column template, the map of regions, the initial connections between them, the learning rules and a few reflexes. Experience fills in the contents. The bitter lesson argues against hand-built *knowledge*, not against architecture; a transformer is itself a lot of built-in structure. So this design puts its structure where the genome does, in the wiring and the learning rules, and leaves the contents to learning ([innate structure](03_system_design.md#innate-structure)).
- **Build on the transformer.** The generator, goal-conditioning and a large built-in skill memory already exist in current models. The design adds what they lack around them, rather than replacing them ([starting point](04_implementation_plan.md#starting-point)).
- **Brains as inspiration, not justification.** Brain parallels suggest how a function can be done and how it fails. A module earns its place by its acceptance criteria, not by its resemblance to a brain region.
- **The top goal stays with people.** Control signals are about the task, not the agent's own state, and the top of the goal hierarchy is set by the people the agent works for (R7).
- **Safety value counts separately.** Modules such as the goal gate and the action gate can be kept for the errors they prevent even when their capability gain disappears with scale.

References for all eight documents are collected in [References](references.md).