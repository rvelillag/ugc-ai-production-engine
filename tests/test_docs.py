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
