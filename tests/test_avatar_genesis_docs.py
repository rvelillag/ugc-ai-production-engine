from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_prompts_avatar_builder_has_reference_sheet_formula():
    content = (REPO_ROOT / "ugc-avatar-genesis" / "prompts_avatar_builder.md").read_text(encoding="utf-8")
    assert "Hoja de Referencia desde Imagen Subida" in content
    assert "front view" in content
    assert "left profile view" in content
    assert "back view" in content
