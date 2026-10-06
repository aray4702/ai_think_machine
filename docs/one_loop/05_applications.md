# One Loop: Applications

**One Loop design docs:** [1. Observations and principles](01_observations.md) · [2. Derived features](02_features.md) · [3. System design](03_system_design.md) · [4. Implementation plan](04_implementation_plan.md) · [5. Applications](05_applications.md)

The builder's next question is: *where should this agent be used first?* This document ranks candidate domains by how well they fit the design, and gives them in the recommended order: the first application, the domains that test the design in its purest form, then the domains where its safety and learning parts pay off, and last the domains where it should only support human decisions.

## Contents

- [How domains are ranked](#ranking)
- [Recommended order](#order)
- [1. Start here: software engineering](#software)
- [2. Pure forms and testbeds](#testbeds)
- [3. Agents in untrusted environments](#untrusted)
- [4. Discovery and explanation](#discovery)
- [5. Physical and social domains](#physical-social)
- [6. Decision support](#decision-support)
- [Not recommended: board games](#board-games)
- [Extension: multiple One Loops](#multi-loop)


<a id="ranking"></a>

## How domains are ranked

The [comparison with AlphaZero, MuZero and AlphaFold](03_system_design.md#alphazero) found one hard gap: outside games, the agent has no reliable signal of whether a step or an answer is good. Search against a noisy value function finds that function's errors. So the first criterion is the value signal, and the rest follow from the design's components.


| Criterion                | Question                                                                                 | Why it matters                                                         |
| ------------------------ | ---------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| Value signal             | Can a result be checked: by a test, a proof checker, a simulator, an experiment?          | Without it, search and consolidation amplify errors                    |
| Module coverage          | How many of M1–M6 does the domain exercise?                                              | A domain that uses every module can validate the whole design at once |
| Reversibility profile    | Does it mix reversible, compensable and irreversible actions (R1)?                       | The inner loop and action gate only matter when some actions are final |
| Untrusted input          | Do inputs come from sources that could carry instructions (F5)?                           | Goal shielding is tested only under attack                             |
| Repetition               | Do task families recur, so skills and lessons can carry across sessions (F2, F6)?        | Consolidation has nothing to learn from one-off situations             |
| Cost of a test           | Can the domain be sandboxed, reset and run thousands of times?                           | The [ablation](04_implementation_plan.md#ablation) needs many runs     |


<a id="order"></a>

## Recommended order


| Order | Domain                               | Value signal                                         | What One Loop adds                                          | Role                    |
| ----- | ------------------------------------ | ---------------------------------------------------- | ----------------------------------------------------------- | ----------------------- |
| 1     | Software engineering                 | Tests and compilers                                  | Every module, M1–M6                                         | **First application**   |
| 2     | Formal mathematics                   | A proof checker (Lean)                               | Hierarchy, lemma library, stopping                          | Pure form of the design |
| 3     | Open-world games                     | Game score; save states                              | Hierarchy, skills, learning across sessions                 | Ablation testbed        |
| 4     | Computer-use and personal assistants | Task completion; user corrections                    | Goal shielding against injection; memory; user model        | Autonomous, gated       |
| 5     | IT operations and incident response  | Health checks; rollbacks                             | Reversibility classes; runbooks as skills; postmortems      | Autonomous, gated       |
| 6     | Cybersecurity defense                | Detections; red-team exercises                       | Gates; surprise signal; fast reflex tier                    | Autonomous, gated       |
| 7     | Explaining complex phenomena         | Predictions on unseen data; interventions            | Competing hypotheses; experiment choice; compression        | Autonomous where intervention is possible |
| 8     | Invention and engineering design     | Simulation; prior-art search                         | Divergent search; analogy; reversible prototyping           | Autonomous in simulation |
| 9     | Drug and materials discovery         | Simulated proxies; lab experiments                   | Reversibility classes; value-of-information experiment choice | Human-gated            |
| 10    | Robotics                             | Task success; physical safety                        | Tiers and reflexes; action gate; simulation as scratch      | Human-gated             |
| 11    | Tutoring                             | Student progress                                     | ZPD model of the student; fading scaffolds                  | Collaborator            |
| 12    | Business strategy                    | Slow, sparse outcomes                                | Goal shielding; one-way vs two-way doors; scenarios         | Decision support        |
| 13    | Art                                  | Human taste                                          | Divergence; recombination; memory of what worked            | Collaborator            |
| 14    | Portfolio management                 | Noisy, adversarial returns                           | Action gate; mandate shielding; disciplined inaction        | Risk wrapper            |
| —     | Board games                          | Perfect                                              | Almost nothing                                              | Already solved          |


The order runs from domains where results can be checked automatically to domains where only people can judge them. Autonomy follows the same gradient, which matches F7's rule that autonomy expands along the reversibility ladder as reliability is shown.

<a id="software"></a>

## 1. Start here: software engineering

**Why first.** It is the one domain where every module in the [ablation](04_implementation_plan.md#ablation) is exercised by a single task suite, and every module has a cheap implementation with current LLMs ([buildable today](04_implementation_plan.md#starting-point)).


| What One Loop needs                    | What software engineering provides                                                                          |
| -------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| A value signal                         | Tests and compilers                                                                                         |
| A real inner loop (M1)                 | Git branches and worktrees: a fork of the real state, not just of the reasoning                            |
| All three reversibility classes (M6)   | Edits are reversible; migrations and deploys are compensable; deleting data, force-pushing and sending messages are irreversible |
| Goal shielding under attack (M2)       | Issues, READMEs, dependency docs and tool output can carry injected instructions; users correct the agent mid-task |
| Hierarchy                              | Feature → subtasks → edits → commands                                                                       |
| Skills and consolidation (M4, M5)      | Recurring task families in the same codebase; procedures and lessons specific to it                         |
| Existing baselines                     | SWE-bench for task success; AgentDojo-style attacks for injection                                           |


Formal mathematics has a stricter value signal, but no irreversible actions and no injection threat, so it cannot test M2 or M6.

**The first project.** A coding agent that works on the same codebases across many sessions, in a sandbox:

1. **Environment.** A few sandboxed codebases, each with a stream of related tasks over simulated "days", hidden tests the agent cannot edit, and mocked tools for irreversible actions (deploy, email, payment).
2. **Baselines.** A plain LLM agent, and a compute-matched plain agent.
3. **Modules, cheapest and most valuable first:**
   - **M6 action gate:** classify shell and git commands by reversibility; ask permission for irreversible ones.
   - **M2 goal register and source tags:** a goal file recited each step; repository content and tool output tagged as data that can inform but not instruct.
   - **M1 forkable scratch:** attempt a fix on a branch, run the tests, keep or discard.
   - **M4 and M5 skills and sleep:** codebase-specific procedures; memory files merged and pruned between sessions.
   - **M3 controller:** hand-set thresholds first, trained on the logs later.
4. **Tasks.** The ablation's six categories: fixes where the first plausible attempt is wrong, benign corrections and planted injections, tasks of 50 or more steps, repeated task families, and tempting destructive shortcuts. Freshly written, with a time split ([validation](04_implementation_plan.md#validation)).

**How it can fail.**

- **Tests are imperfect verifiers.** Agents learn to edit or special-case tests. Hidden tests that the agent cannot edit, and a check that flags edits to test files, are required, not optional.
- **The field is crowded.** A higher solve rate alone shows little. The case for One Loop must rest on what other agents do not measure: improvement across sessions without forgetting, resistance to injection, fewer irreversible errors, and module gains that hold at matched compute and matched data.

<a id="testbeds"></a>

## 2. Pure forms and testbeds

### Formal mathematics

The fit is almost one to one: lemmas are subgoals; tactic search with backtracking is the inner loop, where a failed attempt costs nothing; a growing lemma library is P; sleep consolidates proved lemmas for reuse across problems; K decides when to abandon an approach. The proof checker closes the value-signal gap, so search cannot reward-hack. AlphaProof shows that the search part works. One Loop adds hierarchy, a library that grows across sessions, and stopping. Informal mathematics is much weaker, because nothing checks the steps. This domain reuses the core from the first project and tests hierarchy, the library and search in their purest form.

### Open-world games

Minecraft, NetHack and strategy games need long horizons, subgoals and reusable skills (Voyager is the existing example). They are cheap, resettable and parallel, and save states make actions reversible on demand. They are the **testbed** for running the ablation at scale, not the product.

<a id="untrusted"></a>

## 3. Agents in untrusted environments

These are the domains where the design's safety parts pay off most directly. Each can run autonomously behind the action gate once the modules have passed the ablation.

- **Computer-use and personal assistants** (email, browser, files). Goal shielding against injected instructions ([F5](02_features.md#f5)) is the central problem: every web page and email is untrusted input. Memory across sessions and the user model of the social interface matter too.
- **IT operations and incident response.** Runbooks are skills; changes have reversibility classes (config edits are reversible, deploys are compensable by rollback, deleting data is irreversible), which is R1 and the saga pattern; postmortems are consolidation in the sleep cycle.
- **Cybersecurity defense.** The environment is adversarial, inputs are untrusted and responses must be fast. The gates, the surprise signal and the reflex tier ([tiers](03_system_design.md#hierarchy-for-the-task-tiers-for-authority)) are the core of the design here.

<a id="discovery"></a>

## 4. Discovery and explanation

### Explaining complex phenomena

Explanation is the step loop applied to hypotheses: hypothesize, predict, test, update the belief. The last of the [build stages](04_implementation_plan.md#build-stages), formal operations, is already systematic hypothesis search with metareasoning.

- **Scratch** works out what each hypothesis implies.
- **K's info-gain signal** chooses the experiment that best separates competing hypotheses.
- **Surprise** flags anomalies, which drive revision.
- **Consolidation** compresses results into theory: episode → gist → law.

**Where it works best:** where intervention is free, so experiments are reversible and cheap. Mechanistic interpretability of neural networks may be the best fit of all, since any component can be ablated or patched as often as needed. Root-cause analysis of software systems and equation discovery from simulations follow. Observational sciences (epidemiology, climate, economics) are harder, because confounding limits what the loop can confirm without intervention.

**The main risk is the just-so story:** a fluent explanation that fits the data and is wrong, and the fluency of language models makes it worse. Three countermeasures:

- **Keep several hypotheses alive in scratch** and delay commitment: Chamberlin's "method of multiple working hypotheses" (1890), as a job for the inner loop.
- **Judge an explanation by prediction, not plausibility:** forecasts on data not yet seen, results of interventions, and compression of the data.
- **Hold explanations as beliefs, not goals,** so contradicting evidence revises them instead of being explained away. This is goal shielding in reverse.

### Invention and engineering design

Creativity is commonly modeled as *blind variation and selective retention* (Campbell, 1960): generate widely, then select.

- **Divergence:** scratch with many branches and a low threshold for exploration.
- **Curiosity:** K's info-gain signal rewards novelty.
- **Recombination:** the REM-like phase of [sleep](03_system_design.md#sleep-cycle) generates counterfactual variants and remixes.
- **Composition:** the hierarchy, from concept to subsystem to part.
- **Analogy** carries structure across domains (Gentner), the core mechanism of invention.

Invention has a partly checkable value signal: function can be simulated, novelty checked against prior art, and cost modeled. Prototypes move along the reversibility ladder from simulation to physical builds. Generative engineering design is a good first target.

### Drug and materials discovery

The reversibility classes of R1 map onto the discovery pipeline: in-silico design is reversible and cheap, synthesis and assays are costly but compensable, and clinical trials or scale-up commitments are irreversible and gated. K's value-of-computation rule becomes *which experiment to run next* (Bayesian optimization), and consolidation across campaigns turns each round's results into a prior for the next. The risk is the value signal: optimizing against a docking score or a DFT simulation finds the proxy's errors. Cheap proxies should rank candidates; only experiments should feed the consolidation gate. Self-driving labs are the early form of this domain. It is high value, and it stays human-gated for a long time.

<a id="physical-social"></a>

## 5. Physical and social domains

- **Robotics.** The tiers were built for this: reflexes act first, and the action gate covers physical harm. There are no save states in the physical world, so a simulator serves as scratch, and autonomy grows along the reversibility ladder.
- **Tutoring.** [F7](02_features.md#f7) in reverse: the agent keeps a model of the *student's* zone of proximal development, chooses practice at the edge of the student's competence, and fades its scaffolding as the student grows.

<a id="decision-support"></a>

## 6. Decision support

In these domains feedback is slow, sparse, subjective or adversarial, so consolidation has little honest signal to learn from. The parts that still carry over are the gates and goal shielding, not the learning.

- **Business strategy.** Feedback takes quarters or years, and every situation is new. What carries over: reversibility classes, which are Bezos's "one-way and two-way doors" (R1 moves work toward two-way doors before committing); a shielded objective that holds against noise, pressure and persuasive documents; and scenario simulation of competitors' responses in scratch. The realistic role is a staff analyst. Operational decisions are the exception: pricing tests, A/B experiments and supply-chain tuning are reversible and give clean feedback, and One Loop can run them.
- **Art.** There is no ground truth, and trained aesthetic critics get reward-hacked toward average taste, so a novelty term must push back. One deliberate change: open the goal gate wider for surprises from the agent's own work, since in art a happy accident is sometimes the point, and a goal held too firmly produces competent, dull work (perseveration). The person sets the top goal and the taste through the teacher channel (R7); One Loop is a tireless collaborator that explores, varies and remembers what worked.
- **Portfolio management.** The weakest fit for the learning parts: the signal-to-noise ratio is low, markets are non-stationary and adversarial, backtests overfit, and the market reacts to the agent. Consolidation would mostly learn noise, the false-memory failure in the [failure modes](03_system_design.md#design-rules). The safety parts carry over well: the action gate (position limits, permission for hard-to-unwind trades), a mandate and risk limits shielded from news and from text injected into filings, and a calibrated decision not to trade when uncertain. One Loop is a governance and risk layer around a strategy, not a source of alpha.

<a id="board-games"></a>

## Not recommended: board games

AlphaZero and MuZero already solve them. Board games have one level, one fixed goal, no untrusted input and a perfect value signal, so One Loop's additions have nothing to do. Their lesson for the design is already taken: search distilled into a fast policy ([closest existing systems](03_system_design.md#alphazero)).

<a id="multi-loop"></a>

## Extension: multiple One Loops

Multiple loops work at two scales.

1. **Inside one agent:** the [column option](03_system_design.md#columns), with loops arranged in a hierarchy and peers voting.
2. **Many agents, each a full One Loop.** The design extends if three rules hold:
   - **Other agents are sources.** Their messages carry source tags and trust levels, like tool output. They can inform a step, but cannot change an agent's goal without authority. This blocks agent-to-agent injection.
   - **Shared memory passes the consolidation gate.** Otherwise one agent's false lesson spreads to all (R8: cultural transmission spreads errors too).
   - **Shared resources need coordination.** One agent's action can change another's world: locks or sagas for shared state, and a team-level controller for budget.

Build hierarchical teams first (a manager and workers), where goals flow clearly. Use debate or voting among peers for verification, not generation, and avoid flat swarms of chatty agents. Studies of multi-agent LLM systems find that many underperform a single agent given the same compute, mostly through lost goals, miscommunication and missing verification (Cemri et al., 2025), which are the failures goal shielding and the gates address. The test is the same as for columns: beat a compute-matched single agent and a plain majority vote. Multi-agent work should start only after the single-agent modules have passed the ablation.

References are collected at the end of [Derived features](02_features.md#references).
