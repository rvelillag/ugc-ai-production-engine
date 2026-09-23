# Design: Install-on-Clone Prompt & Guided Avatar Onboarding

Date: 2026-09-23
Status: Approved for planning

## Problem

1. After cloning the repo from any CLI-based coding agent (Claude Code, Codex,
   Cursor/Windsurf via `.cursorrules`, Antigravity via `AGENTS.md`
   conventions), nothing prompts the user to run `install_and_setup.bat`. A
   user can start asking for pipeline work in a repo that has never had its
   Python deps / FFmpeg installed, and only discovers this when a tool call
   fails deep into a task.

2. The avatar onboarding flow (`ugc_studio.bat` → `menu.py` option 1 →
   `tools/init_creator.py`) is a plain, non-creative CLI wizard: it collects
   5 flat fields (name, brand, age, niche, keyword) and scaffolds folders.
   All the creative work — deciding the character archetype, physical
   appearance, personality, and the image-generation prompts to produce the
   avatar's reference photos — is left entirely to the user reading
   `ugc-avatar-genesis/prompts_avatar_builder.md` and filling in bracketed
   placeholders by hand, with no guidance or suggestions if they don't
   already have a character in mind.

## Goals

- Any CLI agent working in this repo checks, at the start of a session,
  whether setup has been run, and proactively offers to run it if not.
- The first interaction of creating a new avatar becomes a friendly,
  AI-guided interview: it proposes a character type and appearance from the
  video niche/audience (with concrete suggestions, not just open questions,
  when the user has nothing in mind), and produces both a human-readable
  character brief and the ready-to-use image-generation prompts.
- No new infrastructure dependency: prompts are still handed to the user as
  text (Midjourney/Flux, pasted manually) — no image-generation API is
  wired in.

## Non-goals

- Generating the avatar image automatically via an MCP image tool (decided
  against — keep the system working for users without such tools connected).
- Rewriting the 4-phase production pipeline (Fases 1-4) — this only touches
  the pre-Fase-1 avatar/creator onboarding step and installation.
- Cross-platform (non-Windows) installer support — out of scope, matches
  existing `.bat`-only tooling.

## Part 1: Install-on-clone prompt

### Mechanism

- `install_and_setup.bat`'s final step (after all 4 steps succeed) writes a
  marker file `.setup_complete` at the repo root containing an ISO date and
  the `requirements.txt` content hash (so a future dependency change can be
  detected too, though acting on hash mismatches is left to a future task —
  for now the file's mere existence is the signal).
- A new section is added at the **very top of `CLAUDE.md`**, above the
  Quick Command Reference, titled "Setup Check (run once per session)":
  it instructs the agent to check for `.setup_complete` at the repo root
  before doing any pipeline work, and if absent, to tell the user this looks
  like a fresh clone and offer to run `install_and_setup.bat` for them
  (via Bash/PowerShell) before continuing.
- `AGENTS.md` already tells every agent to "Read [CLAUDE.md] in full before
  any production task" — so this single addition propagates to Codex,
  Cursor, Windsurf, and any other AGENTS.md-aware CLI without touching
  `.cursorrules` or `AGENTS.md` themselves.

### Files touched

- `install_and_setup.bat` — write `.setup_complete` at the end.
- `CLAUDE.md` — new top section.
- `.gitignore` — add `.setup_complete` (it's a local machine marker, not
  something to commit).

## Part 2: Guided avatar onboarding

### Where the intelligence lives

The creative interview (asking questions, proposing archetypes, suggesting
appearance details, drafting prose) requires LLM reasoning conditioned on
whatever the user says — it cannot be a static Python script. It is
implemented as **agent instructions in `ugc-avatar-genesis/SKILL.md`**,
followed by whichever agent (Claude, Codex, etc.) the user is chatting with.
`tools/init_creator.py` remains the mechanical last step: given the fully
decided values, it scaffolds folders and files exactly as it does today,
plus two additions (below).

`menu.py`'s existing input()-based option 1 is kept as a bare-minimum
fallback for someone who double-clicks `ugc_studio.bat` with no AI agent
attached — it gets one added line pointing them at the richer, agent-guided
flow when available.

### New Paso 0 in `ugc-avatar-genesis/SKILL.md`: Entrevista de Personaje

Inserted before the current Paso 1 (Inicializar el Espacio de Trabajo).
Written as a step-by-step script for the agent to follow conversationally,
one question at a time:

1. **Contexto del video/audiencia.** Ask for the content niche/subject and
   any audience research the user already has. If they have none, ask 2-3
   quick questions (who struggles with what, what's the emotional hook) to
   sketch a lightweight audience picture — don't block on a full research
   doc.
2. **Tipo de personaje.** Propose one of the 5 archetypes below with a
   one-line rationale tied to what was learned in step 1; let the user
   accept or ask for an alternative:
   - **Especialista** — professional authority, accessible, no lab coat /
     distant language.
   - **Espejo** — identical to the audience, starts skeptical, shares an
     honest discovery.
   - **Familiar** — a peer/friend sharing an everyday routine effortlessly.
   - **Insider** — speaks from inside the industry/company, "here's what
     they don't tell you."
   - **Convertido** — a former skeptic/sufferer who found the solution and
     now evangelizes it.
3. **Ficha del personaje.** Fill in, proposing concrete suggestions (not
   just open questions) whenever the user has nothing in mind:
   - Nombre, edad, género, apariencia general (clase social que transparece).
   - Jeito de ser: cómo habla, qué valora, energía (cansada, acogedora,
     animada, seria).
   - Apariencia física: cabello, piel, cuerpo, ropa, accesorios — anclados a
     parecerse a la audiencia descrita en el paso 1, no a un modelo genérico.
   - Expresión de rostro en reposo.
   - Gancho de atención: qué hace que la persona no siga scrolleando.
4. **Confirmación.** Show the assembled ficha back to the user for a final
   yes/adjust before writing anything to disk.
5. **Escritura de archivos** (only after confirmation):
   - Draft `CHARACTER_BRIEF.md` (new — see below).
   - Draft the compact anchor paragraph for `*_CHARACTER_DNA.md`, following
     the existing no-real-name rule (physical descriptor only, never a full
     name, to avoid Veo3/Kling "real person" filters).
   - Compile the 3 image-generation prompts from
     `prompts_avatar_builder.md`'s formulas, substituting the ficha's
     details, and present them as copy-ready text for Midjourney/Flux.
   - Call `tools/init_creator.py` with all decided values to scaffold the
     creator folder.

The existing Pasos 1-5 are renumbered Pasos 1-5 → stay conceptually the
same but now consume the ficha/brief produced in Paso 0 instead of asking
the user to invent everything from scratch inline.

### New file: `CHARACTER_BRIEF.md`

Location: `02_AVATAR_ASSETS/01_Character/CHARACTER_BRIEF.md`.
Human-readable, includes the *why* behind each choice (not just the final
values) — this is the richer creative artifact; `*_CHARACTER_DNA.md` stays
as today: the compact, prompt-ready anchor paragraph. Sections:

```markdown
# Character Brief — <Nombre>

## Contexto de Audiencia
<niche, audience research summary>

## Tipo de Personaje: <Especialista|Espejo|Familiar|Insider|Convertido>
<why this type fits this audience>

## Jeito de Ser
<how they talk, what they value, energy>

## Apariencia Física
<hair, skin, body, clothing, accessories — and why each choice mirrors the audience>

## Expresión en Reposo
<...>

## Gancho de Atención
<what makes people stop scrolling>
```

### `creator_profile.yaml` / `init_creator.py` changes

- `_CREATOR_TEMPLATE/creator_profile.yaml`: `archetype` field comment
  updated to list the 5 types (Especialista, Espejo, Familiar, Insider,
  Convertido) in place of the current 3.
- `tools/init_creator.py`:
  - New `--archetype` arg, validated against the 5-type enum (replaces the
    current hardcoded `"Mirror + Convert"` substitution).
  - New `--target-audience` arg, written into `creator_profile.yaml`'s
    `creator.target_audience` field (currently left at its template
    default).
  - After scaffolding, writes a `CHARACTER_BRIEF.md` stub (headers only, per
    the template above) into `01_Character/` for the agent to fill in the
    same call sequence — OR (simpler) the agent writes `CHARACTER_BRIEF.md`
    itself directly before/after calling `init_creator.py`, since it already
    has all the content. **Decision: the agent writes it directly** — no
    stub-writing responsibility added to `init_creator.py` — keeps
    `init_creator.py` a pure mechanical scaffolder, consistent with its
    current role.

### `prompts_avatar_builder.md` changes

- Keep the 2 existing formulas (Retrato de Perfil, Hoja de Consistencia
  Facial) — no format change, still bracketed-placeholder templates the
  agent fills in from the ficha.
- Add a 3rd formula: **Reference Sheet desde Imagen Subida** (based on the
  4th prompt shared by the user) — a technical turnaround-sheet prompt
  that takes the confirmed portrait as a starting reference and produces
  the multi-angle/multi-expression grid, for use once the portrait itself
  is approved.
- Environment prompts (Cocina, Baño) stay as-is — out of scope, they're
  brand-scenario prompts, not character prompts.

### `menu.py` change

- `option_create_avatar`: add one printed line before the existing
  input() flow, e.g. "Para una entrevista guiada con sugerencias de IA,
  pídeselo a tu agente de código (Claude Code, Codex, etc.) en vez de usar
  este wizard básico." No behavioral change to the existing fallback path.

## Testing

- No automated tests exist for `menu.py`/`init_creator.py` today (they're
  interactive CLI scripts) — manual verification:
  - Run `install_and_setup.bat` end-to-end, confirm `.setup_complete` is
    created.
  - Delete `.setup_complete`, start a fresh Claude Code session in the repo,
    confirm the agent proactively flags missing setup per the new `CLAUDE.md`
    section.
  - Run `init_creator.py` with the new `--archetype`/`--target-audience`
    args, confirm `creator_profile.yaml` is populated correctly and an
    invalid archetype value is rejected.
  - Manually walk through the Paso 0 interview with an agent for a sample
    niche, confirm `CHARACTER_BRIEF.md`, the DNA anchor, and the 3 prompts
    are all produced and internally consistent.

## Open questions

None — all prior decision points were resolved during brainstorming
(install trigger scope, onboarding engine choice, image-generation scope,
archetype taxonomy, character brief file location).
