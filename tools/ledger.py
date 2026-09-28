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
    return re.findall(r"[a-záéíóúñü0-9']+", text.lower())


def _lcs_length(a: List[str], b: List[str]) -> int:
    """Longest Common Subsequence length for token lists."""
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m):
        for j in range(n):
            if a[i] == b[j]:
                dp[i + 1][j + 1] = dp[i][j] + 1
            else:
                dp[i + 1][j + 1] = max(dp[i + 1][j], dp[i][j + 1])
    return dp[m][n]


def fidelity(ref_text: str, gen_text: str) -> float:
    """Calcula la fidelidad del texto generado respecto a la referencia.

    Combina la retención léxica de vocabulario (unigram overlap) con la preservación
    del orden secuencial sintáctico (Longest Common Subsequence / ROUGE-L).
    """
    ref_tokens = tokenize(ref_text)
    gen_tokens = tokenize(gen_text)
    total = len(ref_tokens)
    if not total:
        return 1.0

    ref_counter = Counter(ref_tokens)
    gen_counter = Counter(gen_tokens)
    unigram_score = sum((ref_counter & gen_counter).values()) / total
    lcs_score = _lcs_length(ref_tokens, gen_tokens) / total

    # 50% retención léxica + 50% preservación del orden sintáctico
    return round(0.5 * unigram_score + 0.5 * lcs_score, 3)


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
    try:
        return [r.t_start for r in load_ledger(path).rows]
    except Exception as e:
        print(f"Aviso: reference_ledger.json inválido, se ignoran anclas ({str(e).splitlines()[0]})", file=sys.stderr)
        return []
