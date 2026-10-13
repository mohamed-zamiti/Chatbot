"""Talks to the LLM through LangChain, with conversation memory.

The provider and model are chosen in the .env file, so you can switch
between Anthropic, OpenAI, Google... without touching this code.

How memory works:
  1. Every conversation has a session_id.
  2. RunnableWithMessageHistory loads the stored messages of that session,
     puts them in the prompt (the "history" slot), calls the model,
     then saves the new question and answer back into the store.
"""

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory

from app.services.prompts import SYSTEM_PROMPT

# The .env file lives in backend/app/.env (one folder above this file)
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

# How many previous messages the bot remembers (10 = 5 questions + 5 answers).
# Higher = better memory, but slower and more expensive.
MAX_HISTORY_MESSAGES = 10

# Safety limit: how many conversations are kept in the server's RAM.
MAX_SESSIONS = 200


class LLMServiceError(Exception):
    """Raised when the LLM is not configured correctly."""


# ---------------------------------------------------------------------------
# Memory store: one InMemoryChatMessageHistory per session_id.
# NOTE: it lives in RAM, so it is erased when the server restarts.
# ---------------------------------------------------------------------------
_store: dict[str, InMemoryChatMessageHistory] = {}


def get_session_history(session_id: str) -> BaseChatMessageHistory:
    """Return the history of a conversation (created if it doesn't exist)."""
    if session_id not in _store:
        if len(_store) >= MAX_SESSIONS:
            # Forget the oldest conversation so memory doesn't grow forever
            _store.pop(next(iter(_store)))
        _store[session_id] = InMemoryChatMessageHistory()

    history = _store[session_id]

    # Keep only the most recent messages
    if len(history.messages) > MAX_HISTORY_MESSAGES:
        history.messages = history.messages[-MAX_HISTORY_MESSAGES:]
    # Some providers (like Gemini) want the conversation to start with the user
    while history.messages and history.messages[0].type != "human":
        history.messages.pop(0)

    return history


def clear_session(session_id: str) -> None:
    """Forget one conversation."""
    _store.pop(session_id, None)


# ---------------------------------------------------------------------------
# Model + chain
# ---------------------------------------------------------------------------
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


@lru_cache(maxsize=1)
def _get_chain():
    """prompt -> model, wrapped so it reads and saves the history automatically."""
    # Careful: {curly braces} in SYSTEM_PROMPT would be treated as variables.
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder("history"),  # <- earlier messages go here
            ("human", "{question}"),
        ]
    )
    return RunnableWithMessageHistory(
        prompt | _get_model(),
        get_session_history,
        input_messages_key="question",
        history_messages_key="history",
    )


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


def get_answer(question: str, session_id: str) -> str:
    """Send the question to the LLM (with this session's memory) and return the answer."""
    response = _get_chain().invoke(
        {"question": question},
        config={"configurable": {"session_id": session_id}},
    )
    answer = _extract_text(response.content).strip()
    return answer or "Sorry, I could not generate an answer."