import json
import os
from scripts2kb.utils.llm_client import call_llm
from scripts2kb.utils.state import ArtifactState
from scripts2kb.config.settings import TRANSLATION_SCHEMA


def load_cache(cache_path: str) -> dict:
    if os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_cache(cache: dict, cache_path: str):
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def is_non_english(text: str) -> bool:
    if not text:
        return False
    ascii_count = sum(1 for c in text if ord(c) < 128)
    return (ascii_count / max(len(text), 1)) < 0.8


def translate(state: ArtifactState, config) -> ArtifactState:
    texts_to_translate = []
    if is_non_english(state.element_name):
        texts_to_translate.append(state.element_name)
    for comment in state.comments:
        if is_non_english(comment):
            texts_to_translate.append(comment)

    if not texts_to_translate:
        state.translation = state.element_name
        return state

    cache = load_cache(config.translation_cache_path)
    translations = []

    for text in texts_to_translate:
        if text in cache:
            translations.append(cache[text])
            continue

        prompt = f"""Translate the following text to English.
Return JSON: {{"source": "<original>", "english": "<translation>"}}

Text: {text}"""

        try:
            result = call_llm(prompt, TRANSLATION_SCHEMA, config)
            english = result.get("english", text)
            cache[text] = english
            translations.append(english)
        except Exception:
            translations.append(text)

    save_cache(cache, config.translation_cache_path)
    state.translation = " | ".join(translations)
    state.original_language_text = " | ".join(texts_to_translate)
    return state
