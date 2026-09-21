import copy
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from test_harness import _chunk
from tools.schemas.production_package import ProductionPackage

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
