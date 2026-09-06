import os
import sys
import subprocess
from pathlib import Path
from typing import Optional

from app.core.ffmpeg_utils import FFmpegLocator

class FFmpegBurner:
    """Burns subtitles into video files using FFmpeg libass filter."""

    @staticmethod
    def _escape_filter_path(file_path: Path) -> str:
        """
        Escapes paths for FFmpeg complex filter strings across Windows and POSIX.
        Colons and backslashes need special handling in FFmpeg filter syntax.
        """
        # Convert path to absolute POSIX format (forward slashes)
        posix_path = str(file_path.resolve()).replace("\\", "/")
        # In FFmpeg filter syntax on Windows, C:/path must be escaped as C\:/path
        escaped = posix_path.replace(":", "\\:")
        # Escape single quotes and brackets
        escaped = escaped.replace("'", "'\\''").replace("[", "\\[").replace("]", "\\]")
        return escaped

    @classmethod
    def burn_subtitles(
        cls,
        input_video: Path,
        ass_subtitle: Path,
        output_video: Path,
        fonts_dir: Optional[Path] = None,
        preset: str = "fast",
        crf: int = 20
    ) -> Path:
        """
        Burns the .ass subtitle file onto the input video using FFmpeg.
        Preserves video dimensions and original audio track.
        """
        output_video.parent.mkdir(parents=True, exist_ok=True)
        escaped_ass = cls._escape_filter_path(ass_subtitle)
        ffmpeg_bin, _ = FFmpegLocator.get_binaries()

        # Build filter argument
        if fonts_dir and fonts_dir.exists():
            escaped_fonts = cls._escape_filter_path(fonts_dir)
            ass_filter = f"ass='{escaped_ass}':fontsdir='{escaped_fonts}'"
        else:
            ass_filter = f"ass='{escaped_ass}'"

        # Attempt 1: Copy audio stream directly for zero audio re-encoding loss
        cmd_copy_audio = [
            ffmpeg_bin,
            "-y",
            "-i", str(input_video),
            "-vf", ass_filter,
            "-c:v", "libx264",
            "-preset", preset,
            "-crf", str(crf),
            "-c:a", "copy",
            "-movflags", "+faststart",
            str(output_video)
        ]

        try:
            result = subprocess.run(cmd_copy_audio, capture_output=True, text=True, check=True)
            return output_video
        except subprocess.CalledProcessError as e:
            # Fallback: re-encode audio to AAC if copy is not compatible with mp4 container
            cmd_aac = [
                ffmpeg_bin,
                "-y",
                "-i", str(input_video),
                "-vf", ass_filter,
                "-c:v", "libx264",
                "-preset", preset,
                "-crf", str(crf),
                "-c:a", "aac",
                "-b:a", "192k",
                "-movflags", "+faststart",
                str(output_video)
            ]
            try:
                subprocess.run(cmd_aac, capture_output=True, text=True, check=True)
                return output_video
            except subprocess.CalledProcessError as e2:
                raise RuntimeError(
                    f"FFmpeg burning failed: {e2.stderr or e.stderr or 'Unknown error'}"
                )
