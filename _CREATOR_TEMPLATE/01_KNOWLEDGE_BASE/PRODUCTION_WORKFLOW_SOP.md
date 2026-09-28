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
2. **Fase 2 (Extracción, Ledger & Checkpoint 1):** Ejecutar `ugc-video-beat-extractor` para obtener timestamps, keyframes 1:1 (cantidad variable según cortes/duración, sin tope fijo) y transcripción Whisper; completar `reference_ledger.json` viendo los frames de contacto; presentar el Checkpoint 1 (Escenario, Outfit, Keyword, Cover Headline, Ledger y exageración de hook opt-in) para confirmación del usuario.
3. **Fase 3 (Generación JSON-First & Prompts Estructurados):**
   * **Ledger + Fidelidad Verbatim (≥85%):** Todas las acciones de la referencia se mantienen en el mismo orden que el ledger confirmado (GATE_8); el diálogo de cada fila conserva ≥85% de las palabras literales (GATE_7), con cadencia $\le 2.4$ WPS. Las referencias suelen rondar ~3 WPS: se alcanza el mismo número de palabras con más clips (y más largos, ≤10s cada uno) en vez de recortar diálogo. La exageración del hook es opt-in (`hook_exaggeration` en `checkpoint1.json`), no obligatoria.
   * **Cero Marcas en el Video (Desacoplamiento ManyChat):** El video educa de forma genérica (*"hydrating essence"*, *"grip primer"*, *"serum foundation"*). La venta y recomendación de marca específica se delegan al 100% a ManyChat cuando el usuario comenta la palabra clave. Nunca usar 'age'/'edad' ni 'DM' (GATE_3), ni en el guion ni en los ejemplos de producto.
   * **Estructura Canónica de Video Prompts (UGC Script Writing System v2):** (1) Header de consistencia 9:16 + entorno canónico + descriptor físico sin nombre propio + años aparentes (ej. `47yo`, nunca 'edad') + ropa, (2) Bloques `*ACTION:*` con timeline de sub-segundos, mecánica táctil detallada (dedos, props, textura), sincronización visual con el audio (`Visual-to-Voiceover Sync`) y diálogos entrecomillados, (3) Los 4 Bloques Universales: Skin/Hair After Lock, Application Lock (transparente), B-Roll Sequencing (sin revelación prematura) y Realismo UGC (luz de ventana, gestos de palma abierta, sin manos en bolsillos), y (4) Capa acústica y Foley (`*SFX:*`).
   * **Generación JSON y Markdown:** Rellenar `ledger_rows`, `ref_window`, `voiceover_reference` y `action_timeline` por chunk; compilar los prompts I2V con `python tools/prompt_compiler.py --json ...` y luego `production_package_PROD_<ID>.json` / `prompts_and_script_PROD_<ID>.md`.
4. **Fase 4 (Producción Audiovisual):** Generar los First Frames (Midjourney/Flux) y animar los clips (Veo3/Kling/Grok) en `03_Raw_Clips/` — tantos como chunks tenga el paquete (el número no es fijo, depende del ledger).
5. **Fase 5 (Recorte de Silencios, Montaje y Subtitulado Dinámico):** Recortar silencios muertos con Whisper y unir clips con subtítulos oficiales (`viral_yellow_highlight`: Montserrat Bold mayúsculas, tamaño compacto 4.5%, resaltado uniforme Amarillo Viral, margen inferior seguro 18%) ejecutando `python tools/assemble_project.py --project PROD_<ID>_<nombre>`.
6. **Fase 6 (Entrega Canónica & QA):** Exportar a `05_PROCESSED_DELIVERABLES/<ID>/` los 4 archivos limpios (`.mp4`, `.srt`, `Cover.jpg` y `post_copy_title_and_caption.txt`) y auditar con `python tools/ugc_harness.py --project PROD_<ID>_<nombre>` (todos los gates PASS: 7/7, u 8/8 con ledger).
