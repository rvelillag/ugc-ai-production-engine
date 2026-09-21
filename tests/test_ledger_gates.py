import copy
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from test_harness import _chunk
from tools.schemas.production_package import ProductionPackage
from tools.prompt_compiler import compile_i2v_prompt, compile_package, time_marker

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
