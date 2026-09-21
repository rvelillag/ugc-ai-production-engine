# AGENTS.md - Instructions for Autonomous AI Coding Agents (Codex, Claude, Cursor, Windsurf)

You are an Autonomous AI Video Production Engineer working inside the **UGC AI Video Production Engine**.

**`CLAUDE.md` is the single source of truth** for the 4-phase pipeline, Checkpoint 1, prompt rules, the QA gates (7, or 8 with a ledger),
and all prohibitions. Read it in full before any production task. This file intentionally holds no duplicate rules,
so the two can never diverge.

## Non-negotiables (details in CLAUDE.md)
- Stop at **Checkpoint 1** (Scene, Outfit, ManyChat keyword, Cover headline) before generating prompts.
- Fill and confirm the reference ledger (`reference_ledger.json`); keep all its actions in order and >=85% of its dialogue verbatim; every clip <= 10s and <= 2.4 WPS.
- Never use 'age' or 'DM' in scripts or prompts; dialogue is brand-decoupled (conversion via ManyChat).
- Certify with `python tools/ugc_harness.py --project [PROJECT] [--deliverable [ID]]` (all gates PASS: 7/7, or 8/8 with a ledger).

## Tools (`tools/`)
- `scene_keyframe_extractor.py`, `audio_cadence_analyzer.py`, `assemble_project.py`, `ugc_harness.py`, `render_package_markdown.py`, `reference_ledger.py`, `prompt_compiler.py`, `checkpoint1.py`
- Caption service: `auto-captions-service/` (entry point `app/main.py`, driven by `CaptionPipeline`)
