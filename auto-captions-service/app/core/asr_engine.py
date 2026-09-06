import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from app.config import settings

logger = logging.getLogger(__name__)

class ASREngine:
    """ASR transcription engine supporting faster-whisper (local) and OpenAI Whisper API (fallback)."""

    _faster_whisper_model = None

    @classmethod
    def get_faster_whisper_model(cls):
        """Lazy load and singleton cache for faster-whisper model."""
        if cls._faster_whisper_model is None:
            from faster_whisper import WhisperModel
            device = settings.WHISPER_DEVICE
            if device == "auto":
                try:
                    import torch
                    device = "cuda" if torch.cuda.is_available() else "cpu"
                except Exception:
                    device = "cpu"

            compute_type = settings.WHISPER_COMPUTE_TYPE
            if compute_type == "default":
                compute_type = "float16" if device == "cuda" else "int8"

            logger.info(f"Loading faster-whisper model '{settings.WHISPER_MODEL_SIZE}' on {device} ({compute_type})...")
            cls._faster_whisper_model = WhisperModel(
                settings.WHISPER_MODEL_SIZE,
                device=device,
                compute_type=compute_type
            )
        return cls._faster_whisper_model

    @classmethod
    def transcribe(
        cls,
        audio_path: Path,
        language: Optional[str] = "es",
        engine: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transcribes the audio file and extracts word-level timestamps.
        Returns:
            {
                "language": str,
                "words": [{"word": str, "start": float, "end": float, "score": float}, ...]
            }
        """
        engine_type = engine or settings.ASR_ENGINE

        if engine_type == "openai" or (not engine_type and settings.OPENAI_API_KEY):
            return cls._transcribe_openai(audio_path, language)
        else:
            return cls._transcribe_faster_whisper(audio_path, language)

    @classmethod
    def _transcribe_faster_whisper(cls, audio_path: Path, language: Optional[str]) -> Dict[str, Any]:
        model = cls.get_faster_whisper_model()
        segments, info = model.transcribe(
            str(audio_path),
            language=language if language != "auto" else None,
            word_timestamps=True,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=400)
        )

        detected_language = info.language if hasattr(info, "language") else (language or "es")
        words_list: List[Dict[str, Any]] = []

        for segment in segments:
            if hasattr(segment, "words") and segment.words:
                for w in segment.words:
                    word_text = w.word.strip()
                    if word_text:
                        words_list.append({
                            "word": word_text,
                            "start": round(w.start, 3),
                            "end": round(w.end, 3),
                            "score": round(w.probability, 3) if hasattr(w, "probability") else 1.0
                        })
            else:
                # Fallback if segment has no word breakdown: split evenly
                seg_text = segment.text.strip()
                tokens = seg_text.split()
                if tokens:
                    dur_per_word = (segment.end - segment.start) / len(tokens)
                    for i, tok in enumerate(tokens):
                        w_start = segment.start + (i * dur_per_word)
                        w_end = w_start + dur_per_word
                        words_list.append({
                            "word": tok,
                            "start": round(w_start, 3),
                            "end": round(w_end, 3),
                            "score": 0.95
                        })

        return {
            "language": detected_language,
            "words": words_list
        }

    @classmethod
    def _transcribe_openai(cls, audio_path: Path, language: Optional[str]) -> Dict[str, Any]:
        from openai import OpenAI
        api_key = settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY must be provided for OpenAI ASR engine.")

        client = OpenAI(api_key=api_key)
        with open(audio_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=language if language != "auto" else None,
                response_format="verbose_json",
                timestamp_granularities=["word"]
            )

        words_list: List[Dict[str, Any]] = []
        if hasattr(transcript, "words") and transcript.words:
            for w in transcript.words:
                word_text = w.word.strip()
                if word_text:
                    words_list.append({
                        "word": word_text,
                        "start": round(w.start, 3),
                        "end": round(w.end, 3),
                        "score": 1.0
                    })
        elif isinstance(transcript, dict) and "words" in transcript:
            for w in transcript["words"]:
                word_text = w.get("word", "").strip()
                if word_text:
                    words_list.append({
                        "word": word_text,
                        "start": round(w.get("start", 0.0), 3),
                        "end": round(w.get("end", 0.0), 3),
                        "score": 1.0
                    })

        return {
            "language": getattr(transcript, "language", language or "es"),
            "words": words_list
        }
