import os
import shutil
import logging
from pathlib import Path
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

class FFmpegLocator:
    """Locates or provides ffmpeg and ffprobe binary paths on Windows, Linux and macOS."""

    _ffmpeg_path: Optional[str] = None
    _ffprobe_path: Optional[str] = None

    @classmethod
    def get_binaries(cls) -> Tuple[str, str]:
        """Returns tuple of (ffmpeg_path, ffprobe_path)."""
        if cls._ffmpeg_path and cls._ffprobe_path and cls._ffprobe_path != "ffprobe":
            return cls._ffmpeg_path, cls._ffprobe_path

        # 1. Check static_ffmpeg package (has both ffmpeg and ffprobe for Windows)
        try:
            import static_ffmpeg
            static_ffmpeg.add_paths()
        except Exception:
            pass

        # 2. Check system PATH
        ffmpeg = shutil.which("ffmpeg")
        ffprobe = shutil.which("ffprobe")

        # 3. Check imageio_ffmpeg if available
        if not ffmpeg:
            try:
                import imageio_ffmpeg
                img_ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
                if img_ffmpeg and os.path.exists(img_ffmpeg):
                    ffmpeg = img_ffmpeg
            except Exception:
                pass

        # 4. Check common Windows installation paths
        if os.name == "nt":
            user_home = Path(os.path.expanduser("~"))
            common_dirs = [
                Path("C:/ffmpeg/bin"),
                Path("C:/tools/ffmpeg/bin"),
                Path("C:/Program Files/ffmpeg/bin"),
                Path("C:/ProgramData/chocolatey/bin"),
                user_home / "AppData/Local/Microsoft/WinGet/Links",
                user_home / "AppData/Local/Microsoft/WinGet/Packages",
                Path(__file__).resolve().parent.parent.parent / "bin"
            ]
            for c_dir in common_dirs:
                if c_dir.exists():
                    if not ffmpeg:
                        # Check direct or recursive
                        cand = c_dir / "ffmpeg.exe"
                        if cand.exists():
                            ffmpeg = str(cand)
                        else:
                            for found in c_dir.rglob("ffmpeg.exe"):
                                ffmpeg = str(found)
                                break
                    if not ffprobe:
                        cand = c_dir / "ffprobe.exe"
                        if cand.exists():
                            ffprobe = str(cand)
                        else:
                            for found in c_dir.rglob("ffprobe.exe"):
                                ffprobe = str(found)
                                break

        cls._ffmpeg_path = ffmpeg or "ffmpeg"
        cls._ffprobe_path = ffprobe or "ffprobe"

        logger.info(f"FFmpeg binary resolved: {cls._ffmpeg_path}")
        logger.info(f"FFprobe binary resolved: {cls._ffprobe_path}")

        return cls._ffmpeg_path, cls._ffprobe_path

    @classmethod
    def is_available(cls) -> bool:
        ffmpeg, _ = cls.get_binaries()
        return bool(shutil.which(ffmpeg) or (ffmpeg and os.path.exists(ffmpeg)))
