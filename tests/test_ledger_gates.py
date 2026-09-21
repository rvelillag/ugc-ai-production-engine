import copy
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from test_harness import _chunk
from tools.schemas.production_package import ProductionPackage
from tools.prompt_compiler import compile_i2v_prompt, compile_package, time_marker
from tools.checkpoint1 import write_checkpoint
from tools.ledger import ledger_hash

D1 = "I stopped washing my hair with shampoo alone"
D2 = "and here is why it works"


def _ledger_chunk():
    ch = _chunk(1, f"{D1} {D2}", dur=8)
    ch["ledger_rows"] = ["r01", "r02"]
    ch["ref_window"] = [0, 8]
    ch["voiceover_reference"] = f"{D1} {D2}"
    ch["action_timeline"] = [
        {"t0": 0, "t1": 4, "ledger_row": "r01", "action": "Holds the bottle up to the camera",
         "props": ["bottle"], "dialogue": D1},
        {"t0": 4, "t1": 8, "ledger_row": "r02", "action": "Pours it into her palm",
         "props": ["bottle"], "dialogue": D2},
    ]
    return ch


def _package(chunks):
    return {
        "project_id": "PROD_001", "reference_video": "r.mp4", "reference_duration_s": 8.0,
        "topic": "t", "brand": "Glowlab", "avatar_name": "Avatar", "avatar_age": 47,
        "avatar_archetype": "x", "wardrobe_previous": "a", "wardrobe_assigned": "cream knit sweater",
        "audio_voice_direction_anchor": "v", "standard_skeleton_25_30s": "s", "chunks": chunks,
        "post_copy": {"cover_headline": "Stop Doing This Every Morning", "title": "t",
                      "caption": "c", "manychat_keyword": "GLOW", "hashtags": ["#a"]},
    }


def test_schema_accepts_action_timeline():
    pkg = ProductionPackage(**_package([_ledger_chunk()]))
    ch = pkg.chunks[0]
    assert ch.ledger_rows == ["r01", "r02"] and ch.action_timeline[1].t0 == 4
    assert tuple(ch.ref_window) == (0, 8)


def test_schema_legacy_chunk_still_valid():
    pkg = ProductionPackage(**_package([_chunk(1, "this simple trick changed my mornings completely")]))
    assert pkg.chunks[0].action_timeline == [] and pkg.chunks[0].ledger_rows == []


def test_time_marker_uses_en_dash_and_trims_zeros():
    assert time_marker(0, 4) == "0–4s"
    assert time_marker(3.5, 8.0) == "3.5–8s"


def test_compiled_prompt_follows_canonical_template():
    pkg = _package([_ledger_chunk()])
    prompt = compile_i2v_prompt(pkg, pkg["chunks"][0])
    assert prompt.startswith("Hyper-realistic vertical 9:16 smartphone UGC video. Use the canonical ")
    assert "Avatar, 47yo, wearing cream knit sweater" in prompt
    assert "Preserve her identity, clothing, lighting, environment, table position, props and camera style" in prompt
    assert "*ACTION:*" in prompt
    assert f'0–4s: Holds the bottle up to the camera, and says: "{D1}"' in prompt
    assert f'4–8s: Pours it into her palm, while continuing: "{D2}"' in prompt
    assert "Natural realistic hand movements. No cuts. No exaggerated acting." in prompt
    assert "*SFX:*" in prompt
    assert not any(w in prompt.lower().split() for w in ("age", "dm"))


def test_compile_package_rewrites_only_chunks_with_timeline(tmp_path):
    legacy = _chunk(2, "this simple trick changed my mornings completely")
    p = tmp_path / "p.json"
    p.write_text(json.dumps(_package([_ledger_chunk(), legacy])), encoding="utf-8")
    assert compile_package(p) == 1
    data = json.loads(p.read_text(encoding="utf-8"))
    assert "*ACTION:*" in data["chunks"][0]["video_motion_prompt_i2v"]
    assert data["chunks"][1]["video_motion_prompt_i2v"] == "she talks"


LEDGER = {"reference_video": "r.mp4", "duration_s": 8.0, "rows": [
    {"id": "r01", "t_start": 0, "t_end": 4, "dialogue_verbatim": D1, "action": "Holds the bottle up"},
    {"id": "r02", "t_start": 4, "t_end": 8, "dialogue_verbatim": D2, "action": "Pours into palm"},
]}


def _project(tmp_path, ledger=LEDGER):
    (tmp_path / "01_Reference").mkdir(exist_ok=True)
    if ledger is not None:
        (tmp_path / "01_Reference" / "reference_ledger.json").write_text(json.dumps(ledger), encoding="utf-8")
    return tmp_path


def test_checkpoint_records_ledger_hash_and_default_no_exaggeration(tmp_path):
    proj = _project(tmp_path)
    out = write_checkpoint(proj, "adapt_to_brand", "cream sweater", "GLOW", "Stop Doing This", ledger_confirmed=True)
    cp = json.loads(out.read_text(encoding="utf-8"))
    assert cp["ledger_hash"] == ledger_hash(proj / "01_Reference" / "reference_ledger.json")
    assert cp["hook_exaggeration"] is False


def test_checkpoint_hook_exaggeration_is_opt_in(tmp_path):
    proj = _project(tmp_path)
    out = write_checkpoint(proj, "adapt_to_brand", "o", "GLOW", "Stop Doing This", hook_exaggeration=True)
    assert json.loads(out.read_text(encoding="utf-8"))["hook_exaggeration"] is True


def test_checkpoint_ledger_confirmed_requires_valid_ledger(tmp_path):
    with pytest.raises(FileNotFoundError):
        write_checkpoint(_project(tmp_path, ledger=None), "adapt_to_brand", "o", "GLOW", "h", ledger_confirmed=True)


def test_checkpoint_without_ledger_flag_has_no_hash(tmp_path):
    out = write_checkpoint(_project(tmp_path), "adapt_to_brand", "o", "GLOW", "h")
    assert "ledger_hash" not in json.loads(out.read_text(encoding="utf-8"))


from tools.project_state import record_gates
from tools.prompt_compiler import compile_i2v_prompt as _compile
from tools.ugc_harness import UGCHarness


def _setup(tmp_path, chunks=None, ledger=None, confirm=True):
    """Crea proyecto con ledger, checkpoint1 (confirmado si confirm) y paquete compilado. Devuelve (json_path, project_dir)."""
    ledger = copy.deepcopy(ledger or LEDGER)
    proj = _project(tmp_path, ledger)
    if confirm:
        write_checkpoint(proj, "adapt_to_brand", "o", "GLOW", "Stop Doing This", ledger_confirmed=True)
    else:
        write_checkpoint(proj, "adapt_to_brand", "o", "GLOW", "Stop Doing This")
    pkg = _package(chunks if chunks is not None else [_ledger_chunk()])
    for ch in pkg["chunks"]:
        if ch.get("action_timeline"):
            ch["video_motion_prompt_i2v"] = _compile(pkg, ch)
    pj = tmp_path / "p.json"
    pj.write_text(json.dumps(pkg), encoding="utf-8")
    return pj, proj


def test_ledger_active_detection(tmp_path):
    assert not UGCHarness.ledger_active(tmp_path)
    _project(tmp_path)
    assert UGCHarness.ledger_active(tmp_path)


def test_gate8_passes_on_faithful_package(tmp_path):
    pj, proj = _setup(tmp_path)
    r = UGCHarness.audit_action_coverage(pj, proj)
    assert r.passed, r.details
    assert r.gate_id == "GATE_8"


def test_gate8_fails_when_ledger_row_not_covered(tmp_path):
    ledger = copy.deepcopy(LEDGER)
    ledger["duration_s"] = 12.0
    ledger["rows"].append({"id": "r03", "t_start": 8, "t_end": 12, "dialogue_verbatim": "", "action": "smiles"})
    pj, proj = _setup(tmp_path, ledger=ledger)
    r = UGCHarness.audit_action_coverage(pj, proj)
    assert not r.passed and any("r03" in d for d in r.details)


def test_gate8_fails_on_timeline_gap(tmp_path):
    ch = _ledger_chunk()
    ch["action_timeline"][1]["t0"] = 5
    pj, proj = _setup(tmp_path, chunks=[ch])
    r = UGCHarness.audit_action_coverage(pj, proj)
    assert not r.passed and any("hueco" in d.lower() or "solape" in d.lower() for d in r.details)


def test_gate8_fails_when_steps_out_of_ledger_order(tmp_path):
    ch = _ledger_chunk()
    ch["action_timeline"][0]["ledger_row"], ch["action_timeline"][1]["ledger_row"] = "r02", "r01"
    pj, proj = _setup(tmp_path, chunks=[ch])
    r = UGCHarness.audit_action_coverage(pj, proj)
    assert not r.passed and any("orden" in d.lower() for d in r.details)


def test_gate8_fails_when_step_ends_after_clip_duration(tmp_path):
    ch = _ledger_chunk()
    ch["recommended_duration_s"] = 6
    pj, proj = _setup(tmp_path, chunks=[ch])
    assert not UGCHarness.audit_action_coverage(pj, proj).passed


def test_gate8_fails_when_prompt_lacks_timeline_dialogue(tmp_path):
    pj, proj = _setup(tmp_path)
    pkg = json.loads(pj.read_text(encoding="utf-8"))
    pkg["chunks"][0]["video_motion_prompt_i2v"] = "she talks"
    pj.write_text(json.dumps(pkg), encoding="utf-8")
    assert not UGCHarness.audit_action_coverage(pj, proj).passed


def test_gate8_fails_when_ledger_edited_after_confirmation(tmp_path):
    pj, proj = _setup(tmp_path)
    lp = proj / "01_Reference" / "reference_ledger.json"
    data = json.loads(lp.read_text(encoding="utf-8"))
    data["rows"][0]["action"] = "sneakily changed"
    lp.write_text(json.dumps(data), encoding="utf-8")
    r = UGCHarness.audit_action_coverage(pj, proj)
    assert not r.passed and any("cambi" in d.lower() for d in r.details)


def test_gate8_fails_when_ledger_never_confirmed(tmp_path):
    pj, proj = _setup(tmp_path, confirm=False)
    assert not UGCHarness.audit_action_coverage(pj, proj).passed


def test_gate7_ledger_passes_verbatim_dialogue(tmp_path):
    pj, proj = _setup(tmp_path)
    r = UGCHarness.audit_ledger_dialogue(pj, proj)
    assert r.passed and r.gate_id == "GATE_7", r.details


def test_gate7_ledger_fails_paraphrased_dialogue(tmp_path):
    ch = _ledger_chunk()
    ch["action_timeline"][0]["dialogue"] = "I quit using regular shampoo by itself"
    ch["voiceover_clean_tts"] = "I quit using regular shampoo by itself " + D2
    ch["word_count"] = len(ch["voiceover_clean_tts"].split())
    pj, proj = _setup(tmp_path, chunks=[ch])
    r = UGCHarness.audit_ledger_dialogue(pj, proj)
    assert not r.passed and any("r01" in d for d in r.details)


def test_gate7_ledger_exempts_cta_rows(tmp_path):
    ledger = copy.deepcopy(LEDGER)
    ledger["rows"][1]["is_cta"] = True
    ch = _ledger_chunk()
    ch["action_timeline"][1]["dialogue"] = "Comment GLOW below for my routine"
    pj, proj = _setup(tmp_path, chunks=[ch], ledger=ledger)
    assert UGCHarness.audit_ledger_dialogue(pj, proj).passed


def test_record_gates_certifies_with_or_without_gate8(tmp_path):
    seven = [{"gate_id": f"GATE_{i}", "passed": True} for i in range(1, 8)]
    assert record_gates(tmp_path, seven)["phase"] == "certificado"
    p2 = tmp_path / "b"
    p2.mkdir()
    assert record_gates(p2, seven + [{"gate_id": "GATE_8", "passed": True}])["phase"] == "certificado"
    p3 = tmp_path / "c"
    p3.mkdir()
    assert record_gates(p3, seven + [{"gate_id": "GATE_8", "passed": False}])["phase"] != "certificado"


def test_gate8_malformed_data_does_not_raise(tmp_path):
    pj, proj = _setup(tmp_path)
    pkg = json.loads(pj.read_text(encoding="utf-8"))
    del pkg["chunks"][0]["action_timeline"][0]["t0"]
    pj.write_text(json.dumps(pkg), encoding="utf-8")
    r = UGCHarness.audit_action_coverage(pj, proj)
    assert not r.passed and any("t0" in d for d in r.details)

    ch2 = _ledger_chunk()
    ch2["action_timeline"][0]["t0"] = "0"
    ch2["chunk_id"] = None
    pkg = json.loads(pj.read_text(encoding="utf-8"))
    pkg["chunks"] = [ch2, "junk", {"chunk_id": 3, "ledger_rows": "r01", "action_timeline": [None, 5]}]
    pkg["chunks"].append({"chunk_id": 4, "ledger_rows": ["r01"], "action_timeline": [{"t0": 0, "t1": 1, "ledger_row": "r01"}],
                          "recommended_duration_s": None})
    pj.write_text(json.dumps(pkg), encoding="utf-8")
    assert not UGCHarness.audit_action_coverage(pj, proj).passed


def test_gate8_fails_when_t1_not_after_t0(tmp_path):
    ch = _ledger_chunk()
    ch["action_timeline"][0]["t1"] = 0
    pj, proj = _setup(tmp_path, chunks=[ch])
    assert not UGCHarness.audit_action_coverage(pj, proj).passed


def test_gate8_fails_on_blank_action(tmp_path):
    ch = _ledger_chunk()
    ch["action_timeline"][0]["action"] = "  "
    pj, proj = _setup(tmp_path, chunks=[ch])
    r = UGCHarness.audit_action_coverage(pj, proj)
    assert not r.passed and any("sin acci" in d for d in r.details)


def test_gate7_ledger_none_dialogue_does_not_raise(tmp_path):
    pj, proj = _setup(tmp_path)
    pkg = json.loads(pj.read_text(encoding="utf-8"))
    pkg["chunks"][0]["action_timeline"][0]["dialogue"] = None
    pkg["chunks"].append("junk")
    pj.write_text(json.dumps(pkg), encoding="utf-8")
    r = UGCHarness.audit_ledger_dialogue(pj, proj)
    assert not r.passed


def _brand_project(tmp_path, with_ledger):
    brand = tmp_path / "Brand"
    proj = brand / "04_IN_PRODUCTION" / "PROD_001_test"
    (proj / "02_First_Frames").mkdir(parents=True)
    if with_ledger:
        (tmp_path / "src").mkdir()
        pj, src = _setup(tmp_path / "src")
        import shutil
        shutil.copytree(src / "01_Reference", proj / "01_Reference")
        shutil.copy(src / "checkpoint1.json", proj / "checkpoint1.json")
        shutil.copy(pj, proj / "02_First_Frames" / "production_package_PROD_test.json")
    else:
        (proj / "01_Reference").mkdir()
    return brand


def test_run_full_audit_uses_ledger_gates(tmp_path):
    brand = _brand_project(tmp_path, True)
    rep = UGCHarness.run_full_project_audit(brand, "PROD_001_test", precheck=True)
    by = {g["gate_id"]: g for g in rep["gates"]}
    assert "GATE_8" in by and by["GATE_8"]["passed"], by.get("GATE_8")
    assert by["GATE_7"]["passed"] and "Ledger" in by["GATE_7"]["name"]


def test_run_full_audit_legacy_has_no_gate8(tmp_path):
    brand = _brand_project(tmp_path, False)
    rep = UGCHarness.run_full_project_audit(brand, "PROD_001_test", precheck=True)
    ids = {g["gate_id"] for g in rep["gates"]}
    assert "GATE_7" in ids and "GATE_8" not in ids
