import sys
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from ugc import suggest_avatar_names, evaluate_name, detect_workspace


def test_suggest_avatar_names_female_hair():
    names = suggest_avatar_names("Haircare / Cuidado capilar", "female")
    assert len(names) >= 4
    assert any("Rachel" in n or "Camila" in n for n in names)


def test_suggest_avatar_names_male_tech():
    names = suggest_avatar_names("Tech / IA", "male")
    assert len(names) >= 4
    assert any("David" in n or "Lucas" in n for n in names)


def test_evaluate_name_single_word_suggests_surname():
    suggested = evaluate_name("Sofia", "Skincare")
    assert suggested == "Sofia Torres"


def test_evaluate_name_two_words_cleaned():
    suggested = evaluate_name("camila vega", "Haircare")
    assert suggested == "Camila Vega"


def test_detect_workspace_finds_creator_profile(tmp_path):
    avatar_dir = tmp_path / "Sofia Torres"
    avatar_dir.mkdir()
    (avatar_dir / "creator_profile.yaml").write_text("creator:\n  name: Sofia\n", encoding="utf-8")
    
    found = detect_workspace(str(avatar_dir))
    assert found == avatar_dir
