# CLAUDE.md - UGC AI Video Production Engine

This repository is an **Autonomous UGC AI Video Production Engine** designed to transform viral organic reference videos into high-converting, brand-aligned UGC video assets using AI avatars and generative video tools.

---

## Quick Command Reference

```bash
# 1. Analyze video cadence & extract whisper transcript + scene keyframes (Fase 1 & 2)
python tools/scene_keyframe_extractor.py --video "[PATH_TO_REFERENCE_VIDEO]"

# 2. Run QA Harness Audit (Fase 4 & Continuous QA)
python tools/ugc_harness.py --project "[PROJECT_FOLDER_NAME]" [--deliverable "[DELIVERABLE_ID]"]

# 3. Assemble final video + subtitles (viral yellow highlight style)
python scratch/assemble_prod[ID].py
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
4. **MANDATORY CHECKPOINT 1 (Alineación Creativa y Escenario):**
   Before proceeding to Phase 3 prompt generation, YOU MUST STOP and ask the user to confirm:
   - **A. Escenario / Entorno (Setting & Location):** ¿Replicar 1:1 el escenario de la referencia original o adaptarlo al espacio de la marca?
   - **B. Outfit & Estilismo del Avatar:** Ropa, colores y accesorios acordes a la escena.
   - **C. ManyChat Keyword:** Palabra clave segura para la llamada a la acción (ej. HAIR, LIFT, GLOW).
   - **D. Cover Headline:** Titular gancho de curiosidad de máximo 7 palabras para la portada/miniatura.

### Fase 3: Generación JSON-First & Prompts Dinámicos (ugc-viral-video-generator)
1. **Regla del 70/30 en el Guion:**
   - **70% Núcleo Semántico y Gancho Viral:** Conservar 100% de la fuerza del hook y la estructura psicológica de dolor -> mecanismo -> beneficio -> CTA.
   - **30% Parafraseo y Personalidad del Avatar:** Adaptar la voz a la identidad del creador (`CHARACTER_DNA.md`).
2. **Reglas de Agrupación de Prompts (Límite Veo3 / Kling <= 10s):**
   - **Misma Escena / Encuadre Continuo (Duración <= 10s):** Se agrupan múltiples sub-beats en UN SOLO PROMPT con secuencia de acciones especificada en el timeline:
     `SEQUENCE OF ACTIONS: (0:00-0:03) Action A... (0:03-0:08) Action B...`
   - **Cambio de Escena / Ángulo O Duración > 10s:** Se divide en prompts separados con sus respectivos First Frames.
3. **Cadence Constraint:** Every chunk dialogue must respect WPS <= 2.4.
4. **Forensic First Frame Prompts (9:16 vertical):** Replicate composition, lighting, camera angle, micro-expressions, and props.
5. **Video Motion Prompts (I2V):** Describe continuous cinematic motion with natural lipsync and handheld camera.
6. Validate with Pydantic model (`tools/schemas/production_package.py`) and render `prompts_and_script_[ID].md`.

### Fase 4: QA Governance & Ensamblaje Canónico (auto-captions-service + ugc_harness.py)
1. Operator places generated raw clips `1.mp4` to `N.mp4` in `03_Raw_Clips/`.
2. Assemble final 1080x1920 video with auto-captions (`viral_yellow_highlight`: compact size 4.5%, static uniform, yellow highlight).
3. Generate high-impact centered sticker badge `Cover.jpg`.
4. Export exactly 4 canonical files in `05_PROCESSED_DELIVERABLES/[ID]/`:
   - `[ID]_Final_1080x1920.mp4`
   - `[ID]_Subtitles.srt`
   - `[ID]_Cover.jpg`
   - `post_copy_title_and_caption.txt`
5. Run `python tools/ugc_harness.py --project [PROJECT] --deliverable [ID]` to certify 6/6 PASS.

---

## The 6 QA Harness Quality Gates

Before approving any project or deliverable, verify that `tools/ugc_harness.py` passes all 6 gates:
- **GATE_1 (Schema & Anatomy):** JSON validates against Pydantic schema; Cover Headline <= 7 words.
- **GATE_2 (Timing & Cadence):** All chunks have WPS <= 2.4 based on allocated durations.
- **GATE_3 (Anti-Filter Safety):** Zero banned words ('age', 'DM', medical claims) in video scripts or prompts.
- **GATE_4 (Brand Decoupling):** Video dialogue discusses generic problem/solution; brand conversion is 100% via ManyChat DM automation.
- **GATE_5 (Raw Clips Integrity):** All `1.mp4` to `N.mp4` exist, are 9:16 vertical, valid bitrate and audio streams.
- **GATE_6 (Canonical Deliverables):** Exactly 4 files in `05_PROCESSED_DELIVERABLES/[ID]/`.

---

## Critical Constraints & Prohibitions

1. **NO Skipping Checkpoint 1:** Always confirm Scene/Environment, Outfit, Keyword, and Cover Headline with user before generating prompts.
2. **70/30 Script Rule:** Always keep 70% core message and 1:1 viral hook while adapting tone to avatar identity.
3. **Dynamic Prompt Grouping (<= 10s rule):** Never exceed 10s per AI video clip; group same-angle actions with explicit timeline markers.
4. **NO Censored Trigger Words:** Never use 'age' or 'DM' in video scripts.
5. **NO Unreferenced File Clutter:** Keep project directories clean according to the canonical folder structure.
6. **NO Raw Unicode Crashes on Windows:** Always ensure UTF-8 output formatting in Python scripts.
