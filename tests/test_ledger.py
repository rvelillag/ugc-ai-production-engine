import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.ledger import (Ledger, LedgerRow, anchor_times, build_draft_rows, fidelity,
                          ledger_hash, load_ledger, tokenize)


def _ledger_dict():
    return {"reference_video": "r.mp4", "duration_s": 8.0, "rows": [
        {"id": "r01", "t_start": 0, "t_end": 4, "dialogue_verbatim": "hello there", "action": "waves"},
        {"id": "r02", "t_start": 4, "t_end": 8, "dialogue_verbatim": "second row", "action": "points"},
    ]}


def test_row_rejects_non_positive_duration():
    with pytest.raises(ValueError):
        LedgerRow(id="r01", t_start=3, t_end=3)


def test_ledger_rejects_duplicate_ids():
    d = _ledger_dict()
    d["rows"][1]["id"] = "r01"
    with pytest.raises(ValueError):
        Ledger(**d)


def test_ledger_rejects_unordered_rows():
    d = _ledger_dict()
    d["rows"][0]["t_start"], d["rows"][0]["t_end"] = 5, 6
    with pytest.raises(ValueError):
        Ledger(**d)


def test_hash_ignores_whitespace_but_detects_edits(tmp_path):
    p = tmp_path / "l.json"
    p.write_text(json.dumps(_ledger_dict()), encoding="utf-8")
    h1 = ledger_hash(p)
    p.write_text(json.dumps(_ledger_dict(), indent=4), encoding="utf-8")
    assert ledger_hash(p) == h1
    d = _ledger_dict()
    d["rows"][0]["action"] = "changed"
    p.write_text(json.dumps(d), encoding="utf-8")
    assert ledger_hash(p) != h1


def test_load_ledger_roundtrip(tmp_path):
    p = tmp_path / "l.json"
    p.write_text(json.dumps(_ledger_dict()), encoding="utf-8")
    assert [r.id for r in load_ledger(p).rows] == ["r01", "r02"]


def test_tokenize_and_fidelity():
    assert tokenize("Don't stop, ÑOÑO!") == ["don't", "stop", "ñoño"]
    assert fidelity("one two three four", "one two three four") == 1.0
    assert fidelity("one two three four", "one two") == 0.5
    assert fidelity("", "anything") == 1.0


def _w(word, start, end):
    return {"word": word, "start": start, "end": end}


def test_draft_rows_split_on_pause_and_are_contiguous():
    words = [_w("hello", 0.5, 1.0), _w("there", 1.0, 1.5), _w("second", 2.5, 3.0), _w("row", 3.0, 3.5)]
    rows = build_draft_rows(words, duration_s=5.0)
    assert [(r.id, r.t_start, r.t_end) for r in rows] == [("r01", 0.0, 1.5), ("r02", 1.5, 5.0)]
    assert rows[0].dialogue_verbatim == "hello there"
    assert rows[1].dialogue_verbatim == "second row"


def test_draft_rows_split_on_max_len():
    words = [_w(f"w{i}", i, i + 1.0) for i in range(6)]
    rows = build_draft_rows(words, duration_s=6.0, max_len=4.0)
    assert len(rows) == 2 and len(rows[0].dialogue_verbatim.split()) == 4


def test_draft_rows_without_words_is_single_silent_row():
    rows = build_draft_rows([], duration_s=7.0)
    assert len(rows) == 1 and (rows[0].t_start, rows[0].t_end) == (0.0, 7.0)


def test_anchor_times(tmp_path):
    p = tmp_path / "l.json"
    assert anchor_times(p) == []
    p.write_text(json.dumps(_ledger_dict()), encoding="utf-8")
    assert anchor_times(p) == [0.0, 4.0]
