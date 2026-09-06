import time
import shutil
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from app.config import settings
from app.schemas.job import CaptionRequest
from app.services.job_queue import JobManager

logger = logging.getLogger(__name__)

class VideoDropHandler(FileSystemEventHandler):
    """Watches for new video files added to the watch/input directory."""

    SUPPORTED_EXTENSIONS = {".mp4", ".mov", ".mkv", ".avi", ".webm"}

    def on_created(self, event):
        if event.is_directory:
            return

        file_path = Path(event.src_path)
        if file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS:
            logger.info(f"New video detected in watch folder: {file_path.name}")
            # Wait for file write to complete
            self._wait_for_file_settled(file_path)
            self._process_video(file_path)

    def _wait_for_file_settled(self, file_path: Path, max_wait: int = 30):
        """Ensures file is fully written before reading."""
        prev_size = -1
        for _ in range(max_wait):
            try:
                current_size = file_path.stat().st_size
                if current_size == prev_size and current_size > 0:
                    time.sleep(1)
                    return
                prev_size = current_size
            except Exception:
                pass
            time.sleep(1)

    def _process_video(self, file_path: Path):
        try:
            # Copy to storage uploads
            upload_target = settings.STORAGE_DIR / "uploads" / f"watch_{file_path.name}"
            shutil.copy2(file_path, upload_target)

            req = CaptionRequest(
                language=settings.DEFAULT_LANGUAGE,
                template=settings.DEFAULT_TEMPLATE,
                max_words_per_cue=settings.DEFAULT_MAX_WORDS_PER_CUE,
                auto_emoji=settings.DEFAULT_AUTO_EMOJI,
                export_srt=True,
                export_ass=True
            )

            import asyncio
            loop = asyncio.get_event_loop() if asyncio.get_event_loop().is_running() else asyncio.new_event_loop()
            
            # Start job
            asyncio.run_coroutine_threadsafe(
                JobManager.create_job(req, local_video_path=upload_target),
                loop
            )
            logger.info(f"Dispatched watch folder job for {file_path.name}")
        except Exception as e:
            logger.error(f"Error processing watch folder video {file_path}: {e}")

class WatchFolderService:
    """Service to manage background watchdog observer."""

    _observer: Observer = None

    @classmethod
    def start(cls):
        if cls._observer is not None:
            return

        settings.WATCH_INPUT_DIR.mkdir(parents=True, exist_ok=True)
        settings.WATCH_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        event_handler = VideoDropHandler()
        cls._observer = Observer()
        cls._observer.schedule(event_handler, str(settings.WATCH_INPUT_DIR), recursive=False)
        cls._observer.start()
        logger.info(f"Watch folder observer active on {settings.WATCH_INPUT_DIR}")

    @classmethod
    def stop(cls):
        if cls._observer:
            cls._observer.stop()
            cls._observer.join()
            cls._observer = None
            logger.info("Watch folder observer stopped.")
