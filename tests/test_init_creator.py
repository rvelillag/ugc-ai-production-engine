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


def test_template_archetype_comment_lists_five_types():
    repo_root = Path(__file__).resolve().parent.parent
    template = (repo_root / "_CREATOR_TEMPLATE" / "creator_profile.yaml").read_text(encoding="utf-8")
    archetype_line = next(line for line in template.splitlines() if line.strip().startswith("archetype:"))
    for archetype in ARCHETYPES:
        assert archetype in archetype_line, f"{archetype} missing from archetype comment: {archetype_line}"
