"""Manual mode: the director writes the final prompt for the person's own
generation tool instead of calling specialist agents.

The personal side (intent, concrete detail, avoid list, concept) comes from
the session as usual. Each target profile describes that tool's prompt
conventions, so the prompt is also friendly to the model it is meant for.
Conventions change between tool versions; the profiles are guidance for the
director, and the output notes tell the person what to check.
"""

from __future__ import annotations

from dataclasses import dataclass

from pydantic import BaseModel, Field

from .director import DIRECTOR_SYSTEM, Concept
from .llm import DIRECTOR_MODEL, LLM, image_block
from .working import WorkingState


@dataclass(frozen=True)
class Target:
    name: str
    label: str
    media: tuple[str, ...]
    conventions: str


TARGETS: dict[str, Target] = {t.name: t for t in [
    Target("midjourney", "Midjourney", ("poster",),
           "Short, dense visual description: subject first, then style, light, composition, "
           "palette. Parameters go at the end: aspect ratio (--ar 4:5 for a 1080x1350 poster), "
           "exclusions with --no, and --style raw for less default stylization if the version "
           "supports it. Rendered text is unreliable: keep it to a few words in quotes, or plan "
           "to add text afterwards."),
    Target("chatgpt-image", "ChatGPT / OpenAI image generation", ("poster",),
           "Natural-language paragraphs. Describe the scene, style and layout explicitly, give "
           "exact text to render in quotes with its placement, state the aspect ratio in words, "
           "and list what to avoid as plain sentences."),
    Target("ideogram", "Ideogram", ("poster",),
           "Strong at rendering text: put each piece of exact text in quotes with its role "
           "(title, subtitle, date). Describe typography and layout, then style and palette. "
           "State the aspect ratio. Use the negative prompt field for exclusions if available."),
    Target("stable-diffusion", "Stable Diffusion (and similar open models)", ("poster",),
           "Comma-separated descriptive phrases, most important first; a separate negative "
           "prompt for exclusions and common artifacts. Text rendering is weak: plan to add text "
           "in an editor. Suggest width/height for the aspect ratio."),
    Target("flux", "FLUX", ("poster",),
           "Natural-language description, specific and visual; handles short text in quotes "
           "reasonably well. No negative prompt: phrase exclusions positively (describe what "
           "is there instead)."),
    Target("gamma", "Gamma / AI slide tools", ("slides",),
           "A titled outline: one section per slide with the slide's message, its key text "
           "(short), and a note on the visual for that slide. State the overall theme, palette "
           "and fonts once at the top, and the tone."),
    Target("generic", "Any other tool", ("poster", "slides"),
           "A clear natural-language prompt: subject, style, composition, palette, exact text "
           "in quotes, aspect ratio, and what to avoid as plain sentences."),
]}


class FinalPrompt(BaseModel):
    target: str
    prompt: str = Field(description="The prompt to paste into the tool")
    negative_prompt: str = Field(default="", description="Exclusions, only if the tool has a separate field")
    parameters: str = Field(default="", description="Settings such as aspect ratio, if the tool takes them")
    text_to_add_afterwards: list[str] = Field(
        default_factory=list, description="Exact text the tool may garble, to add in an editor instead")
    variations: list[str] = Field(default_factory=list,
                                  description="Two alternative prompts that push in different directions")
    tips: list[str] = Field(default_factory=list, description="Short notes for the person using the tool")


class Revision(BaseModel):
    what_works: list[str]
    what_misses_the_intent: list[str]
    revised: FinalPrompt


def _ask(target: Target, w: WorkingState, concept: Concept) -> str:
    medium = w.intent.medium if w.intent else "poster"
    return (
        f"Write the final prompt for the person to use in {target.label} to make their {medium}.\n\n"
        f"Concept they chose:\n{concept.model_dump_json(indent=2)}\n\n"
        f"Conventions for this tool:\n{target.conventions}\n\n"
        "The prompt must carry the person's concrete detail and feeling, respect their avoid "
        "list, and include their required text exactly. Avoid generic stock phrases (such as "
        "'stunning', 'masterpiece', '8k') that pull the result toward the typical look. "
        f"Set target to '{target.name}'."
    )


def compile_prompt(llm: LLM, w: WorkingState, concept: Concept, target_name: str) -> FinalPrompt:
    target = TARGETS[target_name]
    return llm.structured(model=DIRECTOR_MODEL, system=DIRECTOR_SYSTEM, content=_ask(target, w, concept),
                          schema=FinalPrompt, purpose=f"prompt:{target.name}", pinned=w.pinned())


def revise_prompt(llm: LLM, w: WorkingState, concept: Concept, previous: FinalPrompt,
                  result_png: bytes, person_note: str = "") -> Revision:
    target = TARGETS[previous.target]
    content = [
        image_block(result_png),
        {"type": "text", "text": (
            f"The person generated this with {target.label} using the prompt below.\n\n"
            f"Prompt used:\n{previous.model_dump_json(indent=2)}\n\n"
            f"Concept:\n{concept.model_dump_json(indent=2)}\n\n"
            + (f"The person says: {person_note}\n\n" if person_note else "")
            + f"Conventions for this tool:\n{target.conventions}\n\n"
            "Judge the image against the person's intent, honestly. Then write a revised "
            "prompt that keeps what works and fixes what misses, changing as little as needed.")},
    ]
    return llm.structured(model=DIRECTOR_MODEL, system=DIRECTOR_SYSTEM, content=content,
                          schema=Revision, purpose=f"revise:{target.name}", pinned=w.pinned())


def to_markdown(p: FinalPrompt) -> str:
    t = TARGETS[p.target]
    out = [f"# Prompt for {t.label}", "", "## Prompt", "", "```", p.prompt, "```"]
    if p.negative_prompt:
        out += ["", "## Negative prompt", "", "```", p.negative_prompt, "```"]
    if p.parameters:
        out += ["", "## Parameters", "", "```", p.parameters, "```"]
    if p.text_to_add_afterwards:
        out += ["", "## Text to add afterwards in an editor", ""] + [f"- {x}" for x in p.text_to_add_afterwards]
    if p.variations:
        out += ["", "## Variations", ""]
        for i, v in enumerate(p.variations, 1):
            out += [f"{i}.", "```", v, "```"]
    if p.tips:
        out += ["", "## Tips", ""] + [f"- {x}" for x in p.tips]
    out += ["", "_This prompt contains personal details you shared. Check it before pasting it "
            "into another service._", ""]
    return "\n".join(out)
