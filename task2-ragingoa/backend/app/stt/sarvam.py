import os

from sarvamai import SarvamAI

from app.stt.base import SpeechToText

LANGUAGE_CODES = {
    "en": "en-IN",
    "hi": "hi-IN",
    "bn": "bn-IN",
    "ta": "ta-IN",
    "te": "te-IN",
    "mr": "mr-IN",
    "gu": "gu-IN",
    "kn": "kn-IN",
    "ml": "ml-IN",
    "pa": "pa-IN",
    "od": "od-IN",
    "as": "as-IN",
}

class SarvamSTT(SpeechToText):

    MODEL_NAME = "saaras:v4"

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

    def transcribe(
            self,
            audio_path: str,
            language: str | None = None,
    ) -> str:

        if not audio_path:
            raise ValueError("audio_path cannot be empty")

        sarvam_language = LANGUAGE_CODES.get(language)

        if language is not None and sarvam_language is None:
            raise ValueError(f"Unsupported language: {language}")

        with open(audio_path, "rb") as audio_file:
            response = self.client.speech_to_text.transcribe(
                file=audio_file,
                model=self.model_name,
                mode="transcribe",
                language_code=sarvam_language,
                with_timestamps=False,
            )

        transcript = response.transcript

        if not transcript:
            raise RuntimeError(
                "Sarvam STT returned an empty transcript"
            )

        return transcript.strip()