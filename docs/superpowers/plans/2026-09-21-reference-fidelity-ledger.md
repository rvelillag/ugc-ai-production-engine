# Reference Fidelity Ledger Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make generated prompts preserve every action and (≥85 %) of the dialogue of the reference video, changing only avatar/outfit/scenario.

**Architecture:** A confirmed `reference_ledger.json` is the source of truth. Chunks map to ledger rows through an `action_timeline`; the I2V prompt is compiled from that timeline; GATE_7 (dialogue) and the new GATE_8 (action coverage) verify it. All new schema fields are optional and the gates fall back to legacy behavior when no ledger exists.

**Tech Stack:** Python 3, Pydantic v2, pytest, faster-whisper, ffmpeg/ffprobe.

**Spec:** `docs/superpowers/specs/2026-09-21-reference-fidelity-ledger-design.md`

## Global Constraints

- Windows: every Python script that prints must keep UTF-8 output (`sys.stdout.reconfigure(encoding="utf-8")` guarded by `hasattr`), as the existing tools do.
- Never use the words `age`/`DM` in generated prompts or scripts (GATE_3). Use `47yo`-style apparent years.
- Existing 39 tests in `tests/` must keep passing; legacy packages (no ledger) must behave exactly as before.
- Keep `01_Reference/` clean: only the video, `01_`–`10_` keyframes, `script_beats_*.txt`, and the new `reference_ledger.json`.
- Clip duration ≤ 10 s; WPS ≤ 2.4 (unchanged).
- Dialogue fidelity threshold: 0.85 (`UGCHarness.MIN_DIALOGUE_FIDELITY`).
- Run tests with `python -m pytest tests -q` from the repo root `C:\Users\Asus\Downloads\DTC`.

---

### Task 1: Ledger model, hashing, fidelity, draft builder

**Files:**
- Create: `tools/ledger.py`
- Test: `tests/test_ledger.py`

**Interfaces:**
- Produces (used by Tasks 2, 5, 6, 7):
  - `LEDGER_FILE = "reference_ledger.json"`
  - `class LedgerRow(BaseModel)`: `id: str, t_start: float, t_end: float, dialogue_verbatim: str = "", action: str = "", framing: str = "", props: List[str] = [], gaze: str = "", gesture: str = "", is_cta: bool = False`
  - `class Ledger(BaseModel)`: `reference_video: str, duration_s: float, language: str = "en", rows: List[LedgerRow]`
  - `load_ledger(path: Path) -> Ledger`
  - `ledger_hash(path: Path) -> str`
  - `tokenize(text: str) -> List[str]`
  - `fidelity(ref_text: str, gen_text: str) -> float`
  - `build_draft_rows(words: List[dict], duration_s: float, max_gap: float = 0.6, max_len: float = 4.0) -> List[LedgerRow]`
  - `anchor_times(ledger_path: Path) -> List[float]`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_ledger.py
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
```

- [ ] **Step 2: Run to verify failure**

Run: `python -m pytest tests/test_ledger.py -q`
Expected: FAIL (`ModuleNotFoundError: No module named 'tools.ledger'`).

- [ ] **Step 3: Implement `tools/ledger.py`**

```python
"""Ledger de referencia: acciones y diálogo literal del video original, en orden temporal."""
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import List

from pydantic import BaseModel, Field, model_validator

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

LEDGER_FILE = "reference_ledger.json"


class LedgerRow(BaseModel):
    id: str
    t_start: float = Field(..., ge=0)
    t_end: float
    dialogue_verbatim: str = ""
    action: str = ""
    framing: str = ""
    props: List[str] = Field(default_factory=list)
    gaze: str = ""
    gesture: str = ""
    is_cta: bool = False

    @model_validator(mode="after")
    def _positive_duration(self):
        if self.t_end <= self.t_start:
            raise ValueError(f"fila {self.id}: t_end debe ser mayor que t_start")
        return self


class Ledger(BaseModel):
    reference_video: str
    duration_s: float
    language: str = "en"
    rows: List[LedgerRow]

    @model_validator(mode="after")
    def _ordered_unique(self):
        ids = [r.id for r in self.rows]
        if len(set(ids)) != len(ids):
            raise ValueError("ids de fila duplicados en el ledger")
        starts = [r.t_start for r in self.rows]
        if starts != sorted(starts):
            raise ValueError("las filas del ledger deben estar ordenadas por t_start")
        return self


def load_ledger(path: Path) -> Ledger:
    return Ledger(**json.loads(Path(path).read_text(encoding="utf-8")))


def ledger_hash(path: Path) -> str:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    canon = json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()


def tokenize(text: str) -> List[str]:
    return re.findall(r"[a-záéíóúñü']+", text.lower())


def fidelity(ref_text: str, gen_text: str) -> float:
    """Fracción de las palabras de la referencia que se conservan en el texto generado (con multiplicidad)."""
    ref, gen = Counter(tokenize(ref_text)), Counter(tokenize(gen_text))
    total = sum(ref.values())
    if not total:
        return 1.0
    return sum((ref & gen).values()) / total


def build_draft_rows(words: List[dict], duration_s: float, max_gap: float = 0.6, max_len: float = 4.0) -> List[LedgerRow]:
    """Agrupa palabras de Whisper en filas por pausas; las filas cubren [0, duration_s] sin huecos."""
    groups, cur = [], []
    for w in words:
        if cur and (w["start"] - cur[-1]["end"] >= max_gap or w["end"] - cur[0]["start"] > max_len):
            groups.append(cur)
            cur = []
        cur.append(w)
    if cur:
        groups.append(cur)
    if not groups:
        return [LedgerRow(id="r01", t_start=0.0, t_end=duration_s)]
    rows, prev_end = [], 0.0
    for i, g in enumerate(groups):
        end = duration_s if i == len(groups) - 1 else g[-1]["end"]
        end = max(end, round(prev_end + 0.1, 2))
        rows.append(LedgerRow(id=f"r{i + 1:02d}", t_start=prev_end, t_end=end,
                              dialogue_verbatim=" ".join(x["word"] for x in g)))
        prev_end = end
    return rows


def anchor_times(ledger_path: Path) -> List[float]:
    """t_start de cada fila del ledger, o [] si no existe."""
    path = Path(ledger_path)
    if not path.exists():
        return []
    return [r.t_start for r in load_ledger(path).rows]
```

- [ ] **Step 4: Run to verify pass**

Run: `python -m pytest tests/test_ledger.py -q`
Expected: 10 passed.

- [ ] **Step 5: Commit**

```bash
git add tools/ledger.py tests/test_ledger.py
git commit -m "feat(ledger): reference ledger model, hash, fidelity and draft builder"
```

---

### Task 2: `reference_ledger.py` CLI (Whisper + contact frames → draft ledger)

**Files:**
- Create: `tools/reference_ledger.py`

**Interfaces:**
- Consumes: `tools.ledger.{Ledger, LEDGER_FILE, build_draft_rows}`, `tools.checkpoint1.find_project(name_or_path, base_dir) -> Path`
- Produces: CLI `python tools/reference_ledger.py --project PROD_XXX_ref [--language en] [--model medium] [--fps 2] [--force]`; writes `01_Reference/reference_ledger.json` and prints the temp directory with contact frames (`f_0001.jpg` is at t = (n-1)/fps).

This task is a thin I/O wrapper around tested code (Task 1); it is verified by a smoke test, not a unit test.

- [ ] **Step 1: Write the script**

```python
"""Genera el borrador del ledger de referencia: diálogo literal (Whisper) + frames de contacto para describir acciones."""
import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.checkpoint1 import find_project
from tools.ledger import LEDGER_FILE, Ledger, build_draft_rows


def _duration(video: Path) -> float:
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(video)], text=True)
    return float(out.strip())


def make_draft(project_dir: Path, language, model_size: str, fps: float, force: bool) -> Path:
    ref_dir = project_dir / "01_Reference"
    videos = sorted(ref_dir.glob("*.mp4"))
    if not videos:
        raise FileNotFoundError(f"No hay .mp4 en {ref_dir}")
    out = ref_dir / LEDGER_FILE
    if out.exists() and not force:
        raise FileExistsError(f"{out} ya existe (usa --force para regenerar; invalida el Checkpoint 1)")
    video = videos[0]
    duration = _duration(video)

    from faster_whisper import WhisperModel
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    segments, info = model.transcribe(str(video), word_timestamps=True, language=language)
    words = [{"word": w.word.strip(), "start": round(w.start, 2), "end": round(w.end, 2)}
             for s in segments for w in (s.words or [])]

    ledger = Ledger(reference_video=video.name, duration_s=round(duration, 2),
                    language=info.language, rows=build_draft_rows(words, duration))
    out.write_text(ledger.model_dump_json(indent=2), encoding="utf-8")

    frames_dir = Path(tempfile.mkdtemp(prefix="ledger_frames_"))
    subprocess.run(["ffmpeg", "-y", "-i", str(video), "-vf", f"fps={fps}", "-q:v", "3",
                    str(frames_dir / "f_%04d.jpg")], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    print(f"Borrador del ledger: {out} ({len(ledger.rows)} filas, {len(words)} palabras)")
    print(f"Frames de contacto (f_0001.jpg = t 0s; t = (n-1)/{fps}): {frames_dir}")
    print("Siguiente paso: describir action/framing/props/gaze/gesture de cada fila viendo los frames y marcar is_cta.")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Crea el borrador de reference_ledger.json")
    ap.add_argument("--project", required=True)
    ap.add_argument("--language", default=None, help="Código de idioma del audio (en/es); auto si se omite")
    ap.add_argument("--model", default="medium", help="Modelo faster-whisper (base/small/medium)")
    ap.add_argument("--fps", type=float, default=2.0)
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    base = Path(__file__).resolve().parent.parent
    make_draft(find_project(a.project, base), a.language, a.model, a.fps, a.force)
```

- [ ] **Step 2: Smoke test**

Run: `python tools/reference_ledger.py --help`
Expected: usage text, exit 0.

If a project with a reference video exists (`Sofia Torres - GlowLab/04_IN_PRODUCTION/PROD_*/01_Reference/*.mp4`), run on a copy in a temp project folder with `--model base` and verify it writes a valid ledger (`python -c "from tools.ledger import load_ledger; print(len(load_ledger('<path>').rows))"`). Delete the temp copy afterwards. Do not leave a ledger in an existing project.

- [ ] **Step 3: Commit**

```bash
git add tools/reference_ledger.py
git commit -m "feat(ledger): reference_ledger.py drafts ledger from Whisper words and contact frames"
```

---

### Task 3: Schema — action timeline fields on `ChunkItem`

**Files:**
- Modify: `tools/schemas/production_package.py` (add `ActionStep`; extend `ChunkItem`; update imports)
- Test: `tests/test_ledger_gates.py` (created here, extended in Tasks 4–6)

**Interfaces:**
- Produces: `ActionStep(t0: float, t1: float, ledger_row: str, action: str, props: List[str] = [], dialogue: str = "")`; `ChunkItem` gains `ledger_rows: List[str] = []`, `ref_window: Optional[Tuple[float, float]] = None`, `action_timeline: List[ActionStep] = []`, `voiceover_reference: str = ""`, `sfx: str = ""`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_ledger_gates.py
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
```

- [ ] **Step 2: Run to verify failure**

Run: `python -m pytest tests/test_ledger_gates.py -q`
Expected: FAIL (`AttributeError`/`ledger_rows` missing on `ChunkItem`).

- [ ] **Step 3: Edit `tools/schemas/production_package.py`**

Change the first import line to:

```python
from typing import List, Optional, Dict, Any, Tuple
```

Add before `class ChunkItem`:

```python
class ActionStep(BaseModel):
    t0: float = Field(..., ge=0, description="Inicio del paso dentro del clip (s)")
    t1: float = Field(..., description="Fin del paso dentro del clip (s)")
    ledger_row: str = Field(..., description="Id de la fila del ledger de referencia que replica")
    action: str = Field(..., min_length=1, description="Acción física exacta (misma que la referencia)")
    props: List[str] = Field(default_factory=list)
    dialogue: str = ""
```

Add to the end of `ChunkItem` (after `continuity_notes: str`):

```python
    ledger_rows: List[str] = Field(default_factory=list, description="Ids del ledger que cubre este chunk")
    ref_window: Optional[Tuple[float, float]] = Field(None, description="Ventana [t0, t1] de la referencia que reemplaza")
    action_timeline: List[ActionStep] = Field(default_factory=list)
    voiceover_reference: str = Field("", description="Diálogo original literal del segmento")
    sfx: str = Field("", description="Capa acústica/Foley del clip")
```

- [ ] **Step 4: Run all tests**

Run: `python -m pytest tests -q`
Expected: all pass (39 old + 10 ledger + 2 new).

- [ ] **Step 5: Commit**

```bash
git add tools/schemas/production_package.py tests/test_ledger_gates.py
git commit -m "feat(schema): optional ledger_rows, ref_window and action_timeline on ChunkItem"
```

---

### Task 4: Prompt compiler

**Files:**
- Create: `tools/prompt_compiler.py`
- Test: `tests/test_ledger_gates.py` (append)

**Interfaces:**
- Consumes: package/chunk dicts shaped as in Task 3.
- Produces (used by Task 6): `time_marker(t0: float, t1: float) -> str` (e.g. `"0–4s"`), `compile_i2v_prompt(pkg: dict, chunk: dict) -> str`, `compile_package(json_path: Path) -> int` (rewrites `video_motion_prompt_i2v` of every chunk that has an `action_timeline`; returns how many). CLI: `python tools/prompt_compiler.py --json <production_package.json>`.

- [ ] **Step 1: Append failing tests to `tests/test_ledger_gates.py`**

```python
from tools.prompt_compiler import compile_i2v_prompt, compile_package, time_marker


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
```

- [ ] **Step 2: Run to verify failure**

Run: `python -m pytest tests/test_ledger_gates.py -q`
Expected: FAIL (`No module named 'tools.prompt_compiler'`).

- [ ] **Step 3: Implement `tools/prompt_compiler.py`**

```python
"""Compila video_motion_prompt_i2v desde el action_timeline (plantilla canónica de CLAUDE.md, Fase 3 punto 6)."""
import argparse
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REALISM = "Natural realistic hand movements. No cuts. No exaggerated acting."
DEFAULT_SFX = "Natural room ambience with subtle sounds of the props being handled."


def time_marker(t0: float, t1: float) -> str:
    return f"{t0:g}–{t1:g}s"


def compile_i2v_prompt(pkg: dict, chunk: dict) -> str:
    env = chunk["composition_audit"]["environment_background"].rstrip(".")
    header = (
        f"Hyper-realistic vertical 9:16 smartphone UGC video. Use the canonical {env}. "
        f"{pkg['avatar_name']}, {pkg['avatar_age']}yo, wearing {pkg['wardrobe_assigned']}. "
        "Preserve her identity, clothing, lighting, environment, table position, props and camera style "
        "throughout the entire clip."
    )
    lines = ["*ACTION:*"]
    spoke = False
    for step in chunk["action_timeline"]:
        line = f"{time_marker(step['t0'], step['t1'])}: {step['action'].rstrip('.')}"
        if step.get("dialogue"):
            line += f', {"while continuing" if spoke else "and says"}: "{step["dialogue"]}"'
            spoke = True
        lines.append(line)
    sfx = chunk.get("sfx") or DEFAULT_SFX
    return "\n\n".join([header, "\n\n".join(lines), REALISM, f"*SFX:* {sfx}"])


def compile_package(json_path: Path) -> int:
    path = Path(json_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    count = 0
    for chunk in data.get("chunks", []):
        if chunk.get("action_timeline"):
            chunk["video_motion_prompt_i2v"] = compile_i2v_prompt(data, chunk)
            count += 1
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return count


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Compila los prompts I2V desde el action_timeline de cada chunk")
    ap.add_argument("--json", required=True, help="production_package_PROD_XXX.json")
    n = compile_package(Path(ap.parse_args().json))
    print(f"Prompts I2V compilados: {n}")
```

- [ ] **Step 4: Run to verify pass**

Run: `python -m pytest tests/test_ledger_gates.py -q`
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add tools/prompt_compiler.py tests/test_ledger_gates.py
git commit -m "feat(prompts): compile I2V motion prompts from the action timeline"
```

---

### Task 5: Checkpoint 1 records ledger hash and hook-exaggeration opt-in

**Files:**
- Modify: `tools/checkpoint1.py` (`write_checkpoint` signature + CLI flags + imports)
- Test: `tests/test_ledger_gates.py` (append)

**Interfaces:**
- Consumes: `tools.ledger.{LEDGER_FILE, ledger_hash, load_ledger}`
- Produces: `write_checkpoint(project_dir, scene_mode, outfit, keyword, headline, ledger_confirmed: bool = False, hook_exaggeration: bool = False) -> Path`. `checkpoint1.json` gains `ledger_hash` (only when `ledger_confirmed`) and `hook_exaggeration` (always). CLI flags `--ledger-confirmed` and `--hook-exaggeration`.

- [ ] **Step 1: Append failing tests**

```python
from tools.checkpoint1 import write_checkpoint
from tools.ledger import ledger_hash

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
```

- [ ] **Step 2: Run to verify failure**

Run: `python -m pytest tests/test_ledger_gates.py -q`
Expected: FAIL (`unexpected keyword argument 'ledger_confirmed'`).

- [ ] **Step 3: Edit `tools/checkpoint1.py`**

Under `from tools.project_state import save_state` add:

```python
from tools.ledger import LEDGER_FILE, ledger_hash, load_ledger
```

Replace the `write_checkpoint` signature and the tail so it reads:

```python
def write_checkpoint(project_dir: Path, scene_mode: str, outfit: str, keyword: str, headline: str,
                     ledger_confirmed: bool = False, hook_exaggeration: bool = False) -> Path:
    if scene_mode not in SCENE_MODES:
        raise ValueError(f"scene_mode debe ser uno de {SCENE_MODES}")
    if len(headline.split()) > 7:
        raise ValueError(f"cover_headline excede 7 palabras ({len(headline.split())})")
    if not all(v.strip() for v in (outfit, keyword, headline)):
        raise ValueError("outfit, keyword y headline no pueden estar vacíos")
    data = {
        "scene_mode": scene_mode,
        "outfit": outfit.strip(),
        "manychat_keyword": keyword.strip(),
        "cover_headline": headline.strip(),
        "hook_exaggeration": bool(hook_exaggeration),
        "confirmed_by_user": True,
        "confirmed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    if ledger_confirmed:
        ledger_path = Path(project_dir) / "01_Reference" / LEDGER_FILE
        if not ledger_path.exists():
            raise FileNotFoundError(f"Falta {ledger_path}: genera y completa el ledger antes de confirmarlo")
        load_ledger(ledger_path)  # valida el esquema
        data["ledger_hash"] = ledger_hash(ledger_path)
    out = project_dir / CHECKPOINT_FILE
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    save_state(project_dir, phase="checkpoint1")
    return out
```

In the CLI block, after `--headline` add:

```python
    parser.add_argument("--ledger-confirmed", action="store_true",
                        help="El usuario confirmó el reference_ledger.json (guarda su hash)")
    parser.add_argument("--hook-exaggeration", action="store_true",
                        help="Opt-in: el usuario pidió exagerar el disparador del hook (por defecto: acción idéntica a la referencia)")
```

and change the final call to:

```python
    path = write_checkpoint(find_project(args.project, base), args.scene, args.outfit, args.keyword, args.headline,
                            ledger_confirmed=args.ledger_confirmed, hook_exaggeration=args.hook_exaggeration)
```

- [ ] **Step 4: Run all tests**

Run: `python -m pytest tests -q`
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add tools/checkpoint1.py tests/test_ledger_gates.py
git commit -m "feat(checkpoint1): record ledger hash and hook-exaggeration opt-in"
```

---

### Task 6: Harness — ledger-based GATE_7 and new GATE_8

**Files:**
- Modify: `tools/ugc_harness.py` (imports, constants, three new static methods, `run_full_project_audit`, header docstring/CLI help text)
- Modify: `tools/project_state.py:40` (`record_gates` certification condition)
- Test: `tests/test_ledger_gates.py` (append)

**Interfaces:**
- Consumes: `tools.ledger.{LEDGER_FILE, fidelity, ledger_hash, load_ledger, tokenize}`, `tools.prompt_compiler.time_marker`
- Produces:
  - `UGCHarness.MIN_DIALOGUE_FIDELITY = 0.85`, `UGCHarness.TIME_TOLERANCE_S = 0.05`
  - `UGCHarness.ledger_active(project_dir: Path) -> bool`
  - `UGCHarness.audit_ledger_dialogue(json_path: Path, project_dir: Path) -> HarnessGateResult` (id `GATE_7`)
  - `UGCHarness.audit_action_coverage(json_path: Path, project_dir: Path) -> HarnessGateResult` (id `GATE_8`)
  - `run_full_project_audit` uses the ledger GATE_7 + GATE_8 when `ledger_active`, else legacy GATE_7 only.
  - `record_gates` certifies when GATE_1..GATE_7 are all present and every recorded gate passed.

- [ ] **Step 1: Append failing tests**

```python
from tools.checkpoint1 import write_checkpoint  # noqa: F811  (already imported above; kept for clarity)
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
```

- [ ] **Step 2: Run to verify failure**

Run: `python -m pytest tests/test_ledger_gates.py -q`
Expected: FAIL (`ledger_active` / `audit_action_coverage` missing).

- [ ] **Step 3: Edit `tools/project_state.py`**

Replace line `    if not precheck and len(merged) == 7 and all(merged.values()):` with:

```python
    required = {f"GATE_{i}" for i in range(1, 8)}
    if not precheck and required <= set(merged) and all(merged.values()):
```

- [ ] **Step 4: Edit `tools/ugc_harness.py`**

Add imports below `from tools.project_state import record_gates`:

```python
from tools.ledger import LEDGER_FILE, fidelity, ledger_hash, load_ledger, tokenize
from tools.prompt_compiler import time_marker
```

Update the class docstring line to `... contra los 8 Quality Gates (GATE_8 solo si hay ledger de referencia).`

Insert these members immediately before `@classmethod def run_full_project_audit`:

```python
    MIN_DIALOGUE_FIDELITY = 0.85
    TIME_TOLERANCE_S = 0.05

    @staticmethod
    def ledger_active(project_dir: Path) -> bool:
        """True si el proyecto usa ledger de referencia (archivo presente o hash registrado en checkpoint1.json)."""
        if (Path(project_dir) / "01_Reference" / LEDGER_FILE).exists():
            return True
        try:
            cp = json.loads((Path(project_dir) / "checkpoint1.json").read_text(encoding="utf-8"))
            return bool(cp.get("ledger_hash"))
        except Exception:
            return False

    @staticmethod
    def audit_ledger_dialogue(json_path: Path, project_dir: Path) -> HarnessGateResult:
        """GATE_7 con ledger: cada fila (salvo CTA) conserva >= 85% de sus palabras en los pasos que la replican."""
        name = "Reference Fidelity (Ledger, dialogue verbatim)"
        try:
            ledger = load_ledger(Path(project_dir) / "01_Reference" / LEDGER_FILE)
            chunks = json.loads(Path(json_path).read_text(encoding="utf-8")).get("chunks", [])
        except Exception as e:
            return HarnessGateResult("GATE_7", name, False, f"No se pudo leer el ledger o el paquete: {e}")
        errors, details = [], []
        for row in ledger.rows:
            if row.is_cta or not tokenize(row.dialogue_verbatim):
                continue
            gen = " ".join(s.get("dialogue", "") for ch in chunks for s in ch.get("action_timeline", [])
                           if s.get("ledger_row") == row.id)
            score = fidelity(row.dialogue_verbatim, gen)
            details.append(f"{row.id}: {score:.2f} de las palabras conservadas (mínimo {UGCHarness.MIN_DIALOGUE_FIDELITY:.2f})")
            if score < UGCHarness.MIN_DIALOGUE_FIDELITY:
                errors.append(f"Error: {row.id} se aleja del diálogo literal de la referencia.")
        passed = not errors
        return HarnessGateResult(
            "GATE_7", name, passed,
            "Diálogo fiel a la referencia" if passed else "El diálogo se aleja de la referencia",
            details + errors)

    @staticmethod
    def audit_action_coverage(json_path: Path, project_dir: Path) -> HarnessGateResult:
        """GATE_8: cada fila del ledger está cubierta, en orden, con timeline contiguo y reflejada en el prompt."""
        name = "Action Coverage (Ledger)"
        project_dir = Path(project_dir)
        ledger_path = project_dir / "01_Reference" / LEDGER_FILE
        try:
            ledger = load_ledger(ledger_path)
            pkg = json.loads(Path(json_path).read_text(encoding="utf-8"))
            cp = json.loads((project_dir / "checkpoint1.json").read_text(encoding="utf-8"))
        except Exception as e:
            return HarnessGateResult("GATE_8", name, False, f"No se pudo leer ledger, paquete o checkpoint1.json: {e}")

        tol = UGCHarness.TIME_TOLERANCE_S
        errors = []
        confirmed = cp.get("ledger_hash")
        if not confirmed:
            errors.append("El ledger no está confirmado en Checkpoint 1 (falta ledger_hash; usa --ledger-confirmed).")
        elif confirmed != ledger_hash(ledger_path):
            errors.append("El ledger cambió después de confirmarlo en Checkpoint 1; vuelve a confirmarlo.")

        order = {r.id: n for n, r in enumerate(ledger.rows)}
        covered, last_order = set(), -1
        for ch in pkg.get("chunks", []):
            cid = ch.get("chunk_id")
            rows, steps = ch.get("ledger_rows", []), ch.get("action_timeline", [])
            if not rows or not steps:
                errors.append(f"Chunk {cid}: falta ledger_rows o action_timeline.")
                continue
            for rid in rows:
                if rid not in order:
                    errors.append(f"Chunk {cid}: ledger_rows contiene '{rid}', que no existe en el ledger.")
            prompt = ch.get("video_motion_prompt_i2v", "")
            prev_t1, step_rows = 0.0, set()
            for s in steps:
                t0, t1, rid = s.get("t0", 0), s.get("t1", 0), s.get("ledger_row")
                if t1 <= t0:
                    errors.append(f"Chunk {cid}: paso {rid} con t1 <= t0.")
                if abs(t0 - prev_t1) > tol:
                    errors.append(f"Chunk {cid}: hueco o solape en el timeline ({prev_t1:g}s -> {t0:g}s).")
                prev_t1 = t1
                if rid not in rows or rid not in order:
                    errors.append(f"Chunk {cid}: el paso '{rid}' no está en los ledger_rows del chunk/ledger.")
                    continue
                step_rows.add(rid)
                covered.add(rid)
                if order[rid] < last_order:
                    errors.append(f"Chunk {cid}: pasos fuera de orden respecto al ledger ({rid}).")
                last_order = max(last_order, order[rid])
                if not str(s.get("action", "")).strip():
                    errors.append(f"Chunk {cid}: paso {rid} sin acción.")
                if time_marker(t0, t1) not in prompt:
                    errors.append(f"Chunk {cid}: el prompt no contiene el marcador {time_marker(t0, t1)} (recompila con tools/prompt_compiler.py).")
                if s.get("dialogue") and s["dialogue"] not in prompt:
                    errors.append(f"Chunk {cid}: el prompt no contiene el diálogo del paso {rid}.")
            if prev_t1 > ch.get("recommended_duration_s", 0) + tol:
                errors.append(f"Chunk {cid}: el timeline termina en {prev_t1:g}s, más allá de la duración del clip.")
            for rid in set(rows) - step_rows:
                errors.append(f"Chunk {cid}: la fila {rid} está en ledger_rows pero ningún paso la replica.")

        missing = [r.id for r in ledger.rows if r.id not in covered]
        if missing:
            errors.append(f"Filas del ledger sin cubrir: {missing}")
        passed = not errors
        details = errors or [f"Las {len(ledger.rows)} filas del ledger están cubiertas, en orden y con timeline contiguo."]
        return HarnessGateResult(
            "GATE_8", name, passed,
            "Todas las acciones de la referencia están cubiertas" if passed else "Acciones de la referencia sin cubrir o timeline inválido",
            details)

```

In `run_full_project_audit`, replace the Gate 7 block

```python
        # Gate 7 (regla 70/30: extensión y sentido de la referencia)
        all_gates.append(cls.audit_reference_fidelity(json_path, prod_dir / "01_Reference"))
```

with:

```python
        # Gate 7 (+ Gate 8 con ledger): fidelidad a la referencia
        if cls.ledger_active(prod_dir):
            all_gates.append(cls.audit_ledger_dialogue(json_path, prod_dir))
            all_gates.append(cls.audit_action_coverage(json_path, prod_dir))
        else:
            all_gates.append(cls.audit_reference_fidelity(json_path, prod_dir / "01_Reference"))
```

Update the `--precheck` help string to `"Corre solo los gates 1-4, 7 y 8 (sin clips ni entregables) ..."` (keep the rest of the sentence).

- [ ] **Step 5: Run all tests**

Run: `python -m pytest tests -q`
Expected: all pass (existing 39 unchanged).

- [ ] **Step 6: Commit**

```bash
git add tools/ugc_harness.py tools/project_state.py tests/test_ledger_gates.py
git commit -m "feat(harness): ledger-based GATE_7 dialogue fidelity and new GATE_8 action coverage"
```

---

### Task 7: Keyframe extractor stops faking actions and uses ledger anchors

**Files:**
- Modify: `tools/scene_keyframe_extractor.py`

**Interfaces:**
- Consumes: `tools.ledger.{LEDGER_FILE, anchor_times}` (tested in Task 1)
- Produces: `extract_scenes_and_cadence(video_path, output_dir=None, model_size="medium", language=None)`; CLI flags `--model`, `--language`.

- [ ] **Step 1: Edit imports** — after `from faster_whisper import WhisperModel` add:

```python
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.ledger import LEDGER_FILE, anchor_times
```

(`sys.path.insert` must run before the import; keep the existing `sys.stdout.reconfigure` line where it is.)

- [ ] **Step 2: Edit signature and Whisper call**

```python
def extract_scenes_and_cadence(video_path: Path, output_dir: Path = None, model_size: str = "medium", language: str = None):
```
```python
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    segments, info = model.transcribe(str(video_path), word_timestamps=True, language=language)
```

- [ ] **Step 3: Replace the fallback anchors** — replace the block `if len(cut_timestamps) < 4:` … through its closing `]` with:

```python
    # Few genuine cuts (typical single-take UGC): prefer the ledger's action boundaries over arbitrary percentages
    if len(cut_timestamps) < 4:
        anchors = anchor_times(output_dir / LEDGER_FILE)
        if len(anchors) >= 4:
            cut_timestamps = anchors
        else:
            cut_timestamps = [
                0.0,
                round(total_duration * 0.18, 2),
                round(total_duration * 0.36, 2),
                round(total_duration * 0.54, 2),
                round(total_duration * 0.72, 2),
                round(total_duration * 0.88, 2)
            ]
```

- [ ] **Step 4: Replace the fake action line** — replace

```python
* Acción y Encuadre: Plano correspondiente al corte visual detectado en {start_t:.2f}s.
```

with

```python
* Acción y Encuadre: (no se infiere del corte; se documenta en {LEDGER_FILE})
```

- [ ] **Step 5: Edit CLI** — add before `args = parser.parse_args()`:

```python
    parser.add_argument("--model", default="medium", help="Modelo faster-whisper (base/small/medium)")
    parser.add_argument("--language", default=None, help="Idioma del audio (en/es); auto si se omite")
```

and change the last line to `extract_scenes_and_cadence(video, out, model_size=args.model, language=args.language)`.

- [ ] **Step 6: Verify**

Run: `python tools/scene_keyframe_extractor.py --help` → shows `--model` and `--language`, exit 0.
Run: `python -m pytest tests -q` → all pass.

- [ ] **Step 7: Commit**

```bash
git add tools/scene_keyframe_extractor.py
git commit -m "fix(extractor): no fake action text, use ledger anchors, configurable whisper model/language"
```

---

### Task 8: Docs and skills (CLAUDE.md, extractor skill, generator skill)

**Files:**
- Modify: `CLAUDE.md`, `ugc-video-beat-extractor/SKILL.md`, `ugc-viral-video-generator/SKILL.md`

Apply each edit with the Edit tool (exact `old_string` → `new_string`).

- [ ] **Step 1: `CLAUDE.md` — command reference.** After the line `python tools/scene_keyframe_extractor.py --video "[PATH_TO_REFERENCE_VIDEO]"` block entry, add a new numbered command block. Replace

```
# 2. Run QA Harness Audit (Fase 4 & Continuous QA)
```
with
```
# 1b. Draft the reference ledger (dialogue + contact frames), then fill in actions from the frames (Fase 2)
python tools/reference_ledger.py --project "[PROJECT_FOLDER_NAME]" [--language es|en]

# 1c. Compile I2V prompts from each chunk's action_timeline (Fase 3)
python tools/prompt_compiler.py --json "[PATH_TO_production_package.json]"

# 2. Run QA Harness Audit (Fase 4 & Continuous QA)
```

- [ ] **Step 2: `CLAUDE.md` — Fase 2.** After item 3 (`**Strict Governance:** ...`) insert:

```
4. **Ledger de Referencia (fuente de verdad de acciones y diálogo):** Ejecuta `python tools/reference_ledger.py --project [PROJECT]`, mira los frames de contacto y completa en `01_Reference/reference_ledger.json`, fila por fila y en orden: `action`, `framing`, `props`, `gaze`, `gesture` e `is_cta` (el diálogo literal ya viene de Whisper; corrígelo escuchando si hace falta). Una fila por acción física distinta, aunque ocurra dentro de la misma toma.
```

and renumber the old items 4 and 5 to 5 and 6.

- [ ] **Step 3: `CLAUDE.md` — Checkpoint 1.** In the (former) item 4 list add after `D. Cover Headline`:

```
   - **E. Ledger de Referencia:** Muestra la tabla del ledger (acción + diálogo por fila) para que el usuario la confirme.
   - **F. Exageración del hook (opt-in):** Por defecto la acción del hook es idéntica a la referencia; solo se exagera si el usuario lo pide.
```

and in the registration command add `--ledger-confirmed` (and `--hook-exaggeration` solo si el usuario lo pidió). Add the sentence: `GATE_8 exige que el hash del ledger coincida con el confirmado aquí.`

- [ ] **Step 4: `CLAUDE.md` — Fase 3.** Replace rule 1 heading and body:

old: `1. **Regla de Escenario Propio vs. Disparador Stop-Scroll Replicado / Hiper-Exagerado:**` (and its two sub-bullets)
new:
```
1. **Escenario y Hook (gobierna `scene_mode` del Checkpoint 1):**
   - `replicate_1to1`: se replica el entorno de la referencia. `adapt_to_brand`: se usa el escenario canónico de la marca. Solo cambian avatar, vestuario y (si se eligió) escenario.
   - **Acciones idénticas:** el hook y todas las acciones de la referencia se mantienen tal cual, en el mismo orden. La hiper-exageración solo aplica si `hook_exaggeration` es `true` en `checkpoint1.json`.
```

Replace rule 2 (`**Regla del 70/30 en el Guion:**` and sub-bullets) with:

```
2. **Regla de Fidelidad Verbatim (≥85 %):**
   - El diálogo de cada fila del ledger se conserva ≥85 % palabra por palabra (GATE_7). Solo se permiten ajustes mínimos de voz del avatar y el cambio de marcas/CTA por las fórmulas anti-filtro (las filas `is_cta` están exentas).
   - Cada chunk lleva `ledger_rows`, `ref_window`, `voiceover_reference` y un `action_timeline` (`t0, t1, ledger_row, action, props, dialogue`) contiguo y en el orden del ledger. Toda fila del ledger debe quedar cubierta (GATE_8).
```

In rule 6 add a first sentence: `Los prompts I2V se **compilan** desde el `action_timeline` con `python tools/prompt_compiler.py --json ...`; no se escriben a mano.`

- [ ] **Step 5: `CLAUDE.md` — gates and prohibitions.** Replace the `GATE_7` bullet with:

```
- **GATE_7 (Reference Fidelity):** Con ledger: cada fila (salvo CTA) conserva ≥85 % de las palabras del diálogo literal. Sin ledger (proyectos antiguos): longitud ±10 % y ≥50 % de palabras de contenido. Heurística léxica; el sentido sigue requiriendo revisión humana.
- **GATE_8 (Action Coverage, solo con ledger):** El ledger está confirmado y sin cambios desde el Checkpoint 1; toda fila está cubierta por algún chunk; el `action_timeline` es contiguo, ordenado y ≤ duración del clip; el prompt contiene el marcador de tiempo y el diálogo de cada paso.
```

Change the heading `## The 7 QA Harness Quality Gates` to `## The 7+1 QA Harness Quality Gates` and its first sentence to `verify that ... passes all gates (GATE_8 applies when a reference ledger exists)`. Replace Critical Constraint 2 (`**70/30 Script Rule:**` …) with:

```
2. **Ledger + Verbatim Rule:** Mantén todas las acciones de la referencia, en orden, y ≥85 % del diálogo literal (GATE_7/GATE_8). Como las referencias suelen rondar ~3 WPS, alcanza el mismo número de palabras con más/longer clips (<= 10s cada uno) en lugar de recortar palabras.
```

Also change Fase 1 heading list reference `70/30` mentions elsewhere: run `grep -n "70/30" CLAUDE.md` and update any leftover mention to the ledger rule.

- [ ] **Step 6: `ugc-viral-video-generator/SKILL.md`.** Replace section `### A. Regla Dorada: ...` (heading and both bullets) with:

```
### A. Escenario y Disparador de Hook (gobernados por Checkpoint 1)
* **Escenario:** lo decide `scene_mode` de `checkpoint1.json`: `replicate_1to1` replica el entorno de la referencia; `adapt_to_brand` usa el escenario canónico de la marca.
* **Acciones:** se replican idénticas, en orden, desde `01_Reference/reference_ledger.json`. La hiper-exageración del disparador visual solo se aplica si `hook_exaggeration` es `true`.
```

Replace section 6 item 1 (`La Regla 70/30 en el Guión`, three sub-bullets) with:

```
1. **Regla de Fidelidad Verbatim (≥85 %):** el diálogo de cada fila del ledger se conserva ≥85 % palabra por palabra; solo se permiten ajustes mínimos de voz del avatar y el cambio de marcas/CTA por las fórmulas seguras. Cadencia ≤ 2.4 WPS.
```

In section 4 (Pipeline) insert before step 2 a step: `Rellenar por chunk ledger_rows, ref_window, voiceover_reference y action_timeline; luego compilar los prompts I2V: python tools/prompt_compiler.py --json "<json>"`. Add to section 8 intro: `Los prompts se generan con tools/prompt_compiler.py a partir del action_timeline; la plantilla de abajo describe su salida.` Update the frontmatter description to replace "fidelidad visual 1:1" wording only if it contradicts (leave otherwise).

- [ ] **Step 7: `ugc-video-beat-extractor/SKILL.md`.** Replace step 2's folder list to include `05_Montage/`; replace step 4's "Gobernanza" list item 2 with `01_beat1_hook.jpg` … (máx 10 keyframes según `CLAUDE.md`) and add item 4 `reference_ledger.json`. Add a new step after step 5:

```
### 5b. Ledger de Referencia (obligatorio)
- Ejecutar `python tools/reference_ledger.py --project PROD_<ID>_<nombre>`; ver los frames de contacto impresos (f_0001 = 0 s; t = (n-1)/2) y completar por fila `action`, `framing`, `props`, `gaze`, `gesture`, `is_cta`. Una fila por acción física distinta, aunque sea dentro de una misma toma.
- Mostrar la tabla al usuario en el Checkpoint 1 y registrar `--ledger-confirmed`.
```

Add to the checklist: `- [ ] reference_ledger.json completo y confirmado por el usuario.`

- [ ] **Step 8: Verify and commit**

Run: `python -m pytest tests -q` → all pass.
Run: `grep -n "70/30" CLAUDE.md ugc-viral-video-generator/SKILL.md ugc-video-beat-extractor/SKILL.md` → no stale rule text (a historical mention is acceptable only if it says it was replaced).

```bash
git add CLAUDE.md ugc-viral-video-generator/SKILL.md ugc-video-beat-extractor/SKILL.md
git commit -m "docs: replace 70/30 with ledger + verbatim rule; document ledger workflow and GATE_8"
```

---

## Self-Review

**Spec coverage:** Ledger + draft tool → Tasks 1–2. Checkpoint hash + exaggeration opt-in → Task 5. Schema fields → Task 3. Prompt compiler → Task 4. GATE_7 ledger (≥0.85, CTA exempt), GATE_8, backward compatibility, `record_gates` → Task 6. Extractor placeholder removal, ledger anchors, Whisper model/language → Task 7. Rules/skills/CLAUDE.md → Task 8. Tests for GATE_8 good/missing action/gap plus compiler → Tasks 4 and 6.

**Placeholders:** none; all code steps show code. Task 2 is verified by smoke test since it wraps Whisper/ffmpeg.

**Type consistency:** `time_marker` (Task 4) is used by the harness (Task 6) with the same signature; `write_checkpoint` keyword names (`ledger_confirmed`, `hook_exaggeration`) match between Tasks 5 and 6 tests; ledger ids `r01`/`r02` and `D1`/`D2` are defined once in `tests/test_ledger_gates.py` (Tasks 3, 5) and reused later; `LEDGER` is defined in Task 5 and used in Task 6, so Tasks 5 and 6 must run in order.

**Known limitation:** the tests import `_chunk` via `from test_harness import _chunk`, which relies on pytest's default `rootdir/tests` import mode (no `__init__.py`). If that import ever fails, copy `_chunk` into the new test file.
