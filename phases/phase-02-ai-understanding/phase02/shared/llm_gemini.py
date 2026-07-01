from __future__ import annotations

import json
import logging
import re
from typing import Any

import os

import google.generativeai as genai

from phase02.shared.config import settings
from phase02.shared.llm_provider import LLMProvider

logger = logging.getLogger(__name__)

_JSON_FENCE = re.compile(r"^```(?:json)?\s*|\s*```$", re.MULTILINE)


class GeminiProvider(LLMProvider):
    def __init__(
        self,
        api_key: str | None = None,
        model_name: str | None = None,
    ) -> None:
        key = api_key or os.environ.get("GEMINI_API_KEY") or settings.gemini_api_key
        if not key:
            raise ValueError(
                "GEMINI_API_KEY is not set. Add it to .env locally or Streamlit Cloud secrets."
            )
        self._model_name = model_name or settings.gemini_model
        genai.configure(api_key=key)
        self._text_model = genai.GenerativeModel(self._model_name)
        self._json_model = genai.GenerativeModel(
            self._model_name,
            generation_config={"response_mime_type": "application/json"},
        )

    def generate_text(self, prompt: str, *, system: str | None = None) -> str:
        full_prompt = f"{system}\n\n{prompt}" if system else prompt
        response = self._text_model.generate_content(full_prompt)
        return (response.text or "").strip()

    def generate_json(self, prompt: str, *, system: str | None = None) -> Any:
        full_prompt = f"{system}\n\n{prompt}" if system else prompt
        response = self._json_model.generate_content(full_prompt)
        raw = (response.text or "").strip()
        raw = _JSON_FENCE.sub("", raw).strip()
        return json.loads(raw)


def get_llm_provider() -> LLMProvider:
    return GeminiProvider()
