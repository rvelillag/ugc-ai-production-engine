"""
Script para generar videos de muestra sintéticos en formato vertical (1080x1920, 9:16)
y probar el quemado de subtítulos en las plantillas hype_yellow, clean_white y karaoke_highlight.
"""

import os
import subprocess
from pathlib import Path
from app.config import settings
from app.core.ass_generator import ASSGenerator
from app.core.cue_segmenter import CueSegmenter
from app.core.emoji_tagger import EmojiTagger
from app.core.ffmpeg_burner import FFmpegBurner
from app.services.template_manager import TemplateManager

def generate_blank_video_with_audio(output_video: Path, duration_sec: int = 5):
    """Generates a 9:16 (1080x1920) 30fps MP4 video with a test audio tone."""
    output_video.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg",
        "-y",
        "-f", "lavfi",
        "-i", f"color=c=0x111827:s=1080x1920:r=30:d={duration_sec}",
        "-f", "lavfi",
        "-i", f"sine=f=440:d={duration_sec}",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-c:a", "aac",
        "-shortest",
        str(output_video)
    ]
    subprocess.run(cmd, capture_output=True, text=True, check=True)
    print(f"Generated base synthetic video at {output_video}")

def main():
    samples_dir = settings.STORAGE_DIR / "sample_renders"
    samples_dir.mkdir(parents=True, exist_ok=True)

    base_video = samples_dir / "base_vertical.mp4"
    generate_blank_video_with_audio(base_video, duration_sec=5)

    sample_words = [
        {"word": "Este", "start": 0.20, "end": 0.50, "score": 0.99},
        {"word": "es", "start": 0.55, "end": 0.75, "score": 0.98},
        {"word": "el", "start": 0.80, "end": 0.95, "score": 0.99},
        {"word": "secreto", "start": 1.00, "end": 1.50, "score": 0.99},
        {"word": "para", "start": 1.70, "end": 1.90, "score": 0.97},
        {"word": "ganar", "start": 1.95, "end": 2.30, "score": 0.99},
        {"word": "dinero", "start": 2.35, "end": 2.80, "score": 0.99},
        {"word": "con", "start": 3.00, "end": 3.20, "score": 0.98},
        {"word": "videos", "start": 3.25, "end": 3.60, "score": 0.99},
        {"word": "virales", "start": 3.65, "end": 4.30, "score": 0.99}
    ]

    tagger = EmojiTagger()
    templates = ["hype_yellow", "clean_white", "karaoke_highlight"]

    for t_name in templates:
        print(f"\n--- Generando muestra para plantilla: {t_name} ---")
        tmpl = TemplateManager.get_template(t_name)
        cues = CueSegmenter.segment_words_into_cues(
            sample_words,
            max_words_per_cue=tmpl.max_words_per_cue,
            uppercase=tmpl.uppercase
        )
        cues = tagger.tag_cues(cues)

        ass_file = samples_dir / f"{t_name}.ass"
        ASSGenerator.generate_ass(
            cues=cues,
            template=tmpl,
            video_width=1080,
            video_height=1920,
            output_file=ass_file
        )
        print(f"Generated ASS file: {ass_file}")

        out_video = samples_dir / f"rendered_{t_name}.mp4"
        try:
            FFmpegBurner.burn_subtitles(
                input_video=base_video,
                ass_subtitle=ass_file,
                output_video=out_video
            )
            print(f"SUCCESS: Rendered video saved to {out_video}")
        except Exception as e:
            print(f"Render note: {e}")

if __name__ == "__main__":
    main()
