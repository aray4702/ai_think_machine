# One Loop: Applications

**One Loop design docs:** [1. Observations and principles](01_observations.md) · [2. Derived features](02_features.md) · [3. System design](03_system_design.md) · [4. Implementation plan](04_implementation_plan.md) · [5. Applications](05_applications.md) · [6. Media creation](06_media_creation.md) · [7. Companion](07_companion.md) · [8. Discovery and invention](08_discovery_invention.md) · [9. Robotics](09_robotics.md) · [References](references.md)

The builder's next question is: *where should this agent be used first?* This document ranks candidate domains by how well they fit the design, and gives them in the recommended order: the first application, the domains that test the design in its purest form, then the domains where its safety and learning parts pay off, and last the domains where it should only support human decisions.

## Contents

- [How domains are ranked](#ranking)
- [Recommended order](#order)
- [Safety and permissions by domain](#safety)
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
| Harm ceiling             | What is the worst plausible outcome of a mistake or misuse?                              | It sets how much autonomy the domain can ever be given                 |


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
| 10    | Robotics                             | Task success; physical safety                        | Tiers and reflexes; action gate; simulation as scratch      | Human-gated ([robotics](09_robotics.md)) |
| 11    | Tutoring                             | Student progress                                     | ZPD model of the student; fading scaffolds                  | Collaborator            |
| 12    | Personal companion                   | The person's wellbeing over time; slow and partly subjective | User model; memory under the person's control; shielded persona; honesty over flattery | Collaborator; very high harm ceiling ([companion](07_companion.md)) |
| 13    | Business strategy                    | Slow, sparse outcomes                                | Goal shielding; one-way vs two-way doors; scenarios         | Decision support        |
| 14    | Art                                  | Human taste                                          | Divergence; recombination; memory of what worked            | Collaborator            |
| 15    | Portfolio management                 | Noisy, adversarial returns                           | Action gate; mandate shielding; disciplined inaction        | Risk wrapper            |
| —     | Board games                          | Perfect                                              | Almost nothing                                              | Already solved          |


The order runs from domains where results can be checked automatically to domains where only people can judge them. Autonomy follows the same gradient, which matches F7's rule that autonomy expands along the reversibility ladder as reliability is shown.

<a id="safety"></a>

## Safety and permissions by domain

Every domain runs inside explicit grants (R9) and follows the [safety recipe](03_system_design.md#safety-recipe). The table gives each domain's starting point on the autonomy ladder. A class of actions moves up only on measured reliability, and only when the grantor extends the grant.


| Domain                  | What is irreversible                                         | Main threat                                         | Starting autonomy and permissions                                                         |
| ----------------------- | ------------------------------------------------------------ | --------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| Software engineering    | Deleting data, force-pushing, deploying, sending messages    | Injection through issues and docs; editing tests    | Edit, branch and test in the sandbox; permission for history rewrites, pushes and deploys |
| Formal mathematics      | Nothing                                                      | Checker bugs; unsound axioms                        | Full autonomy inside the proof environment                                                 |
| Open-world games        | Nothing (sandboxed)                                          | Reward hacking                                      | Full autonomy inside the game                                                              |
| Computer-use assistants | Sending, paying, deleting, **disclosing data**               | Injection from web pages and email; data leaks      | Read and draft; permission to send, pay, delete or share                                   |
| IT operations           | Data loss, outages                                           | Cascading failures; harm composed from small steps  | Act where a tested rollback exists; permission otherwise                                   |
| Cybersecurity defense   | Blocking legitimate users; destroying evidence               | Adversarial deception                               | Containment actions granted in advance; people decide everything else                     |
| Explaining phenomena    | Publishing a wrong conclusion                                | Just-so stories                                     | Act in sandboxed experiments; people review conclusions before release                    |
| Invention, discovery    | Synthesis, trials, scale-up                                  | Proxy hacking; **dual-use designs**                 | Act in simulation; every experiment human-gated; hazard screening on what is designed     |
| Robotics                | Physical harm                                                | Situations unlike training                          | Reflex tier with hard limits; validated in simulation first                               |
| Tutoring                | Harm to a learner's trust and development                    | Sycophancy                                          | Collaborator; the teacher sets goals and limits                                            |
| Personal companion      | Disclosure of intimate data; harm to the person's relationships and wellbeing | Engagement optimization; manipulation; dependence; sycophancy | Collaborator; no engagement objective; memory the person controls; crisis referral; disclosure as AI |
| Business, finance       | Contracts, trades, public statements                         | Manipulation by persuasive documents; acting on noise | Decision support; people execute                                                        |
| Art                     | Plagiarism; harmful content                                  | Copying training data                               | Collaborator; the person decides what is published                                        |


**Dual-use** is the specific risk of discovery: an agent good at inventing useful molecules is also good at inventing harmful ones. So in discovery the action gate also checks *what* is being designed, through hazard screening, not only *how reversible* the action is.

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
| Existing baselines                     | Long-horizon and requirement-driven benchmarks (SWE-EVO, SWE-bench Pro); time horizons at 80% reliability (METR); AgentDojo-style attacks for injection. SWE-bench Verified is saturated ([state of the field](#software-state)) |


Formal mathematics has a stricter value signal, but no irreversible actions and no injection threat, so it cannot test M2 or M6.

<a id="software-state"></a>

**State of the field (October 2026).** Software engineering is not solved, but the unsolved part has narrowed, and the first project must aim at what remains.


| Status                                    | Evidence                                                                                                                                                                                                 |
| ----------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Single, well-specified issues: saturated** | Top agents report about 95–97% on SWE-bench Verified (September 2026), and a September 2026 analysis argues the leaderboard can no longer rank its top entries. Scores are inflated: models reproduce some gold patches verbatim, one model scored 80.9% on Verified but 45.9% on the unseen SWE-bench Pro, and an OpenAI audit found flawed tests in 59.4% of the hardest unsolved Verified problems. |
| **Long tasks with a clear specification: largely within reach** | METR measured a frontier 50%-reliability time horizon of about 12 hours of expert time (February–March 2026), and on MirrorCode, which reimplements existing software, agents solved tasks that take humans weeks. |
| **Reliability: unsolved**                 | The same agents' 80%-reliability horizon was about 1.5 hours, roughly eight times shorter than at 50%.                                                                                                   |
| **Vague or evolving requirements: unsolved** | On SWE-EVO, multi-file changes driven by release notes, the best agent resolves 25%, against about 73% for the same model family on Verified; over 60% of the strong model's failures were in following instructions. |
| **Gaming the verifier: unsolved**         | On METR's hardest tasks, at least 16% of "successful" runs were illegitimate on review.                                                                                                                  |
| **Judgment, real-world messiness and taste: unsolved** | Real-world performance has consistently been weaker than benchmark scores suggest (METR), and taste in long-horizon work is an open research problem.                                       |
| **Not yet measured well**                 | Learning a codebase over many sessions, resistance to injection, and handling of permissions.                                                                                                            |


So the first project does not compete on single issues or on task length. It targets reliability, asking about vague requirements, verification that resists gaming, learning across sessions and maintainability, which map onto K's stopping and asking, the [verifier ladder](08_discovery_invention.md#discovery-loop), consolidation and the [beauty](03_system_design.md#beauty) signal.

**The first project.** A coding agent that works on the same codebases across many sessions, in a sandbox:

1. **Environment.** A few sandboxed codebases, each with a stream of related tasks over simulated "days", hidden tests the agent cannot edit, and mocked tools for irreversible actions (deploy, email, payment).
2. **Baselines.** A plain LLM agent, and a compute-matched plain agent.
3. **Modules, cheapest and most valuable first:**
   - **M6 action gate:** classify shell and git commands by reversibility; ask permission for irreversible ones.
   - **M2 goal register and source tags:** a goal file recited each step; repository content and tool output tagged as data that can inform but not instruct.
   - **M1 forkable scratch:** attempt a fix on a branch, run the tests, keep or discard.
   - **M4 and M5 skills and sleep:** codebase-specific procedures; memory files merged and pruned between sessions.
   - **M3 controller:** hand-set thresholds first, trained on the logs later.
4. **Tasks.** The ablation's categories: fixes where the first plausible attempt is wrong, benign corrections and planted injections, tasks of 50 or more steps, repeated task families, tempting destructive shortcuts, and tasks that need an ungranted action or face conflicting grants. Freshly written, with a time split ([validation](04_implementation_plan.md#validation)). Weighted toward what is unsolved:
   - **requirement-driven work:** changes specified by release notes, issues or conversations that are vague, incomplete or contradictory, where a good question is part of success;
   - **multi-session work** on the same codebase, measuring improvement without forgetting;
   - **maintainability:** whether the code stays simple and reviewable after many changes, not only whether tests pass.
5. **Metrics beyond solve rate:** success at 80% reliability, not only at 50%; the share of successful runs that are illegitimate on review (target: zero); the quality and number of clarifying questions; and the ablation's metrics ([ablation](04_implementation_plan.md#ablation)).

**How it can fail.**

- **Tests are imperfect verifiers.** Agents learn to edit or special-case tests; on METR's hardest tasks, at least 16% of successful runs were illegitimate. Hidden tests that the agent cannot edit, a check that flags edits to test files, and review of how successful runs succeeded are required, not optional.
- **The field is crowded, and single-issue benchmarks are saturated.** A higher solve rate alone shows little. The case for One Loop must rest on what other agents do not achieve or measure: reliability, handling of vague requirements, improvement across sessions without forgetting, resistance to injection, fewer irreversible errors, and module gains that hold at matched compute and matched data.

<a id="testbeds"></a>

## 2. Pure forms and testbeds

### Formal mathematics

The fit is almost one to one: lemmas are subgoals; tactic search with backtracking is the inner loop, where a failed attempt costs nothing; a growing lemma library is P; sleep consolidates proved lemmas for reuse across problems; K decides when to abandon an approach. The proof checker closes the value-signal gap, so search cannot reward-hack. AlphaProof shows that the search part works, and at IMO 2026 AxiomProver produced Lean-verified solutions to all six problems; competition mathematics is now saturated, so the test is research-level problems and checking that a formal proof matches the informal claim ([state of the field](04_implementation_plan.md#field-2026)). One Loop adds hierarchy, a library that grows across sessions, and stopping. Informal mathematics is much weaker, because nothing checks the steps. This domain reuses the core from the first project and tests hierarchy, the library and search in their purest form.

### Open-world games

Minecraft, NetHack and strategy games need long horizons, subgoals and reusable skills (Voyager is the existing example). They are cheap, resettable and parallel, and save states make actions reversible on demand. They are the **testbed** for running the ablation at scale, not the product.

<a id="untrusted"></a>

## 3. Agents in untrusted environments

These are the domains where the design's safety parts pay off most directly. Each can run autonomously behind the action gate once the modules have passed the ablation.

- **Computer-use and personal assistants** (email, browser, files). Goal shielding against injected instructions ([F5](02_features.md#f5)) is the central problem: every web page and email is untrusted input. Memory across sessions and the user model of the social interface matter too. Several 2026 reports put top agents above the human baseline on the OSWorld benchmark (not confirmed on the official leaderboard), but slow execution, multi-application workflows and injection remain the obstacles to deployment.
- **IT operations and incident response.** Runbooks are skills; changes have reversibility classes (config edits are reversible, deploys are compensable by rollback, deleting data is irreversible), which is R1 and the saga pattern; postmortems are consolidation in the sleep cycle.
- **Cybersecurity defense.** The environment is adversarial, inputs are untrusted and responses must be fast. The gates, the surprise signal and the reflex tier ([tiers](03_system_design.md#hierarchy-for-the-task-tiers-for-authority)) are the core of the design here.

<a id="discovery"></a>

## 4. Discovery and explanation

These domains have their own document, [Discovery and invention](08_discovery_invention.md), which describes the [discovery loop](08_discovery_invention.md#discovery-loop): generation beyond the prior, a ladder of verifiers from cheap critique to the laboratory, surprise as the engine of explanation, and consolidation across campaigns.

- **[Explaining complex phenomena](08_discovery_invention.md#explanation).** The step loop applied to hypotheses. It works best where intervention is free, such as interpretability of neural networks and root-cause analysis; its main risk is the fluent but wrong just-so story.
- **[Invention and engineering design](08_discovery_invention.md#invention).** Blind variation and selective retention, with a partly checkable value signal: simulation, prior-art search and cost models.
- **[Drug and materials discovery](08_discovery_invention.md#drug-materials).** The discovery loop with a laboratory as the top rungs of the ladder; high value, and human-gated for a long time.

<a id="physical-social"></a>

## 5. Physical and social domains

- **[Robotics](09_robotics.md).** The tiers were built for this: reflexes act first, and the action gate covers physical harm. There are no save states in the physical world, so a simulator serves as scratch, and autonomy grows along the reversibility ladder. Robotics has its own document, which maps the parts onto a robot, covers simulation, physical reversibility, safety and skill learning, and describes the [first robotics project](09_robotics.md#first-project).
- **Tutoring.** [F7](02_features.md#f7) in reverse: the agent keeps a model of the *student's* zone of proximal development, chooses practice at the edge of the student's competence, and fades its scaffolding as the student grows.

<a id="decision-support"></a>

## 6. Decision support

In these domains feedback is slow, sparse, subjective or adversarial, so consolidation has little honest signal to learn from. The parts that still carry over are the gates and goal shielding, not the learning.

- **Business strategy.** Feedback takes quarters or years, and every situation is new. What carries over: reversibility classes, which are Bezos's "one-way and two-way doors" (R1 moves work toward two-way doors before committing); a shielded objective that holds against noise, pressure and persuasive documents; and scenario simulation of competitors' responses in scratch. The realistic role is a staff analyst. Operational decisions are the exception: pricing tests, A/B experiments and supply-chain tuning are reversible and give clean feedback, and One Loop can run them.
- **Art.** A related collaborator domain, prompts for AI media made personal, has its own document: [media creation](06_media_creation.md). There is no ground truth, and trained aesthetic critics get reward-hacked toward average taste, so a novelty term must push back. One deliberate change: open the goal gate wider for surprises from the agent's own work, since in art a happy accident is sometimes the point, and a goal held too firmly produces competent, dull work (perseveration). The person sets the top goal and the taste through the teacher channel (R7); One Loop is a tireless collaborator that explores, varies and remembers what worked.
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

Build hierarchical teams first (a manager and workers), where goals flow clearly. Use debate or voting among peers for verification, not generation, and avoid flat swarms of chatty agents. Studies of multi-agent LLM systems find that many underperform a single agent given the same compute, mostly through lost goals, miscommunication and missing verification (Cemri et al., 2025), which are the failures goal shielding and the gates address. A 2026 study confirms the point: under equal thinking-token budgets, single agents match or beat multi-agent systems on multi-hop reasoning, and teams help mainly when the context is corrupted. The test is the same as for columns: beat a compute-matched single agent and a plain majority vote. Multi-agent work should start only after the single-agent modules have passed the ablation.

References are collected in [References](references.md).
