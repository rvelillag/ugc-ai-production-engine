import re
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, Tuple

from app.core.ffmpeg_utils import FFmpegLocator

class AudioExtractor:
    """Extracts audio and probes video metadata using FFmpeg and FFprobe."""

    @staticmethod
    def probe_video(video_path: Path) -> Dict[str, Any]:
        """
        Probes video metadata (width, height, fps, duration, has_audio).
        Tries ffprobe first; if ffprobe is absent, uses ffmpeg -i as fallback.
        """
        ffmpeg_bin, ffprobe_bin = FFmpegLocator.get_binaries()

        # Try FFprobe first if available
        if ffprobe_bin != "ffprobe" or shutil_has_binary(ffprobe_bin):
            try:
                cmd = [
                    ffprobe_bin,
                    "-v", "quiet",
                    "-print_format", "json",
                    "-show_format",
                    "-show_streams",
                    str(video_path)
                ]
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                data = json.loads(result.stdout)
                streams = data.get("streams", [])
                format_info = data.get("format", {})

                video_stream = next((s for s in streams if s.get("codec_type") == "video"), None)
                audio_stream = next((s for s in streams if s.get("codec_type") == "audio"), None)

                if video_stream:
                    width = int(video_stream.get("width", 1080))
                    height = int(video_stream.get("height", 1920))
                    r_frame_rate = video_stream.get("r_frame_rate", "30/1")
                    try:
                        num, den = map(int, r_frame_rate.split("/"))
                        fps = num / den if den != 0 else 30.0
                    except Exception:
                        fps = 30.0

                    duration = float(format_info.get("duration", video_stream.get("duration", 0.0)))
                    return {
                        "width": width,
                        "height": height,
                        "fps": fps,
                        "duration": duration,
                        "has_audio": audio_stream is not None,
                        "audio_codec": audio_stream.get("codec_name") if audio_stream else None,
                        "video_codec": video_stream.get("codec_name")
                    }
            except Exception:
                pass  # Fallback to ffmpeg -i

        # Fallback: probe directly using ffmpeg -i
        return AudioExtractor._probe_with_ffmpeg(ffmpeg_bin, video_path)

    @staticmethod
    def _probe_with_ffmpeg(ffmpeg_bin: str, video_path: Path) -> Dict[str, Any]:
        """Probes video by parsing ffmpeg -i stderr output."""
        try:
            cmd = [ffmpeg_bin, "-i", str(video_path)]
            result = subprocess.run(cmd, capture_output=True, text=True)
            output = result.stderr or result.stdout or ""
        except FileNotFoundError:
            raise RuntimeError(
                f"No se encontró FFmpeg en el sistema ('{ffmpeg_bin}'). "
                "Por favor ejecuta: pip install static-ffmpeg"
            )

        # Parse Duration: 00:00:15.30
        duration = 10.0
        dur_match = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.?\d*)", output)
        if dur_match:
            h, m, s = dur_match.groups()
            duration = int(h) * 3600 + int(m) * 60 + float(s)

        # Parse Resolution (e.g. 1080x1920 or 720x1280)
        width, height = 1080, 1920
        res_match = re.search(r"Video:.*,\s*(\d{3,5})x(\d{3,5})", output)
        if res_match:
            width = int(res_match.group(1))
            height = int(res_match.group(2))

        # Parse FPS
        fps = 30.0
        fps_match = re.search(r"(\d+(?:\.\d+)?)\s*fps", output)
        if fps_match:
            try:
                fps = float(fps_match.group(1))
            except Exception:
                fps = 30.0

        has_audio = "Audio:" in output

        return {
            "width": width,
            "height": height,
            "fps": fps,
            "duration": round(duration, 2),
            "has_audio": has_audio,
            "audio_codec": "aac" if has_audio else None,
            "video_codec": "h264"
        }

    @staticmethod
    def extract_audio(video_path: Path, output_wav_path: Path) -> Path:
        """Extracts 16kHz mono WAV audio required for Whisper/ASR."""
        output_wav_path.parent.mkdir(parents=True, exist_ok=True)
        ffmpeg_bin, _ = FFmpegLocator.get_binaries()
        cmd = [
            ffmpeg_bin,
            "-y",
            "-i", str(video_path),
            "-vn",
            "-acodec", "pcm_s16le",
            "-ar", "16000",
            "-ac", "1",
            str(output_wav_path)
        ]
        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True)
        except FileNotFoundError:
            raise RuntimeError(
                f"No se encontró FFmpeg en el sistema ('{ffmpeg_bin}'). "
                "Por favor ejecuta: pip install static-ffmpeg"
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"FFmpeg audio extraction failed: {e.stderr}")
        return output_wav_path

def shutil_has_binary(name: str) -> bool:
    import shutil
    return bool(shutil.which(name))
