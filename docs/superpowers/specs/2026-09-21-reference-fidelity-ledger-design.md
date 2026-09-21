# Reference Fidelity Ledger — Design

**Date:** 2026-09-21 · **Status:** approved by user in chat (dialogue option B: ≥85 % verbatim)

## Problem
The pipeline captures one keyframe per camera cut and a free-text "action" placeholder. Actions inside a
single long take are lost, the package schema has nowhere to store per-action timing, and no gate checks
that every reference action / line of dialogue survives into the prompts. Skill rules also contradict the
goal (scenario "never cloned", hook "hyper-exaggerated", dialogue paraphrased 70/30).

## Goal
Output prompts that keep **every action, in order, and the dialogue (≥85 % verbatim)** of the reference.
Only avatar, outfit and (optionally) scenario change, as decided at Checkpoint 1.

## Components
1. **Ledger** — `01_Reference/reference_ledger.json`. Rows: `id, t_start, t_end, dialogue_verbatim, action,
   framing, props[], gaze, gesture, is_cta`. Drafted by `tools/reference_ledger.py` (Whisper words grouped
   by pauses + 2 fps contact frames); actions are filled in by Claude from the frames, then user-confirmed.
2. **Checkpoint 1** records `ledger_hash` (sha256 of canonical ledger JSON) and `hook_exaggeration`
   (opt-in, default false).
3. **Schema** — `ChunkItem` gains optional `ledger_rows`, `ref_window`, `action_timeline[ActionStep]`,
   `voiceover_reference`, `sfx`. Optional so legacy packages still validate.
4. **Prompt compiler** — `tools/prompt_compiler.py` builds `video_motion_prompt_i2v` from the
   `action_timeline` using the canonical template (header, `*ACTION:*` timestamps, realism line, `*SFX:*`).
5. **Gates** — when a ledger exists (or checkpoint has `ledger_hash`):
   - GATE_7 becomes per-row dialogue fidelity ≥ 0.85 (CTA rows exempt).
   - GATE_8 (new) action coverage: ledger confirmed & unchanged, every row covered, timeline contiguous,
     ordered, ≤ clip duration, prompt contains each step's time marker and dialogue.
   Without a ledger the legacy GATE_7 applies and GATE_8 is skipped (backward compatible).
6. **Rules/docs** — CLAUDE.md and the two skills: scenario governed by `scene_mode`, exaggeration opt-in,
   70/30 replaced by "ledger + ≥85 % verbatim".

## Out of scope
Automated visual description of actions by a local model; assembly/subtitle changes.
