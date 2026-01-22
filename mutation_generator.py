"""Simple instruction mutation generator for robustness experiments."""

from __future__ import annotations

import random
import re
from typing import Callable, Dict, List


MUTATION_CATEGORIES: List[str] = [
    "synonyms",
    "passive_voice",
    "spatial_reordering",
    "formal_informal",
    "verb_phrasing",
    "object_descriptors",
    "directional_language",
    "temporal_modifiers",
    "negation_positive",
    "complexity_variation",
]


def _replace_any(text: str, replacements: Dict[str, List[str]], rng: random.Random) -> str:
    for key, choices in replacements.items():
        if re.search(rf"\b{re.escape(key)}\b", text, flags=re.IGNORECASE):
            replacement = rng.choice(choices)
            return re.sub(rf"\b{re.escape(key)}\b", replacement, text, flags=re.IGNORECASE)
    return text


def _ensure_change(original: str, mutated: str, fallback: Callable[[], str]) -> str:
    if mutated.strip().lower() == original.strip().lower():
        return fallback()
    return mutated


def _synonyms(text: str, rng: random.Random) -> str:
    replacements = {
        "pick": ["grab", "lift", "take"],
        "move": ["shift", "relocate", "transport"],
        "place": ["put", "set", "position"],
        "put": ["place", "set", "position"],
        "stack": ["pile", "layer"],
        "open": ["unseal", "unlock", "pull open"],
        "close": ["shut", "seal", "push closed"],
        "into": ["inside", "in"],
        "on": ["on top of"],
    }
    mutated = text
    changed = False
    for key, choices in replacements.items():
        if re.search(rf"\b{re.escape(key)}\b", mutated, flags=re.IGNORECASE):
            replacement = rng.choice(choices)
            mutated = re.sub(rf"\b{re.escape(key)}\b", replacement, mutated, flags=re.IGNORECASE)
            changed = True
    if not changed:
        mutated = f"Please {text[0].lower() + text[1:]}"
    return _ensure_change(text, mutated, lambda: f"Please {text[0].lower() + text[1:]}")


def _passive_voice(text: str, rng: random.Random) -> str:
    m = re.match(r"^(\\w+)(.*)$", text.strip())
    if not m:
        return f"{text} should be done."
    verb, rest = m.group(1), m.group(2).strip()
    if not rest:
        return f"{text} should be performed."
    return f"{rest} should be {verb.lower()}ed."


def _spatial_reordering(text: str, rng: random.Random) -> str:
    # Try to front-load a spatial phrase like "into X" or "on Y".
    m = re.search(r"\b(into|in|on|inside)\b\s+([^,]+)", text, flags=re.IGNORECASE)
    if m:
        phrase = f"{m.group(1)} {m.group(2).strip()}"
        rest = re.sub(re.escape(m.group(0)), "", text, flags=re.IGNORECASE).strip()
        mutated = f"{phrase.capitalize()}, {rest}"
        return _ensure_change(text, mutated, lambda: text)
    # Fallback to spatial word substitution.
    replacements = {
        "left": ["on the left", "to your left"],
        "right": ["on the right", "to your right"],
        "front": ["in front", "ahead"],
        "behind": ["in the back", "behind you"],
    }
    mutated = _replace_any(text, replacements, rng)
    return _ensure_change(text, mutated, lambda: f"{text} on the left side.")


def _formal_informal(text: str, rng: random.Random) -> str:
    replacements = {
        "get": ["retrieve", "obtain"],
        "grab": ["retrieve", "obtain"],
        "take": ["retrieve", "obtain"],
        "move": ["relocate", "transport"],
        "put": ["place", "deposit"],
        "pick": ["retrieve", "lift"],
    }
    mutated = _replace_any(text, replacements, rng)
    return _ensure_change(
        text,
        mutated,
        lambda: rng.choice(
            [f"Please {text[0].lower() + text[1:]}", f"Hey, {text[0].lower() + text[1:]}"]
        ),
    )


def _verb_phrasing(text: str, rng: random.Random) -> str:
    replacements = {
        "pick up": ["lift up", "raise", "collect"],
        "move": ["move over", "carry", "bring"],
        "place": ["set down", "put down"],
        "put": ["set down", "drop off"],
        "stack": ["pile up", "stack up"],
        "open": ["pull open", "swing open"],
        "close": ["push shut", "swing shut"],
    }
    for key, choices in replacements.items():
        if key in text.lower():
            mutated = re.sub(key, rng.choice(choices), text, flags=re.IGNORECASE)
            return _ensure_change(text, mutated, lambda: text)
    return f"Go ahead and {text[0].lower() + text[1:]}"


def _object_descriptors(text: str, rng: random.Random) -> str:
    replacements = {
        "red": ["crimson", "scarlet"],
        "green": ["emerald", "lime"],
        "blue": ["azure", "navy"],
        "coke": ["soda", "cola"],
        "eggplant": ["purple eggplant", "fresh eggplant"],
        "basket": ["wire basket", "small basket"],
        "carrot": ["orange carrot", "fresh carrot"],
    }
    mutated = _replace_any(text, replacements, rng)
    return _ensure_change(text, mutated, lambda: f"{text} using the item in view.")


def _directional_language(text: str, rng: random.Random) -> str:
    replacements = {
        "toward": ["in the direction of", "closer to"],
        "near": ["close to", "adjacent to"],
        "away": ["farther from", "further from"],
    }
    mutated = _replace_any(text, replacements, rng)
    return _ensure_change(text, mutated, lambda: f"{text} toward the target.")


def _temporal_modifiers(text: str, rng: random.Random) -> str:
    if "now" in text.lower():
        return re.sub(r"\bnow\b", rng.choice(["right away", "immediately"]), text, flags=re.IGNORECASE)
    return f"{text} right away."


def _negation_positive(text: str, rng: random.Random) -> str:
    if "don't" in text.lower() or "do not" in text.lower():
        return text.replace("don't", "avoid").replace("do not", "avoid")
    lead = rng.choice(["Don't forget to", "Please remember to", "Make sure to"])
    return f"{lead} {text[0].lower() + text[1:]}"


def _complexity_variation(text: str, rng: random.Random) -> str:
    if "carefully" in text.lower():
        return re.sub(r"\bcarefully\b", "", text, flags=re.IGNORECASE).strip()
    return f"Carefully {text[0].lower() + text[1:]}"


_MUTATORS: Dict[str, Callable[[str, random.Random], str]] = {
    "synonyms": _synonyms,
    "passive_voice": _passive_voice,
    "spatial_reordering": _spatial_reordering,
    "formal_informal": _formal_informal,
    "verb_phrasing": _verb_phrasing,
    "object_descriptors": _object_descriptors,
    "directional_language": _directional_language,
    "temporal_modifiers": _temporal_modifiers,
    "negation_positive": _negation_positive,
    "complexity_variation": _complexity_variation,
}


def generate_mutation(instruction: str, category: str, seed: int) -> str:
    """Generate a mutated instruction for the given category."""
    rng = random.Random(seed)
    mutator = _MUTATORS.get(category)
    if mutator is None:
        return instruction
    mutated = mutator(instruction, rng).strip()
    return mutated if mutated else instruction

