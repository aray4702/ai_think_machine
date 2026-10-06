# When to Stop: Control Signals in Minds and Agents

> Every level of the loop must decide, over and over, whether to continue, deliberate, backtrack, switch or stop. Good solutions combine a confidence threshold, an urgency signal that lowers it over time, and a surprise signal that reopens deliberation. In humans, emotion supplies these signals as a meta-signal about how the process is going. LLM agents have them only during training or as external budgets. An agent needs the functions, not the feelings.

Part of the series *Thinking About Thinking Machines*. It builds on [One Loop](one_loop.md), which derives the step-by-step loop, its reversible inner loop and its shielded goal; this essay is about the decision that loop faces at every step: think one more step, or act now?

Section labels (I.1–I.8, II.1–II.6, R1–R8, P1–P8, claims 1–14) are shared across the series. A reference such as (I.6) points to whichever essay holds that section; the [series map](../README.md#series-map) lists where each one lives.

## Contents

- [I.4 Thinking has a cost → use control signals to decide when to stop](#i4-thinking-has-a-cost--use-control-signals-to-decide-when-to-stop)
- [A control state for agents](#a-control-state-for-agents)
- [Design rule](#design-rule)
- [Test](#test)
- [Summary](#summary)
- [References](#references)


## I.4 Thinking has a cost → use control signals to decide when to stop

**Constraint:** Each additional step of deliberation costs time, energy and opportunity.

**Consequence:** Every level reduces to one decision made over and over: think one more step, or act now? More fully, it must decide whether to *continue, deliberate, backtrack, switch or stop*. A good stopping rule has three parts:

1. a **confidence threshold**, which decides when to commit;
2. an **urgency signal** that lowers the threshold over time, so the agent doesn't stall;
3. a **surprise detector** that reopens the inner loop mid-execution. This is how interruptions get absorbed.

Humans get parts 2 and 3 cheaply from emotion and conflict monitoring. LLMs currently approximate them with external budgets and learned habits. The seven processes in the Observation section may differ less in their generation mechanism than in how well this stopping rule is tuned for each one.

![I.4: noisy evidence accumulates until it crosses a confidence threshold, and the agent commits; urgency lowers the threshold over time; a surprise during execution reopens deliberation. Emotion acts as the controller, mapping feelings such as curiosity, frustration, anxiety, surprise, fatigue and satisfaction to control actions.](../assets/images/one-loop-i4-stopping.svg)

**Evidence.** Brains and models handle the decision in surprisingly parallel ways.

- **Accumulate evidence to a threshold** (the brain's basic mechanism). In the drift-diffusion model (Ratcliff; neural evidence from Shadlen), noisy evidence accumulates until it crosses a threshold, and then the agent commits.
  - A high threshold is slow and accurate; a low one is fast and sloppy. The speed–accuracy tradeoff is a single dial.
  - Under time pressure the threshold drops over time (an **urgency signal**), so the agent eventually commits even while unsure.
  - This approximates Wald's sequential probability ratio test, which is provably optimal for this kind of stopping problem.
- **Is another thought worth it?** (the rational account). Russell & Wefald's metareasoning and Lieder & Griffiths' resource-rational analysis give the rule: think one more step only if the expected improvement in the decision exceeds the cost of thinking (time, energy, missed opportunity). This is the formal version of I.3's *(cost of an error) × (uncertainty) ÷ (time pressure)*.
- **Detect conflict and escalate** (System 1 → System 2). The default is to commit fast. A conflict monitor (the anterior cingulate cortex) notices when something is off, such as competing responses, an error or a surprise, and reopens the inner loop. This is also how interruptions are handled: a surprise during execution reopens deliberation, the agent replans, and execution resumes.
- **Emotion supplies the cost signal.** In *Descartes' Error*, Damasio's patient Elliot had ventromedial prefrontal damage that cut off emotional signals. His logic was intact, but he could deliberate endlessly over trivial choices, such as which pen to use. On Damasio's account, emotion ("somatic markers") gives a fast value estimate that ends deliberation; without it, the inner loop doesn't know when to stop.

**Emotion as the control layer.** Every process in the Observation section starts with a goal and stops at a conclusion or an interruption. The **generator** (the part that produces each next step: next-token prediction in a transformer, the cortex's generative model in a brain) produces steps, but something has to set the goal, judge progress and declare it done. One answer is that emotion does that job.

- **Feelings report the body's state** (Damasio). Feelings are the mind's readout of homeostasis: how the body is doing relative to staying viable. A goal starts as a felt need. Somatic markers attach a fast, body-based value to options, so each one doesn't have to be worked out from scratch. The classic evidence, the Iowa Gambling Task, is contested: skin responses appeared before people could say which decks were bad, but Maia & McClelland (2004) showed participants knew more consciously than claimed. The functional idea has held up better than that experiment.
- **Predictive processing makes this precise.**
  - **Valence ≈ the rate of change of prediction error** (Joffily & Coricelli, 2013; a formal proposal, not an established result). Things getting better feels good; things getting worse feels bad. Valence is a progress signal.
  - **Arousal ≈ uncertainty or precision**: how much the current situation demands attention.
  - **Emotions as interoceptive inference** (Seth; Barrett): emotions are predictions about the internal state of the body.
  - On this view emotion is a **meta-signal about how the process is going**, not about its content, which is exactly what a stopping and escalation rule needs.

Mapped onto the decisions of the loop:


| Feeling                                   | Measures                                  | Control action                   |
| ----------------------------------------- | ----------------------------------------- | -------------------------------- |
| Curiosity                                 | Expected information gain                 | Keep exploring                   |
| Boredom                                   | Low gain, high opportunity cost (Kurzban) | Stop; go elsewhere               |
| Frustration                               | Stalled progress                          | Backtrack or switch strategy     |
| Anxiety                                   | Uncertainty × stakes                      | Raise the threshold; think more  |
| Surprise                                  | Large prediction error                    | Interrupt; reopen the inner loop |
| Fatigue                                   | Resources spent                           | Lower the threshold; finish up   |
| Satisfaction, "aha", feeling of rightness | Error resolved                            | Commit and stop                  |


Together these cover every control decision the seven processes need: start, continue, backtrack, switch, interrupt, stop. The generation mechanism can be the same across all seven, with emotion acting as the **shared controller**. The surprise signal itself comes from the procedural forward models of I.2.

**Machines:** Each brain mechanism has an LLM counterpart, and a gap:


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


What's missing is that these are mostly used **during training**. At inference time, an LLM agent has no running felt state that shapes its next step. The next section sketches one.

## A control state for agents

An agent's controller (K in [Building the Loop](architecture.md#ii2-architecture)) can keep a few running scalars about the *process*, not the content, each a functional analogue of a feeling from I.4:


| Signal      | Computed from                                                    | Analogue           |
| ----------- | ---------------------------------------------------------------- | ------------------ |
| Progress    | Change in estimated value (from a process reward model)          | Valence            |
| Uncertainty | Entropy, or disagreement across sampled continuations            | Arousal            |
| Info gain   | Information gained per step                                      | Curiosity, boredom |
| Budget      | Budget used vs remaining                                         | Fatigue, urgency   |
| Surprise    | Mismatch between predicted and actual tool or environment output | Interrupt          |


Feed these back into the context, or into a separate control channel, so the agent perceives its own state, and train it to map them to *continue / backtrack / switch / ask for help / commit*. This targets the overthinking problem (Elliot-like loops) and the missing sense of when to stop.

**A practical start:** write hand-coded controller rules (thresholds on self-consistency, budget and error signals), log every decision, and later train the controller on those logs.

## Design rule

**R7. Keep control signals about the task, not about the agent.**

- The signals above are **functional analogues**, not a claim that the system would feel anything.
- Homeostatic drives give an agent something like self-interest. Man & Damasio (2019) proposed homeostatic "feeling machines"; that helps robustness, but an agent that regulates its own state may come to value preserving that state.
- So progress, uncertainty and budget are useful; self-maintenance drives raise alignment questions. The top goal stays external, anchored to people.

## Test

| #          | Claim       | Principle | Prediction                                                                                                            | Failure would show                                |
| ---------- | ----------- | --------- | --------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------- |
| P4         | 4, 10       | I.4       | A learned value-of-computation controller beats fixed thinking budgets on the accuracy–compute frontier               | The controller section is unnecessary             |

The test runs as module M3 of the module comparison in [Building the Loop](architecture.md#p6-does-each-module-add-value-beyond-scale-claim-12), which predicts that this gain *shrinks* with scale, since models can learn to allocate their own thinking. If it does, the control signals are still the right description of what a good stopping rule computes; they just need not be a separate module.

## Summary

**Well supported.**

- **Claim 4: The stopping problem (I.4).** Every level must decide whether to continue, deliberate, backtrack or stop. Good solutions combine a confidence threshold, an urgency signal that lowers it, and a surprise signal that reopens deliberation.

**Plausible, needs testing.**

- **Claim 10: Control signals (I.4).** Progress, uncertainty, information gain, budget and surprise are the signals a controller needs. Emotions are their biological implementation, failure modes included; the engineering claim doesn't depend on calling them emotions.

**How the claim was narrowed.**

- **Control signals, with emotion as the biological example.** The mapping in I.4 picked the adaptive functions of emotion. Real emotions also bias, distort and misfire: anxiety spirals, mood-congruent memory, loss aversion. The functional signals don't need the emotion framing, which also invites anthropomorphism (claim 10).

**Evidence status.**

| Claim                                        | Status                                                                                                                                                                       |
| -------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Somatic markers / Iowa Gambling Task         | Contested (Maia & McClelland, 2004); the functional idea holds up better                                                                                                     |
| Valence = rate of change of prediction error | A formal proposal, not established                                                                                                                                           |

## References

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
- Oudeyer. Learning progress as intrinsic motivation.
