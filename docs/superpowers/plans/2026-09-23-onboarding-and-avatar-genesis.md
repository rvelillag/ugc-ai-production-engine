# Install-on-Clone Prompt & Guided Avatar Onboarding Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make any CLI coding agent proactively offer to run setup on a fresh clone, and turn new-avatar onboarding into an AI-guided interview that produces a character brief and ready-to-use image prompts instead of a bare 5-field form.

**Architecture:** A setup marker file (`.setup_complete`) written by `install_and_setup.bat` and checked via a new instruction block at the top of `CLAUDE.md` (read by every AGENTS.md-aware CLI). A new "Paso 0" interview script in `ugc-avatar-genesis/SKILL.md` that the agent follows conversationally, producing a `CHARACTER_BRIEF.md` and calling the now-extended `tools/init_creator.py` (new `--archetype`/`--target-audience` args) as the final mechanical step. Supporting doc/template updates in `prompts_avatar_builder.md`, `creator_profile.yaml`, and `menu.py`.

**Tech Stack:** Python 3.10+ (argparse, pathlib), Windows Batch (`.bat`), Markdown/YAML docs, pytest for the Python-testable pieces.

**Spec:** `docs/superpowers/specs/2026-09-23-onboarding-and-avatar-genesis-design.md`

## Global Constraints

- No image-generation API is wired in — prompts remain copy-ready text for the user to paste into Midjourney/Flux (spec Non-goals).
- Installer/marker mechanism is Windows-only, matching existing `.bat` tooling (spec Non-goals).
- `AGENTS.md`/`.cursorrules` are not modified — they already route every agent to read `CLAUDE.md` in full (spec Part 1).
- `tools/init_creator.py` stays a pure mechanical scaffolder — it does not write `CHARACTER_BRIEF.md`; the agent writes that file directly (spec Part 2, `creator_profile.yaml` / `init_creator.py` changes, final decision).
- Archetype taxonomy is exactly 5 values: Especialista, Espejo, Familiar, Insider, Convertido (spec Part 2, Paso 0 step 2).
- The existing no-real-name rule for `avatar_visual_descriptor`/DNA anchors is unchanged — never inject a full name into a generator-facing prompt (CLAUDE.md, existing rule; spec Paso 0 step 5).

---

## Task 1: Install-on-clone marker in `install_and_setup.bat`

**Files:**
- Modify: `install_and_setup.bat`
- Test: manual (batch scripts have no pytest harness in this repo — verified by running the marker-writing snippet directly, per repo convention documented in the spec's Testing section)

**Interfaces:**
- Produces: `.setup_complete` file at repo root, containing `<ISO date> <sha256 of requirements.txt>\n`. Task 2 depends on this filename and its mere-existence-as-signal semantics.

- [ ] **Step 1: Renumber existing steps from `[N/4]` to `[N/5]`**

Open `install_and_setup.bat` and change the four step headers so they count out of 5 instead of 4, to make room for the new step:
- `echo [1/4] Verificando version de Python...` → `echo [1/5] Verificando version de Python...`
- `echo [2/4] Instalando paquetes y librerias requeridas (Whisper, FFmpeg, PyTorch, PyYAML)...` → `echo [2/5] ...` (same text otherwise)
- `echo [3/4] Inicializando y verificando binarios de FFmpeg...` → `echo [3/5] ...`
- `echo [4/4] Verificando estructura de plantillas y modulos...` → `echo [4/5] ...`

- [ ] **Step 2: Add the new step 5 marker-writing block**

Insert this new block after the existing step 4's validation block (the one that checks `_CREATOR_TEMPLATE` exists) and before the final `echo ========...` success banner:

```bat
:: 5. Registrar marca de instalacion completa
echo [5/5] Registrando marca de instalacion completa...
python -c "
import hashlib
from pathlib import Path
from datetime import date
req_hash = hashlib.sha256(Path('requirements.txt').read_bytes()).hexdigest()
Path('.setup_complete').write_text(f'{date.today().isoformat()} {req_hash}\n', encoding='utf-8')
print('Marca de instalacion creada: .setup_complete')
"
echo.
```

- [ ] **Step 3: Add `.setup_complete` to `.gitignore`**

Open `.gitignore` and add a new line under the `# Temporary, Logs & Scratch` section (after `temp/`):

```
.setup_complete
```

- [ ] **Step 4: Manually verify the marker-writing snippet**

Run the exact Python snippet from Step 2 directly (not the full `.bat`, to avoid re-running the pip install in this session):

```bash
python -c "
import hashlib
from pathlib import Path
from datetime import date
req_hash = hashlib.sha256(Path('requirements.txt').read_bytes()).hexdigest()
Path('.setup_complete').write_text(f'{date.today().isoformat()} {req_hash}\n', encoding='utf-8')
print('Marca de instalacion creada: .setup_complete')
"
cat .setup_complete
```

Expected: prints `Marca de instalacion creada: .setup_complete`, and `.setup_complete` contains one line matching `YYYY-MM-DD <64-char hex hash>`.

- [ ] **Step 5: Commit**

```bash
git add install_and_setup.bat .gitignore
git commit -m "feat(install): write .setup_complete marker at end of install_and_setup.bat"
```

---

## Task 2: Setup-check instruction block in `CLAUDE.md`

**Files:**
- Modify: `CLAUDE.md:1` (insert new section before line 1's content, i.e. as the new top of the file, before `# CLAUDE.md - UGC AI Video Production Engine`... actually insert immediately after the title/intro, before `## Quick Command Reference`)
- Test: Create: `tests/test_docs.py`

**Interfaces:**
- Consumes: `.setup_complete` filename from Task 1.
- Produces: nothing consumed by later tasks — this is a leaf documentation change, but tested for regression via `tests/test_docs.py`.

- [ ] **Step 1: Write the failing test**

Create `tests/test_docs.py`:

```python
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_claude_md_has_setup_check_section_near_top():
    content = (REPO_ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    # Must appear before the Quick Command Reference so agents see it first.
    setup_idx = content.find("Setup Check")
    quick_ref_idx = content.find("## Quick Command Reference")
    assert setup_idx != -1, "CLAUDE.md is missing a 'Setup Check' section"
    assert quick_ref_idx != -1
    assert setup_idx < quick_ref_idx, "Setup Check section must come before Quick Command Reference"
    assert ".setup_complete" in content
    assert "install_and_setup.bat" in content
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_docs.py -v`
Expected: FAIL — `assert -1 != -1` (no "Setup Check" section found yet).

- [ ] **Step 3: Insert the new section into `CLAUDE.md`**

Edit `CLAUDE.md`, inserting this new section immediately after the intro paragraph and its `---` separator (i.e. between the current lines 1-5 and `## Quick Command Reference`):

```markdown
## Setup Check (run once per session)

Before doing any pipeline work in this repo, check whether `.setup_complete` exists at the repo root.

- **If it exists:** setup has already run — proceed normally.
- **If it's missing:** this looks like a fresh clone. Tell the user setup hasn't been run yet, and offer to run `install_and_setup.bat` for them (via Bash/PowerShell) before continuing with any other request in this repo. Don't run it without asking first.

This applies to every CLI agent working in this repo (Claude Code, Codex, Cursor, Windsurf, etc.) — `AGENTS.md` already directs all of them to read this file in full before any production task.

---
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_docs.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add CLAUDE.md tests/test_docs.py
git commit -m "docs: add setup-check instruction to top of CLAUDE.md"
```

---

## Task 3: Extend `tools/init_creator.py` with `--archetype` and `--target-audience`

**Files:**
- Modify: `tools/init_creator.py:1-92` (refactor `init_creator()`'s argparse setup into a standalone `build_arg_parser()`, and extract the profile-content substitution into a standalone `substitute_profile_fields()`)
- Create: `tests/test_init_creator.py`

**Interfaces:**
- Produces: `ARCHETYPES: list[str]` constant (`["Especialista", "Espejo", "Familiar", "Insider", "Convertido"]`), `build_arg_parser() -> argparse.ArgumentParser`, `substitute_profile_fields(content: str, *, name: str, brand: str, age: int, gender: str, archetype: str, niche: str, keyword: str, target_audience: str) -> str`. Task 6 (SKILL.md) documents the agent calling this CLI with `--archetype` and `--target-audience`.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_init_creator.py`:

```python
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.init_creator import ARCHETYPES, build_arg_parser, substitute_profile_fields


def test_archetypes_are_the_five_canonical_types():
    assert ARCHETYPES == ["Especialista", "Espejo", "Familiar", "Insider", "Convertido"]


def test_parser_accepts_valid_archetype():
    parser = build_arg_parser()
    args = parser.parse_args([
        "--name", "Sofia Torres",
        "--brand", "GlowLab",
        "--archetype", "Espejo",
        "--target-audience", "Mujeres de 30 a 45 anos",
    ])
    assert args.archetype == "Espejo"
    assert args.target_audience == "Mujeres de 30 a 45 anos"


def test_parser_rejects_invalid_archetype():
    parser = build_arg_parser()
    with pytest.raises(SystemExit):
        parser.parse_args([
            "--name", "Sofia Torres",
            "--brand", "GlowLab",
            "--archetype", "NotARealType",
        ])


def test_parser_defaults_archetype_and_target_audience():
    parser = build_arg_parser()
    args = parser.parse_args(["--name", "Sofia Torres", "--brand", "GlowLab"])
    assert args.archetype == "Espejo"
    assert args.target_audience == ""


def test_substitute_profile_fields_replaces_all_placeholders():
    template = (
        'creator:\n'
        '  name: "Nombre del Creador"\n'
        '  age: 47\n'
        '  gender: "female"\n'
        '  archetype: "Mirror + Convert"\n'
        '  target_audience: "Mujeres de 40 a 55 años"\n'
        '\n'
        'brand:\n'
        '  name: "Nombre de la Marca"\n'
        '  niche: "Skincare / Cuidado de la piel"\n'
        '\n'
        'manychat:\n'
        '  default_keyword: "YOUTHFUL"\n'
    )
    result = substitute_profile_fields(
        template,
        name="Sofia Torres",
        brand="GlowLab",
        age=52,
        gender="female",
        archetype="Espejo",
        niche="Skincare",
        keyword="GLOW",
        target_audience="Mujeres de 30 a 45 anos",
    )
    assert 'name: "Sofia Torres"' in result
    assert "age: 52" in result
    assert 'archetype: "Espejo"' in result
    assert 'target_audience: "Mujeres de 30 a 45 anos"' in result
    assert 'name: "GlowLab"' in result
    assert 'niche: "Skincare"' in result
    assert 'default_keyword: "GLOW"' in result
    assert "Mirror + Convert" not in result
    assert "Mujeres de 40 a 55 años" not in result
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_init_creator.py -v`
Expected: FAIL — `ImportError: cannot import name 'ARCHETYPES' from 'tools.init_creator'` (none of the new names exist yet).

- [ ] **Step 3: Refactor `tools/init_creator.py`**

Replace the full contents of `tools/init_creator.py` with:

```python
import os
import sys
import shutil
import argparse
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ARCHETYPES = ["Especialista", "Espejo", "Familiar", "Insider", "Convertido"]


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inicializador de Nuevo Creador / Avatar para UGC Production Engine")
    parser.add_argument("--name", required=True, help="Nombre del creador (ej: 'Sofia Torres')")
    parser.add_argument("--brand", required=True, help="Nombre de la marca (ej: 'GlowLab')")
    parser.add_argument("--age", type=int, default=45, help="Edad del avatar (default: 45)")
    parser.add_argument("--gender", default="female", help="Género del avatar ('female' / 'male')")
    parser.add_argument("--niche", default="Skincare / Cuidado de la piel", help="Nicho de la marca")
    parser.add_argument("--keyword", default="GLOW", help="Keyword predeterminada para ManyChat")
    parser.add_argument("--archetype", default="Espejo", choices=ARCHETYPES,
                         help="Tipo de personaje: " + ", ".join(ARCHETYPES))
    parser.add_argument("--target-audience", default="", dest="target_audience",
                         help="Descripción de la audiencia objetivo (ej: 'Mujeres de 30 a 45 años')")
    return parser


def substitute_profile_fields(content: str, *, name: str, brand: str, age: int, gender: str,
                               archetype: str, niche: str, keyword: str, target_audience: str) -> str:
    content = content.replace('"Nombre del Creador"', f'"{name}"')
    content = content.replace("age: 47", f"age: {age}")
    content = content.replace('"female"', f'"{gender}"')
    content = content.replace('archetype: "Mirror + Convert"', f'archetype: "{archetype}"')
    if target_audience:
        content = content.replace('target_audience: "Mujeres de 40 a 55 años"', f'target_audience: "{target_audience}"')
    content = content.replace('"Nombre de la Marca"', f'"{brand}"')
    content = content.replace('"Skincare / Cuidado de la piel"', f'"{niche}"')
    content = content.replace('"YOUTHFUL"', f'"{keyword}"')
    return content


def init_creator():
    args = build_arg_parser().parse_args()

    base_dir = Path(__file__).resolve().parent.parent
    template_dir = base_dir / "_CREATOR_TEMPLATE"

    if not template_dir.exists():
        print(f"Error: No se encontró la plantilla en {template_dir}")
        sys.exit(1)

    creator_folder_name = f"{args.name} - {args.brand}"
    target_dir = base_dir / creator_folder_name

    if target_dir.exists():
        print(f"Aviso: El directorio '{creator_folder_name}' ya existe en {target_dir}")
        sys.exit(1)

    print(f"--> Creando espacio de trabajo para '{args.name}' ({args.brand})...")
    shutil.copytree(template_dir, target_dir)

    # Asegurar explícitamente la creación de todos los directorios 01 a 05
    (target_dir / "01_KNOWLEDGE_BASE").mkdir(parents=True, exist_ok=True)
    (target_dir / "02_AVATAR_ASSETS" / "01_Character").mkdir(parents=True, exist_ok=True)
    (target_dir / "02_AVATAR_ASSETS" / "02_Environments").mkdir(parents=True, exist_ok=True)
    (target_dir / "03_INBOX_REFERENCES").mkdir(parents=True, exist_ok=True)
    (target_dir / "04_IN_PRODUCTION").mkdir(parents=True, exist_ok=True)
    (target_dir / "05_PROCESSED_DELIVERABLES").mkdir(parents=True, exist_ok=True)

    # Personalizar creator_profile.yaml
    profile_file = target_dir / "creator_profile.yaml"
    if profile_file.exists():
        content = profile_file.read_text(encoding="utf-8")
        content = substitute_profile_fields(
            content,
            name=args.name, brand=args.brand, age=args.age, gender=args.gender,
            archetype=args.archetype, niche=args.niche, keyword=args.keyword,
            target_audience=args.target_audience,
        )
        profile_file.write_text(content, encoding="utf-8")

    # Personalizar y renombrar CHARACTER_DNA_TEMPLATE.md
    char_dir = target_dir / "02_AVATAR_ASSETS" / "01_Character"
    old_dna = char_dir / "CHARACTER_DNA_TEMPLATE.md"
    new_dna_name = f"{args.name.upper().replace(' ', '_')}_CHARACTER_DNA.md"
    new_dna = char_dir / new_dna_name

    if old_dna.exists():
        dna_content = old_dna.read_text(encoding="utf-8")
        dna_content = dna_content.replace("[NOMBRE_CREADOR]", args.name)
        dna_content = dna_content.replace("[Nombre Creador]", args.name)
        dna_content = dna_content.replace("[Nombre]", args.name)
        dna_content = dna_content.replace("[NOMBRE_MARCA]", args.brand)
        dna_content = dna_content.replace("[Edad]", str(args.age))
        dna_content = dna_content.replace("[Arquetipo]", args.archetype)
        new_dna.write_text(dna_content, encoding="utf-8")
        old_dna.unlink()

    print(f"\n[OK] ¡Creador '{creator_folder_name}' inicializado con éxito!")
    print(f"Ubicación: {target_dir}")
    print(f"\nDirectorios listos:")
    print(f"  📁 01_KNOWLEDGE_BASE/")
    print(f"  📁 02_AVATAR_ASSETS/ (01_Character, 02_Environments)")
    print(f"  📁 03_INBOX_REFERENCES/")
    print(f"  📁 04_IN_PRODUCTION/")
    print(f"  📁 05_PROCESSED_DELIVERABLES/")
    print(f"  📄 creator_profile.yaml")
    print(f"  📄 PRODUCT_CATALOG.yaml")
    print(f"\nSiguientes pasos recomendados:")
    print(f"1. Generar fotos de referencia y guardarlas en: '{creator_folder_name}/02_AVATAR_ASSETS/01_Character/'")
    print(f"2. Ajustar el catálogo propio en: '{creator_folder_name}/PRODUCT_CATALOG.yaml'")
    print(f"3. Colocar videos de referencia en: '{creator_folder_name}/03_INBOX_REFERENCES/'")


if __name__ == "__main__":
    init_creator()
```

Note: `args.archetype` now replaces the old hardcoded `"Mirror + Convert"` substitution when personalizing `CHARACTER_DNA_TEMPLATE.md`'s `[Arquetipo]` placeholder too (previously it was hardcoded to `"Mirror + Convert"` regardless of input — this was a latent bug, now fixed as a side effect of threading `--archetype` through).

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_init_creator.py -v`
Expected: PASS (all 5 tests)

- [ ] **Step 5: Commit**

```bash
git add tools/init_creator.py tests/test_init_creator.py
git commit -m "feat(init_creator): add --archetype (5-type enum) and --target-audience args"
```

---

## Task 4: Update `creator_profile.yaml` template archetype comment

**Files:**
- Modify: `_CREATOR_TEMPLATE/creator_profile.yaml:10`
- Modify: `tests/test_init_creator.py` (add one test)

**Interfaces:**
- Consumes: `ARCHETYPES` from Task 3.

- [ ] **Step 1: Write the failing test**

Add to `tests/test_init_creator.py`:

```python
def test_template_archetype_comment_lists_five_types():
    repo_root = Path(__file__).resolve().parent.parent
    template = (repo_root / "_CREATOR_TEMPLATE" / "creator_profile.yaml").read_text(encoding="utf-8")
    archetype_line = next(line for line in template.splitlines() if line.strip().startswith("archetype:"))
    for archetype in ARCHETYPES:
        assert archetype in archetype_line, f"{archetype} missing from archetype comment: {archetype_line}"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_init_creator.py::test_template_archetype_comment_lists_five_types -v`
Expected: FAIL — `AssertionError: Especialista missing from archetype comment: ...`

- [ ] **Step 3: Update the template**

Edit `_CREATOR_TEMPLATE/creator_profile.yaml` line 10, changing:

```yaml
  archetype: "Mirror + Convert"       # "Mirror + Convert" | "Authority Expert" | "Lifestyle Peer"
```

to:

```yaml
  archetype: "Espejo"                 # "Especialista" | "Espejo" | "Familiar" | "Insider" | "Convertido"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_init_creator.py::test_template_archetype_comment_lists_five_types -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add _CREATOR_TEMPLATE/creator_profile.yaml tests/test_init_creator.py
git commit -m "docs(template): update creator_profile.yaml archetype comment to 5-type taxonomy"
```

---

## Task 5: Add reference-sheet prompt formula to `prompts_avatar_builder.md`

**Files:**
- Modify: `ugc-avatar-genesis/prompts_avatar_builder.md`
- Create: `tests/test_avatar_genesis_docs.py`

**Interfaces:**
- Produces: a new `## 4. Prompt Maestro para Hoja de Referencia desde Imagen Subida` section, referenced by Task 6's Paso 0 step 5.

- [ ] **Step 1: Write the failing test**

Create `tests/test_avatar_genesis_docs.py`:

```python
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_prompts_avatar_builder_has_reference_sheet_formula():
    content = (REPO_ROOT / "ugc-avatar-genesis" / "prompts_avatar_builder.md").read_text(encoding="utf-8")
    assert "Hoja de Referencia desde Imagen Subida" in content
    assert "front view" in content
    assert "left profile view" in content
    assert "back view" in content
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_avatar_genesis_docs.py -v`
Expected: FAIL — `AssertionError: assert 'Hoja de Referencia desde Imagen Subida' in ...`

- [ ] **Step 3: Add the new section**

Append to `ugc-avatar-genesis/prompts_avatar_builder.md` (after the existing "3. Prompts Maestros para Entornos Oficiales 9:16" section):

```markdown
---

## 4. Prompt Maestro para Hoja de Referencia desde Imagen Subida (`character_reference_sheet.png`)

Usar este prompt una vez que el `Profile Picture.jpeg` del personaje ya fue aprobado, subiéndolo como imagen de referencia:

```text
Create a professional character reference sheet based strictly on the uploaded reference image. Use a clean, neutral plain background and present the sheet as a technical model turnaround while matching the exact visual style of the reference (same realism level, rendering approach, texture, color treatment, and overall aesthetic). Arrange the composition into two horizontal rows. Top row: four full-body standing views placed side-by-side in this order: front view, left profile view (facing left), right profile view (facing right), back view. Bottom row: three highly detailed close-up portraits aligned beneath the full-body row in this order: front portrait, left profile portrait (facing left), right profile portrait (facing right). Maintain perfect identity consistency across every panel. Keep the subject in a relaxed A-pose and with consistent scale and alignment between views, accurate anatomy, and clear silhouette; ensure even spacing and clean panel separation, with uniform framing and consistent head height across the full-body lineup and consistent facial scale across the portraits. Lighting should be consistent across all panels (same direction, intensity, and softness), with natural, controlled shadows that preserve detail without dramatic mood shifts. Output a crisp, print-ready reference sheet look, sharp details.
```
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_avatar_genesis_docs.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add ugc-avatar-genesis/prompts_avatar_builder.md tests/test_avatar_genesis_docs.py
git commit -m "docs(avatar-genesis): add reference-sheet prompt formula"
```

---

## Task 6: Add "Paso 0: Entrevista de Personaje" to `ugc-avatar-genesis/SKILL.md`

**Files:**
- Modify: `ugc-avatar-genesis/SKILL.md`
- Modify: `tests/test_avatar_genesis_docs.py` (add tests)

**Interfaces:**
- Consumes: `ARCHETYPES` values (Especialista, Espejo, Familiar, Insider, Convertido) from Task 3/4; the reference-sheet prompt name from Task 5; `--archetype`/`--target-audience` CLI flags from Task 3.
- Produces: the `CHARACTER_BRIEF.md` structure (documented inline in SKILL.md, not a separate template file per the Global Constraints).

- [ ] **Step 1: Write the failing tests**

Add to `tests/test_avatar_genesis_docs.py`:

```python
def test_skill_md_has_paso_0_interview():
    content = (REPO_ROOT / "ugc-avatar-genesis" / "SKILL.md").read_text(encoding="utf-8")
    assert "Paso 0: Entrevista de Personaje" in content
    for archetype in ["Especialista", "Espejo", "Familiar", "Insider", "Convertido"]:
        assert archetype in content
    assert "CHARACTER_BRIEF.md" in content
    assert "--archetype" in content
    assert "--target-audience" in content


def test_skill_md_checklist_mentions_character_brief():
    content = (REPO_ROOT / "ugc-avatar-genesis" / "SKILL.md").read_text(encoding="utf-8")
    checklist_start = content.find("## 2. Checklist de Validación del Avatar")
    assert checklist_start != -1
    checklist = content[checklist_start:]
    assert "CHARACTER_BRIEF.md" in checklist
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_avatar_genesis_docs.py -v`
Expected: FAIL — 2 new failures (`Paso 0: Entrevista de Personaje` not found; checklist doesn't mention `CHARACTER_BRIEF.md`).

- [ ] **Step 3: Insert Paso 0 into `ugc-avatar-genesis/SKILL.md`**

Edit the file:

1. Change the section header `## 1. Flujo de Onboarding en 5 Pasos` to `## 1. Flujo de Onboarding en 6 Pasos (0 a 5)`.

2. Insert this new section immediately after that header and before `### Paso 1: Inicializar el Espacio de Trabajo`:

```markdown
### Paso 0: Entrevista de Personaje

Antes de crear ningún archivo, conduce esta entrevista conversacional con el usuario, una pregunta a la vez. El objetivo es producir la ficha del personaje y los prompts de imagen — este paso lo conduce el agente de IA (Claude, Codex, etc.), no es un script.

1. **Contexto del video/audiencia.** Pregunta por el nicho/tema del video y la investigación de audiencia que ya tenga. Si no tiene nada, haz 2-3 preguntas rápidas (quién sufre qué, cuál es el gancho emocional) para esbozar una audiencia ligera — no esperes un documento de investigación completo.

2. **Tipo de personaje.** Propón uno de estos 5 arquetipos con una razón de una línea basada en el contexto del paso 1; el usuario puede aceptar o pedir otra opción:
   - **Especialista** — autoridad profesional, accesible, sin bata blanca ni lenguaje distante.
   - **Espejo** — idéntico a la audiencia, empieza escéptico, comparte un descubrimiento honesto.
   - **Familiar** — un par/amigo que comparte su rutina cotidiana sin esfuerzo.
   - **Insider** — habla desde dentro de la industria/empresa, "esto es lo que no te cuentan."
   - **Convertido** — un ex-escéptico/sufriente que encontró la solución y ahora la evangeliza.

3. **Ficha del personaje.** Completa lo siguiente, proponiendo sugerencias concretas (no solo preguntas abiertas) cuando el usuario no tenga nada en mente:
   - Nombre, edad, género, apariencia general (clase social que transparece).
   - Jeito de ser: cómo habla, qué valora, energía (cansada, acogedora, animada, seria).
   - Apariencia física: cabello, piel, cuerpo, ropa, accesorios — anclados a parecerse a la audiencia del paso 1, no a un modelo genérico.
   - Expresión de rostro en reposo.
   - Gancho de atención: qué hace que la persona no siga scrolleando.

4. **Confirmación.** Muestra la ficha completa al usuario para un sí/ajuste final antes de escribir nada a disco.

5. **Escritura de archivos** (solo después de la confirmación):
   - Redacta `CHARACTER_BRIEF.md` en `02_AVATAR_ASSETS/01_Character/CHARACTER_BRIEF.md` con esta estructura:

     ```markdown
     # Character Brief — <Nombre>

     ## Contexto de Audiencia
     <nicho, resumen de investigación de audiencia>

     ## Tipo de Personaje: <Especialista|Espejo|Familiar|Insider|Convertido>
     <por qué este tipo encaja con esta audiencia>

     ## Jeito de Ser
     <cómo habla, qué valora, energía>

     ## Apariencia Física
     <cabello, piel, cuerpo, ropa, accesorios — y por qué cada elección refleja a la audiencia>

     ## Expresión en Reposo
     <...>

     ## Gancho de Atención
     <qué hace que la persona no siga scrolleando>
     ```

   - Redacta el párrafo-ancla compacto para `*_CHARACTER_DNA.md` (Paso 4), siguiendo la regla existente de no usar nombre completo real.
   - Compila los prompts de imagen desde `prompts_avatar_builder.md` (Retrato de Perfil, Hoja de Consistencia Facial, y Hoja de Referencia desde Imagen Subida) sustituyendo los detalles de la ficha, y preséntalos como texto listo para copiar en Midjourney/Flux.
   - Llama a `python tools/init_creator.py --name "<Nombre>" --brand "<Marca>" --archetype "<Tipo>" --target-audience "<Audiencia>" [--age N] [--gender ...] [--niche ...] [--keyword ...]` para crear la carpeta del creador con todos los valores ya decididos.
```

3. In `## 2. Checklist de Validación del Avatar`, add a new checklist item after the `creator_profile.yaml` line:

```markdown
- [ ] `CHARACTER_BRIEF.md` redactado en `01_Character/` con la ficha completa de la entrevista.
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_avatar_genesis_docs.py -v`
Expected: PASS (all tests in the file)

- [ ] **Step 5: Commit**

```bash
git add ugc-avatar-genesis/SKILL.md tests/test_avatar_genesis_docs.py
git commit -m "feat(avatar-genesis): add agent-led Paso 0 character interview to onboarding skill"
```

---

## Task 7: Point `menu.py`'s basic wizard to the agent-guided flow

**Files:**
- Modify: `tools/menu.py:21-25` (inside `option_create_avatar`)
- Create: `tests/test_menu.py`

**Interfaces:**
- None consumed/produced beyond the printed string — leaf change.

- [ ] **Step 1: Write the failing test**

Create `tests/test_menu.py`:

```python
import inspect
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools import menu


def test_option_create_avatar_points_to_agent_guided_flow():
    source = inspect.getsource(menu.option_create_avatar)
    hint_idx = source.find("agente de código")
    first_input_idx = source.find("input(")
    assert hint_idx != -1, "option_create_avatar should mention the agent-guided flow"
    assert hint_idx < first_input_idx, "the hint must print before the first input() prompt"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_menu.py -v`
Expected: FAIL — `AssertionError: option_create_avatar should mention the agent-guided flow`

- [ ] **Step 3: Add the hint line**

Edit `tools/menu.py`'s `option_create_avatar` function (lines 21-26), changing:

```python
def option_create_avatar(base_dir: Path):
    clear_screen()
    print("========================================================")
    print("     CREAR NUEVO AVATAR / CREADOR (WIZARD GUIADO)")
    print("========================================================\n")
    name = input("1. Nombre del Creador (ej: Sofia Torres): ").strip()
```

to:

```python
def option_create_avatar(base_dir: Path):
    clear_screen()
    print("========================================================")
    print("     CREAR NUEVO AVATAR / CREADOR (WIZARD GUIADO)")
    print("========================================================\n")
    print("Sugerencia: para una entrevista guiada con sugerencias de IA (arquetipo,")
    print("apariencia, ficha de personaje y prompts de imagen), pídeselo a tu agente")
    print("de código (Claude Code, Codex, etc.) en vez de usar este wizard básico.\n")
    name = input("1. Nombre del Creador (ej: Sofia Torres): ").strip()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_menu.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tools/menu.py tests/test_menu.py
git commit -m "docs(menu): point basic avatar wizard to the agent-guided onboarding flow"
```

---

## Task 8: Full test suite sanity check

**Files:** none (verification-only task)

- [ ] **Step 1: Run the full test suite**

Run: `pytest tests/ -v`
Expected: all tests PASS, including the pre-existing `test_harness.py`, `test_ledger.py`, `test_ledger_gates.py`, plus every test added in Tasks 2-7.

- [ ] **Step 2: Manually confirm `.setup_complete` is gitignored**

Run: `git status --porcelain`
Expected: `.setup_complete` (created in Task 1 Step 4) does NOT appear in the output — confirms `.gitignore` is working.
