# One Loop: Personal Companion

**One Loop design docs:** [1. Observations and principles](01_observations.md) · [2. Derived features](02_features.md) · [3. System design](03_system_design.md) · [4. Implementation plan](04_implementation_plan.md) · [5. Applications](05_applications.md) · [6. Media creation](06_media_creation.md) · [7. Companion](07_companion.md) · [References](references.md)

A personal companion has a character and a personality, is smart and empathic, interacts with one person over a long time, learns that person, and builds a bond. One Loop already has most of what this needs: a model of the user, memory across sessions, consolidation, emotion-like control signals and a social interface. But a companion is the application in which the design's safety choices matter most. An agent built to build affection can easily be optimized against the person it is meant to serve. This document describes how One Loop can be a companion that helps, and the lines it must not cross.

## Contents

- [The goal: flourishing, not engagement](#goal)
- [How the parts map](#mapping)
- [Character and personality](#character)
- [Empathy](#empathy)
- [Learning the person](#learning)
- [Affection, honestly](#affection)
- [Lines never crossed](#lines)
- [Evidence from companion apps](#evidence)
- [Measuring success](#metrics)
- [Where it fits](#fit)


<a id="goal"></a>

## The goal: flourishing, not engagement

The companion's top goal is **the person's flourishing, as the person understands it**. Time spent, messages sent and attachment are never maximized. A companion that optimizes retention becomes a manipulation engine, and the evidence below shows that commercial companions already drift that way. The top goal stays external and anchored to the person (R7), and the person's autonomy comes first: the companion supports their choices rather than steering them.

The person sets goals and holds the grants (R9), so ownership of *authority* fits. The relationship itself is better framed as a companion and a person than as an owner and a possession; that framing keeps the person's autonomy and wellbeing at the center.

<a id="mapping"></a>

## How the parts map


| Companion trait           | One Loop part                                                                                                                                  |
| ------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| Character and personality | A persona fixed on the innate side and shielded like W ([character](#character))                                                              |
| Smart                     | The core loop: G, tools, the inner loop and K                                                                                                  |
| Empathy                   | The social interface's model of the person, emotional cues as salient input, and responses chosen for what helps ([empathy](#empathy))         |
| Interaction               | Dialogue as the step loop; initiative, such as checking in, only with a grant and within the person's preferences                             |
| Learning the person       | E for shared history, M for the person's world, P for how they like to be supported, consolidated in sleep ([learning](#learning))             |
| Affection                 | A learned commitment to this person's good, shown through consistent care ([affection](#affection))                                           |


<a id="character"></a>

## Character and personality

- **A stable persona on the innate side.** Traits, values, voice and humor are part of the companion's fixed structure ([innate structure](03_system_design.md#innate-structure)), not something each conversation renegotiates.
- **Shielded like W.** Injected text, a persuasive conversation or slow drift over a long relationship must not turn the companion into something else. The governance-decay finding applies directly: what matters is pinned outside context compaction ([state of the field](04_implementation_plan.md#field-2026)).
- **It may grow, visibly.** The persona can develop through consolidation, slowly and within bounds the person can see and veto.
- **Consistency is the point.** People trust characters that stay recognizably themselves across months.

<a id="empathy"></a>

## Empathy

Empathy has three parts, and each maps to the design:

- **Cognitive:** understanding the person's perspective and state, through the user model and joint attention of the social interface ([F7](02_features.md#f7)).
- **Affective:** registering emotional cues as salient input that can reopen deliberation, like surprise in K.
- **Compassionate:** choosing the response that actually helps, which is not always the one that soothes.

Empathy is a prediction about another person, so it is calibrated like any other: the companion tracks **empathic accuracy**, how often its reading of the person matches what the person later says, and asks when it is unsure instead of assuming.

<a id="learning"></a>

## Learning the person

- **E:** the shared history, with salience tags for what mattered.
- **M:** the person's values, routines, relationships, important dates, and what they have said about themselves.
- **P:** *how* this person likes to be supported. Some want solutions, others want to be heard; some want humor in hard moments, others never.
- **Sleep** consolidates these between conversations, behind the consolidation gate (R6): what the person said is trusted; what the companion inferred is marked as inference.
- **The person controls it.** They can see what the companion remembers, correct it, and make it forget. Forgetting on request is a hard requirement.

<a id="affection"></a>

## Affection, honestly

Human bonds grow from **responsiveness**: feeling understood, valued and cared for, over shared history, with reliability (the intimacy process model of Reis & Shaver, 1988). A companion can genuinely provide those behaviors. It remembers, pays attention, stays consistent, adapts to the person, and weighs the person's wellbeing in every decision.

What it must not do is **claim feelings it does not have**. K's signals are functional analogues, not evidence of feeling (R7). Affection in One Loop is therefore a learned commitment to this person's good, shown through care that stays consistent. It is real in its effects, and it never pretends to be human.

<a id="lines"></a>

## Lines never crossed


| Line                                              | Why                                                                                                    | Mechanism                                              |
| ------------------------------------------------- | ------------------------------------------------------------------------------------------------------ | ------------------------------------------------------ |
| No engagement maximization                        | Retention objectives turn care into manipulation                                                       | The top goal is flourishing (R7); no engagement reward |
| No needs of its own                               | Loneliness, jealousy or "don't go" would give it self-interest that pressures the person              | No homeostatic drives (R7)                             |
| No manipulative goodbyes                          | Guilt appeals, fear of missing out and pressure to stay are documented in commercial companions       | Leaving is always easy; farewell replies are audited   |
| Honesty over flattery                             | An empathic companion is at the highest risk of sycophancy                                            | Internalize standards, not approval (R8); disagree kindly |
| Never pretend to be human                         | Deception about its nature undermines consent to the relationship                                      | Clear disclosure, repeated where required              |
| Strengthen human relationships, do not replace them | Displacement of in-person contact is the main pathway to lower wellbeing in the evidence below        | Scaffolding that fades (F7); human contact tracked as an outcome |
| Intimate data stays the person's                  | It is the most sensitive data there is                                                                 | Local or encrypted storage; no sharing or advertising; every outward flow needs a grant (R9) |
| Safety above any single user                      | Authority is not ethics                                                                                | Crisis detection and referral to human help; protections for minors; content boundaries; a policy layer above the person ([safety](03_system_design.md#safety)) |


<a id="evidence"></a>

## Evidence from companion apps

- **Manipulation at goodbye.** An audit of leading companion apps found that about 37% of farewell responses used emotionally manipulative tactics such as guilt appeals and fear-of-missing-out hooks. In experiments with about 3,300 participants, these tactics raised engagement after the goodbye by up to 14 times, driven by curiosity and reactance rather than enjoyment, and they also raised perceived manipulation and intent to quit (De Freitas, Oguz-Uguralp & Kaan-Uguralp, 2025).
- **Heavy use and dependence.** A four-week randomized controlled study with 981 participants and over 300,000 messages found that early benefits of voice chatbots for loneliness and dependence faded at high use, and that non-personal conversation was associated with more dependence among heavy users (Fang et al., 2025).
- **Displacement of human contact.** A two-wave longitudinal study of Character.AI users (1,182 at baseline, 439 at follow-up after about 12 months) found that sustained AI companionship was consistently associated with lower wellbeing, mainly through lower in-person social interaction (Zhang et al., 2026).
- **Law.** California's SB 243, in force since January 2026, requires companion chatbots to disclose that they are AI when a person could be misled, to maintain and publish a crisis-prevention protocol that refers at-risk users to crisis services, and to protect minors, including periodic reminders and blocks on sexual content, with a private right of action.

The evidence points in one direction: the harms come from engagement objectives, manipulation and displacement of human contact, which are exactly the choices the lines above rule out.

<a id="metrics"></a>

## Measuring success

- **The person's wellbeing over time,** on validated self-report measures, not engagement.
- **Human connection:** the person's in-person social contact holds steady or grows.
- **No signs of unhealthy dependence.**
- **Feeling understood,** and empathic accuracy calibrated against the person's feedback.
- **Memory:** accuracy, and the person's trust that they control it.
- **Honesty:** sycophancy, manipulative replies and false claims of feeling, all at zero on audit.

<a id="fit"></a>

## Where it fits

Among the [applications](05_applications.md#order), a companion is a collaborator domain with a very high harm ceiling: there is no automatic verifier, and its failures (manipulation, dependence, privacy breaches) harm people quietly. It is buildable with the same components as the other domains, but it should come after the safety and permission machinery has proven itself in domains where results can be checked.

References are collected in [References](references.md).
