# One Loop Framework

*One loop design, applied at every level: project, session, task, action.*

## 1. Execution hierarchy

```
Project    goal              the overall outcome            spans many sessions
 └─ Session   subgoal           one milestone toward the goal   one orchestration run
     └─ Task      task goal         one verifiable unit of work
         └─ Action    expected result   one tool call
```

- **Each level breaks its goal into the level below.** The project goal splits into session subgoals, each subgoal into task goals, and each task goal is reached through actions.
- **A model turn is not an action.** One turn can issue several actions in parallel, so budgets should say whether they count turns or actions.
- **A task can run as a subagent:** a nested orchestration with fresh context.

## 2. The 17 components

| Group | # | Component | Purpose |
|---|---|---|---|
| **Core** | 1 | Orchestration | Runs the loop (model → tool calls → results → repeat), plans, and sequences tasks and actions |
| | 2 | Context | What the model sees: system prompt, goal, environment, files |
| | 3 | Memory | What persists: working memory within a session, project memory across sessions |
| | 4 | Tools | The actions the agent can take |
| | 5 | Verification | Proving the output meets the goal at each level, not just that it was produced |
| **Control** | 6 | Termination / budgets | When to stop: goal verified, or out of turns/tokens/cost/time |
| | 7 | Permissions | What the user allows |
| | 8 | Safety | What the system enforces regardless: sandbox, policies, rate limits |
| | 9 | Observability | Logs, traces, token and cost tracking |
| | 10 | Error handling | Retry, re-plan, escalate, recover |
| **Runtime** | 11 | Interface | CLI, IDE, web, headless or SDK |
| | 12 | Session | Persistence, resume, checkpoints |
| **Lifetime** | 13 | Initialization / shutdown | Setup and cleanup; loads and saves project memory |
| | 14 | Configuration | Settings, model selection and fallbacks, effort level |
| **Extension** | 15 | Hooks | User scripts run on events; can block actions |
| | 16 | Subagents | Delegating tasks to separate agents with fresh context: spawn, wait, resume, interrupt, close |
| | 17 | MCP / plugins / skills / commands | Adding capabilities without changing the core |

**How the groups divide:** Core does the work and checks it. Control keeps the loop in bounds. Runtime and Lifetime host the loop. Extension adds capabilities from outside.

**Key links:**

- Verification (5) passing is the "done" signal for termination (6). Budgets are the backstop for when it never passes.
- When verification (5) fails, error handling (10) decides whether to retry, re-plan or escalate.
- Initialization and shutdown (13) read and write memory (3). That is how one session hands off to the next.

## 3. Where each component applies

| Level | Verification | Termination | Error handling | Other components |
|---|---|---|---|---|
| **Project** | Is the project goal achieved? (often a human sign-off) | Goal achieved, or abandoned | Revise the plan: re-split or re-order subgoals | Project plan and progress, project memory, configuration, extensions |
| **Session** | Is the subgoal met? (Independent check: a second model, a subagent or a human) | Subgoal verified, session budget exhausted, or user ends it | Escalate to the user, or end with a handoff report | Orchestration, context, session state, interface, init/shutdown, observability |
| **Task** | Is the task goal met? (tests, lint, render and inspect) | Retry or turn limit per task | Re-plan the task with a different approach | Subagents |
| **Action** | Did it produce the expected result? (exit code, valid output) | Per-action timeout | Retry, or fix the arguments | Tools, permissions, safety, hooks |

## 4. Design principles

1. **Every level has its own goal, verification, termination and error handling.** Problems are handled at the lowest level that can fix them and escalate only when that level can't.
2. **Verification rolls up but isn't automatic.** Verified tasks support the subgoal, yet the subgoal still needs its own check. The same holds between subgoals and the project goal.
3. **The project plan lives outside any session.** Splitting the project goal into subgoals spans sessions, so the plan and its progress must be saved in project memory.
4. **Sessions end with a handoff.** Shutdown writes which subgoal was met, what's left and what was learned. The next session's initialization reads it.
5. **Budgets are the backstop, not the goal.** A loop should stop because its goal was verified. Budgets only cover failure to get there.
6. **The judge never edits itself.** The agent may improve its own harness, but not the components that check, bound or record it (section 5).

<a id="self-edit"></a>

## 5. What the agent may change about itself

The harness is an optimization target too: between sessions, the agent can propose edits to its own harness, test them and keep those that help ([Phase 4 of the sleep cycle](03_system_design.md#sleep-cycle)). The split below decides what it may touch. **Rule: anything that checks, bounds or records the agent is frozen** ([R10](03_system_design.md#design-rules)). A component it could edit would let it raise its score without getting better.

| # | Component | Self-edit | What the agent may change |
|---|---|---|---|
| 1 | Orchestration | Editable, in part | Workflows, plan templates and task decomposition; the core loop stays fixed |
| 2 | Context | Editable | System-prompt text, what is retrieved, kept and shown; never the pinned goal and permission envelope |
| 3 | Memory | Editable, gated | Entries, through the consolidation gate, as itemized changes |
| 4 | Tools | Editable, in part | Descriptions and implementations of ordinary tools, tested in a sandbox; never a tool that enforces a check |
| 5 | Verification | **Frozen** | — |
| 6 | Termination / budgets | Editable, in part | Controller thresholds within fixed hard caps |
| 7 | Permissions | **Frozen** | — (grants come only from people) |
| 8 | Safety | **Frozen** | — |
| 9 | Observability | **Frozen** | — (logs are the evidence that edits are judged on) |
| 10 | Error handling | Editable | Retry, re-plan and escalation policies |
| 11 | Interface | Out of scope | — |
| 12 | Session | **Frozen** | — (checkpoints are what rollback depends on) |
| 13 | Initialization / shutdown | Editable, in part | The handoff format; loading grants and memory stays fixed |
| 14 | Configuration | **Frozen** | — (model choice and effort are set by people) |
| 15 | Hooks | **Frozen** | — (they belong to the user) |
| 16 | Subagents | Editable | Sub-agent prompts, roles and tool sets, within the parent's grants |
| 17 | MCP / plugins / skills / commands | Editable, in part | Skills and commands; adding a new plugin or server is a new capability and needs permission |

Every accepted edit is a bounded change to one component, states a falsifiable prediction, passes held-out tests without regression, and is versioned for rollback.

## 6. Terminology

| Category | Term | Definition |
|---|---|---|
| **Hierarchy** | Project | The long-lived top-level container that holds one goal and spans many sessions |
| | Session | One orchestration run with fresh context, working toward one subgoal |
| | Task | One verifiable unit of work inside a session, with its own task goal |
| | Action | One tool call |
| | Turn | One model response, which may issue several actions in parallel |
| **Goals** | Goal | The overall outcome a project exists to achieve |
| | Subgoal | One milestone toward the project goal, achieved in one session |
| | Task goal | The acceptance criteria for one task |
| | Expected result | What a single action should produce (exit code, valid output) |
| | Project plan | The split of the project goal into subgoals, with progress |
| | Handoff | What a session writes at shutdown: subgoal status, what's left, what was learned |
| **Self-improvement** | Harness | Everything around the model that runs it: the 17 components |
| | Harness edit | A bounded, versioned change to one editable component, with a falsifiable prediction of its effect |
| | Frozen component | A component the agent cannot edit, because it checks, bounds or records the agent |
| | Held-out tests | Tasks the edit loop never sees, used to accept or reject harness edits |
| **Core** | Orchestration | Runs the loop (model → tool calls → results → repeat), plans, and sequences tasks and actions |
| | Context | Everything the model sees on a turn: system prompt, goal, environment, files, history |
| | Memory | Information that persists: working memory within a session, project memory across sessions |
| | Tools | The actions the agent can take: file edits, shell commands, search, APIs |
| | Verification | Checking the output meets the goal at its level, not just that it was produced |
| **Control** | Termination / budgets | The rules for when to stop: goal verified, or limits on turns, tokens, cost or time reached |
| | Permissions | What the user allows the agent to do |
| | Safety | What the system enforces regardless of permissions: sandbox, policies, rate limits |
| | Observability | Logs, traces, and token and cost tracking that show what the loop did |
| | Error handling | What happens on failure: retry, re-plan, escalate, recover |
| **Runtime** | Interface | How users and programs reach the loop: CLI, IDE, web, headless or SDK |
| | Session state | Persistence, resume and checkpoints for a session |
| **Lifetime** | Initialization / shutdown | Setup and cleanup at the start and end of a session; loads and saves project memory |
| | Configuration | Settings, model selection and fallbacks, effort level |
| **Extension** | Hooks | User scripts that run on events (before or after a tool call, at session start) and can block actions |
| | Subagents | Separate agents with fresh context that take on delegated tasks |
| | MCP / plugins / skills / commands | Ways to add tools, knowledge and workflows without changing the core |
