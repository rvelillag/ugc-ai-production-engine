# CLAUDE.md - UGC AI Video Production Engine

This repository is an **Autonomous UGC AI Video Production Engine** designed to transform viral organic reference videos into high-converting, brand-aligned UGC video assets using AI avatars and generative video tools.

---

## Setup Check (run once per session)

Before doing any pipeline work in this repo, check whether `.setup_complete` exists at the repo root.

- **If it exists:** setup has already run — proceed normally.
- **If it's missing:** this looks like a fresh clone. Tell the user setup hasn't been run yet, and offer to run `install_and_setup.bat` for them (via Bash/PowerShell) before continuing with any other request in this repo. Don't run it without asking first.

This applies to every CLI agent working in this repo (Claude Code, Codex, Cursor, Windsurf, etc.) — `AGENTS.md` already directs all of them to read this file in full before any production task.

---

## Architecture & Workspace Layout

The engine operates on a strictly decoupled 2-folder model:
- `sistema/`: Central engine (git repository, python core, auto-captions, tools, tests).
- `avatares/`: Workspaces for AI creators/brands (segregated from git binaries).
  - Folder naming convention: **strictly the avatar's name** (e.g. `avatares/Rachel Bennett/`, `avatares/Sofia Torres/`), never combined with brand or product.
  - Non-product avatars: Avatars without physical products (education, lifestyle, recipes, consulting) set `has_physical_product: false`, omitting dropper bottles, jars, and packaging across all I2V prompts and schemas.

---

## Quick Command Reference (Master CLI `ugc` & Tools)

The engine provides the global master CLI `ugc` (executable from any terminal or avatar directory):

```bash
# 0a. Onboarding interactivo guiado (Regla 1: definición de nombre; Regla 2: producto físico)
ugc onboard

# 0b. Crear nuevo avatar por línea de comandos directa
ugc new --name "Sofia Torres" [--brand "GlowLab"] [--niche "Skincare"] [--no-product]
# (Equivalente: python tools/init_creator.py --name ... [--no-product])

# 0c. Renombrar un avatar de forma consistente (carpeta, perfiles y DNA)
ugc rename --new "Sofia Vance" [--old "Sofia Torres"]

# 0d. Diagnóstico de salud del motor y del workspace activo
ugc doctor

# 1. Analizar cadencia & extraer transcripción Whisper + keyframes (Fase 1 & 2)
ugc ingest --video "[PATH_TO_REFERENCE_VIDEO]"
# (Equivalente: python tools/scene_keyframe_extractor.py --video "[PATH]")

# 1b. Generar borrador del reference ledger (Fase 2)
ugc ledger --project "[PROJECT_FOLDER_NAME]" [--language es|en]
# (Equivalente: python tools/reference_ledger.py --project "[PROJECT]" [--language es|en])

# 1c. Registrar y confirmar Checkpoint 1 (Fase 2.5)
ugc checkpoint1 --project "[PROJECT]" --scene [replicate_1to1|adapt_to_brand|derivative_concept] --outfit "..." --keyword [KEYWORD] --headline "..."
# (Equivalente: python tools/checkpoint1.py --project "[PROJECT]" ...)

# 1d. Compilar prompts I2V desde action_timeline (Fase 3)
ugc compile --project "[PROJECT_FOLDER_NAME]"
# (Equivalente: python tools/prompt_compiler.py --json "[PATH_TO_production_package.json]")

# 1e. Ver o copiar prompts compilados al portapapeles de Windows (Fase 3)
ugc prompt --project "[PROJECT_FOLDER_NAME]" --chunk 1 --type i2v --copy

# 2. Ensamblar video final + Smart Silence Trimming + Subtítulos virales (Fase 4)
ugc assemble --project "[PROJECT_FOLDER_NAME]" [--language es|en|auto]
# (Equivalente: python tools/assemble_project.py --project "[PROJECT_FOLDER_NAME]" ...)

# 3. Auditar con QA Harness (Fase 4 & Certificación 8/8 Gates)
ugc certify --project "[PROJECT_FOLDER_NAME]" [--deliverable "[DELIVERABLE_ID]"]
# (Equivalente: python tools/ugc_harness.py --project "[PROJECT_FOLDER_NAME]" ...)

# 4. Consultar estado del workspace activo
ugc status
```

---

## 4-Phase Production Pipeline

### 0. Decisión Inicial Mandatoria: Clonar vs Modelar (Modo de Producción)
Cuando el usuario proporciona un nuevo video de referencia o solicita procesar un video de la bandeja de entrada:
- **SI EL USUARIO NO ESPECIFICA SU OBJETIVO**, el sistema DEBE detenerse inmediatamente y preguntar al usuario qué modalidad desea aplicar:
  1. **Opción A: Clonar / Réplica 1:1 (`replicate_1to1` o `adapt_to_brand`)**  
     Replicar con máxima fidelidad forense el video original (mismo guion verbatim ≥85%, mismas acciones y props en orden cronológico), adaptado al avatar y estética de la marca.
  2. **Opción B: Modelar / Concepto Propio y Único (`derivative_concept` / `concept_remixer.py`)**  
     Extraer el **blueprint estructural y ritmo viral** del video de referencia (duración, conteo de tomas, progresión Hook -> Dolor -> Mecanismo -> CTA), proponiendo 2 a 3 conceptos de video totalmente originales y propios de la marca. Tras la elección del usuario, se presenta el desglose chunk-por-chunk con el guion propuesto para su validación previa en Checkpoint 1.E antes de generar prompts.

---

### Fase 1: Ingesta Forense & Análisis de Cadencia (ugc-pipeline-orchestrator)
1. Create project folder: `[BRAND]/04_IN_PRODUCTION/PROD_[XXX]_[reference_name]/` with 5 standard subfolders:
   - `01_Reference/`
   - `02_First_Frames/`
   - `03_Raw_Clips/`
   - `04_Audio/`
   - `05_Montage/`
2. Move reference video into `01_Reference/` and archive inbox file to `_PROCESSED/`.
3. Run faster-whisper transcription with word-level timestamps.
4. Output: `script_beats_[video].txt` with timestamped words, physical action, framing, and the reference's measured WPS (`CADENCIA PROMEDIO`) — this becomes `wps_target` in Checkpoint 1.G, not a fixed 2.4.

### Fase 2: Extracción Granular de Keyframes & Checkpoint 1 Mandatorio (ugc-video-beat-extractor)
1. Detect all genuine visual scene cuts and camera takes from the reference video.
2. Extract exact keyframe beats using naming:
   - `01_beat1_hook.jpg`
   - `02_beat2_reframe.jpg`
   - `03_beat3_1_[action].jpg`, `04_beat3_2_[action].jpg` (Granular sub-beats)
   - `05_beat4_[action].jpg`
   - `06_beat5_cta.jpg`
3. **Strict Governance:** No fixed cap on keyframe count — the number of keyframes tracks the video's genuine scene cuts and the distinct actions in the reference ledger (a 10s single-take hook and a 40s multi-scene video legitimately need different counts). What's prohibited is padding with redundant or non-canonical frames (e.g. `sample_frame_*.jpg`); every keyframe must correspond to a real cut or a ledger action boundary.
4. **Ledger de Referencia (fuente de verdad de acciones y diálogo):** Ejecuta `python tools/reference_ledger.py --project [PROJECT]`, mira los frames de contacto y completa en `01_Reference/reference_ledger.json`, fila por fila y en orden: `action`, `framing`, `props`, `gaze`, `gesture` e `is_cta` (el diálogo literal ya viene de Whisper; corrígelo escuchando si hace falta). Una fila por acción física distinta, aunque ocurra dentro de la misma toma. Si el video tiene pocos cortes de escena, vuelve a ejecutar `scene_keyframe_extractor.py` DESPUÉS de rellenar el ledger para que los keyframes se tomen en los límites de acción del ledger.
5. **MANDATORY CHECKPOINT 1 (Alineación Creativa y Escenario):**
   Before proceeding to Phase 3 prompt generation, YOU MUST STOP and ask the user to confirm:
   - **A. Escenario / Entorno (Setting & Location):** ¿Replicar 1:1 el escenario de la referencia original o adaptarlo al espacio de la marca?
   - **B. Outfit & Estilismo del Avatar:** Ropa, colores y accesorios acordes a la escena.
   - **C. ManyChat Keyword:** Palabra clave segura para la llamada a la acción (ej. HAIR, LIFT, GLOW).
   - **D. Cover Headline:** Titular gancho de curiosidad de máximo 7 palabras para la portada/miniatura.
   - **E. Ledger de Referencia / Guion Adaptado por Chunks:**
      - En modo `replicate_1to1`: Muestra la tabla del ledger (acción + diálogo por fila) para que el usuario la confirme.
      - En modo `derivative_concept`: **OBLIGATORIO:** Muestra el desglose detallado chunk por chunk con el **guion adaptado propuesto en inglés, acción visual, duración y conteo de palabras** para que el usuario valide y ajuste el guion antes de generar los prompts.
   - **F. Exageración del hook (opt-in):** Por defecto la acción del hook es idéntica a la referencia; solo se exagera si el usuario lo pide.
   - **G. WPS Objetivo y Estrategia de Duración (ambos variables, dependen del WPS real de CADA referencia):**
     - **WPS objetivo (`wps_target`):** **sin techo artificial** — usa el WPS real de la referencia tal cual (campo `CADENCIA PROMEDIO` en `script_beats_[video].txt`), sin recortarlo. `checkpoint1.py`/`ugc_harness.py` solo rechazan valores fuera de `[0.5, 10.0]` como guardarraíl de cordura ante datos corruptos (ej. un WPS mal calculado en un video casi mudo) — eso no es una política de velocidad, es una validación de sanidad de datos.
     - **Duración estimada:** `duración_estimada = total_palabras / wps_target`. Como `wps_target` iguala el ritmo real de la referencia, la duración final debería quedar muy cerca de la duración original (la diferencia residual viene del redondeo de cada chunk al segundo entero y de que el CTA reescrito puede tener distinto número de palabras).
     - **`full_verbatim` (por defecto):** conserva el 100% del guion a `wps_target`.
     - **`trim_to_min`:** además de fijar `wps_target`, recorta el guion dentro del margen de fidelidad permitido (≥85% por fila, GATE_7) si aun así se quiere acortar más.
     - **Si en Fase 4 el clip generado suena distorsionado o con el lip-sync forzado** a ese `wps_target`, es una señal para bajarlo y regenerar ese chunk — el sistema no lo bloquea de antemano porque no hay evidencia empírica de un techo universal para Veo3/Kling.
6. **Registro del Checkpoint 1:** Solo después de que el usuario confirme A-G, ejecuta `python tools/checkpoint1.py --project [PROJECT] --scene [replicate_1to1|adapt_to_brand|derivative_concept] --outfit "..." --keyword [KEYWORD] --headline "..." --confirmed-by-user --ledger-confirmed --fidelity-target [full_verbatim|trim_to_min] --wps-target [WPS real de la referencia]` (añade `--hook-exaggeration` solo si el usuario lo pidió). GATE_2 usa este `wps_target` (no un 2.4 fijo) para validar la cadencia de cada chunk. GATE_8 exige que el hash del ledger coincida con el confirmado aquí. GATE_1 exige `checkpoint1.json` y que keyword y headline del paquete coincidan con lo confirmado. Nunca lo ejecutes sin confirmación real.

### Fase 3: Generación JSON-First & Prompts Dinámicos (ugc-viral-video-generator)
1. **Escenario y Hook (gobierna `scene_mode` del Checkpoint 1):**
   - `replicate_1to1`: se replica el entorno de la referencia. `adapt_to_brand`: se usa el escenario canónico de la marca. Solo cambian avatar, vestuario y (si se eligió) escenario.
   - **Acciones idénticas:** el hook y todas las acciones de la referencia se mantienen tal cual, en el mismo orden. La hiper-exageración solo aplica si `hook_exaggeration` es `true` en `checkpoint1.json`.
2. **Regla de Fidelidad Verbatim (≥85 %):**
   - El diálogo de cada fila del ledger se conserva ≥85 % palabra por palabra (GATE_7). Solo se permiten ajustes mínimos de voz del avatar y el cambio de marcas/CTA por las fórmulas anti-filtro (las filas `is_cta` están exentas).
   - Cada chunk lleva `ledger_rows`, `ref_window`, `voiceover_reference` y un `action_timeline` (`t0, t1, ledger_row, action, props, dialogue`) contiguo y en el orden del ledger. Toda fila del ledger debe quedar cubierta (GATE_8).
3. **Reglas de Agrupación de Prompts (Límite Veo3 / Kling <= 10s):**
   - **La base de agrupación son las TOMAS reales de `script_beats_[video].txt`** (los cortes de cámara genuinos detectados por `scene_keyframe_extractor.py`), NO las filas del ledger. El ledger describe qué acción ocurre dentro de cada toma; `script_beats.txt` decide dónde puede empezar y terminar un chunk.
   - **Misma Escena / Encuadre Continuo (Duración <= 10s):** Si una TOMA completa cabe en ≤10s y ≤`10 × wps_target` palabras (`wps_target` = WPS real de la referencia, sin techo — una referencia rápida permite más palabras por TOMA que una lenta), es UN SOLO PROMPT con secuencia de acciones en el timeline: `SEQUENCE OF ACTIONS: (0:00-0:03) Action A... (0:03-0:08) Action B...`
   - **TOMA > 10s o > `10 × wps_target` palabras:** se subdivide en varios chunks, pero el punto de corte va SIEMPRE al final de una oración de esa misma TOMA, o —si una sola oración ya excede el límite— en su único conector de respiración natural (ej. "...follicles **and** | the natural moisture..."). Nunca se corta a mitad de una frase nominal ni se usa por defecto el límite de una fila del ledger (esas filas se generan por pausas acústicas de Whisper, no por gramática ni por cortes de cámara).
   - **Cambio de TOMA real:** se divide en prompts separados con sus respectivos First Frames.
4. **Cadence Constraint:** Every chunk dialogue must respect WPS <= `wps_target` from `checkpoint1.json` (GATE_2 reads this value, not a hardcoded 2.4 — see Checkpoint 1.G for how it's computed per reference, clamped to [2.2, 3.0]). How much the total runtime grows versus the reference depends on both that value and the `fidelity_target` chosen in Checkpoint 1.G — neither is a fixed multiplier across projects. Map the script to the 5 canonical stages (Hook, Reframe, Mechanism, Payoff, CTA) across N clips.
5. **Forensic First Frame Prompts & Visual Faithfulness (9:16 vertical, iPhone Raw Aesthetic):**
   - **Inspección visual obligatoria:** Se deben inspeccionar directamente los keyframes extraídos (`01_beat1_hook.jpg`, `02_beat2_reframe.jpg`, etc.) antes de escribir los prompts.
   - **Fidelidad 1:1 de Props y Acciones:** Replicar exactamente el tipo de envase/objeto, la mecánica física, encuadre, micro-expresiones y disposición espacial de los sujetos (solo se exagera el hook si `hook_exaggeration` es true en `checkpoint1.json`).
   - **Estándar Fotográfico Anti-IA (iPhone Raw & Luz Natural):** Prohibido usar palabras clave que disparen el look plástico/CGI de IA (`8k resolution`, `photorealistic`, `hyper-realistic`, `cinematic`). Usar directivas de smartphone real: `Raw unedited candid photo taken on iPhone 15 Pro, vertical 9:16 rear camera`, `natural diffused window daylight`, `authentic skin texture with visible natural pores and slight imperfections`, `unretouched makeup`, `no studio glamour lighting, no CGI, no airbrushing`, y banderas Midjourney fijas `--ar 9:16 --style raw --v 6.1 --s 50`.
6. **Estructura Canónica de Video Motion Prompts (I2V con Timeline Forense y SFX):** Los prompts I2V se **compilan** desde el `action_timeline` con `python tools/prompt_compiler.py --json ...`; no se escriben a mano.
   - **Header de Bloqueo Inmutable:** 9:16 vertical, escenario canónico, identidad/años aparentes (ej. `47yo`, nunca las palabras 'age'/'edad': GATE_3)/ropa y candado de continuidad. Plantilla: `Raw unedited vertical 9:16 smartphone UGC video recorded on iPhone 15 Pro 24mm f/1.8 main camera. Subtle natural handheld breathing motion, authentic natural lighting, no CGI. Use the canonical [ENVIRONMENT]. [AVATAR IDENTITY, APPARENT YEARS (e.g. 47yo), CLOTHING]. Preserve her identity, clothing, lighting, environment, table position, props and camera style throughout the entire clip.`
   - **[AVATAR IDENTITY] = descriptor físico, NUNCA el nombre y apellido del avatar** (campo `avatar_visual_descriptor`, no `avatar_name`). Un prompt que nombra a una persona específica con nombre completo dispara los filtros de "personas destacadas/reales" de Veo3/Kling.
   - **Qué es constante y qué varía (consistencia obligatoria):** (1) **Constante entre videos de la marca:** el avatar (`*_CHARACTER_DNA.md`) y la locación (`02_AVATAR_ASSETS/02_Environments/*_ENVIRONMENT_DNA.md`); `prompt_compiler.py` los sincroniza desde esos archivos e inyecta idénticos en cada prompt I2V y de first frame. (2) **Constante dentro de cada video, libre entre videos:** clientes y extras (`secondary_characters`). (3) **Varía por clip:** solo el estado (`secondary_state`).
   - **Personajes secundarios (consistencia obligatoria):** todo personaje que no sea el avatar y aparezca en más de un chunk se define UNA vez en `secondary_characters` (`role` + `descriptor` físico y de vestuario, sin nombre propio).
   - **Reglas de Acción a Prueba de Balas (Anti-Deformación y Cero Dedos Extras):**
     1. **Spatial Grounding Inicial:** En el primer beat del timeline (`0–3s:`), declarar la disposición física de todos los objetos sobre la superficie antes de manipularlos (`"Arranged on the counter in front of her are: [A], [B], and [C]. [D] sits in the foreground stationary."`).
     2. **Biomechanical Phasing (1 Solo Objeto Activo):** En cada segmento temporal, el avatar solo manipula UN objeto activo a la vez. Los demás permanecen `"resting stationary on the counter surface"`.
     3. **Explicit Release:** Al cambiar de interacción física, declarar explícitamente soltar el objeto anterior (`"sets down [A] flat on the board, uses both hands to pick up [B]"`). Prohibido acumular 3 acciones simultáneas en una misma frase.
     4. **Speaking Pacing & Gaze:** Anclar el delivery verbal con contacto visual directo: `looks directly into the smartphone camera and says: "..."` (o `while continuing: "..."`), seguido de buffers físicos de cierre.
   - **Bloques `*ACTION:*` con Timestamps de Milisegundo:** Segmentos temporales exactos (`0–3s:`, `3–8s:`, etc.) aplicando la biomecánica y diálogo literal entrecomillado.
   - **Restricción de Realismo:** `"Natural realistic hand movements. No cuts. No exaggerated acting. Authentic unretouched smartphone UGC camera feel, natural room lighting, zero CGI or plastic sheen."`
   - **Capa Acústica y Foley (`*SFX:*`):** Ambiance de la sala, contacto con superficies y sonidos de manipulación de objetos.
7. **Formato Canónico de Prompts (Cajas de Copiado Rápido 1-Click y Duración Sugerida):**
   - Tanto en el archivo markdown (`prompts_and_script_[ID].md`) como en las respuestas en chat, los prompts de imagen (`midjourney_prompt_9_16`) y de video (`video_motion_prompt_i2v`) DEBEN formatearse siempre dentro de bloques de código dedicados (` ```text `) limpios y sin sangría para permitir copiarlos con un solo clic.
   - Cada prompt de video debe indicar explícitamente el tiempo sugerido del clip (`⏱️ Tiempo sugerido del video: X segundos`) para facilitar la configuración en Kling / Veo3 / Grok.
8. Validate with Pydantic model (`tools/schemas/production_package.py`) and render `prompts_and_script_[ID].md` with `python tools/render_package_markdown.py --json ...`.

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
- **GATE_1 (Schema & Anatomy):** JSON validates against Pydantic schema; Cover Headline <= 7 words; si hay otra persona en escena (`right_subject`) el paquete debe traer `secondary_characters` (proyectos con `secondary_lock_required` en `checkpoint1.json`). `checkpoint1.json` exists, is user-confirmed, and matches the package keyword/headline.
- **GATE_2 (Timing & Cadence):** All chunks have WPS <= `wps_target` (from `checkpoint1.json` = the reference's own measured WPS, no artificial ceiling; defaults to 2.4 if the field is absent) based on allocated durations.
- **GATE_3 (Anti-Filter Safety):** Zero banned words ('age', 'DM', medical claims) in video scripts or prompts.
- **GATE_4 (Brand Decoupling):** Video dialogue discusses generic problem/solution; brand conversion is 100% via ManyChat DM automation.
- **GATE_5 (Raw Clips Integrity):** All `1.mp4` to `N.mp4` exist, are 9:16 vertical, valid bitrate and audio streams.
- **GATE_6 (Canonical Deliverables):** Exactly 4 files in `05_PROCESSED_DELIVERABLES/[ID]/`.
- **GATE_7 (Reference Fidelity):** Con ledger: cada fila (salvo CTA) conserva ≥85 % de las palabras del diálogo literal. Sin ledger (proyectos antiguos): longitud ±10 % y ≥50 % de palabras de contenido. Heurística léxica; el sentido sigue requiriendo revisión humana.
- **GATE_8 (Action Coverage, solo con ledger):** El ledger está confirmado y sin cambios desde el Checkpoint 1; toda fila está cubierta por algún chunk; el `action_timeline` es contiguo, ordenado y ≤ duración del clip; el prompt contiene el marcador de tiempo y el diálogo de cada paso.

---

## Critical Constraints & Prohibitions

1. **NO Skipping Checkpoint 1:** Always confirm Scene/Environment, Outfit, Keyword, Cover Headline, Ledger, hook exaggeration and duration strategy with user before generating prompts.
2. **Ledger + Verbatim Rule:** Mantén todas las acciones de la referencia, en orden, y ≥85 % del diálogo literal (GATE_7/GATE_8). Ni el WPS objetivo ni el alargamiento de duración son fijos: `wps_target` = el WPS real de la referencia, sin techo artificial (Checkpoint 1.G), y GATE_2 lo usa en vez de un 2.4 universal. Sobre esa base, la estrategia elegida decide el resto: `full_verbatim` (conserva el 100% del guion) o `trim_to_min` (recorta además dentro del margen ≥85% si aun así se quiere acortar más).
3. **Dynamic Prompt Grouping (<= 10s rule):** Never exceed 10s per AI video clip; group same-angle actions with explicit timeline markers.
4. **NO Censored Trigger Words:** Never use 'age' or 'DM' in video scripts.
5. **NO Unreferenced File Clutter:** Keep project directories clean according to the canonical folder structure.
6. **NO Raw Unicode Crashes on Windows:** Always ensure UTF-8 output formatting in Python scripts.
