import shutil
import logging
from pathlib import Path
from typing import Optional, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks, status
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.schemas.job import (
    CaptionRequest,
    JobQueuedResponse,
    JobStatusResponse,
    TranscriptData,
    ManualRenderRequest,
    JobStatus
)
from app.schemas.template import TemplateConfig
from app.services.template_manager import TemplateManager
from app.services.job_queue import JobManager
from app.services.watch_folder import WatchFolderService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("auto-captions-api")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initializing Auto-Captions Service...")
    settings.setup_directories()
    TemplateManager.load_templates()
    if settings.ENABLE_WATCH_FOLDER:
        WatchFolderService.start()
    yield
    # Shutdown
    logger.info("Shutting down Auto-Captions Service...")
    if settings.ENABLE_WATCH_FOLDER:
        WatchFolderService.stop()

app = FastAPI(
    title="Auto-Captions Animated API",
    description="Microservicio de subtitulado animado automático estilo CapCut / Submagic con ASR por palabra, plantillas ASS y quemado FFmpeg.",
    version="1.0.0",
    lifespan=lifespan,
    swagger_ui_parameters={
        "persistAuthorization": True,
        "docExpansion": "list",
        "defaultModelsExpandDepth": 1,
        "tryItOutEnabled": True,
    },
    swagger_css_url="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/4.15.5/swagger-ui.min.css",
    swagger_js_url="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/4.15.5/swagger-ui.min.js",
    swagger_favicon_url="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/4.15.5/favicon-32x32.png",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = Path(__file__).resolve().parent / "static"
STATIC_INDEX = STATIC_DIR / "index.html"

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/", tags=["UI"])
async def serve_ui():
    """Sirve la interfaz web visual para generación de subtítulos animados."""
    if STATIC_INDEX.exists():
        return FileResponse(STATIC_INDEX, media_type="text/html")
    return {"message": "Auto-Captions Animated Service is running. Visit /docs for OpenAPI specs."}

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "asr_engine": settings.ASR_ENGINE,
        "default_template": settings.DEFAULT_TEMPLATE
    }

@app.post(
    "/caption",
    response_model=JobQueuedResponse,
    status_code=status.HTTP_202_ACCEPTED,
    tags=["Captions"]
)
async def create_caption_job(
    request: Optional[CaptionRequest] = None,
    file: Optional[UploadFile] = File(None),
    language: Optional[str] = Form(None),
    template: Optional[str] = Form(None),
    font_family: Optional[str] = Form(None),
    animation: Optional[str] = Form(None),
    highlight_color: Optional[str] = Form(None),
    primary_color: Optional[str] = Form(None),
    outline_color: Optional[str] = Form(None),
    outline_width: Optional[float] = Form(None),
    box_color: Optional[str] = Form(None),
    font_size_pct: Optional[float] = Form(None),
    uppercase: Optional[bool] = Form(None),
    max_words_per_cue: Optional[int] = Form(None),
    auto_emoji: Optional[bool] = Form(None),
    position: Optional[str] = Form(None),
    pause_before_render: Optional[bool] = Form(None),
    callback_url: Optional[str] = Form(None)
):
    """
    Crea un nuevo trabajo de subtitulado animado.
    Acepta tanto JSON (con `video_url`) como subida de archivo multipart (`file`).
    """
    local_video_path = None

    if file:
        # Save uploaded file
        upload_id = f"upload_{file.filename}"
        upload_path = settings.STORAGE_DIR / "uploads" / upload_id
        with open(upload_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        local_video_path = upload_path

        # Construct request from form values
        req = CaptionRequest(
            language=language or settings.DEFAULT_LANGUAGE,
            template=template or settings.DEFAULT_TEMPLATE,
            font_family=font_family,
            animation=animation,
            highlight_color=highlight_color,
            primary_color=primary_color,
            outline_color=outline_color,
            outline_width=outline_width,
            box_color=box_color,
            font_size_pct=font_size_pct,
            uppercase=uppercase,
            max_words_per_cue=max_words_per_cue or settings.DEFAULT_MAX_WORDS_PER_CUE,
            auto_emoji=auto_emoji if auto_emoji is not None else settings.DEFAULT_AUTO_EMOJI,
            position=position or "bottom_center",
            pause_before_render=pause_before_render or False,
            callback_url=callback_url
        )
    elif request and request.video_url:
        req = request
    else:
        raise HTTPException(
            status_code=400,
            detail="Must provide either a file upload or a 'video_url' in the request."
        )

    job_id = await JobManager.create_job(req, local_video_path=local_video_path)
    return JobQueuedResponse(job_id=job_id, status=JobStatus.QUEUED)

@app.get(
    "/caption/{job_id}",
    response_model=JobStatusResponse,
    tags=["Captions"]
)
async def get_job_status(job_id: str):
    """Consulta el estado del job, progreso, métricas y URLs de descarga."""
    job_data = JobManager.get_job(job_id)
    if not job_data:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")

    return JobStatusResponse(
        job_id=job_data["job_id"],
        status=JobStatus(job_data["status"]),
        progress_percentage=job_data.get("progress_percentage", 0),
        stage=job_data.get("stage"),
        output_video_url=job_data.get("output_video_url"),
        srt_url=job_data.get("srt_url"),
        ass_url=job_data.get("ass_url"),
        transcript_url=job_data.get("transcript_url"),
        duration_seconds=job_data.get("duration_seconds"),
        processing_time_seconds=job_data.get("processing_time_seconds"),
        error_message=job_data.get("error_message"),
        created_at=job_data.get("created_at"),
        completed_at=job_data.get("completed_at"),
        metadata=job_data.get("transcript", {}).get("video_metadata")
    )

@app.get(
    "/caption/{job_id}/transcript",
    tags=["Manual Review"]
)
async def get_job_transcript(job_id: str):
    """Devuelve el transcript editable con timestamps por palabra para corrección manual."""
    job_data = JobManager.get_job(job_id)
    if not job_data:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")

    transcript = job_data.get("transcript")
    if not transcript:
        raise HTTPException(
            status_code=400,
            detail="Transcript is not yet available for this job."
        )

    return transcript

@app.post(
    "/caption/{job_id}/render",
    response_model=JobStatusResponse,
    tags=["Manual Review"]
)
async def trigger_manual_render(job_id: str, request: Optional[ManualRenderRequest] = None):
    """
    Reanuda o ejecuta el renderizado con un transcript modificado manualmente
    o parámetros de plantilla actualizados.
    """
    job_data = JobManager.get_job(job_id)
    if not job_data:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")

    req = request or ManualRenderRequest()
    try:
        updated_job = await JobManager.resume_render_with_custom_transcript(
            job_id=job_id,
            custom_transcript=req.transcript,
            template=req.template,
            max_words_per_cue=req.max_words_per_cue,
            auto_emoji=req.auto_emoji
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return JobStatusResponse(
        job_id=updated_job["job_id"],
        status=JobStatus(updated_job["status"]),
        stage=updated_job.get("stage"),
        progress_percentage=updated_job.get("progress_percentage", 50)
    )

@app.get(
    "/caption/{job_id}/download/{file_type}",
    tags=["Downloads"]
)
async def download_job_file(job_id: str, file_type: str):
    """Descarga los archivos generados: 'video', 'srt', 'ass' o 'json'."""
    job_dir = JobManager.get_job_dir(job_id)
    if not job_dir.exists():
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")

    file_mapping = {
        "video": (job_dir / "output_captioned.mp4", "video/mp4", f"{job_id}_captioned.mp4"),
        "srt": (job_dir / "captions.srt", "text/plain", f"{job_id}.srt"),
        "ass": (job_dir / "captions.ass", "text/plain", f"{job_id}.ass"),
        "json": (job_dir / "transcript.json", "application/json", f"{job_id}_transcript.json")
    }

    if file_type not in file_mapping:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file_type '{file_type}'. Supported: video, srt, ass, json"
        )

    file_path, media_type, filename = file_mapping[file_type]
    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"File '{file_type}' has not been generated for this job."
        )

    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=filename
    )

@app.get(
    "/templates",
    response_model=List[TemplateConfig],
    tags=["Templates"]
)
async def list_templates():
    """Lista todas las plantillas de estilo disponibles."""
    return TemplateManager.list_templates()

@app.post(
    "/templates",
    response_model=TemplateConfig,
    tags=["Templates"]
)
async def create_template(template: TemplateConfig):
    """Registra o actualiza una plantilla de estilo visual."""
    TemplateManager.save_template(template)
    return template
