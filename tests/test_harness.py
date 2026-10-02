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


def test_checkpoint1_persists_clip_durations(tmp_path, package):
    proj, _, write = _cp_setup(tmp_path, package)
    write(proj, "adapt_to_brand", "x", "GLOW", "Headline", clip_durations=[5, 10])
    cp = json.loads((proj / "checkpoint1.json").read_text(encoding="utf-8"))
    assert cp.get("clip_durations") == [5, 10]


@pytest.mark.parametrize("bad", ["send me a DM", "drop a d.m now", "D M me", "what ages work", "cuál es tu edad", "it cures acne", "clinically proven"])
def test_gate3_catches_variants(tmp_path, package, bad):
    package["chunks"][0]["voiceover_clean_tts"] = bad
    package["chunks"][0]["word_count"] = len(bad.split())
    assert not _run(tmp_path, package)["GATE_3"].passed


@pytest.mark.parametrize("ok", ["I'd make this every day", "the image is clean", "manage your mornings"])
def test_gate3_no_false_positives(tmp_path, package, ok):
    package["chunks"][0]["voiceover_clean_tts"] = ok
    package["chunks"][0]["word_count"] = len(ok.split())
    assert _run(tmp_path, package)["GATE_3"].passed


def test_gate7_spanish_stopwords_not_counted(tmp_path):
    ref = tmp_path / "01_Reference"
    ref.mkdir()
    (ref / "script_beats_x.txt").write_text('Voiceover Original: "el la los de que y en un una con por para el la los de"', encoding="utf-8")
    pkg = tmp_path / "p.json"
    pkg.write_text(json.dumps({"chunks": [{"voiceover_clean_tts": "el la los de que y en un una con por para el la los de"}]}), encoding="utf-8")
    # solo stopwords en la referencia -> sin contenido comparable, no debe aprobar por solapamiento vacío
    assert not UGCHarness.audit_reference_fidelity(pkg, ref).passed


def test_precheck_skips_clips_and_deliverables(tmp_path):
    proj = tmp_path / "Brand" / "04_IN_PRODUCTION" / "PROD_001_ref"
    (proj / "02_First_Frames").mkdir(parents=True)
    (proj / "01_Reference").mkdir()
    rep = UGCHarness.run_full_project_audit(tmp_path / "Brand", "PROD_001_ref", precheck=True)
    ids = {g["gate_id"] for g in rep["gates"]}
    assert "GATE_5" not in ids and "GATE_6" not in ids and rep["precheck"] is True


def test_gate5_fails_when_package_missing(tmp_path):
    proj = tmp_path / "Brand" / "04_IN_PRODUCTION" / "PROD_001_ref"
    (proj / "02_First_Frames").mkdir(parents=True)
    rep = UGCHarness.run_full_project_audit(tmp_path / "Brand", "PROD_001_ref")
    g5 = next(g for g in rep["gates"] if g["gate_id"] == "GATE_5")
    assert not g5["passed"] and "paquete" in g5["message"]


@pytest.mark.skipif(not FFMPEG, reason="ffmpeg no disponible")
def test_single_pass_trim_concat_duration_and_sync(tmp_path):
    from tools.assemble_project import build_trim_concat_cmd
    a, b = tmp_path / "a.mp4", tmp_path / "b.mp4"
    _make_clip(a, "540x960")
    _make_clip(b, "1080x1920")
    out = tmp_path / "out.mp4"
    cmd = build_trim_concat_cmd(FFMPEG, [(a, 0.2, 0.8), (b, 0.0, 0.5)], out, fps="30")
    subprocess.run(cmd, check=True, capture_output=True)
    info = subprocess.check_output(
        [shutil.which("ffprobe") or FFMPEG.replace("ffmpeg", "ffprobe"), "-v", "error", "-show_entries",
         "stream=codec_type,width,height,duration", "-of", "json", str(out)], text=True)
    streams = {s["codec_type"]: s for s in json.loads(info)["streams"]}
    assert (streams["video"]["width"], streams["video"]["height"]) == (1080, 1920)
    assert abs(float(streams["video"]["duration"]) - 1.1) < 0.1
    assert abs(float(streams["audio"]["duration"]) - float(streams["video"]["duration"])) < 0.1


def test_state_json_records_gates_and_phase(tmp_path):
    from tools.project_state import load_state, record_gates
    record_gates(tmp_path, [{"gate_id": f"GATE_{i}", "passed": True} for i in range(1, 8)])
    st = load_state(tmp_path)
    assert st["phase"] == "certificado" and len(st["gates"]) == 7


def test_precheck_never_certifies(tmp_path):
    from tools.project_state import load_state, record_gates
    record_gates(tmp_path, [{"gate_id": f"GATE_{i}", "passed": True} for i in range(1, 8)], precheck=True)
    assert load_state(tmp_path)["phase"] != "certificado"


def test_compiler_outfit_override_replaces_dna_wardrobe(tmp_path):
    import json
    from tools.prompt_compiler import _apply_outfit_override
    (tmp_path / "checkpoint1.json").write_text(json.dumps({"outfit": "a burgundy satin blouse."}), encoding="utf-8")
    dna = ('A stylist with a bob. She is wearing a dark navy silk blouse under a black apron with '
           '"Bennett Studio" embroidered in gold cursive. She is holding shears and a comb. Warm expression.')
    out = _apply_outfit_override(dna, tmp_path / "pkg.json")
    assert "burgundy satin blouse" in out and "navy" not in out and "apron" not in out
    assert "shears" not in out and "Warm expression." in out
    assert _apply_outfit_override(dna, tmp_path / "sub" / "x" / "pkg.json") == dna


def test_compiler_outfit_reads_as_natural_noun_phrase():
    from tools.prompt_compiler import _as_noun_phrase
    assert _as_noun_phrase("Burgundy satin blouse, gold hoop earrings, delicate gold necklace, ring.") ==         "a burgundy satin blouse, gold hoop earrings, delicate gold necklace, and a ring"
    assert _as_noun_phrase("a navy silk blouse and small earrings") == "a navy silk blouse and small earrings"
    assert _as_noun_phrase("Ivory silk blouse") == "an ivory silk blouse"


def _timeline(steps):
    return [{"t0": a, "t1": b, "ledger_row": "r01", "action": "Does a thing", "props": [], "dialogue": d}
            for a, b, d in steps]


def test_non_generable_clip_duration_fails_gate_2(tmp_path, package):
    package["chunks"][0]["recommended_duration_s"] = 7
    r = _run(tmp_path, package)["GATE_2"]
    assert not r.passed and any("no es generable" in d for d in r.details)


def test_generable_durations_pass_gate_2(tmp_path, package):
    for dur in (4, 6, 8):
        package["chunks"][0]["recommended_duration_s"] = dur
        assert _run(tmp_path, package)["GATE_2"].passed, dur


def test_clip_durations_can_be_overridden_in_checkpoint1(tmp_path, package):
    proj = tmp_path / "PROD_001_x"
    (proj / "02_First_Frames").mkdir(parents=True)
    (proj / "checkpoint1.json").write_text(json.dumps({"clip_durations": [5, 10]}), encoding="utf-8")
    package["chunks"][0]["recommended_duration_s"] = 10
    package["chunks"][0]["voiceover_clean_tts"] = "one two three four five six seven eight"
    package["chunks"][0]["word_count"] = 8
    f = proj / "02_First_Frames" / "p.json"
    f.write_text(json.dumps(package), encoding="utf-8")
    assert {r.gate_id: r for r in UGCHarness.audit_package_json(f)}["GATE_2"].passed


def test_step_over_wps_fails_even_when_clip_average_passes(tmp_path, package):
    # Clip de 8 s con 12 palabras (1.5 WPS de promedio) pero el paso 1 mete 10 palabras en 2 s (5 WPS).
    ch = package["chunks"][0]
    fast, slow = "one two three four five six seven eight nine ten", "eleven twelve"
    ch["voiceover_clean_tts"] = f"{fast} {slow}"
    ch["word_count"] = 12
    ch["action_timeline"] = _timeline([(0, 2, fast), (2, 8, slow)])
    r = _run(tmp_path, package)["GATE_2"]
    assert not r.passed and any("paso 0-2s" in d and "WPS" in d for d in r.details)


def test_steps_within_wps_pass(tmp_path, package):
    ch = package["chunks"][0]
    a, b = "this simple trick changed", "my mornings completely"
    ch["voiceover_clean_tts"] = f"{a} {b}"
    ch["word_count"] = 7
    ch["action_timeline"] = _timeline([(0, 4, a), (4, 8, b)])
    assert _run(tmp_path, package)["GATE_2"].passed
