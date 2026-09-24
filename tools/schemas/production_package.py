from typing import List, Optional, Dict, Any, Tuple
from pydantic import BaseModel, Field

class LeftSubjectAudit(BaseModel):
    name: str = Field(..., description="Nombre del avatar o sujeto izquierdo")
    character_id: str = Field(..., description="ID del character (ej: sofia_torres_45yo)")
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

class ActionStep(BaseModel):
    t0: float = Field(..., ge=0, description="Inicio del paso dentro del clip (s)")
    t1: float = Field(..., description="Fin del paso dentro del clip (s)")
    ledger_row: str = Field(..., description="Id de la fila del ledger de referencia que replica")
    action: str = Field(..., min_length=1, description="Acción física exacta (misma que la referencia)")
    props: List[str] = Field(default_factory=list)
    dialogue: str = ""

class ChunkItem(BaseModel):
    chunk_id: int
    beat_name: str
    recommended_duration_s: int = Field(..., ge=1, le=10, description="Duración del clip IA en segundos (máx 10s: límite Veo3/Kling)")
    word_count: int
    voiceover_clean_tts: str
    visual_direction: str
    composition_audit: FrameCompositionAudit
    midjourney_prompt_9_16: str
    video_motion_prompt_i2v: str
    asset_tags: List[str]
    continuity_notes: str
    ledger_rows: List[str] = Field(default_factory=list, description="Ids del ledger que cubre este chunk")
    ref_window: Optional[Tuple[float, float]] = Field(None, description="Ventana [t0, t1] de la referencia que reemplaza")
    action_timeline: List[ActionStep] = Field(default_factory=list)
    voiceover_reference: str = Field("", description="Diálogo original literal del segmento")
    secondary_state: str = Field("", description="Estado de los personajes secundarios en ESTE clip (ej: 'client's hair wet and slicked back'). "
                                                 "Solo puede variar el estado, nunca la identidad definida en secondary_characters.")
    sfx: str = Field("", description="Capa acústica/Foley del clip")

class PostCopy(BaseModel):
    cover_headline: str = Field(..., description="Titular magnético para la portada/thumbnail del video (máximo 6 a 7 palabras)")
    title: str = Field(..., description="Título / Hook de post")
    caption: str = Field(..., description="Cuerpo del post para Reels / TikTok / FB")
    manychat_keyword: str = Field(..., description="Palabra clave disparadora de ManyChat")
    hashtags: List[str] = Field(..., description="Lista de hashtags optimizados")

class SecondaryCharacter(BaseModel):
    role: str = Field(..., description="Rol en escena (ej: client, background stylist)")
    descriptor: str = Field(..., description="Descriptor físico y de vestuario inmutable, SIN nombre propio. Se inyecta en el header de cada prompt I2V "
                                              "para que el personaje sea idéntico en todos los chunks (igual que el avatar).")


class ProductionPackage(BaseModel):
    project_id: str
    reference_video: str
    reference_duration_s: float
    topic: str
    brand: str
    avatar_name: str
    avatar_age: int
    avatar_archetype: str
    avatar_visual_descriptor: str = Field(
        "", description="Descripción física del avatar SIN nombre propio (ej: 'a 47-year-old woman with a "
                        "collarbone-length layered bob...'). Es lo que se inyecta en los prompts de Midjourney/Veo3/"
                        "Kling en vez de avatar_name — nombrar a una persona con nombre y apellido en un prompt "
                        "hiperrealista dispara los filtros de 'personas destacadas/reales' de estos generadores. "
                        "avatar_name se mantiene solo para continuidad/documentación interna (asset_tags, notas).")
    secondary_characters: List[SecondaryCharacter] = Field(
        default_factory=list, description="Personajes secundarios recurrentes (clienta, extras) con descriptor bloqueado para consistencia entre chunks")
    wardrobe_previous: str
    wardrobe_assigned: str
    audio_voice_direction_anchor: str
    standard_skeleton_25_30s: str
    chunks: List[ChunkItem]
    post_copy: PostCopy
