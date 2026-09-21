# CLAUDE.md - UGC AI Video Production Engine

This repository is an **Autonomous UGC AI Video Production Engine** designed to transform viral organic reference videos into high-converting, brand-aligned UGC video assets using AI avatars and generative video tools.

---

## Quick Command Reference

```bash
# 1. Analyze video cadence & extract whisper transcript + scene keyframes (Fase 1 & 2)
python tools/scene_keyframe_extractor.py --video "[PATH_TO_REFERENCE_VIDEO]"

# 1b. Draft the reference ledger (dialogue + contact frames), then fill in actions from the frames (Fase 2)
python tools/reference_ledger.py --project "[PROJECT_FOLDER_NAME]" [--language es|en]

# 1c. Compile I2V prompts from each chunk's action_timeline (Fase 3)
python tools/prompt_compiler.py --json "[PATH_TO_production_package.json]"

# 2. Run QA Harness Audit (Fase 4 & Continuous QA)
python tools/ugc_harness.py --project "[PROJECT_FOLDER_NAME]" [--deliverable "[DELIVERABLE_ID]"]

# 3. Assemble final video + smart silence trimming + subtitles (viral yellow highlight style)
python tools/assemble_project.py --project "[PROJECT_FOLDER_NAME]" [--language es|en|auto]

# 4. (Optional) Standalone cadence analysis
python tools/audio_cadence_analyzer.py --video "[PATH_TO_REFERENCE_VIDEO]"
```

---

## 4-Phase Production Pipeline

When executing or assisting in a production run, follow these 4 canonical phases strictly:

### Fase 1: Ingesta Forense & Análisis de Cadencia (ugc-pipeline-orchestrator)
1. Create project folder: `[BRAND]/04_IN_PRODUCTION/PROD_[XXX]_[reference_name]/` with 5 standard subfolders:
   - `01_Reference/`
   - `02_First_Frames/`
   - `03_Raw_Clips/`
   - `04_Audio/`
   - `05_Montage/`
2. Move reference video into `01_Reference/` and archive inbox file to `_PROCESSED/`.
3. Run faster-whisper transcription with word-level timestamps.
4. Output: `script_beats_[video].txt` with timestamped words, physical action, framing, and WPS calculation (Target <= 2.4 WPS).

### Fase 2: Extracción Granular de Keyframes & Checkpoint 1 Mandatorio (ugc-video-beat-extractor)
1. Detect all genuine visual scene cuts and camera takes from the reference video.
2. Extract exact keyframe beats using naming:
   - `01_beat1_hook.jpg`
   - `02_beat2_reframe.jpg`
   - `03_beat3_1_[action].jpg`, `04_beat3_2_[action].jpg` (Granular sub-beats)
   - `05_beat4_[action].jpg`
   - `06_beat5_cta.jpg`
3. **Strict Governance:** Maximum 8-10 keyframe files in `01_Reference/`.
4. **Ledger de Referencia (fuente de verdad de acciones y diálogo):** Ejecuta `python tools/reference_ledger.py --project [PROJECT]`, mira los frames de contacto y completa en `01_Reference/reference_ledger.json`, fila por fila y en orden: `action`, `framing`, `props`, `gaze`, `gesture` e `is_cta` (el diálogo literal ya viene de Whisper; corrígelo escuchando si hace falta). Una fila por acción física distinta, aunque ocurra dentro de la misma toma.
5. **MANDATORY CHECKPOINT 1 (Alineación Creativa y Escenario):**
   Before proceeding to Phase 3 prompt generation, YOU MUST STOP and ask the user to confirm:
   - **A. Escenario / Entorno (Setting & Location):** ¿Replicar 1:1 el escenario de la referencia original o adaptarlo al espacio de la marca?
   - **B. Outfit & Estilismo del Avatar:** Ropa, colores y accesorios acordes a la escena.
   - **C. ManyChat Keyword:** Palabra clave segura para la llamada a la acción (ej. HAIR, LIFT, GLOW).
   - **D. Cover Headline:** Titular gancho de curiosidad de máximo 7 palabras para la portada/miniatura.
   - **E. Ledger de Referencia:** Muestra la tabla del ledger (acción + diálogo por fila) para que el usuario la confirme.
   - **F. Exageración del hook (opt-in):** Por defecto la acción del hook es idéntica a la referencia; solo se exagera si el usuario lo pide.
6. **Registro del Checkpoint 1:** Solo después de que el usuario confirme A-F, ejecuta `python tools/checkpoint1.py --project [PROJECT] --scene [replicate_1to1|adapt_to_brand] --outfit "..." --keyword [KEYWORD] --headline "..." --confirmed-by-user --ledger-confirmed` (añade `--hook-exaggeration` solo si el usuario lo pidió). GATE_8 exige que el hash del ledger coincida con el confirmado aquí. GATE_1 exige `checkpoint1.json` y que keyword y headline del paquete coincidan con lo confirmado. Nunca lo ejecutes sin confirmación real.

### Fase 3: Generación JSON-First & Prompts Dinámicos (ugc-viral-video-generator)
1. **Escenario y Hook (gobierna `scene_mode` del Checkpoint 1):**
   - `replicate_1to1`: se replica el entorno de la referencia. `adapt_to_brand`: se usa el escenario canónico de la marca. Solo cambian avatar, vestuario y (si se eligió) escenario.
   - **Acciones idénticas:** el hook y todas las acciones de la referencia se mantienen tal cual, en el mismo orden. La hiper-exageración solo aplica si `hook_exaggeration` es `true` en `checkpoint1.json`.
2. **Regla de Fidelidad Verbatim (≥85 %):**
   - El diálogo de cada fila del ledger se conserva ≥85 % palabra por palabra (GATE_7). Solo se permiten ajustes mínimos de voz del avatar y el cambio de marcas/CTA por las fórmulas anti-filtro (las filas `is_cta` están exentas).
   - Cada chunk lleva `ledger_rows`, `ref_window`, `voiceover_reference` y un `action_timeline` (`t0, t1, ledger_row, action, props, dialogue`) contiguo y en el orden del ledger. Toda fila del ledger debe quedar cubierta (GATE_8).
3. **Reglas de Agrupación de Prompts (Límite Veo3 / Kling <= 10s):**
   - **Misma Escena / Encuadre Continuo (Duración <= 10s):** Se agrupan múltiples sub-beats en UN SOLO PROMPT con secuencia de acciones especificada en el timeline:
     `SEQUENCE OF ACTIONS: (0:00-0:03) Action A... (0:03-0:08) Action B...`
   - **Cambio de Escena / Ángulo O Duración > 10s:** Se divide en prompts separados con sus respectivos First Frames.
4. **Cadence Constraint:** Every chunk dialogue must respect WPS <= 2.4. Map the script to the 5 canonical stages (Hook, Reframe, Mechanism, Payoff, CTA) across N clips.
5. **Forensic First Frame Prompts (9:16 vertical):** Replicate composition, lighting, camera angle, micro-expressions, and props identically to the reference (hook elements are exaggerated only if `hook_exaggeration` is true).
6. **Estructura Canónica de Video Motion Prompts (I2V con Timeline Forense y SFX):** Los prompts I2V se **compilan** desde el `action_timeline` con `python tools/prompt_compiler.py --json ...`; no se escriben a mano.
   - **Header de Bloqueo Inmutable:** 9:16 vertical, escenario canónico, identidad/años aparentes (ej. `47yo`, nunca las palabras 'age'/'edad': GATE_3)/ropa y candado de continuidad. Plantilla: `Hyper-realistic vertical 9:16 smartphone UGC video. Use the canonical [ENVIRONMENT]. [AVATAR IDENTITY, APPARENT YEARS (e.g. 47yo), CLOTHING]. Preserve her identity, clothing, lighting, environment, table position, props and camera style throughout the entire clip.`
   - **Bloques `*ACTION:*` con Timestamps de Milisegundo:** Segmentos temporales exactos (`0–3s:`, `3–8s:`, etc.) con plano de cámara, interacción física con props, dirección de mirada y diálogo literal entrecomillado (`says: "..."` / `while continuing: "..."`).
   - **Restricción de Realismo:** `"Natural realistic hand movements. No cuts. No exaggerated acting."`
   - **Capa Acústica y Foley (`*SFX:*`):** Ambiance de la sala, contacto con superficies y sonidos de manipulación de objetos.
7. Validate with Pydantic model (`tools/schemas/production_package.py`) and render `prompts_and_script_[ID].md`.

### Fase 4: QA Governance & Ensamblaje Canónico (auto-captions-service + ugc_harness.py)
1. Operator places generated raw clips `1.mp4` to `N.mp4` in `03_Raw_Clips/`.
2. Assemble final 1080x1920 video with auto-captions (`viral_yellow_highlight`: compact size 4.5%, static uniform, yellow highlight).
3. Generate high-impact centered sticker badge `Cover.jpg`.
4. Export exactly 4 canonical files in `05_PROCESSED_DELIVERABLES/[ID]/`:
   - `[ID]_Final_1080x1920.mp4`
   - `[ID]_Subtitles.srt`
   - `[ID]_Cover.jpg`
   - `post_copy_title_and_caption.txt`
5. Run `python tools/ugc_harness.py --project [PROJECT] --deliverable [ID]` to certify all gates PASS (7/7, or 8/8 with a ledger).

---

## The 7+1 QA Harness Quality Gates

Before approving any project or deliverable, verify that `tools/ugc_harness.py` passes all gates (GATE_8 applies when a reference ledger exists):
- **GATE_1 (Schema & Anatomy):** JSON validates against Pydantic schema; Cover Headline <= 7 words. `checkpoint1.json` exists, is user-confirmed, and matches the package keyword/headline.
- **GATE_2 (Timing & Cadence):** All chunks have WPS <= 2.4 based on allocated durations.
- **GATE_3 (Anti-Filter Safety):** Zero banned words ('age', 'DM', medical claims) in video scripts or prompts.
- **GATE_4 (Brand Decoupling):** Video dialogue discusses generic problem/solution; brand conversion is 100% via ManyChat DM automation.
- **GATE_5 (Raw Clips Integrity):** All `1.mp4` to `N.mp4` exist, are 9:16 vertical, valid bitrate and audio streams.
- **GATE_6 (Canonical Deliverables):** Exactly 4 files in `05_PROCESSED_DELIVERABLES/[ID]/`.
- **GATE_7 (Reference Fidelity):** Con ledger: cada fila (salvo CTA) conserva ≥85 % de las palabras del diálogo literal. Sin ledger (proyectos antiguos): longitud ±10 % y ≥50 % de palabras de contenido. Heurística léxica; el sentido sigue requiriendo revisión humana.
- **GATE_8 (Action Coverage, solo con ledger):** El ledger está confirmado y sin cambios desde el Checkpoint 1; toda fila está cubierta por algún chunk; el `action_timeline` es contiguo, ordenado y ≤ duración del clip; el prompt contiene el marcador de tiempo y el diálogo de cada paso.
---

## Critical Constraints & Prohibitions

1. **NO Skipping Checkpoint 1:** Always confirm Scene/Environment, Outfit, Keyword, Cover Headline, Ledger and hook exaggeration with user before generating prompts.
2. **Ledger + Verbatim Rule:** Mantén todas las acciones de la referencia, en orden, y ≥85 % del diálogo literal (GATE_7/GATE_8). Como las referencias suelen rondar ~3 WPS, alcanza el mismo número de palabras con más/longer clips (<= 10s cada uno) en lugar de recortar palabras.
3. **Dynamic Prompt Grouping (<= 10s rule):** Never exceed 10s per AI video clip; group same-angle actions with explicit timeline markers.
4. **NO Censored Trigger Words:** Never use 'age' or 'DM' in video scripts.
5. **NO Unreferenced File Clutter:** Keep project directories clean according to the canonical folder structure.
6. **NO Raw Unicode Crashes on Windows:** Always ensure UTF-8 output formatting in Python scripts.
