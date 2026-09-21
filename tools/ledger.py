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
