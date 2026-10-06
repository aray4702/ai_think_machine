# <img src="assets/images/next-step-icon.svg" alt="Next Step icon: a rising path of committed steps leading to a glowing next step" width="128"> **Thinking About Thinking Machines**

<br/>

My understanding of AI: how minds and machines decide what comes next.

## [One Loop: Minds and Transformers](docs/one_loop.md)

**Summary.** Perception, reasoning, planning, action and language all work like transformer generation: *next step = f(goal, everything so far)*. The essay argues that the loop itself is cheap and that competence comes from two control decisions: how much reversible deliberation to place before each commitment, and which inputs may change the goal rather than only inform the next step. LLM agents handle both poorly, for architectural reasons, and the essay proposes tests that could prove the claim wrong.

## [When to Stop: Control Signals in Minds and Agents](docs/when_to_stop.md)

**Summary.** Every step of the loop asks: think more, or act now? Good stopping rules combine a confidence threshold, an urgency signal and a surprise detector. In humans, emotion supplies these signals; agents need the functions, not the feelings.

## [Memory and Skill: How Experience Becomes Knowledge](docs/memory_and_skill.md)

**Summary.** Practice compiles steps into skills that make a hierarchy affordable, and separate memory stores with selective consolidation keep new learning from overwriting old. LLMs have a vast built-in skill memory but can't yet add to it from their own experience.

## [Learning in Order: Development, Teaching and Imitation](docs/development.md)

**Summary.** Learning happens at the edge of competence, and some capabilities depend on others. Piaget, Vygotsky and research on imitation suggest how an agent should be taught, and whether LLM agents, which learned from the top down, need to back-fill the basics.

## [Building the Loop: An Agent Architecture and Its Tests](docs/architecture.md)

**Summary.** The principles from the other essays, assembled into one agent design, with each module treated as a hypothesis that has to beat a larger plain model to be kept.

## Series map

Section labels are shared across the essays, so a reference such as (I.6) or R4 can be followed from any of them.

| Labels | Topic | Essay |
| --- | --- | --- |
| I.1, I.3, I.5, I.8 | The loop, the reversible inner loop, the shielded goal, predictions about humans | [One Loop](docs/one_loop.md) |
| I.4 | Stopping and control signals | [When to Stop](docs/when_to_stop.md) |
| I.2, I.6 | Compiled procedures; memory stores and consolidation | [Memory and Skill](docs/memory_and_skill.md) |
| I.7, II.4 | Edge of competence, development, imitation; build order | [Learning in Order](docs/development.md) |
| II.1–II.3, II.5, II.6 | Requirements, architecture, design-rule index, where transformers stand, tests against scale | [Building the Loop](docs/architecture.md) |
| R1–R4 · R5, R6 · R7 · R8 | Design rules | One Loop · Memory and Skill · When to Stop · Learning in Order |
| P1, P2, P7, P8 · P3 · P4 · P5 · P6 | Falsifiable predictions | One Loop · Memory and Skill · When to Stop · Learning in Order · Building the Loop |
| Claims 1, 3, 5, 13 · 2, 6, 9 · 4, 10 · 7, 8, 11, 14 · 12 | Graded claims | One Loop · Memory and Skill · When to Stop · Learning in Order · Building the Loop |

## Copyright

© 2026 David Xu. All rights reserved.