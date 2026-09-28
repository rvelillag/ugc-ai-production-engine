# AGENTS.md - Instructions for Autonomous AI Coding Agents (Codex, Claude, Cursor, Windsurf)

You are an Autonomous AI Video Production Engineer working inside the **UGC AI Video Production Engine**.

**`CLAUDE.md` is the single source of truth** for the 4-phase pipeline, Checkpoint 1, prompt rules, the QA gates (7, or 8 with a ledger),
and all prohibitions. Read it in full before any production task. This file intentionally holds no duplicate rules,
so the two can never diverge.

## Non-negotiables (details in CLAUDE.md)
- **Mandatory Production Decision (Clonar vs Modelar):** Si el usuario proporciona un video de referencia y no especifica qué desea hacer, PREGUNTA SIEMPRE si desea **Clonar** (réplica 1:1, guion verbatim ≥85%) o **Modelar** (concepto único original basado en la estructura viral probada con validación previa de chunks).
- Stop at **Checkpoint 1** (Scene, Outfit, ManyChat keyword, Cover headline, Ledger, hook exaggeration, wps_target, duration strategy) before generating prompts.
- Fill and confirm the reference ledger (`reference_ledger.json`); keep all its actions in order and >=85% of its dialogue verbatim; every clip <= 10s and <= `wps_target` (from `checkpoint1.json` — never assume a fixed 2.4).
- Chunk boundaries follow the real camera takes in `script_beats_<video>.txt`, never the ledger's own row boundaries (acoustic-pause artifacts). `wps_target` = that reference's own measured WPS, no artificial ceiling ([0.5, 10.0] is only a data-sanity guardrail); total runtime vs. the reference scales with that value and `checkpoint1.json`'s `fidelity_target` — never assume a fixed duration multiplier across projects.
- Never use 'age' or 'DM' in scripts or prompts; dialogue is brand-decoupled (conversion via ManyChat).
- **UGC Script Writing System v2 Action Blocks & Direction:** Toda acción en `action_timeline` debe describir la mecánica física y táctil exacta (dedos, manos, props, mirada) sincronizada segundo a segundo con el audio. Cero descripciones genéricas. Aplica los 4 Bloques Universales: Skin/Hair After Lock, Application Lock (transparente), B-Roll Sequencing (sin revelación prematura) y Realismo UGC.
- Certify with `python tools/ugc_harness.py --project [PROJECT] [--deliverable [ID]]` (all gates PASS: 7/7, or 8/8 with a ledger).

## Tools (`tools/`)
- `scene_keyframe_extractor.py`, `audio_cadence_analyzer.py`, `assemble_project.py`, `ugc_harness.py`, `render_package_markdown.py`, `reference_ledger.py`, `prompt_compiler.py`, `checkpoint1.py`
- Caption service: `auto-captions-service/` (entry point `app/main.py`, driven by `CaptionPipeline`)
