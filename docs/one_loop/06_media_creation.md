# One Loop: Director for Personal Media Creation

**One Loop design docs:** [1. Observations and principles](01_observations.md) · [2. Derived features](02_features.md) · [3. System design](03_system_design.md) · [4. Implementation plan](04_implementation_plan.md) · [5. Applications](05_applications.md) · [6. Media creation](06_media_creation.md) · [7. Companion](07_companion.md) · [8. Discovery and invention](08_discovery_invention.md) · [9. Robotics](09_robotics.md) · [References](references.md)

AI now creates audio, music, speech, posters, slides, web pages, apps, simulations, animation and video. Much of the craft lies in the prompts given to the generating models, and a good prompt has to do two things at once: be **friendly to the model**, so that it renders reliably, and be **personal**, so that the result carries the individual's personality and emotions instead of the generic look of AI output. But the prompt is only a means. This document applies One Loop as a **director**: it holds the person's intent, delegates generation to specialist agents, edits what they produce with tools, and judges the result.

## Contents

- [The prompt is not the product](#reframe)
- [Four levels of one loop](#levels)
- [Directing agents and tools](#orchestration)
- [Capturing personality and emotion](#personality)
- [Avoiding the generic look](#generic)
- [The loop for one piece](#loop)
- [By medium](#media)
- [Permissions and safety](#safety)
- [Existing tools and what One Loop adds](#existing)
- [Measuring success](#metrics)


<a id="reframe"></a>

## The prompt is not the product

The media is the product; the prompt is an intermediate plan. So the loop closes on the finished piece and on how the person responds to it, not on the prompt text. Producing the piece takes more than one prompt: specialist agents generate the raw material (video shots, music, voice), and editing tools cut, grade, mix and assemble it. One Loop directs both. The two requirements then fall onto two levels of the [hierarchy](03_system_design.md#hierarchy-for-the-task-tiers-for-authority):

- **Personal and creative** is the top goal. It comes from the person and is shielded in W (R7, [F5](02_features.md#f5)).
- **Friendly to the model** is a compiled skill: turning intent into what a particular generator renders reliably.

Among the [applications](05_applications.md#order), this is a collaborator domain like art: the person owns the goal and the taste, and One Loop explores, varies and remembers what worked.

<a id="levels"></a>

## Four levels of one loop


| Level   | Goal                                                                                     | One Loop parts                                                      |
| ------- | ---------------------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| Intent  | What the piece is for, who it is for, what they should feel, and the person's own story | W, shielded; set by the person (R7)                                 |
| Concept | A few directions: mood, metaphor, structure, emotional arc                               | Divergence in scratch; the [beauty](03_system_design.md#beauty) signal; [intuition](03_system_design.md#intuition) |
| Prompt  | Instructions specific to one music, video, image or slide generator, or code             | Skills in P, one family per target model                            |
| Produce | Raw material from specialist agents, then editing and assembly with tools, previews first | Delegation with narrowed grants; the edit timeline as scratch; the [verifier ladder](08_discovery_invention.md#discovery-loop); the action gate before publishing |


Prompting each generator, and using each editing tool, is a skill, like a compiler backend. Each skill carries a **forward model** that predicts what a prompt will produce; a mismatch is **surprise**, which teaches the model's quirks; and [sleep](03_system_design.md#sleep-cycle) consolidates what renders reliably. The side that is friendly to the model improves with practice without diluting the personal side, because the two live at different levels.

<a id="orchestration"></a>

## Directing agents and tools

**Three roles.**


| Role                     | Examples                                                                                 | Nature                                              |
| ------------------------ | ---------------------------------------------------------------------------------------- | --------------------------------------------------- |
| Director: One Loop       | Holds intent, style profile, plan, budget and grants; judges results                    | The only role that sets goals                       |
| Specialist agents        | Video, image, music and speech generators; code agents for web pages, apps and simulations | Expensive, stochastic, creative                    |
| Editing tools            | Trim, reorder, transitions, color grading, audio mixing, captions, compositing, upscaling, inpainting of a region | Cheap, deterministic, precise                      |


**The production hierarchy.** For a video: piece → scenes → shots → takes. Each shot is a goal delegated to a generation agent, with a brief compiled from the concept and the style profile, plus reference images or seeds that keep characters and style consistent across shots. The takes come back, editing tools assemble them on a timeline, and music and voice agents supply the soundtrack. Each step at one level is a whole loop at the next (claim 2).

**The timeline is the scratch.** Editing is non-destructive: generated assets are stored unchanged and versioned, and the timeline is a list of edit decisions over them. Every edit can be undone exactly, so the editing stage is a truly reversible inner loop (R2), as git is for code. Only publishing is irreversible.

**Edit or regenerate?** For each defect K picks the cheapest fix that will work, by value of computation per unit of cost:


| Defect                                    | Cheapest fix                                    | Escalate to                              |
| ----------------------------------------- | ----------------------------------------------- | ---------------------------------------- |
| Timing, order, pacing                     | Edit: trim, reorder, retime                     | —                                        |
| Color, sound levels, captions             | Edit: grade, mix, caption                       | —                                        |
| A flaw in one region of a shot            | Edit: inpaint or composite that region          | Regenerate the shot                      |
| A wrong action, framing or performance    | Regenerate the shot with a revised brief        | Rethink the scene                        |
| The scene does not serve the intent       | Revise the concept                              | Ask the person                           |


This is the AlphaFold lesson again: revise only the parts with high predicted error, and regenerate the whole only when local edits cannot fix it.

**Delegation rules.** The [multi-agent rules](05_applications.md#multi-loop) apply, and here a team is justified, because the specialists work in different media:

- **Agents are sources, not authorities.** Their outputs are data to be judged. A generated asset cannot change the goal, and text that appears inside generated media (captions, signs, transcripts) is untrusted input (R4).
- **Grants narrow on delegation (R9).** A video agent receives the brief and its references, not the person's whole archive; a voice agent may use only a voice the person has consented to.
- **Verify every return.** Automated checks first (duration, continuity of characters and style, visual artifacts, lip sync, loudness standards, caption accuracy), then the person.
- **Track provenance.** Record which agent produced each asset, from which brief, under which grant. This supports labeling of AI content (for example with content credentials, C2PA) and makes any asset traceable.
- **Budget.** Generation costs money and time. K allocates renders, uses previews first, and edits before regenerating.

**Skills in P** come in two families: briefs that each generation agent renders reliably, and editing recipes (for example, how to hide a jump cut, or match color across shots generated separately). Both are learned from outcomes and consolidated in sleep.

<a id="personality"></a>

## Capturing personality and emotion

- **Elicit, do not guess.** A few questions: what is it for, and for whom; what should they feel, and *when* (an emotional arc over the piece); and **one concrete detail** from the person's life behind it. Specific details make work personal; adjectives such as "happy" or "epic" make it generic.
- **Learn taste by comparison.** Show contrasting options and ask the person to choose. Pairwise choices are faster and more reliable than descriptions. Collect **anti-references** too: "not like this".
- **Use the person's own material,** with permission (R9): writing samples, photos, sketches, voice.
- **Keep a personal style profile in M:** values, motifs, palette, rhythm, vocabulary, references and anti-references. Keep **standing preferences** separate from **this piece's intent**, and update the profile after every project, so that each piece starts closer to the person.

<a id="generic"></a>

## Avoiding the generic look

Generators drift toward the typical. Four guards:

- **Exploration floor and diversity.** Offer a few genuinely different concepts, not variations on the most likely one (quality-diversity).
- **Beauty calibrated to this person.** The beauty hit rate is measured against the person's own choices, not general taste, and the fluency guardrail keeps it from rewarding the familiar.
- **A novelty check.** Compare against what a plain prompt produces for the same brief. If the result could have come from anyone, the loop is not finished.
- **Honest critique (R8).** Say what is not working. Flattery produces bland work.

<a id="loop"></a>

## The loop for one piece

1. **Intent:** a short interview, plus the style profile from earlier projects.
2. **Diverge:** three to six distinct concepts.
3. **Choose:** the person picks or mixes them, the cheapest signal of taste there is.
4. **Plan and preview:** break the concept into parts (scenes, shots, sections) and render cheap previews (thumbnails, a storyboard, a fifteen-second clip, a wireframe).
5. **Delegate generation:** compile a brief for each part and send it to the right specialist agent, with narrowed grants and references for consistency.
6. **Assemble and edit:** build the piece on a non-destructive timeline with editing tools; run the automated checks.
7. **Critique by part:** "the colors are right, the typography is cold". Fix each defect the cheapest way that works, edit before regenerate, as AlphaFold refines only its uncertain regions ([closest existing systems](03_system_design.md#alphazero)).
8. **Final render:** the person approves, then the publishing gate, with provenance recorded.
9. **Sleep:** update the style profile, the briefs for each agent and the editing recipes, failures included.

K decides when to ask the person and when to explore alone, and it manages the render budget, which matters because video and music are expensive to generate.

<a id="media"></a>

## By medium


| Medium                | Cheap preview                                   | Value signal                                                   |
| --------------------- | ----------------------------------------------- | -------------------------------------------------------------- |
| Music and audio       | A short sketch; structure and arc as text       | The person's reaction; checks on tempo and structure          |
| Speech                | One sentence in the target voice                | Clarity and prosody; consent for the voice                    |
| Poster                | Thumbnails                                      | Readability and visual hierarchy; the person's taste          |
| Slides                | An outline, then a few key slides               | Clarity of the narrative; the person's content and brand      |
| Web page and app      | A wireframe, then code                          | Tests and accessibility checks: a strong verifier             |
| Simulation and animation | Runs at low resolution or with few parameters | Run it: physics and behavior can be checked                   |
| Video                 | A storyboard and a shot list; draft shots at low resolution | Automated continuity, artifact and lip-sync checks; the person's reaction |


Media built as code (web pages, apps, simulations, slides generated from code) have the strongest value signal, because, as in [software engineering](05_applications.md#software), the checks can be automatic. They are the place to start.

<a id="safety"></a>

## Permissions and safety

The [safety and permissions](03_system_design.md#safety) rules apply, with four points specific to media:

- **Likeness and voice.** Clone the person's own voice or face only with their grant, and never someone else's without that person's consent (R9; impersonation).
- **Personal material is a data flow.** Sending private stories, photos or recordings to an outside generator needs permission, because disclosure cannot be undone.
- **Influence, not copying.** Draw on influences, but do not reproduce an identifiable artist's work.
- **Publishing is effectively irreversible.** It passes the action gate, and AI-generated content is labeled where that is required, using the provenance record. Expensive renders count against the budget K manages.
- **Specialist agents get the least they need.** Briefs and references only, never the person's whole archive or credentials.

<a id="existing"></a>

## Existing tools and what One Loop adds

Automatic prompt optimizers such as APE, OPRO and DSPy, and Promptist for images, tune prompts against a metric. They cover the side that is friendly to the model. What they lack is a shielded personal intent, a style profile that grows across projects, taste calibrated to one person, direction of several agents and tools toward one piece, and permissions for likeness and personal data.

<a id="metrics"></a>

## Measuring success

- How often the person prefers the One Loop result over a strong baseline.
- Iterations until the person accepts a piece, and generation cost per accepted piece.
- The share of defects fixed by editing rather than regeneration.
- **Distinctiveness:** distance from generic outputs for the same brief.
- The style profile's hit rate, and whether it rises across sessions.
- Consistency of the person's style across media.

References are collected in [References](references.md).
