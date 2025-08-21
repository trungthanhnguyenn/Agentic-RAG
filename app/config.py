# app/config.py

import os
from typing import Optional

from dotenv import load_dotenv

# LangChain integrations
try:
    # Newer integration packages
    from langchain_openai import ChatOpenAI
except Exception:  # pragma: no cover - fallback if not installed
    ChatOpenAI = None  # type: ignore

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except Exception:  # pragma: no cover - fallback if not installed
    ChatGoogleGenerativeAI = None  # type: ignore


load_dotenv()


def get_env(name: str, default: Optional[str] = None) -> Optional[str]:
    """Helper to fetch environment variables via os.getenv."""
    return os.getenv(name, default)


def get_openai_llm() -> "ChatOpenAI":
    """
    Return a ChatOpenAI LLM configured to use an OpenAI-compatible router
    via OPENAI_BASE_URL, MODEL_NAME, and OPENAI_API_KEY from the environment.
    """
    if ChatOpenAI is None:
        raise RuntimeError(
            "langchain-openai is not installed. Please add 'langchain-openai' to requirements.txt."
        )

    api_key = get_env("OPENAI_API_KEY")
    base_url = get_env("OPENAI_BASE_URL")
    model = get_env("MODEL_NAME")

    if not api_key or not base_url or not model:
        raise RuntimeError(
            "Missing OPENAI_API_KEY, OPENAI_BASE_URL, or MODEL_NAME in environment variables"
        )

    return ChatOpenAI(
        api_key=api_key,
        base_url=base_url,
        model=model,
        temperature=0.2,
    )


def get_gemini_llm(model: str = "gemini-1.5-pro") -> "ChatGoogleGenerativeAI":
    """
    Return a Gemini chat model for the Supervisor using GOOGLE_API_KEY.
    """
    if ChatGoogleGenerativeAI is None:
        raise RuntimeError(
            "langchain-google-genai is not installed. Please add 'langchain-google-genai' and 'google-generativeai' to requirements.txt."
        )

    google_api_key = get_env("GOOGLE_API_KEY")
    if not google_api_key:
        raise RuntimeError("Missing GOOGLE_API_KEY in environment variables")

    return ChatGoogleGenerativeAI(
        api_key=google_api_key,
        model=model,
        temperature=0.2,
    )
