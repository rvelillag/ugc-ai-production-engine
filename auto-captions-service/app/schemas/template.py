from typing import Optional
from pydantic import BaseModel, Field

class TemplateConfig(BaseModel):
    name: str = Field(..., description="Identificador único del template")
    description: Optional[str] = Field(None, description="Descripción visual del estilo")
    font_family: str = Field("Montserrat Bold", description="Nombre de la fuente tipográfica")
    font_size_pct_of_height: float = Field(7.0, description="Tamaño de fuente como % de la altura del video")
    primary_color: str = Field("#FFFFFF", description="Color principal del texto (Hex, ej: #FFFFFF)")
    highlight_color: str = Field("#FFD400", description="Color de la palabra activa en pronunciación")
    secondary_color: Optional[str] = Field("#E0E0E0", description="Color de palabras secundarias/inactivas")
    outline_color: str = Field("#000000", description="Color del borde o contorno")
    outline_width: float = Field(4.0, description="Grosor del contorno")
    shadow_color: Optional[str] = Field("#80000000", description="Color de la sombra")
    shadow_depth: Optional[float] = Field(2.0, description="Profundidad de la sombra")
    box_color: Optional[str] = Field(None, description="Color de caja de fondo si aplica (ej: #90000000)")
    position: str = Field("bottom_center", description="Alineación: 'bottom_center', 'center', 'top_center'")
    vertical_margin_pct: float = Field(15.0, description="Margen vertical como % de la altura del video")
    animation: str = Field("pop_scale", description="Tipo de animación: 'pop_scale', 'fade', 'karaoke', 'none'")
    pop_scale_from: Optional[float] = Field(115.0, description="Porcentaje de escala inicial para pop (ej: 115%)")
    pop_scale_duration_ms: Optional[int] = Field(120, description="Duración en ms del efecto pop")
    fade_duration_ms: Optional[int] = Field(100, description="Duración en ms del fade-in / fade-out")
    uppercase: bool = Field(True, description="Forzar texto a mayúsculas")
    italic: bool = Field(False, description="Aplicar estilo cursiva/itálica")
    max_words_per_cue: int = Field(3, description="Máximo palabras por bloque de visualización")

