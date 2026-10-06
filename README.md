# <img src="assets/images/next-step-icon.svg" alt="Next Step icon: a rising path of committed steps leading to a glowing next step" width="128"> **Thinking About Thinking Machines**

<br/>

My understanding of AI: how minds and machines decide what comes next.

## One Loop: design of a brain-inspired agent

The design of an agent built around a control structure that brains and transformers share: a hierarchy of goal-conditioned loops that commit one step at a time. Each feature is derived from a constraint every agent faces, informed by recent advances in AI and neuroscience, then turned into components, design rules and a staged implementation plan.

1. **[Observations and design principles](docs/one_loop/01_observations.md).** The observation that perception, reasoning, planning, action and language work like transformer generation; what the design covers; the seven constraints the features come from; and the design stance.
2. **[Derived features](docs/one_loop/02_features.md).** Seven features (F1–F7), each derived from a constraint with evidence from brains and machines: the step loop, compiled skills, a reversible inner loop, a controller that decides when to stop, a shielded goal, memory with consolidation, and learning at the edge of competence.
3. **[System design](docs/one_loop/03_system_design.md).** Requirements, the architecture and its components, the step and sleep cycles, and the design rules (R1–R8).
4. **[Implementation plan](docs/one_loop/04_implementation_plan.md).** What current models already provide, the build stages, how the learned components are bootstrapped, acceptance criteria and ablations for each module, and the design's assumptions and risks.
5. **[Applications](docs/one_loop/05_applications.md).** Where to use the agent, in the recommended order: software engineering first, then formal mathematics and open-world games, agents in untrusted environments, discovery and explanation, and decision support last.

References for the series are collected in [References](docs/one_loop/references.md).

## Copyright

© 2026 David Xu. All rights reserved.