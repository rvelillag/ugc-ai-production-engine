from pathlib import Path
from typing import List, Dict, Any, Optional

class SRTGenerator:
    """Generates standard SubRip (.srt) subtitle files."""

    @staticmethod
    def format_timestamp(seconds: float) -> str:
        """Converts float seconds to SRT timestamp format: HH:MM:SS,mmm"""
        if seconds < 0:
            seconds = 0.0
        hrs = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        secs = seconds % 60
        millis = int(round((secs - int(secs)) * 1000))
        if millis >= 1000:
            millis = 999
        return f"{hrs:02d}:{mins:02d}:{int(secs):02d},{millis:03d}"

    @classmethod
    def generate_srt(
        cls,
        cues: List[Dict[str, Any]],
        output_file: Optional[Path] = None
    ) -> str:
        """Generates standard SRT subtitles from cues."""
        blocks = []
        for i, cue in enumerate(cues, start=1):
            start_str = cls.format_timestamp(cue["start"])
            end_str = cls.format_timestamp(cue["end"])
            text = cue.get("text", " ".join([w["word"] for w in cue.get("words", [])]))
            blocks.append(f"{i}\n{start_str} --> {end_str}\n{text}\n")

        srt_content = "\n".join(blocks)
        if output_file:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(srt_content, encoding="utf-8")

        return srt_content
