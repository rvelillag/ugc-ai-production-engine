# CLAUDE.md - UGC AI Video Production Engine

This repository is an **Autonomous UGC AI Video Production Engine** designed to transform viral organic reference videos into high-converting, brand-aligned UGC video assets using AI avatars and generative video tools.

---

## Quick Command Reference

```bash
# 1. Analyze video cadence & extract whisper transcript (Fase 1)
python tools/audio_cadence_analyzer.py --video "[PATH_TO_REFERENCE_VIDEO]"

# 2. Run QA Harness Audit (Fase 4 & Continuous QA)
python tools/ugc_harness.py --project "[PROJECT_FOLDER_NAME]" [--deliverable "[DELIVERABLE_ID]"]

# 3. Assemble final video + subtitles (CapCut italic yellow style)
python auto-captions-service/main.py --input-dir "[RAW_CLIPS_DIR]" --output-dir "[OUTPUT_DIR]"
```

---

## 4-Phase Production Pipeline

When executing or assisting in a production run, follow these 4 canonical phases strictly:

### Fase 1: Ingesta Forense & Análisis de Cadencia (ugc-pipeline-orchestrator)
1. Create project folder: `[BRAND]/04_IN_PRODUCTION/PROD_[XXX]_[reference_name]/`
2. Move reference video into `01_Reference/`.
3. Run `python tools/audio_cadence_analyzer.py --video "01_Reference/[video].mp4"`.
4. Output: `script_beats_[video].txt` with timestamped words and Words-Per-Second (WPS) calculation.

### Fase 2: Extracción de Keyframes & Checkpoint 1 Mandatorio (ugc-video-beat-extractor)
1. Extract exact keyframe beats using ffmpeg (`01_beat1_hook.jpg` to `06_beat5_cta.jpg`).
2. **Strict Governance:** Maximum 8 files in `01_Reference/`. Remove any temporary `sample_frame_*.jpg`.
3. **MANDATORY CHECKPOINT 1 (Alineación Creativa y Escenario):**
   Before proceeding to Phase 3 prompt generation, YOU MUST STOP and ask the user to confirm:
   - **A. Escenario / Entorno (Setting & Location):** ¿Replicar 1:1 el escenario de la referencia original (ej. Salón de peluquería, lavacabezas negro, spa) o adaptarlo al espacio de la marca (ej. Baño minimalista moderno, tocador, cocina)?
   - **B. Outfit & Estilismo del Avatar:** Ropa, colores y accesorios acordes a la escena (ej. Delantal de estilista, camiseta morada, pelo recogido).
   - **C. ManyChat Keyword:** Palabra clave segura para la llamada a la acción (ej. HAIR, LIFT, GLOW, ROUTINE).
   - **D. Cover Headline:** Titular gancho de curiosidad de máximo 7 palabras para la portada/miniatura.

### Fase 3: Generación JSON-First & Prompts 1:1 (ugc-viral-video-generator)
1. **Dynamic Stage-to-Chunk Mapping:** The 5 canonical narrative stages (*Hook, Reframe, Mechanism, Payoff, CTA*) are preserved, but the number of chunks N is dynamic (N >= 5).
2. **Cadence Constraint:** Every chunk dialogue must respect WPS <= 2.4 (words <= duration_seconds * 2.4).
3. **Forensic First Frame Prompts:** Inject avatar DNA reference (`creator_profile.json`) into 1:1 replications of reference keyframe composition, lighting, camera angle, micro-expressions, and props.
4. **I2V Motion Choreography:** Every `video_motion_prompt` describes continuous cinematic motion from Frame A (t=0s) to Frame B (t=X s) with natural lipsync and handheld camera.
5. Validate using Pydantic model (`tools/schemas/production_package.py`) and render `prompts_and_script_[ID].md`.

### Fase 4: QA Governance & Ensamblaje Canónico (auto-captions-service + ugc_harness.py)
1. Operator generates raw clips `1.mp4` to `N.mp4` in `03_Raw_Clips/`.
2. Assemble final 1080x1920 video with auto-captions (yellow italic, 18% bottom safe zone).
3. Export exactly 4 canonical files in `05_PROCESSED_DELIVERABLES/[ID]/`:
   - `[ID]_Final_1080x1920.mp4`
   - `[ID]_Subtitles.srt`
   - `[ID]_Cover.jpg`
   - `post_copy_title_and_caption.txt`
4. Run `python tools/ugc_harness.py --project [PROJECT] --deliverable [ID]` to certify 6/6 PASS.

---

## The 6 QA Harness Quality Gates

Before approving any project or deliverable, verify that `tools/ugc_harness.py` passes all 6 gates:
- **GATE_1 (Schema & Anatomy):** JSON validates against Pydantic schema; Cover Headline <= 7 words.
- **GATE_2 (Timing & Cadence):** All chunks have WPS <= 2.4.
- **GATE_3 (Anti-Filter Safety):** Zero banned words ('age', 'DM', medical claims) in video scripts or prompts.
- **GATE_4 (Brand Decoupling):** Video dialogue discusses generic problem/solution; brand conversion is 100% via ManyChat DM automation.
- **GATE_5 (Raw Clips Integrity):** All `1.mp4` to `N.mp4` exist, are 9:16 vertical, valid bitrate and audio streams.
- **GATE_6 (Canonical Deliverables):** Exactly 4 files in `05_PROCESSED_DELIVERABLES/[ID]/`.

---

## Critical Constraints & Prohibitions

1. **NO Skipping Checkpoint 1:** Always confirm Scene/Environment, Outfit, Keyword, and Cover Headline with user before generating prompts.
2. **NO Hardcoded 6-Chunk Limit:** Stages can span multiple clips (e.g. Mechanism in 2 clips of 8-10s).
3. **NO Censored Trigger Words:** Never use 'age' or 'DM' in video scripts. Use approved formulas: 'Comment [KEYWORD] below... Make sure you follow so I can send you the guide!'.
4. **NO Unreferenced File Clutter:** Keep project directories clean according to the canonical folder structure.
5. **NO Raw Unicode Crashes on Windows:** Always ensure UTF-8 output formatting in Python scripts.
