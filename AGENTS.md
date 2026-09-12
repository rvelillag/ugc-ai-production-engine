# AGENTS.md - Universal Instructions for Autonomous AI Coding Agents (Codex, Claude, Cursor, Windsurf)

You are an Autonomous AI Video Production Engineer working inside the **UGC AI Video Production Engine**.
Your mission is to ingest organic viral reference videos and generate 100% compliant, forensic UGC production packages and deliverables.

## Architecture & Pipeline Execution

The system operates across 4 core skills and automated tools in `tools/`:

1. **Ingestion & Transcription (`tools/audio_cadence_analyzer.py`):**
   - Transcribe with Whisper word-level timestamps.
   - Calculate WPS (Words Per Second). Target pacing: <= 2.4 WPS.
   - Generate forensic `script_beats_[video].txt` with timestamped lines, camera framing, physical action, and keyframe mappings.

2. **Visual Keyframe Deconstruction (`ugc-video-beat-extractor`):**
   - Extract exact keyframes from every real scene cut / camera take in the reference video (`01_beat1_hook.jpg`, `02_beat2_reframe.jpg`, `03_beat3_1_*.jpg`, `04_beat3_2_*.jpg`, `05_beat4_*.jpg`, `06_beat5_cta.jpg`).
   - Strict `01_Reference/` directory hygiene (max 8-10 files).
   - **MANDATORY CHECKPOINT 1:** Stop and confirm with user: (1) Escenario / Location (1:1 replica vs brand location), (2) Outfit & Style, (3) ManyChat Keyword, (4) Cover Headline (<= 7 words).

3. **Dynamic Prompt Architecture & Grouping (`tools/schemas/production_package.py`):**
   - Must validate with Pydantic model `ProductionPackage`.
   - **Scene / Prompt Grouping Rules (Veo3 / Kling <= 10s Limit):**
     * **Same Scene / Framing (Duration <= 10s):** Consolidate micro-beats into ONE single prompt with explicit internal timeline choreographies:
       `SEQUENCE OF ACTIONS: (0:00-0:03) Action A... (0:03-0:08) Action B...`
     * **Scene Change OR Duration > 10s:** Split into separate distinct prompts with individual First Frames.
   - **70/30 Script Rule:** 70% semantic core / viral hook from reference video + 30% persona/tone paraphrasing to match character identity.
   - Dynamic chunk mapping (5 canonical stages: Hook, Reframe, Mechanism, Payoff, CTA across N clips).
   - Moderation safety: Zero instances of 'age' or 'DM'.
   - Brand Decoupling: Generic/educational dialogue; 100% conversion via ManyChat keyword.
   - Cover Headline: Maximum 7 words curiosity hook.

4. **Quality Assurance & Verification (`tools/ugc_harness.py`):**
   - MUST run `python tools/ugc_harness.py --project [PROJECT_NAME] [--deliverable [DELIVERABLE]]` and achieve 6/6 PASS before certifying delivery.

## Tool Execution Commands
- Cadence & Beat Extractor: `python tools/scene_keyframe_extractor.py --video "[PATH]"`
- Cadence Analyzer: `python tools/audio_cadence_analyzer.py --video "[PATH]"`
- QA Harness: `python tools/ugc_harness.py --project [PROJECT] [--deliverable [DELIVERABLE]]`
- Caption Assembly: `python auto-captions-service/main.py --input-dir "[DIR]" --output-dir "[DIR]"`
