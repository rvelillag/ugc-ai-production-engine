import copy
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.ugc_harness import UGCHarness

FFMPEG = shutil.which("ffmpeg")


def _chunk(cid, text, dur=8):
    return {
        "chunk_id": cid, "beat_name": "hook", "recommended_duration_s": dur,
        "word_count": len(text.split()), "voiceover_clean_tts": text,
        "visual_direction": "v",
        "composition_audit": {
            "camera_shot_type": "c", "foreground_props": "p",
            "left_subject": {"name": "A", "character_id": "a_1", "orientation": "o", "pose": "p",
                            "hands_interaction": "h", "gaze_direction": "g", "outfit": "o"},
            "environment_background": "e", "lighting_style": "l",
        },
        "midjourney_prompt_9_16": "a woman in a kitchen",
        "video_motion_prompt_i2v": "she talks",
        "asset_tags": [], "continuity_notes": "n",
    }


@pytest.fixture
def package():
    return {
        "project_id": "PROD_001", "reference_video": "r.mp4", "reference_duration_s": 20.0,
        "topic": "t", "brand": "Glowlab", "avatar_name": "A", "avatar_age": 40,
        "avatar_archetype": "x", "wardrobe_previous": "a", "wardrobe_assigned": "b",
        "audio_voice_direction_anchor": "v", "standard_skeleton_25_30s": "s",
        "chunks": [_chunk(1, "this simple trick changed my mornings completely")],
        "post_copy": {"cover_headline": "Stop Doing This Every Morning", "title": "t",
                      "caption": "c", "manychat_keyword": "GLOW", "hashtags": ["#a"]},
    }


def _run(tmp_path, pkg):
    f = tmp_path / "p.json"
    f.write_text(json.dumps(pkg), encoding="utf-8")
    return {r.gate_id: r for r in UGCHarness.audit_package_json(f)}


def test_valid_package_passes_gates_1_to_4(tmp_path, package):
    assert all(r.passed for r in _run(tmp_path, package).values())


def test_duration_over_10s_fails(tmp_path, package):
    package["chunks"][0]["recommended_duration_s"] = 15
    r = _run(tmp_path, package)
    assert not r["GATE_2"].passed and not r["GATE_1"].passed


def test_declared_word_count_mismatch_fails(tmp_path, package):
    package["chunks"][0]["word_count"] = 2
    assert not _run(tmp_path, package)["GATE_2"].passed


def test_wps_over_limit_fails(tmp_path, package):
    package["chunks"][0]["voiceover_clean_tts"] = " ".join(["word"] * 30)
    package["chunks"][0]["word_count"] = 30
    assert not _run(tmp_path, package)["GATE_2"].passed


def test_banned_term_in_image_prompt_fails(tmp_path, package):
    package["chunks"][0]["midjourney_prompt_9_16"] = "a woman of a certain age"
    assert not _run(tmp_path, package)["GATE_3"].passed


def test_own_brand_in_dialogue_fails(tmp_path, package):
    package["chunks"][0]["voiceover_clean_tts"] = "try Glowlab today"
    package["chunks"][0]["word_count"] = 3
    assert not _run(tmp_path, package)["GATE_4"].passed


def test_missing_manychat_keyword_fails(tmp_path, package):
    package["post_copy"]["manychat_keyword"] = ""
    assert not _run(tmp_path, package)["GATE_4"].passed


def _make_clip(path, size, audio=True):
    cmd = [FFMPEG, "-y", "-f", "lavfi", "-i", f"nullsrc=size={size}:rate=30:duration=1,geq=random(1)*255:128:128"]
    if audio:
        cmd += ["-f", "lavfi", "-i", "sine=frequency=440:duration=1"]
    cmd += ["-b:v", "2M", "-pix_fmt", "yuv420p", str(path)]
    subprocess.run(cmd, check=True, capture_output=True)


@pytest.mark.skipif(not FFMPEG, reason="ffmpeg no disponible")
@pytest.mark.parametrize("size,audio,ok", [
    ("1080x1920", True, True),
    ("1920x1080", True, False),
    ("1080x1920", False, False),
])
def test_gate5_clip_checks(tmp_path, size, audio, ok):
    _make_clip(tmp_path / "1.mp4", size, audio)
    assert UGCHarness.audit_raw_clips(tmp_path, 1).passed is ok


def _deliverables(d, extra=None, omit=None):
    d.mkdir()
    files = {"X_Final_1080x1920.mp4": "", "X_Subtitles.srt": "", "X_Cover.jpg": "",
             "post_copy_title_and_caption.txt": "HEADLINE DE PORTADA:\nhi"}
    files.update(extra or {})
    for name, body in files.items():
        if name != omit:
            (d / name).write_text(body, encoding="utf-8")
    return UGCHarness.audit_deliverables(d, "X")


def test_gate6_exact_four_passes(tmp_path):
    assert _deliverables(tmp_path / "d").passed


def test_gate6_extra_file_fails(tmp_path):
    assert not _deliverables(tmp_path / "d", extra={"junk.txt": "x"}).passed


def test_gate6_missing_file_fails(tmp_path):
    assert not _deliverables(tmp_path / "d", omit="X_Subtitles.srt").passed


def test_keyframe_labels_match_canonical_naming():
    from tools.scene_keyframe_extractor import beat_label
    assert beat_label(0, 6) == "beat1_hook" and beat_label(1, 6) == "beat2_reframe"
    assert beat_label(5, 6) == "beat5_cta"
    assert beat_label(2, 6) == "beat3_1_action" and beat_label(3, 6) == "beat3_2_action"
    assert beat_label(4, 6) == "beat4_action"
    assert len({beat_label(i, 10) for i in range(10)}) == 10


REF = ("Just put baking soda on your hair and you will not believe what happens next "
       "because this simple mixture removes buildup and leaves your scalp clean and soft")


def _fidelity(tmp_path, package, ref_text, gen_text):
    ref = tmp_path / "01_Reference"
    ref.mkdir()
    (ref / "script_beats_x.txt").write_text(
        f"DURACIÓN\n=====\nTRANSCRIPCIÓN COMPLETA LITERAL:\n=======================================================\n{ref_text}\n=======================================================\nFIN\n",
        encoding="utf-8")
    package["chunks"][0]["voiceover_clean_tts"] = gen_text
    package["chunks"][0]["word_count"] = len(gen_text.split())
    f = tmp_path / "p.json"
    f.write_text(json.dumps(package), encoding="utf-8")
    return UGCHarness.audit_reference_fidelity(f, ref)


def test_gate7_same_length_and_meaning_passes(tmp_path, package):
    gen = ("Simply put baking soda on your hair and you will not believe what happens next "
           "because this easy mixture removes buildup and leaves your scalp clean and soft")
    assert _fidelity(tmp_path, package, REF, gen).passed


def test_gate7_too_short_fails(tmp_path, package):
    r = _fidelity(tmp_path, package, REF, "put baking soda on your hair and see what happens")
    assert not r.passed


def test_gate7_same_length_different_meaning_fails(tmp_path, package):
    gen = " ".join(["walking daily improves heart health while reducing stress levels quickly"] * 2 + ["every morning"])
    assert not _fidelity(tmp_path, package, REF, gen).passed


def test_gate7_missing_reference_fails(tmp_path, package):
    f = tmp_path / "p.json"
    f.write_text(json.dumps(package), encoding="utf-8")
    assert not UGCHarness.audit_reference_fidelity(f, tmp_path / "nope").passed


def _cp_setup(tmp_path, package, **overrides):
    from tools.checkpoint1 import write_checkpoint
    proj = tmp_path / "PROD_001_x"
    (proj / "02_First_Frames").mkdir(parents=True)
    jp = proj / "02_First_Frames" / "production_package_PROD_001.json"
    jp.write_text(json.dumps(package), encoding="utf-8")
    return proj, jp, write_checkpoint


def test_checkpoint1_missing_fails(tmp_path, package):
    proj, jp, _ = _cp_setup(tmp_path, package)
    assert not UGCHarness.audit_checkpoint1(jp, proj)[0]


def test_checkpoint1_matching_passes(tmp_path, package):
    proj, jp, write = _cp_setup(tmp_path, package)
    write(proj, "adapt_to_brand", "beige blazer", "glow", "Stop Doing This Every Morning")
    assert UGCHarness.audit_checkpoint1(jp, proj)[0]


def test_checkpoint1_keyword_mismatch_fails(tmp_path, package):
    proj, jp, write = _cp_setup(tmp_path, package)
    write(proj, "adapt_to_brand", "beige blazer", "HAIR", "Stop Doing This Every Morning")
    assert not UGCHarness.audit_checkpoint1(jp, proj)[0]


def test_checkpoint1_unconfirmed_fails(tmp_path, package):
    proj, jp, write = _cp_setup(tmp_path, package)
    cp = write(proj, "adapt_to_brand", "beige blazer", "GLOW", "Stop Doing This Every Morning")
    data = json.loads(cp.read_text(encoding="utf-8")); data["confirmed_by_user"] = False
    cp.write_text(json.dumps(data), encoding="utf-8")
    assert not UGCHarness.audit_checkpoint1(jp, proj)[0]


def test_checkpoint1_rejects_long_headline(tmp_path, package):
    proj, _, write = _cp_setup(tmp_path, package)
    with pytest.raises(ValueError):
        write(proj, "adapt_to_brand", "x", "GLOW", "one two three four five six seven eight")
