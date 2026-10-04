# One Loop: Perception, Reasoning, Action, Language and Transformers

> At the level where behavior is committed step by step, perception, reasoning, planning, action and language share one functional structure: **a hierarchy of goal-conditioned control loops whose steps are compiled procedures**, chunked upward through practice. Each loop places a **reversible inner loop** (simulation, search, drafting) before **irreversible commitments**, and must solve a **stopping problem** using progress, uncertainty and surprise signals. Interruptions are absorbed to the extent that a **shielded goal** separates what informs the next step from what may change the goal. Experience becomes knowledge, and deliberation becomes skill, through **selective consolidation**; learning is most effective at the **edge of competence** under fading support. Transformers implement the generator and much of the procedural substrate well; whether they need the remaining functions as explicit modules, or will acquire them with scale, is an empirical question.

## 1. The observation

Many human processes seem to share a structure with transformer next-token generation:

1. **Perception** starts with a goal. The eyes saccade in a sequence. Each saccade is not planned in advance; it depends on the previous ones. The sequence stops when perception concludes or is interrupted.
2. **Reasoning** starts with a goal and runs a flow of thoughts, with or without backtracking. Each thought depends on the previous ones. It stops at a conclusion or an interruption.
3. **Planning** works the same way: a flow of planning steps, with or without backtracking.
4. **Execution and navigation** may be guided by a plan or a map, but still proceed through small decisions that refer to previous steps.
5. **Physical action** starts from a rough idea, not an exact sequence of moves. Each sub-action depends on the previous ones.
6. **Talking and writing**: we don't know our later words at the start; they are generated on the fly from what came before.
7. **Transformers** generate a sequence of tokens, each depending on the previous ones, for text, speech, audio, video and actions. They stop at a conclusion and can be interrupted by new information injected into the context.

All of these have goals, run sequentially with or without backtracking, end in a conclusion or an interruption, and handle interruptions and off-track events by attending to relevant information and ignoring irrelevant information.

This draft develops that observation into a thesis, tests it against what is known, and narrows it where it fails.

## 2. Scope and definitions

**Scope.** The thesis is about the **serial control level** of behavior: the level at which an agent commits outputs one after another (gaze shifts, words, moves, decisions, actions) in pursuit of something. That level runs on top of parallel, continuous machinery it does not describe: fast feed-forward recognition, motor dynamics, background monitoring. It is a **functional** claim, not a claim that brains and transformers share a mechanism.

**Definitions.**

- **Step**: a committed output at a given level of the hierarchy.
- **Not planned beforehand**: the full sequence is not *explicitly represented* in advance. The internal state can still carry *implicit look-ahead*: speech errors show that later words are already active; hippocampal "theta sweeps" alternate between possible futures several times a second; LLMs choose a rhyme before writing the line. Step-by-step generation and implicit look-ahead are compatible.
- **Goal**: whatever conditions the sequence toward an end state. It may be set from above, triggered by the environment, driven by needs or curiosity, or **reconstructed after the fact**.

A caution from the start: any sequence factors as p(x₁…xₙ) = ∏ p(xₜ | x₍<ₜ₎), so "each step depends on previous steps" is true of everything. The non-trivial claim is about *function*: that one general next-step generator, organized as below, is enough.

## 3. Claims, graded by confidence

### A. Well supported

1. **Serial control loop.** At the commitment level, each process generates the next step conditioned on a goal and a belief built from history. Committing step by step with feedback is the tractable solution when the option space is huge, the world is noisy and partly observable, and memory is limited. Engineered systems arrive at the same loop: model predictive control plans a horizon, executes one step and replans; AlphaZero searches, commits one move and searches again.
2. **Hierarchy through procedural compilation.** The steps at each level are **compiled procedures**. Practice turns deliberation into skill, and **chunking turns a sequence at one level into a single step for the level above**. This makes deep hierarchies affordable and frees working memory and control.
3. **Two loops separated by reversibility.** A **revisable inner loop** (simulation, search, drafting) sits in front of an **irreversible outer loop** (commit, then feedback). Inner-loop operations can be undone or compensated and preserve invariants. That allows cheap backtracking and **verification before commitment**. How much inner loop comes before a commitment scales with the cost of error, uncertainty and the time available.
4. **The stopping problem.** Every level must decide whether to continue, deliberate, backtrack or stop. Good solutions combine a confidence threshold, an urgency signal that lowers it over time, and a surprise signal that reopens deliberation.
5. **Interruption handling depends on goal maintenance.** Interruptions are absorbed with **graceful degradation, not robustness**. Recovery depends on how well the goal was maintained and shielded. Shielding must separate information that *informs the next step* from information that *changes the goal*, and it should do so by source and salience rather than by content.
6. **Consolidation.** Experience must be selectively moved from fast episodic storage into slow semantic and procedural knowledge without overwriting what is already known.
7. **The zone of proximal development.** Practice is most informative where success is possible but unreliable, under support that fades.

### B. Plausible, needs testing

8. **Thought is partly internalized action and dialogue.** The inner loop develops by moving action (Piaget) and dialogue (Vygotsky) inside. Chain-of-thought corresponds to private speech; its compression into latent reasoning corresponds to inner speech.
9. **One generative model, several uses.** Remembering, perceiving, planning and acting may share one generative world model run in different modes. The evidence is strongest in rodent navigation and less certain for abstract human planning.
10. **Control signals.** Progress, uncertainty, information gain, budget and surprise are the signals a controller needs. Emotions are the biological implementation, *including their failure modes*. The engineering claim does not depend on calling them emotions.
11. **Capability dependencies.** Some capabilities require others: forward models before planning, planning before verification, a shielded goal before safe autonomy. Piaget's stages are one *human* realization of these dependencies, not a necessary order.

### C. Speculative

12. **Explicit modules.** Agents may need these functions as explicit modules, or the functions may **emerge with scale**. Each module is a hypothesis about a function, kept only if it beats a larger plain baseline.
13. **Convergence or inheritance.** Some parallels between LLMs and humans may be **inherited** from human text rather than convergent. Claim 1's generality has to rest on agents trained without human data, not on LLMs' resemblance to us.
14. **Grounding back-fill.** LLM agents may benefit from building lower-level competences in their own action domain. In symbolic domains like code, this may turn out to be easy or unnecessary.

## 4. Hierarchy and procedural memory

The loop is a **TOTE unit** (Miller, Galanter & Pribram, 1960): *Test* the state against the goal, *Operate*, *Test* again, *Exit* when they match. TOTE units nest. The seven processes in section 1 are better seen as **levels of one hierarchy** than as parallel processes:

```
need (hunger)                         hours
 └ goal (get lunch)
    └ plan (go to the café)           minutes
       └ navigation (turn left)       seconds
          └ action (reach, grasp)     ~100s of ms
             └ saccade (find handle)  ~200 ms
   (talking and reasoning attach at any level)
```

**Procedural memory supplies the steps.** Every step is a compiled skill ("scheme" in Piaget's terms): a saccade program, a word's articulation, a grasp, a familiar inference move. It is knowing *how* rather than knowing *that* (Ryle), acquired by practice, hard to verbalize, and a separate memory system: the amnesic patient H.M. improved at mirror drawing without remembering any practice.

- **Formation.** Skills move from cognitive (following explicit instructions) to associative to autonomous (Fitts & Posner). Declarative steps are compiled into single procedures (ACT-R knowledge compilation; Soar chunking). The basal ganglia learn which action fits which context through dopamine prediction errors; the cerebellum learns **forward models** that predict an action's consequences.
- **Why it is indispensable.**
  - The loop *composes* procedures; without them every step would need deliberation.
  - Chunking turns sequences into steps for the level above. This answers Lashley's (1951) problem of serial order.
  - Automatic skills run without supervision, so a working memory of about four items can attend to what is new.
  - Forward models generate the **surprise signal** the controller depends on.
  - Expertise in perception and reasoning is also largely procedural: chess masters see positions as chunks, and radiologists' saccades go straight to anomalies.
- **Failure mode: habit capture.** A habit fires after the goal has changed (salt in the coffee, driving to the old office). The controller must be able to veto running habits.

## 5. Reversibility: what makes the inner loop an inner loop

**Piaget's two forms of reversibility:** *inversion* (undo: pour the water back) and *compensation* (taller but thinner). In conservation tasks, the concrete-stage child justifies "it's the same amount" with three arguments: **identity** (nothing was added or removed), **inversion** (you can pour it back) and **compensation** (taller but thinner). The preoperational child judges by the end state and fixates on one salient dimension.

**Why reversibility matters.**

- **Free backtracking.** Search needs undo; chess engines make and unmake moves millions of times.
- **Verification by inversion.** Round-trip checks, revert-and-compare, substituting a solution back into the problem.
- **Conservation means invariants.** Knowing what a transformation leaves unchanged compresses the world model, prunes search, and turns violations into high-value surprise signals. This is the cognitive counterpart of Noether's link between symmetry and conservation.

**Piaget's arguments as verification checks for agents.**

| Argument | Check |
|---|---|
| Identity | Diff audit: did the change touch only what was intended? |
| Inversion | Round-trip; revert-and-compare; substitute back |
| Compensation | Invariants preserved: totals, passing tests, behavior through a refactor |

**Three classes of action.**

| Class | Examples | Handling |
|---|---|---|
| Reversible | Edit under version control; draft; move in a simulator | Act; backtrack freely |
| Compensable | Refund; rollback migration; "I mean…" | Act with a logged compensation plan (saga pattern) |
| Irreversible | Send money; delete without backup; physical harm | Deliberate fully; require permission |

Design principle: **move work toward the reversible end before committing** (sandboxes, dry runs, transactions, branches). Much of human engineering does this already: undo, version control, drafts, insurance, contracts.

**Where transformers fall short.** Reasoning tokens are append-only: "wait, that's wrong" compensates but does not invert, and the wrong thought stays in context. True inversion requires forking or rolling back the context. Conservation failures (entity tracking over long operation sequences, objects appearing or vanishing in generated video) resemble preoperational errors. The *reversal curse* (models trained on "A is B" failing at "B is A") is suggestive but weaker than it looks, since models reverse relations fine in context; it is an asymmetry in how facts are stored.

## 6. Stopping and control signals

Every level repeatedly faces one question: *think one more step, or act now?*

- **Accumulation to threshold.** In the drift-diffusion model (Ratcliff; Shadlen), evidence accumulates until it crosses a threshold. The threshold sets the speed–accuracy trade-off, and under time pressure it drops (an urgency signal). This approximates Wald's optimal sequential test.
- **Value of computation.** Think another step only if the expected improvement exceeds its cost (Russell & Wefald; Lieder & Griffiths).
- **Conflict monitoring.** By default people commit fast; a conflict or surprise reopens deliberation (System 1 → System 2). This is also how interruptions are absorbed.
- **Emotion ends deliberation.** Damasio's patient Elliot, after ventromedial prefrontal damage, kept intact logic but deliberated endlessly over trivial choices.

**Control signals and the decisions they drive.**

| Signal (biological form) | Measures | Decision |
|---|---|---|
| Curiosity | Expected information gain | Keep exploring |
| Boredom | Low gain, high opportunity cost | Stop; go elsewhere |
| Frustration | Stalled progress | Backtrack or switch |
| Anxiety | Uncertainty × stakes | Deliberate more |
| Surprise | Prediction error | Interrupt; reopen the inner loop |
| Fatigue | Resources spent | Wrap up |
| Satisfaction | Error resolved | Commit and stop |

Under predictive-processing accounts, valence tracks the *rate of change* of prediction error (Joffily & Coricelli; a formal proposal, not an established result).

**LLMs.** They have no intrinsic stopping sense, which shows up as overthinking on easy problems. In the *s1* paper (2025), suppressing the end-of-thinking token and appending "Wait" improved accuracy: an external "are you sure?". Most comparable signals in AI (reward prediction error, curiosity bonuses, process reward models) are used during training rather than as running state during inference.

## 7. Goals and goal shielding

**A goal is a prediction the agent makes come true.** In active inference, goals are prior preferences; prediction error can be reduced by changing the belief (perception) or by changing the world (action). This is the same mechanism as conditioning a transformer on a prompt ("Here is a correct proof:"), or on a target return in the Decision Transformer.

**Not every goal is top-down.** Affordances suggest goals (you see a cup and reach for it), and goals are sometimes constructed after the fact (choice blindness; Gazzaniga's interpreter).

**How the brain shields goals.**

- **Active maintenance** with top-down bias: the prefrontal cortex continuously favors goal-relevant processing (Miller & Cohen).
- **A learned gate** on working memory: in the PBWM model (O'Reilly & Frank), maintenance and updating are separate operations.
- **Source monitoring**: tracking where information came from.
- **A stability–flexibility balance.** Too much shielding produces perseveration; too little produces distractibility.

**AI parallels.**

| Human failure | Agent failure |
|---|---|
| Utilization behavior (frontal patients use any object they see) | Prompt injection |
| Goal neglect (Duncan) | Goal drift in long tasks |
| Habit capture | Repeating a learned pattern after the goal changed |
| Performing for approval | Sycophancy |

**Mitigations:** instruction hierarchy, role or data embeddings, dual-model quarantine (e.g., CaMeL), goal recitation, permission gates. The principle is **shield by source, open by trust and salience**. Relevance only exists relative to a goal; without a protected goal, everything in context competes equally.

## 8. Memory and consolidation

| Store | Brain | Role | Learns by |
|---|---|---|---|
| Working | Prefrontal cortex | Goal stack and belief; small and protected | Gated updates |
| Episodic | Hippocampus | One-shot events, cue-based recall | Logging |
| Semantic | Neocortex | Gist, world knowledge, invariants | Consolidation |
| Procedural | Basal ganglia, cerebellum | Skills: the steps of the loop | Practice, reward, error |

- **Compress or keep everything.** The optimal agent needs a *belief state*, a sufficient summary of history. Brains compress it (working memory); transformers keep the raw context and attend to it. Compression forces abstraction; raw context allows reinterpreting the past. Hybrids look best.
- **Attention and the hippocampus.** Modern Hopfield networks are mathematically equivalent to attention, and transformers with suitable position encodings reproduce hippocampal codes. This is a formal parallel, not evidence that the brain computes softmax attention.
- **Memory is reconstructive** (Bartlett). Recall itself runs on the generative loop.
- **Consolidation** (Complementary Learning Systems: McClelland, McNaughton & O'Reilly). During sleep, time-compressed replay moves salience-tagged experience from hippocampus to cortex. Reverse replay at reward sites assigns credit; synaptic downscaling prunes; episodes become gist.
- **Replay as planning.** Hippocampal sequences sweep ahead at choice points, replay predicts the path about to be taken, and the brain prioritizes replay by *gain × need* (Mattar & Daw). Repeated planning gets cached into habit, which Dyna, world-model agents and chain-of-thought distillation all reproduce.

Agents are rebuilding these pieces one at a time: context compaction (compression), retrieval (episodic recall), memory files (crude consolidation). Continual learning into weights, without forgetting or poisoning, is the missing step. Untrusted content consolidated into weights would become a **persistent injection**, so consolidation needs the same source gate as the goal.

The loop runs at three timescales: commitment (milliseconds), deliberation (seconds to minutes), consolidation (days).

## 9. Development: a build path

**Piaget** gives the mechanism: thought is internalized action. Schemes are *assimilated* (applied) and *accommodated* (revised) under **equilibration**, a self-regulation driven by disequilibrium that is close to prediction-error minimization. **Vygotsky** gives the social source: every higher function appears twice, first between people and then within. Private speech becomes inner speech, learning happens in the zone of proximal development, and scaffolding should fade.

| # | Capability (Piaget / Vygotsky) | Agent component | Exit test |
|---|---|---|---|
| 0 | Reflexes; core priors | Generator; primitive tools | Executes primitives |
| 1–2 | Circular reactions; imitation | Forward models; skill compilation | Calibrated surprise; reproduces effects |
| 3 | Means–ends; shared goals | Goal stack; TOTE; chunking; joint attention | Multi-step means–ends tasks |
| 4 | Experimentation, with guidance | Controller with information gain; ZPD curriculum | Finds hidden mechanics efficiently |
| 5–6 | Internal simulation; object permanence; symbols; private speech | World model; belief state; episodic memory; chain-of-thought | Detour without trial and error; deferred imitation |
| 7 | Decentration; theory of mind | Source tagging; goal shield; user model | False-belief task; not fooled by surface cues |
| 8 | Reversibility; conservation | Operations with inverses; invariants; forkable state | Conservation; verify by undoing |
| 9 | Formal operations; internalized debate | Hypothesis search; value-of-computation controller; internal critic | Pendulum task: isolate the causal variable |

**Autonomy grows along the reversibility ladder.** Read-only, then reversible actions, then compensable ones, then irreversible ones with permission, each promoted by track record. This mirrors legitimate peripheral participation (Lave & Wenger).

**Development in reverse.** LLMs entered at the symbolic and formal level by reading the culture: they have Vygotsky's "scientific concepts" without grounded "everyday concepts". An agent's path is to **back-fill the lower stages in its own action domain**. For a coding agent that means forward models of its tools, compiled skills, experimentation, simulating before acting, tests as conservation, and hypothesis-driven debugging.

**ZPD in training.** In group-relative RL methods such as GRPO, problems that are always or never solved produce zero learning signal; only intermediate pass rates produce gradient.

**Caveats.** Infants show some competences earlier than Piaget thought, stages are uneven (décalage), and culture matters more than he allowed. Read the stages as a dependency order of capabilities, not fixed ages.

## 10. Where transformers stand

| Have | Gaining | Missing |
|---|---|---|
| Step-by-step generator | Inner loop (reasoning tokens) | Native, shielded goal register |
| Large built-in procedural knowledge | External memory; skill documents; code skills | Calibrated controller and stopping sense |
| Goal-conditioning as prediction | Movement from explicit to latent reasoning | Compiling new skills from their own experience |
| The absorbed culture | Social scaffolding (RLHF, critics) | Reversible thought; grounding; consolidation across sessions |

## 11. Weak points

1. **Unfalsifiability risk.** A frame that absorbs every analogy predicts nothing, which is why section 12 exists.
2. **Same description is not same mechanism.** Fast recognition is largely feed-forward (Thorpe et al., 1996), motor control looks like continuous population dynamics, and the brain is massively parallel. The serial loop may describe only the serial bottleneck.
3. **"Everything starts with a goal" is shaky.** Habits, play and mind-wandering exist, and goals are sometimes narrated afterwards.
4. **Interruption handling is overstated.** Humans show resumption lags and switching costs (Altmann & Trafton). Claim graceful degradation, not robustness.
5. **The bitter lesson.** A many-module design resembles Soar and ACT-R, which did not scale. Modules have to earn their place against scale.
6. **The developmental order may be contingent** on human biology rather than logically necessary.
7. **Inheritance vs convergence is unresolved.**
8. **Emotion framing** picks out the adaptive functions and ignores the distortions.

**Evidence status of cited claims.**

| Claim | Status |
|---|---|
| Somatic markers / Iowa Gambling Task | Contested |
| Valence = rate of change of prediction error | Formal proposal |
| Overfitted-brain theory of dreams | Speculative |
| Hippocampal preplay | Debated |
| Replay as planning | Strong in rodent navigation; contested for abstract human planning |
| Attention ≈ hippocampus | Formal equivalence, not a mechanism claim |
| "LLMs are preoperational" | A metaphor; failures are inconsistent |
| Reversal curse as missing reciprocity | Weaker than it looks; a storage asymmetry |

## 12. Tests

| Claim | Test | If it fails |
|---|---|---|
| 3 | Forkable inner loop vs append-only chain-of-thought, at equal compute | Reversibility is not the key separator |
| 5 | Goal register + source tagging vs recitation, on injection and drift | Explicit shielding is unnecessary |
| 2, 6 | Practice-compiled skills: less compute, no regression | The compilation claim fails for agents |
| 4, 10 | Learned value-of-computation controller vs fixed budgets | An explicit controller is unnecessary |
| 11 | Dependency-ordered vs random curriculum for a grounded agent (P5) | The development section is decorative |
| 12 | Each module ablated against a larger plain baseline (P6) | Drop the module |

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
- **Predictions.** C1 ≈ C4 > C3 > C5 > C2 in the grounded world, with a smaller gap in the symbolic one. Removing S1 hurts S5 and S8 most. C4's chosen order correlates with the dependency graph.
- **Interpretation.**

| Result | Meaning |
|---|---|
| C1 ≈ C4 ≫ C2, C3, and the graph matches Piaget | The developmental path holds |
| C4 ≫ C1 | Use an adaptive ZPD selector rather than a fixed sequence |
| No order effect | Section 9 is decorative |
| Effect only for learner (i) | Pretrained LLMs already carry the lower stages |
| Graph differs from Piaget | Real dependencies, but not in human order |

- **Order of work.** Run P6 first, then build the P5 environments, then P5 (i), then P5 (ii) with the modules that survived P6.

## References

**Serial order, hierarchy, procedural memory**
- Lashley (1951). *The Problem of Serial Order in Behavior.*
- Miller, Galanter & Pribram (1960). *Plans and the Structure of Behavior.*
- Ryle (1949). *The Concept of Mind.*
- Milner (1962), on H.M.'s mirror-drawing learning.
- Fitts & Posner (1967). *Human Performance.*
- Anderson. ACT-R; Newell & Rosenbloom, chunking and the power law of practice.
- Yin & Knowlton (2006). The role of the basal ganglia in habit formation.
- Chase & Simon (1973). Perception in chess.
- Norman (1981); Reason (1990). Action slips.

**Control, stopping, emotion**
- Ratcliff; Gold & Shadlen. Drift-diffusion and decision neuroscience.
- Wald (1947). *Sequential Analysis.*
- Russell & Wefald (1991). *Do the Right Thing.*
- Lieder & Griffiths (2020). Resource-rational analysis.
- Todorov & Jordan (2002). Optimal feedback control.
- Damasio (1994). *Descartes' Error.*
- Joffily & Coricelli (2013). Emotional valence and the free-energy principle.
- Muennighoff et al. (2025). s1: Simple test-time scaling.

**Goals and shielding**
- Friston. Active inference.
- Chen et al. (2021). Decision Transformer.
- Miller & Cohen (2001). An integrative theory of prefrontal cortex function.
- O'Reilly & Frank (2006). PBWM.
- Duncan, on goal neglect.
- Lhermitte, on utilization behavior.
- Johansson & Hall (2005). Choice blindness.
- Wallace et al. (2024). The instruction hierarchy.
- Debenedetti et al. (2025). CaMeL: defeating prompt injections by design.

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

**LLM-specific**
- Berglund et al. (2023). The reversal curse.
- Wang et al. (2023). Voyager.
- Sutton (2019). The Bitter Lesson.

**Related reading in this repo:** [interesting topics](interesting%20topics.md), covering the predictive mind, emergence and the brain.
