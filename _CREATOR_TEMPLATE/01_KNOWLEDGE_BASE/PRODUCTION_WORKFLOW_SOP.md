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
2. **Fase 2 (Extracción & Diagnóstico):** Ejecutar `ugc-video-beat-extractor` para obtener timestamps, frames clave 1:1, transcribir con Whisper y presentar el Checkpoint de Entorno.
3. **Fase 3 (Generación JSON-First & Guion Literal Verbatim):**
   * **Fidelidad Textual Literal 1:1:** El guión hablado es **100% fiel al video viral de referencia (palabra por palabra)**, conservando la cadencia, ganchos y frases retóricas del creador original (*"sliding off by lunch"*, *"it's not your fault"*, *"tested on 22-year-olds"*).
   * **Cero Marcas en el Video (Desacoplamiento ManyChat):** El video educa de forma genérica (*"hydrating essence"*, *"grip primer"*, *"serum foundation"*). La venta y la recomendación de marca específica se delegan al 100% a ManyChat cuando el usuario comenta la palabra clave.
   * **Única Modificación:** La frase final del CTA para insertar la palabra clave segura de ManyChat (ej. `LIFT`, `GLOW`) evitando términos bloqueados como `age` o `DM`.
   * **Generación JSON y Markdown:** Autogeneración de `production_package_PROD_<ID>.json` y `prompts_and_script_PROD_<ID>.md`.
4. **Fase 4 (Producción Audiovisual):** Generar los First Frames (Midjourney/Flux) y animar los clips (Veo3/Kling/Grok) en `03_Raw_Clips/`.
5. **Fase 5 (Montaje y Subtitulado Dinámico):** Concatenar los clips y quemar subtítulos oficiales (`capcut_italic_yellow` a 18% de margen seguro) con `auto-captions-service`.
6. **Fase 6 (Entrega Canónica):** Exportar a `05_PROCESSED_DELIVERABLES/<ID>/` los 4 archivos limpios (`.mp4`, `.srt`, `Cover.jpg` y `post_copy_title_and_caption.txt`).
