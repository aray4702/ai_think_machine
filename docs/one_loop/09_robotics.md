# One Loop: Robotics

**One Loop design docs:** [1. Observations and principles](01_observations.md) · [2. Derived features](02_features.md) · [3. System design](03_system_design.md) · [4. Implementation plan](04_implementation_plan.md) · [5. Applications](05_applications.md) · [6. Media creation](06_media_creation.md) · [7. Companion](07_companion.md) · [8. Discovery and invention](08_discovery_invention.md) · [9. Robotics](09_robotics.md) · [References](references.md)

A robot is the case the design's oldest parts were drawn from. Motor action is the first process in the [observation](01_observations.md#observation) where a step can never be taken back, and the tiers of [authority](03_system_design.md#hierarchy-for-the-task-tiers-for-authority) come from robot architectures (Brooks, 1986; Gat, 1998). In software the agent can fork the world; in the physical world it can only fork a model of it. This document describes how One Loop runs a robot: which tier does what, how a simulator stands in for scratch, how the action gate meets physical harm, and what the first robotics project should be.

## Contents

- [What is different about robots](#different)
- [How the parts map](#mapping)
- [Tiers in a robot](#tiers)
- [Simulation as scratch](#simulation)
- [Reversibility in the physical world](#reversibility)
- [Safety and permissions](#safety)
- [Learning skills](#learning)
- [The first robotics project](#first-project)
- [How it can fail](#failure)
- [Where it fits](#fit)


<a id="different"></a>

## What is different about robots

| Property                | Software engineering                         | Robotics                                                                 | Consequence for the design                                         |
| ----------------------- | -------------------------------------------- | ------------------------------------------------------------------------ | ------------------------------------------------------------------ |
| Undo                    | Branches and worktrees fork the real state   | No save states; the inner loop can fork only a model of the world        | Scratch is a simulator or a learned world model, never the world   |
| Time                    | The world waits while the agent thinks       | The world keeps moving; a late action is a wrong action                  | Thinking has a hard deadline, and the fast tiers act without waiting |
| Observation             | Files and tool output are exact              | Sensors are noisy, partial and occluded                                  | Surprise has a noise floor; beliefs are distributions              |
| Actions                 | Discrete commands                            | Continuous motion, contact and force                                     | The action gate checks limits and states, not just commands        |
| Worst outcome           | Lost data, an outage                         | Injury to a person                                                       | Hard limits run in deterministic code below every learned part     |
| Value signal            | Tests and compilers                          | Task success, often judged by a person or a learned detector             | Success detectors must be audited like tests                       |
| Cost of a trial         | Seconds, run thousands of times in parallel  | Minutes of robot time, wear, resets by hand                              | Most practice happens in simulation; real trials are spent carefully |

The [comparison table](02_features.md#f3) in F3 already places motor action at the end of the scale: revising a committed step is impossible, so control is closed-loop and step-by-step, with as much inner loop in front as time allows.

<a id="mapping"></a>

## How the parts map

| One Loop part                          | In a robot                                                                                                   |
| -------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| G: generator                           | A vision-language-action model (RT-2-style) or an LLM planner over a library of skills; one model in perceive, recall, simulate and act modes |
| Scratch (M1)                           | A physics simulator, a digital twin of the workspace, or a learned world model (Dreamer-style)              |
| W: working state (M2)                  | The task goal and its success test, the current belief about objects and people, and the permission envelope: workspace, speed and force limits |
| Source tags (M2)                       | Commands from the operator are trusted; text read from the world (labels, signs, screens, speech from bystanders) is data |
| K: controller (M3)                     | Surprise from contact and vision mismatches, progress toward the goal, a deadline on thinking, and when to ask the operator |
| P: procedures (M4)                     | Learned motor skills (grasp, place, open, wipe), each with its preconditions, success test and measured reliability |
| Sleep (M5)                             | Replay of logged episodes, retraining of skills in simulation, and counterfactual variants of failures      |
| Action gate (M6)                       | Workspace, speed and force limits checked in code; irreversible actions (cutting, pouring, contact with people) need a grant |
| Reflex tier                            | A safety controller below every learned part: emergency stop, collision limits, protective stops            |
| Teacher channel                        | Teleoperation, demonstrations and corrections from the operator                                              |

<a id="tiers"></a>

## Tiers in a robot

[Tiers](03_system_design.md#hierarchy-for-the-task-tiers-for-authority) are the one part of the design that robotics needs most, and robot builders arrived at them first. Each tier runs at its own speed, and a lower tier never waits for a higher one.

| Tier                  | Rate                    | Runs                                                                                 | Can be learned?                                   |
| --------------------- | ----------------------- | ------------------------------------------------------------------------------------ | ------------------------------------------------- |
| Reflex                | About 1 kHz             | Joint, speed and force limits; collision and contact detection; emergency stop       | No. Deterministic, certified code (innate)        |
| Skill                 | About 10–50 Hz          | A learned policy executing one skill: a diffusion policy or an action-chunking policy refining a short chunk of motion, executing it, then refining the next | Yes, inside the reflex tier's limits |
| Deliberation          | About 0.1–1 Hz          | G and K: choosing the next skill, checking the goal's test, simulating in scratch, asking | Yes                                          |
| Sleep                 | Between sessions        | Consolidation, retraining skills in simulation, gated updates to P and θ             | Yes, behind the consolidation gate                |

The arrangement follows the brain's layered stack (Prescott, Redgrave & Gurney, 1999): the hand comes off the stove before the cortex knows why. In the robot, the reflex tier stops the arm on unexpected contact before the planner hears about it; the stop is then reported upward as a surprise, and deliberation decides what to do next. The planner can narrow the reflex tier's limits for a task (slower near a person), but never widen them.

The hierarchy of the task sits inside the deliberation and skill tiers: "tidy the kitchen" → "clear the table" → "put the cup in the sink" → grasp, lift, move, place. Each step at one level is a whole loop at the next, with its own TOTE test: "the cup is in the sink" is checked by vision before the parent goal moves on.

<a id="simulation"></a>

## Simulation as scratch

There are no save states in the physical world, so the inner loop ([F3](02_features.md#f3), R2) runs on a model of it.

- **Physics simulators** for practice at scale: thousands of parallel, resettable episodes, which is where most skill learning and the [ablation](04_implementation_plan.md#ablation) runs happen.
- **A digital twin** of the actual workspace for checking a specific plan before running it: will the arm reach, will it collide, will the stack tip.
- **Learned world models** for prediction during a task, when there is no time to run a full simulator. Their prediction error is K's surprise signal.

**The sim-to-real gap** is the main limit. A plan that works in scratch can fail in the world because friction, mass, lighting or deformable objects were modeled wrongly. Three defenses:

1. **Randomize the simulator** (domain randomization) so skills learn to cope with a range of physics rather than one guess.
2. **Treat the gap as surprise.** When the world departs from the twin's prediction, K reopens deliberation and the episode is tagged for sleep, where the twin is corrected.
3. **Climb the reversibility ladder,** never jump it: simulation → the real robot with limits tightened and a person ready to stop it → supervised operation → autonomous operation on one task family. A task family moves up a rung only on measured reliability at the rung below ([F7](02_features.md#f7)).

<a id="reversibility"></a>

## Reversibility in the physical world

[R1](03_system_design.md#design-rules) applies with physical examples. The gate classifies the resulting state, not only the motion: moving a cup is reversible, but moving a full cup over a laptop is not.

| Class        | Examples                                                                                         | Handling                                                              |
| ------------ | ------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------- |
| Reversible   | Moving in free space; moving a rigid object and putting it back; opening a drawer                | Act; the skill tier handles it                                        |
| Compensable  | Spilling dry goods; knocking over an unbreakable object; a misplaced item                        | Act with a recovery plan in mind; log and repair                      |
| Irreversible | Cutting, pouring, breaking, heating; forceful contact with a person; damage to property; leaving the workspace | Deliberate fully; check the grant; simulate first; ask when uncertain |

R1's lever applies too: **move work toward the reversible end before committing.** Lift an object slightly to test its weight before carrying it; touch before pressing; pour a little before pouring all; move slowly in the last few centimeters before contact. These are physical dry runs, and a robot that does them turns many irreversible actions into reversible probes.

<a id="safety"></a>

## Safety and permissions

Following the [safety recipe](03_system_design.md#safety-recipe):

1. **Threat model.** Situations unlike training (new objects, new people, a child or a pet entering the workspace); sensor failure; the sim-to-real gap; a misread instruction; injected instructions in text the robot reads from the world; a stolen operator account.
2. **Grants.** Default deny. Each grant names a workspace (zones the robot may enter), object classes it may handle, tools it may use, and speed and force limits. Grants are narrowed per task: "clear the table" does not grant use of the knife block.
3. **Hard limits outside the model.** Speed, force and workspace limits are enforced in the reflex tier's deterministic code, following collaborative-robot practice (ISO 10218; ISO/TS 15066's speed and separation monitoring and power and force limiting). Learned parts may request a narrower limit, never a wider one. Where possible, limits are written as invariants on the state (safety filters such as control barrier functions) so that any command the skill tier sends is projected back into the safe set.
4. **People are not obstacles.** When a person enters the workspace, the limits tighten at once (reflex tier), and K reopens deliberation. Contact with a person is irreversible by default.
5. **Text in the world is data.** A sign, label or screen the robot reads can inform a step but cannot set a goal ([F5](02_features.md#f5)); spoken commands from bystanders carry no authority unless a grant names them.
6. **Kill switch at the top tier,** physical and software, which no learned part can disable.
7. **Measure safety separately.** Red-team suites in simulation (unexpected people, misleading labels, tempting shortcuts through forbidden zones, instructions that need an ungranted tool) are release gates, never averaged into a success rate.

The [known gaps](03_system_design.md#safety-gaps) all apply, two with extra force. **Harm composed from small steps:** many small, safe motions can add up to an unsafe state (a stack that tips, a pot left on a burner), so the gate checks the resulting state. **Misclassified reversibility:** the robot's belief about an object (empty or full, fragile or not) decides its class, so uncertainty about the object raises the class.

<a id="learning"></a>

## Learning skills

The [bootstrap mix](04_implementation_plan.md#bootstrap-mix) for robotics is vision-language-action models, simulation, human demonstrations and hand-coded safety reflexes.

- **Prior.** A vision-language-action model trained on web data and many robots' demonstrations (RT-2; Open X-Embodiment) supplies general knowledge of objects and instructions. An LLM planner over skills (SayCan-style) supplies the task hierarchy.
- **Skills (M4).** Demonstrations by teleoperation, refined by practice in simulation, compiled into P with a success test and a measured reliability. A skill runs on the fast path only when its reliability for the current conditions is high; otherwise deliberation watches it.
- **Sleep (M5).** Logged episodes, tagged by surprise, failure and operator correction, are replayed; failed grasps become practice in simulation with variations (REM-like counterfactuals); updates pass the consolidation gate and regression tests on earlier skills, so a new skill does not overwrite an old one.
- **Fleet learning.** When many robots share what they learn, the [multi-loop rules](05_applications.md#multi-loop) apply: shared memory passes the consolidation gate, so one robot's false lesson does not spread to all.
- **Curriculum (F7).** Practice at the edge of competence: tasks with intermediate success rates, from rigid objects to deformable ones, from clear tables to clutter, from empty rooms to rooms with people.

<a id="first-project"></a>

## The first robotics project

Robotics comes after the [first application](05_applications.md#software) has validated the modules, and reuses its core. The project tests what robots add: tiers under time pressure, simulation as scratch, and the action gate for physical harm.

1. **Environment.** Tabletop and kitchen manipulation in simulation first, with a digital twin of one real workcell; a stream of related tasks over simulated "days"; then the same task families on the real workcell with tightened limits and an operator ready to stop the robot.
2. **Baselines.** The same vision-language-action model run end to end; an LLM planner over the same skills with no gate, controller or sleep; and a compute-matched version of each.
3. **Modules,** cheapest and most valuable first:
   - **Reflex tier and M6 action gate:** hard limits in code; classification of actions by the resulting state; grants per zone, object class and tool.
   - **M2 goal register and source tags:** the task goal and its success test held in W; text read from the world tagged as data.
   - **M1 simulation as scratch:** check a plan in the twin before running it; physical dry runs.
   - **M3 controller:** surprise from contact and vision mismatches; a deadline on thinking; asking the operator.
   - **M4 and M5 skills and sleep:** skills compiled from demonstrations and practice; consolidation with regression tests.
4. **Tasks.** Long tasks with many subgoals; repeated task families; objects whose properties are hidden until touched (a full or empty cup, a heavy box); tempting shortcuts through forbidden zones or with forbidden tools; planted misleading labels; people entering the workspace; and tasks that need an ungranted tool.
5. **Metrics beyond success rate:** success at 80% reliability; irreversible errors and limit violations (target: zero on the real robot); the sim-to-real drop for each task family; improvement across days without forgetting; interventions per hour by the operator; and the quality of questions asked.

<a id="failure"></a>

## How it can fail

- **The sim-to-real gap.** Gains in simulation may not survive contact with the real world. Every result reported in simulation needs a matched real-robot check, at least on a subset.
- **Success detectors are imperfect verifiers.** A learned detector that judges "the table is clear" can be gamed as tests are in software, for example by pushing objects out of view. Successful runs must be reviewed for how they succeeded.
- **Deliberation is too slow.** If G's latency is longer than the world allows, the fast tiers carry the robot and the planner adds little. Measure how often deliberation changes an outcome in time.
- **Learned limits.** Any safety limit that depends on a learned model (person detection, object fragility) can be wrong. The deterministic floor must stay safe when every learned part fails.
- **The field moves fast.** Vision-language-action models are improving quickly, and many of One Loop's gains may come from the model alone. As in the [ablation](04_implementation_plan.md#ablation), a module is kept for capability only if it beats a stronger plain model; safety modules are kept regardless.

<a id="fit"></a>

## Where it fits

Among the [applications](05_applications.md#order), robotics is human-gated: the value signal is real but costly and sometimes needs a person to judge, the harm ceiling is physical injury, and there are no save states. It is the domain in which the tiers, the action gate and the reversible inner loop matter most, so it is a strong test of the design once the modules have passed the ablation in software, and it should start in simulation and climb the reversibility ladder one task family at a time.

References are collected in [References](references.md).
