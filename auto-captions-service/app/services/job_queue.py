import os
import time
import json
import uuid
import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import httpx

from app.config import settings
from app.schemas.job import JobStatus, CaptionRequest, TranscriptData
from app.core.pipeline import CaptionPipeline
from app.services.webhook_client import WebhookClient

logger = logging.getLogger(__name__)

class JobManager:
    """Manages execution and persistence of captioning jobs."""

    _jobs: Dict[str, Dict[str, Any]] = {}
    _lock = asyncio.Lock()

    @classmethod
    def generate_job_id(cls) -> str:
        return f"cap_{uuid.uuid4().hex[:8]}"

    @classmethod
    def get_job_dir(cls, job_id: str) -> Path:
        return settings.STORAGE_DIR / "jobs" / job_id

    @classmethod
    def save_job_state(cls, job_id: str, data: Dict[str, Any]):
        job_dir = cls.get_job_dir(job_id)
        job_dir.mkdir(parents=True, exist_ok=True)
        job_file = job_dir / "job.json"
        with open(job_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        cls._jobs[job_id] = data

    @classmethod
    def get_job(cls, job_id: str) -> Optional[Dict[str, Any]]:
        if job_id in cls._jobs:
            return cls._jobs[job_id]
        job_file = cls.get_job_dir(job_id) / "job.json"
        if job_file.exists():
            try:
                with open(job_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                cls._jobs[job_id] = data
                return data
            except Exception as e:
                logger.error(f"Error loading job {job_id}: {e}")
        return None

    @classmethod
    async def create_job(
        cls,
        request: CaptionRequest,
        local_video_path: Optional[Path] = None
    ) -> str:
        job_id = cls.generate_job_id()
        job_dir = cls.get_job_dir(job_id)
        job_dir.mkdir(parents=True, exist_ok=True)

        job_data = {
            "job_id": job_id,
            "status": JobStatus.QUEUED.value,
            "progress_percentage": 0,
            "stage": "Encolado",
            "request": request.dict(),
            "local_video_path": str(local_video_path) if local_video_path else None,
            "created_at": datetime.utcnow().isoformat(),
            "completed_at": None,
            "duration_seconds": None,
            "processing_time_seconds": None,
            "error_message": None,
            "output_files": {}
        }
        cls.save_job_state(job_id, job_data)

        # Launch background task
        asyncio.create_task(cls.run_job(job_id))
        return job_id

    @classmethod
    async def run_job(cls, job_id: str):
        job_data = cls.get_job(job_id)
        if not job_data:
            return

        start_time = time.time()
        job_dir = cls.get_job_dir(job_id)
        req = CaptionRequest(**job_data["request"])

        def update_progress(stage_name: str, pct: int, status: JobStatus = None):
            job_data["stage"] = stage_name
            job_data["progress_percentage"] = pct
            if status:
                job_data["status"] = status.value
            cls.save_job_state(job_id, job_data)

        try:
            update_progress("Iniciando preprocesamiento", 5, JobStatus.PREPROCESSING)

            # Step 1: Resolve Video File (Download if URL provided)
            video_path = None
            if job_data.get("local_video_path"):
                video_path = Path(job_data["local_video_path"])
            elif req.video_url:
                update_progress("Descargando video de URL", 10)
                video_path = job_dir / "input_video.mp4"
                async with httpx.AsyncClient(timeout=60.0) as client:
                    resp = await client.get(req.video_url)
                    resp.raise_for_status()
                    with open(video_path, "wb") as f:
                        f.write(resp.content)
            else:
                raise ValueError("No video provided (neither upload nor video_url).")

            pipeline = CaptionPipeline(job_dir)

            # Step 2: ASR Transcription
            update_progress("Transcribiendo audio y timestamps por palabra", 30, JobStatus.TRANSCRIBING)
            loop = asyncio.get_event_loop()
            
            transcript_data = await loop.run_in_executor(
                None,
                lambda: pipeline.process_stage_asr(
                    input_video_path=video_path,
                    language=req.language,
                    asr_engine=None,
                    progress_cb=update_progress
                )
            )

            job_data["transcript"] = transcript_data
            duration = transcript_data.get("video_metadata", {}).get("duration", 0.0)
            job_data["duration_seconds"] = duration

            # Step 3: Check if manual review paused
            if req.pause_before_render:
                update_progress("Esperando revisión manual de transcript", 50, JobStatus.WAITING_FOR_REVIEW)
                return

            # Step 4: Render Subtitles
            await cls.execute_render(job_id, transcript_data["words"], req, video_path, start_time)

        except Exception as e:
            logger.exception(f"Job {job_id} failed: {e}")
            job_data["status"] = JobStatus.FAILED.value
            job_data["error_message"] = str(e)
            job_data["completed_at"] = datetime.utcnow().isoformat()
            cls.save_job_state(job_id, job_data)

            if req.callback_url:
                await WebhookClient.send_callback(req.callback_url, job_data)

    @classmethod
    async def execute_render(
        cls,
        job_id: str,
        words: list,
        req: CaptionRequest,
        video_path: Path,
        start_time: float
    ):
        job_data = cls.get_job(job_id)
        job_dir = cls.get_job_dir(job_id)
        pipeline = CaptionPipeline(job_dir)
        loop = asyncio.get_event_loop()

        def update_progress(stage_name: str, pct: int, status: JobStatus = None):
            job_data["stage"] = stage_name
            job_data["progress_percentage"] = pct
            if status:
                job_data["status"] = status.value
            cls.save_job_state(job_id, job_data)

        update_progress("Generando subtítulos y renderizando video", 70, JobStatus.RENDERING)

        render_res = await loop.run_in_executor(
            None,
            lambda: pipeline.process_stage_render(
                input_video_path=video_path,
                words=words,
                template_name=req.template or settings.DEFAULT_TEMPLATE,
                max_words_per_cue=req.max_words_per_cue,
                auto_emoji=req.auto_emoji,
                position=req.position,
                font_family=req.font_family,
                animation=req.animation,
                highlight_color=req.highlight_color,
                primary_color=req.primary_color,
                outline_color=req.outline_color,
                outline_width=req.outline_width,
                box_color=req.box_color,
                font_size_pct=req.font_size_pct,
                uppercase=req.uppercase,
                export_srt=req.export_srt,
                export_ass=req.export_ass,
                progress_cb=update_progress
            )
        )

        elapsed = round(time.time() - start_time, 2)
        job_data["processing_time_seconds"] = elapsed
        job_data["status"] = JobStatus.COMPLETED.value
        job_data["stage"] = "Finalizado exitosamente"
        job_data["progress_percentage"] = 100
        job_data["completed_at"] = datetime.utcnow().isoformat()

        base_url = settings.BASE_URL.rstrip("/")
        job_data["output_video_url"] = f"{base_url}/caption/{job_id}/download/video"
        job_data["srt_url"] = f"{base_url}/caption/{job_id}/download/srt" if req.export_srt else None
        job_data["ass_url"] = f"{base_url}/caption/{job_id}/download/ass" if req.export_ass else None
        job_data["transcript_url"] = f"{base_url}/caption/{job_id}/transcript"

        cls.save_job_state(job_id, job_data)

        if req.callback_url:
            await WebhookClient.send_callback(req.callback_url, job_data)

    @classmethod
    async def resume_render_with_custom_transcript(
        cls,
        job_id: str,
        custom_transcript: Optional[TranscriptData] = None,
        template: Optional[str] = None,
        max_words_per_cue: Optional[int] = None,
        auto_emoji: Optional[bool] = None
    ) -> Dict[str, Any]:
        """Resumes rendering for a job that was in WAITING_FOR_REVIEW state."""
        job_data = cls.get_job(job_id)
        if not job_data:
            raise ValueError(f"Job {job_id} not found.")

        req_dict = job_data["request"]
        if template:
            req_dict["template"] = template
        if max_words_per_cue:
            req_dict["max_words_per_cue"] = max_words_per_cue
        if auto_emoji is not None:
            req_dict["auto_emoji"] = auto_emoji

        req = CaptionRequest(**req_dict)
        job_data["request"] = req.dict()

        words = []
        if custom_transcript and custom_transcript.words:
            words = [w.dict() for w in custom_transcript.words]
            job_data["transcript"]["words"] = words
        else:
            words = job_data.get("transcript", {}).get("words", [])

        if not words:
            raise ValueError("No transcript words available to render.")

        job_dir = cls.get_job_dir(job_id)
        video_path = None
        if job_data.get("local_video_path"):
            video_path = Path(job_data["local_video_path"])
        else:
            video_path = job_dir / "input_video.mp4"

        start_time = time.time()
        asyncio.create_task(
            cls.execute_render(job_id, words, req, video_path, start_time)
        )

        job_data["status"] = JobStatus.RENDERING.value
        job_data["stage"] = "Renderizado manual iniciado"
        cls.save_job_state(job_id, job_data)
        return job_data
