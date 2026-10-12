"""Talks to the LLM through LangChain.

The provider and model are chosen in the .env file, so you can switch
between Anthropic, OpenAI, Google... without touching this code.
"""

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage

from app.services.prompts import SYSTEM_PROMPT

# The .env file lives in backend/app/.env (one folder above this file)
load_dotenv(Path(__file__).resolve().parents[1] / ".env")


class LLMServiceError(Exception):
    """Raised when the LLM is not configured correctly."""


@lru_cache(maxsize=1)
def _get_model():
    """Create the model once, then reuse it for every request."""
    provider = os.getenv("LLM_PROVIDER")
    model_name = os.getenv("LLM_MODEL")

    if not provider or not model_name:
        raise LLMServiceError(
            "LLM_PROVIDER and LLM_MODEL must be set in backend/app/.env"
        )

    # The API key is read automatically from the environment
    # (ANTHROPIC_API_KEY, OPENAI_API_KEY, GOOGLE_API_KEY...)
    return init_chat_model(model_name, model_provider=provider, temperature=0.3)


def _extract_text(content) -> str:
    """Some providers return a string, others a list of content blocks."""
    if isinstance(content, str):
        return content
    parts = []
    for block in content:
        if isinstance(block, str):
            parts.append(block)
        elif isinstance(block, dict) and block.get("type") == "text":
            parts.append(block.get("text", ""))
    return "".join(parts)


def get_answer(question: str) -> str:
    """Send the question to the LLM and return its answer as plain text."""
    model = _get_model()
    response = model.invoke(
        [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=question),
        ]
    )
    answer = _extract_text(response.content).strip()
    return answer or "Sorry, I could not generate an answer."