from abc import ABC, abstractmethod


class SpeechToText(ABC):

    @abstractmethod
    def transcribe(
        self,
        audio_path: str,
        language: str | None = None,
    ) -> str:
        raise NotImplementedError