import os
import time

from dotenv import load_dotenv

from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
from langchain_google_genai import (
    ChatGoogleGenerativeAI
)


load_dotenv()


_provider = os.environ.get(
    "LLM_PROVIDER",
    "ollama"
)

_model = os.environ.get(
    "LLM_MODEL",
    "qwen3:8b"
)


print("\n=== LLM CONFIGURATION ===")
print(f"Provider: {_provider}")
print(f"Model: {_model}")


if _provider == "ollama":

    print("Initializing Ollama model...")

    init_start = time.time()

    _llm = ChatOllama(
        model=_model,
        temperature=0.1
    )

    init_end = time.time()

    print(
        f"Ollama initialized in "
        f"{init_end - init_start:.2f}s"
    )

elif _provider == "groq":

    api_key_exists = bool(
        os.environ.get("GROQ_API_KEY")
    )

    print(
        f"Groq API Key Exists: "
        f"{api_key_exists}"
    )

    if not api_key_exists:

        raise ValueError(
            "GROQ_API_KEY not found."
        )

    print("Initializing Groq model...")

    init_start = time.time()

    _llm = ChatGroq(
        model=_model,
        temperature=0.1,
        api_key=os.environ.get(
            "GROQ_API_KEY"
        )
    )

    init_end = time.time()

    print(
        f"Groq initialized in "
        f"{init_end - init_start:.2f}s"
    )

elif _provider == "gemini":

    api_key_exists = bool(
        os.environ.get("GOOGLE_API_KEY")
    )

    print(
        f"Google API Key Exists: "
        f"{api_key_exists}"
    )

    if not api_key_exists:

        raise ValueError(
            "GOOGLE_API_KEY not found."
        )

    print("Initializing Gemini model...")

    init_start = time.time()

    _llm = ChatGoogleGenerativeAI(
        model=_model,
        temperature=0.1,
        google_api_key=os.environ.get(
            "GOOGLE_API_KEY"
        )
    )

    init_end = time.time()

    print(
        f"Gemini initialized in "
        f"{init_end - init_start:.2f}s"
    )

else:

    raise ValueError(
        f"Unsupported LLM provider: "
        f"{_provider}"
    )


def get_llm():

    print(
        f"\n[LLM REQUEST] "
        f"Provider={_provider} | "
        f"Model={_model}"
    )

    return _llm
