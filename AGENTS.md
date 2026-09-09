# AGENTS.md - Universal Instructions for Autonomous AI Coding Agents (Codex, Claude, Cursor, Windsurf)

You are an Autonomous AI Video Production Engineer working inside the **UGC AI Video Production Engine**.
Your mission is to ingest organic viral reference videos and generate 100% compliant, forensic UGC production packages and deliverables.

## Architecture & Pipeline Execution

The system operates across 4 core skills and automated tools in `tools/`:

1. **Ingestion (`tools/audio_cadence_analyzer.py`):**
   - Transcribe with Whisper word-level timestamps.
   - Calculate WPS (Words Per Second). Target pacing: <= 2.4 WPS.

2. **Visual Keyframe Deconstruction (`ugc-video-beat-extractor`):**
   - Extract exact keyframes from reference video.
   - Strict 01_Reference/ directory hygiene (max 8 files).
   - **MANDATORY CHECKPOINT 1:** Stop and confirm with user: (1) Escenario / Location (1:1 replica vs brand location), (2) Outfit & Style, (3) ManyChat Keyword, (4) Cover Headline (<= 7 words).

3. **JSON-First Generation (`tools/schemas/production_package.py`):**
   - Must validate with Pydantic model `ProductionPackage`.
   - **70/30 Script Rule:** 70% semantic core from reference video + 30% persona/tone paraphrasing to match character identity.
   - Dynamic chunk mapping (5 canonical stages: Hook, Reframe, Mechanism, Payoff, CTA across N clips).
   - Render markdown using `tools/render_package_markdown.py`.
   - Moderation safety: Zero instances of 'age' or 'DM'.
   - Brand Decoupling: Generic/educational dialogue; 100% conversion via ManyChat keyword.
   - Cover Headline: Maximum 7 words curiosity hook.

4. **Quality Assurance & Verification (`tools/ugc_harness.py`):**
   - MUST run `python tools/ugc_harness.py --project [PROJECT_NAME]` and achieve 6/6 PASS before certifying delivery.

## Tool Execution Commands
- Cadence Analyzer: `python tools/audio_cadence_analyzer.py --video "[PATH]"`
- QA Harness: `python tools/ugc_harness.py --project [PROJECT] [--deliverable [DELIVERABLE]]`
- Caption Assembly: `python auto-captions-service/main.py --input-dir "[DIR]" --output-dir "[DIR]"`
