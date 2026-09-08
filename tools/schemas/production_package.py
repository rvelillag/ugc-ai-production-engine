from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class LeftSubjectAudit(BaseModel):
    name: str = Field(..., description="Nombre del avatar o sujeto izquierdo")
    character_id: str = Field(..., description="ID del character (ej: rachel_bennett_47yo)")
    orientation: str = Field(..., description="Orientación exacta del torso y rostro (ej: 3/4 profile facing right)")
    pose: str = Field(..., description="Pose de brazos y cuerpo exacta (ej: Right arm raised holding soft cosmetic puff near right subject's forehead)")
    hands_interaction: str = Field(..., description="Acción física de las manos")
    gaze_direction: str = Field(..., description="Dirección de la mirada (ej: Looking at camera / looking at right subject)")
    outfit: str = Field(..., description="Descripción del vestuario actual asignado")

class RightSubjectAudit(BaseModel):
    role: str = Field(..., description="Rol del sujeto derecho (ej: Friend / Model 52yo)")
    orientation: str = Field(..., description="Orientación (ej: Facing camera slightly turned left)")
    pose: str = Field(..., description="Pose de cuerpo y brazos (ej: Holding grey plastic caddy basket with both hands against chest)")
    hands_interaction: str = Field(..., description="Qué sostienen las manos")
    facial_expression: str = Field(..., description="Expresión facial exacta (ej: Worried, bewildered side glance)")
    skin_condition_exaggerated: str = Field(..., description="Condición visual de la piel / síntoma exagerado")

class FrameCompositionAudit(BaseModel):
    camera_shot_type: str = Field(..., description="Tipo de plano (ej: Vertical 9:16 medium close-up, eye level, 28mm lens)")
    foreground_props: str = Field(..., description="Utilería y objetos en primer plano inferior (ej: Dark marble counter with black sink basin and faucet)")
    left_subject: LeftSubjectAudit
    right_subject: Optional[RightSubjectAudit] = None
    environment_background: str = Field(..., description="Fondo y escenario (ej: Cozy domestic kitchen with soft morning window daylight)")
    lighting_style: str = Field(..., description="Estilo de iluminación y textura (ej: Soft natural morning daylight, realistic skin pores, zero text)")

class ChunkItem(BaseModel):
    chunk_id: int
    beat_name: str
    recommended_duration_s: int
    word_count: int
    voiceover_clean_tts: str
    visual_direction: str
    composition_audit: FrameCompositionAudit
    midjourney_prompt_9_16: str
    video_motion_prompt_i2v: str
    asset_tags: List[str]
    continuity_notes: str

class PostCopy(BaseModel):
    cover_headline: str = Field(..., description="Titular magnético para la portada/thumbnail del video (máximo 6 a 7 palabras)")
    title: str = Field(..., description="Título / Hook de post")
    caption: str = Field(..., description="Cuerpo del post para Reels / TikTok / FB")
    manychat_keyword: str = Field(..., description="Palabra clave disparadora de ManyChat")
    hashtags: List[str] = Field(..., description="Lista de hashtags optimizados")

class ProductionPackage(BaseModel):
    project_id: str
    reference_video: str
    reference_duration_s: float
    topic: str
    brand: str
    avatar_name: str
    avatar_age: int
    avatar_archetype: str
    wardrobe_previous: str
    wardrobe_assigned: str
    audio_voice_direction_anchor: str
    standard_skeleton_25_30s: str
    chunks: List[ChunkItem]
    post_copy: PostCopy
