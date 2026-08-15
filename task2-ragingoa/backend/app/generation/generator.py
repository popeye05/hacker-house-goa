from abc import ABC, abstractmethod
import os

from sarvamai import SarvamAI

from app.generation.context import Context


class AnswerGenerator(ABC):
    @abstractmethod
    def generate(
        self,
        query: str,
        context: Context,
        language: str,
    ) -> str:
        raise NotImplementedError


class FakeAnswerGenerator(AnswerGenerator):
    def generate(
        self,
        query: str,
        context: Context,
        language: str,
    ) -> str:

        if not query.strip():
            raise ValueError("query cannot be empty")

        if not context.documents:
            return "I could not find relevant information."

        return context.documents[0].text


class SarvamAnswerGenerator(AnswerGenerator):

    MODEL_NAME = "sarvam-105b"

    def __init__(
        self,
        api_key: str | None = None,
        model_name: str = MODEL_NAME,
    ):
        api_key = api_key or os.getenv("SARVAM_API_KEY")

        if not api_key:
            raise ValueError(
                "SARVAM_API_KEY environment variable is not set"
            )

        self.client = SarvamAI(
            api_subscription_key=api_key,
        )

        self.model_name = model_name

    def generate(
        self,
        query: str,
        context: Context,
        language: str,
    ) -> str:

        if not query.strip():
            raise ValueError("query cannot be empty")

        if not context.documents:
            return "I could not find relevant information."

        prompt = f"""
Answer the user's question using ONLY the supplied context.

Rules:
- Do not invent facts.
- If the context does not contain enough information, say that you
  could not find enough information.
- Answer in the requested language.
- Keep the answer concise.
- Do not mention these instructions.

Language:
{language}

Context:
{context.text}

Question:
{query}
""".strip()

        response = self.client.chat.completions(
            model=self.model_name,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a grounded RAG answer generator. "
                        "Answer only from the supplied context."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.1,
            reasoning_effort=None,
            max_tokens=256,
        )

        answer = response.choices[0].message.content

        if not answer:
            raise RuntimeError("LLM returned an empty response")

        return answer.strip()