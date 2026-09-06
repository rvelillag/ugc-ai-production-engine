from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class JobStatus(str, Enum):
    QUEUED = "queued"
    PREPROCESSING = "preprocessing"
    TRANSCRIBING = "transcribing"
    WAITING_FOR_REVIEW = "waiting_for_review"
    GENERATING_CAPTIONS = "generating_captions"
    RENDERING = "rendering"
    COMPLETED = "completed"
    FAILED = "failed"

class WordTiming(BaseModel):
    word: str
    start: float
    end: float
    score: Optional[float] = 1.0

class CueSegment(BaseModel):
    words: List[WordTiming]
    start: float
    end: float
    text: str

class TranscriptData(BaseModel):
    language: str
    words: List[WordTiming]
    cues: Optional[List[CueSegment]] = None

class CaptionRequest(BaseModel):
    video_url: Optional[str] = Field(None, description="URL del video a procesar")
    language: Optional[str] = Field("es", description="Idioma del audio ('es', 'en', etc.)")
    template: Optional[str] = Field("hype_yellow", description="Nombre de la plantilla de estilo")
    font_family: Optional[str] = Field(None, description="Sobrescribir fuente: Montserrat Bold, Impact, Bebas Neue, Anton, Roboto, etc.")
    animation: Optional[str] = Field(None, description="Sobrescribir animación: pop_scale, elastic_bounce, karaoke, glow_flash, fade_in")
    highlight_color: Optional[str] = Field(None, description="Color de la palabra activa en Hex (ej: #FFD400)")
    primary_color: Optional[str] = Field(None, description="Color principal del texto en Hex")
    outline_color: Optional[str] = Field(None, description="Color del borde en Hex")
    outline_width: Optional[float] = Field(None, description="Grosor del contorno")
    box_color: Optional[str] = Field(None, description="Color de la caja/pill de fondo en Hex con alfa (ej: #90000000). Vacío = sin caja de fondo")
    font_size_pct: Optional[float] = Field(None, description="Tamaño de fuente como % de la altura del video")
    uppercase: Optional[bool] = Field(None, description="Forzar texto en MAYÚSCULAS")
    max_words_per_cue: Optional[int] = Field(3, ge=1, le=8, description="Máximo número de palabras mostradas simultáneamente")
    highlight_active_word: Optional[bool] = Field(True, description="Resaltar la palabra activa que se está pronunciando")
    auto_emoji: Optional[bool] = Field(True, description="Insertar emojis contextuales automáticamente")
    position: Optional[str] = Field("bottom_center", description="Posición de los subtítulos: 'bottom_center', 'center', 'top_center'")
    export_srt: Optional[bool] = Field(True, description="Generar y poner a disposición archivo .srt")
    export_ass: Optional[bool] = Field(True, description="Generar y poner a disposición archivo .ass")
    pause_before_render: Optional[bool] = Field(False, description="Si es true, pausa el job en waiting_for_review para corrección manual")
    callback_url: Optional[str] = Field(None, description="Webhook URL que recibirá notificación POST al finalizar")

class JobQueuedResponse(BaseModel):
    job_id: str
    status: JobStatus = JobStatus.QUEUED
    message: str = "Job successfully queued"

class JobStatusResponse(BaseModel):
    job_id: str
    status: JobStatus
    progress_percentage: Optional[int] = 0
    stage: Optional[str] = None
    output_video_url: Optional[str] = None
    srt_url: Optional[str] = None
    ass_url: Optional[str] = None
    transcript_url: Optional[str] = None
    duration_seconds: Optional[float] = None
    processing_time_seconds: Optional[float] = None
    error_message: Optional[str] = None
    created_at: Optional[str] = None
    completed_at: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class ManualRenderRequest(BaseModel):
    template: Optional[str] = None
    max_words_per_cue: Optional[int] = None
    auto_emoji: Optional[bool] = None
    transcript: Optional[TranscriptData] = None
