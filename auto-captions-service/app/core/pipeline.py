import time
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Callable

from app.config import settings
from app.core.audio_extractor import AudioExtractor
from app.core.asr_engine import ASREngine
from app.core.cue_segmenter import CueSegmenter
from app.core.emoji_tagger import EmojiTagger
from app.core.ass_generator import ASSGenerator
from app.core.srt_generator import SRTGenerator
from app.core.ffmpeg_burner import FFmpegBurner
from app.services.template_manager import TemplateManager
from app.schemas.template import TemplateConfig

logger = logging.getLogger(__name__)

class CaptionPipeline:
    """Orchestrates the entire end-to-end auto-caption generation workflow."""

    def __init__(self, job_dir: Path):
        self.job_dir = job_dir
        self.job_dir.mkdir(parents=True, exist_ok=True)
        self.audio_extractor = AudioExtractor()
        self.emoji_tagger = EmojiTagger()

    def process_stage_asr(
        self,
        input_video_path: Path,
        language: str = "es",
        asr_engine: Optional[str] = None,
        progress_cb: Optional[Callable[[str, int], None]] = None
    ) -> Dict[str, Any]:
        """
        Stage 1: Probe video, extract audio, and transcribe word-level timestamps.
        """
        if progress_cb:
            progress_cb("Probing video metadata", 10)

        meta = self.audio_extractor.probe_video(input_video_path)
        if not meta["has_audio"]:
            raise ValueError("Input video does not contain an audio stream.")

        if progress_cb:
            progress_cb("Extracting 16kHz audio", 20)

        wav_path = self.job_dir / "audio_16k.wav"
        self.audio_extractor.extract_audio(input_video_path, wav_path)

        if progress_cb:
            progress_cb("Transcribing audio with word timestamps", 40)

        transcript_raw = ASREngine.transcribe(
            wav_path,
            language=language,
            engine=asr_engine
        )

        transcript_data = {
            "language": transcript_raw.get("language", language),
            "words": transcript_raw.get("words", []),
            "video_metadata": meta
        }

        # Save transcript to job directory
        transcript_file = self.job_dir / "transcript.json"
        with open(transcript_file, "w", encoding="utf-8") as f:
            json.dump(transcript_data, f, indent=2, ensure_ascii=False)

        return transcript_data

    def process_stage_render(
        self,
        input_video_path: Path,
        words: list,
        template_name: str = "hype_yellow",
        max_words_per_cue: Optional[int] = None,
        auto_emoji: bool = True,
        position: Optional[str] = None,
        font_family: Optional[str] = None,
        animation: Optional[str] = None,
        highlight_color: Optional[str] = None,
        primary_color: Optional[str] = None,
        outline_color: Optional[str] = None,
        outline_width: Optional[float] = None,
        box_color: Optional[str] = None,
        font_size_pct: Optional[float] = None,
        uppercase: Optional[bool] = None,
        export_srt: bool = True,
        export_ass: bool = True,
        progress_cb: Optional[Callable[[str, int], None]] = None
    ) -> Dict[str, Any]:
        """
        Stage 2: Segment cues, apply emojis, generate .ass / .srt and render final hardsubbed video.
        """
        template_base = TemplateManager.get_template(template_name)
        template_dict = template_base.dict()

        # Apply runtime overrides if specified
        if max_words_per_cue:
            template_dict["max_words_per_cue"] = max_words_per_cue
        if position:
            template_dict["position"] = position
        if font_family:
            template_dict["font_family"] = font_family
        if animation:
            template_dict["animation"] = animation
        if highlight_color:
            template_dict["highlight_color"] = highlight_color
        if primary_color:
            template_dict["primary_color"] = primary_color
        if outline_color:
            template_dict["outline_color"] = outline_color
        if outline_width is not None:
            template_dict["outline_width"] = outline_width
        if box_color is not None:
            template_dict["box_color"] = box_color or None
        if font_size_pct is not None:
            template_dict["font_size_pct_of_height"] = font_size_pct
        if uppercase is not None:
            template_dict["uppercase"] = uppercase

        template = TemplateConfig(**template_dict)

        if progress_cb:
            progress_cb("Segmenting words into cues", 60)

        cues = CueSegmenter.segment_words_into_cues(
            words,
            max_words_per_cue=template.max_words_per_cue,
            pause_threshold_s=0.45,
            uppercase=template.uppercase
        )

        if auto_emoji:
            cues = self.emoji_tagger.tag_cues(cues)

        meta = self.audio_extractor.probe_video(input_video_path)
        v_width = meta.get("width", 1080)
        v_height = meta.get("height", 1920)

        # Generate ASS
        ass_file = self.job_dir / "captions.ass"
        ASSGenerator.generate_ass(
            cues=cues,
            template=template,
            video_width=v_width,
            video_height=v_height,
            output_file=ass_file
        )

        # Generate SRT if requested
        srt_file = None
        if export_srt:
            srt_file = self.job_dir / "captions.srt"
            SRTGenerator.generate_srt(cues=cues, output_file=srt_file)

        if progress_cb:
            progress_cb("Burning animated subtitles with FFmpeg", 80)

        output_video_path = self.job_dir / "output_captioned.mp4"
        FFmpegBurner.burn_subtitles(
            input_video=input_video_path,
            ass_subtitle=ass_file,
            output_video=output_video_path
        )

        if progress_cb:
            progress_cb("Completed", 100)

        return {
            "output_video_path": output_video_path,
            "ass_path": ass_file if export_ass else None,
            "srt_path": srt_file,
            "cues": cues,
            "video_metadata": meta
        }
