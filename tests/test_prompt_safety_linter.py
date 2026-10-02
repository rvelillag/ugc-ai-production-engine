import pytest
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from tools.prompt_safety_linter import lint_text, verify_hook_front_loading


def test_lint_text_sanitizes_bare_back_and_leggings():
    raw = "The patient has a bare lower back with low-rise leggings while standing in the room."
    clean, fixes = lint_text(raw)
    assert "bare lower back" not in clean
    assert "low-rise leggings" not in clean
    assert "athletic" in clean
    assert len(fixes) == 2


def test_lint_text_sanitizes_pinching_contact():
    raw = "The specialist pinches skin on the back to demonstrate elasticity."
    clean, fixes = lint_text(raw)
    assert "pinches skin" not in clean
    assert "clinical two-finger palpation" in clean
    assert len(fixes) >= 1


def test_lint_text_removes_plastic_buzzwords():
    raw = "Authentic portrait, 8k resolution, photorealistic portrait of an aesthetic doctor."
    clean, fixes = lint_text(raw)
    assert "8k resolution" not in clean
    assert "photorealistic" not in clean
    assert "Authentic portrait" in clean


def test_verify_hook_front_loading():
    # Bad hook: avatar first, shock late
    bad_hook = "Specialist Rachel Bennett standing in kitchen holding a cup while talking about a severe swollen pitting edema on the foot."
    res_bad = verify_hook_front_loading(bad_hook)
    assert res_bad["has_pathology_or_shock"] is True
    assert res_bad["is_front_loaded"] is False

    # Good hook: shock first
    good_hook = "Extreme macro forced perspective in foreground: severely swollen pitting edema on foot with deep depression under glove."
    res_good = verify_hook_front_loading(good_hook)
    assert res_good["has_pathology_or_shock"] is True
    assert res_good["is_front_loaded"] is True
