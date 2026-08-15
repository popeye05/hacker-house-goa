from abc import ABC, abstractmethod

from app.generation.context import Context


class AnswerGenerator(ABC):
    """
    Interface for models that generate an answer
    from a user query and retrieved context.
    """

    @abstractmethod
    def generate(
        self,
        query: str,
        context: Context,
        language: str,
    ) -> str:
        """
        Generate an answer grounded in the supplied context.
        """
        raise NotImplementedError


class FakeAnswerGenerator(AnswerGenerator):
    """
    Deterministic generator used for testing.
    """

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