# Standard Operating Procedure (SOP) — Flujo de Producción UGC AI

Este espacio de trabajo contiene la estructura estándar oficial para la ingesta, análisis, generación y entrega de videos virales UGC adaptados a tu marca y avatar.

---

## 1. Estructura de Carpetas

* `📁 01_KNOWLEDGE_BASE/` — Guías, frameworks de guion y este SOP.
* `📁 02_AVATAR_ASSETS/` — ADN inmutable del avatar, fotos y fondos oficiales.
* `📁 03_INBOX_REFERENCES/` — Ingesta de videos descargados de TikTok / Reels por procesar.
* `📁 04_IN_PRODUCTION/` — Proyectos en curso (Fases 2, 3, 4 y 5).
* `📁 05_PROCESSED_DELIVERABLES/` — Videos finales listos para publicar (4 archivos canónicos).
* `📄 creator_profile.yaml` — Configuración del avatar, voz y paleta de color.
* `📄 PRODUCT_CATALOG.yaml` — Catálogo de productos propios de la marca.

---

## 2. Flujo de Producción en 6 Fases

1. **Fase 1 (Ingesta):** Colocar el video de referencia `.mp4` en `03_INBOX_REFERENCES/<cuenta>/`.
2. **Fase 2 (Extracción):** Ejecutar `ugc-video-beat-extractor` para obtener timestamps, frames clave y transcribir con Whisper.
3. **Fase 3 (Generación de Prompts y Guion):** Ejecutar `ugc-viral-video-generator` para crear `prompts_and_script_PROD_<ID>.md` adaptado a tu avatar y sustituyendo marcas terceras por tu `PRODUCT_CATALOG.yaml`.
4. **Fase 4 (Producción Audiovisual):** Generar los First Frames (Midjourney/Flux) y animar los clips (Veo3/Kling/Grok) en `03_Raw_Clips/`.
5. **Fase 5 (Montaje y Subtitulado):** Concatenar y quemar subtítulos dinámicos oficiales (`capcut_italic_yellow` a 18% de margen) con `auto-captions-service`.
6. **Fase 6 (Entrega):** Exportar a `05_PROCESSED_DELIVERABLES/<ID>/` con los 4 archivos limpios.
