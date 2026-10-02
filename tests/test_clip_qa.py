import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.clip_qa import analyze_chunk, run_qa


def _words(text, start, per_word=0.4):
    return [{"word": w, "start": round(start + i * per_word, 2), "end": round(start + (i + 1) * per_word - 0.05, 2)}
            for i, w in enumerate(text.split())]


S1, S2 = "put two drops of oil", "and rub it in gently"


def _chunk(dur=8):
    return {"chunk_id": 1, "recommended_duration_s": dur, "voiceover_clean_tts": f"{S1} {S2}",
            "action_timeline": [{"t0": 0, "t1": 4, "action": "a", "dialogue": S1},
                                {"t0": 4, "t1": 8, "action": "b", "dialogue": S2}]}


def test_clean_clip_has_no_issues():
    words = _words(S1, 0.0) + _words(S2, 4.0)
    r = analyze_chunk(_chunk(), words, 8.0)
    assert r["issues"] == [] and r["text_match"] == 1.0
    assert [s["heard_at"] for s in r["steps"]] == [0.0, 4.0]


def test_step_drift_is_reported_with_suggested_window():
    words = _words(S1, 0.0) + _words(S2, 2.6)        # 2º paso planeado en 4 s, se oye en 2.6 s
    r = analyze_chunk(_chunk(), words, 8.0)
    assert any("desfase -1.4s" in i for i in r["issues"])
    assert r["steps"][1]["drift_s"] == -1.4
    assert r["steps"][1]["suggested_window"][0] == 2.6


def test_real_duration_different_from_plan_is_flagged():
    words = _words(S1, 0.0) + _words(S2, 4.0)
    r = analyze_chunk(_chunk(dur=7), words, 8.0)
    assert any("duración real 8.0s ≠ planeada 7s" in i for i in r["issues"])


def test_text_mismatch_is_flagged():
    words = _words("totally different words here now", 0.0)
    r = analyze_chunk(_chunk(), words, 8.0)
    assert r["text_match"] < 0.9 and any("coincide solo" in i for i in r["issues"])


def test_missing_voice_is_flagged():
    r = analyze_chunk(_chunk(), [], 8.0)
    assert any("no se detectó voz" in i for i in r["issues"])


def test_voice_cut_at_clip_end_is_flagged():
    words = _words(S1, 0.0) + _words(S2, 5.0, per_word=0.5)   # termina en 7.45 s
    r = analyze_chunk(_chunk(), words, 7.5)
    assert any("posible corte" in i for i in r["issues"])


def test_chunk_without_timeline_uses_voiceover():
    ch = {"chunk_id": 2, "recommended_duration_s": 6, "voiceover_clean_tts": S1}
    r = analyze_chunk(ch, _words(S1, 0.0), 6.0)
    assert r["issues"] == [] and len(r["steps"]) == 1


def test_run_qa_writes_report_and_flags_missing_clip(tmp_path):
    proj = tmp_path / "PROD_001_x"
    (proj / "02_First_Frames").mkdir(parents=True)
    (proj / "03_Raw_Clips").mkdir()
    pkg = {"chunks": [_chunk(), {**_chunk(), "chunk_id": 2}]}
    (proj / "02_First_Frames" / "production_package_PROD_001.json").write_text(json.dumps(pkg), encoding="utf-8")
    (proj / "03_Raw_Clips" / "1.mp4").write_bytes(b"x")   # el clip 2 no existe

    def fake(path, language, model):
        return _words(S1, 0.0) + _words(S2, 4.0), 8.0

    report, ok = run_qa(proj, transcriber=fake)
    assert not ok
    assert report["chunks"][0]["issues"] == []
    assert "falta el clip 2.mp4" in report["chunks"][1]["issues"][0]
    assert json.loads((proj / "clip_qa_report.json").read_text(encoding="utf-8"))["ok"] is False
