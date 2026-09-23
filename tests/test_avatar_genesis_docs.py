from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_prompts_avatar_builder_has_reference_sheet_formula():
    content = (REPO_ROOT / "ugc-avatar-genesis" / "prompts_avatar_builder.md").read_text(encoding="utf-8")
    assert "Hoja de Referencia desde Imagen Subida" in content
    assert "front view" in content
    assert "left profile view" in content
    assert "back view" in content


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
