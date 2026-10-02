"""QA posterior a la generación: compara cada clip crudo (03_Raw_Clips/N.mp4) con lo planeado.

Para cada chunk del paquete transcribe el audio del clip con Whisper y reporta:
  - coincidencia del texto hablado con el diálogo planeado,
  - duración real del clip frente a la planeada (los generadores solo producen 4/6/8 s),
  - momento real en que se oye la primera palabra de cada paso frente a su ventana planeada (desfase),
  - voz cortada al final del clip o clip sin voz.

Solo mide el AUDIO: no verifica que la acción visual ocurra en ese momento.
Uso: ugc qa --project PROD_027_xxx   (o: python tools/clip_qa.py --project ...)
"""
import argparse
import difflib
import json
import re
import sys
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

REPORT_FILE = "clip_qa_report.json"

MIN_TEXT_MATCH = 0.90        # coincidencia mínima del texto oído con el planeado
MAX_STEP_DRIFT_S = 1.0       # desfase máximo tolerado entre ventana planeada y voz real de un paso
MAX_DURATION_DELTA_S = 0.75  # diferencia máxima entre duración real y planeada del clip
CUTOFF_MARGIN_S = 0.15       # voz que termina a menos de esto del final del clip = posible corte

Word = Dict[str, float]  # {"word": str, "start": float, "end": float}


def tokenize(text: str) -> List[str]:
    return re.findall(r"[a-z0-9áéíóúñü']+", (text or "").lower().replace("’", "'"))


def _plan_steps(chunk: dict) -> List[dict]:
    """Pasos con diálogo del chunk; si no hay timeline, usa el voiceover como un único paso."""
    steps = [s for s in (chunk.get("action_timeline") or []) if isinstance(s, dict) and tokenize(s.get("dialogue", ""))]
    if steps:
        return steps
    text = chunk.get("voiceover_clean_tts", "")
    if tokenize(text):
        return [{"t0": 0.0, "t1": float(chunk.get("recommended_duration_s") or 0), "dialogue": text}]
    return []


def analyze_chunk(chunk: dict, words: List[Word], clip_duration: float) -> dict:
    """Análisis puro (sin I/O) de un clip: `words` son las palabras oídas con tiempos reales."""
    cid = chunk.get("chunk_id", chunk.get("id"))
    planned = chunk.get("recommended_duration_s")
    steps = _plan_steps(chunk)
    exp: List[str] = []
    step_ranges: List[Tuple[int, int]] = []
    for s in steps:
        toks = tokenize(s["dialogue"])
        step_ranges.append((len(exp), len(exp) + len(toks)))
        exp.extend(toks)
    got = [t for w in words for t in tokenize(w["word"])]
    # una palabra de Whisper puede tokenizar a varios tokens: se asigna el tiempo de su palabra
    got_times = [w for w in words for _ in tokenize(w["word"])]

    issues: List[str] = []
    report = {
        "chunk_id": cid,
        "planned_duration_s": planned,
        "real_duration_s": round(clip_duration, 2),
        "expected_words": len(exp),
        "heard_words": len(got),
        "text_match": None,
        "speech_start_s": None,
        "speech_end_s": None,
        "steps": [],
        "issues": issues,
    }

    if planned is not None and abs(clip_duration - planned) > MAX_DURATION_DELTA_S:
        issues.append(f"duración real {clip_duration:.1f}s ≠ planeada {planned}s: los marcadores del timeline están desfasados")

    if not got:
        if exp:
            issues.append("no se detectó voz en el clip")
        return report

    report["speech_start_s"] = round(got_times[0]["start"], 2)
    report["speech_end_s"] = round(got_times[-1]["end"], 2)
    if got_times[-1]["end"] >= clip_duration - CUTOFF_MARGIN_S:
        issues.append(f"la voz llega hasta el último instante del clip ({report['speech_end_s']}s de {clip_duration:.1f}s): posible corte")

    matcher = difflib.SequenceMatcher(None, exp, got, autojunk=False)
    ratio = matcher.ratio() if exp else 1.0
    report["text_match"] = round(ratio, 3)
    if ratio < MIN_TEXT_MATCH:
        issues.append(f"el texto oído coincide solo al {ratio:.0%} con el planeado (mín {MIN_TEXT_MATCH:.0%})")

    exp_to_got: Dict[int, int] = {}
    for block in matcher.get_matching_blocks():
        for k in range(block.size):
            exp_to_got[block.a + k] = block.b + k

    heard_starts: List[Optional[float]] = []
    for (lo, hi) in step_ranges:
        idx = next((exp_to_got[i] for i in range(lo, hi) if i in exp_to_got), None)
        heard_starts.append(round(got_times[idx]["start"], 2) if idx is not None else None)

    for n, (s, heard) in enumerate(zip(steps, heard_starts)):
        t0, t1 = float(s.get("t0", 0)), float(s.get("t1", 0))
        entry = {"planned_t0": t0, "planned_t1": t1, "heard_at": heard, "drift_s": None}
        if heard is None:
            issues.append(f"paso {t0:g}-{t1:g}s: no se oye su diálogo")
        else:
            drift = round(heard - t0, 2)
            entry["drift_s"] = drift
            nxt = next((h for h in heard_starts[n + 1:] if h is not None), None)
            entry["suggested_window"] = [heard, round(nxt if nxt is not None else report["speech_end_s"], 2)]
            if abs(drift) > MAX_STEP_DRIFT_S:
                issues.append(f"paso {t0:g}-{t1:g}s: la voz real arranca en {heard}s (desfase {drift:+.1f}s)")
        report["steps"].append(entry)
    return report


def transcribe_clip(path: Path, language: Optional[str] = "en", model_size: str = "base",
                    _cache: dict = {}) -> Tuple[List[Word], float]:
    """Transcribe un clip con faster-whisper. Devuelve (palabras con tiempos, duración del clip)."""
    from faster_whisper import WhisperModel
    if model_size not in _cache:
        _cache[model_size] = WhisperModel(model_size, device="cpu", compute_type="int8")
    lang = None if (not language or language.lower() == "auto") else language
    segments, info = _cache[model_size].transcribe(str(path), word_timestamps=True, language=lang)
    words = [{"word": w.word, "start": w.start, "end": w.end} for s in segments for w in (s.words or [])]
    return words, float(info.duration)


def _find_package(project_dir: Path) -> Path:
    for folder in (project_dir / "02_First_Frames", project_dir):
        found = sorted(folder.glob("production_package_*.json"))
        if found:
            return found[0]
    raise FileNotFoundError(f"No hay production_package_*.json en {project_dir}")


def run_qa(project_dir: Path, language: Optional[str] = "en", model_size: str = "base",
           transcriber: Callable = transcribe_clip) -> Tuple[dict, bool]:
    """Analiza todos los clips del proyecto, escribe clip_qa_report.json y devuelve (reporte, todo_ok)."""
    project_dir = Path(project_dir)
    package = json.loads(_find_package(project_dir).read_text(encoding="utf-8"))
    clips_dir = project_dir / "03_Raw_Clips"
    chunks_report = []
    for chunk in package.get("chunks", []):
        cid = chunk.get("chunk_id", chunk.get("id"))
        clip = clips_dir / f"{cid}.mp4"
        if not clip.exists():
            chunks_report.append({"chunk_id": cid, "issues": [f"falta el clip {clip.name} en 03_Raw_Clips/"]})
            continue
        words, duration = transcriber(clip, language, model_size)
        chunks_report.append(analyze_chunk(chunk, words, duration))
    ok = all(not c["issues"] for c in chunks_report)
    report = {
        "project": project_dir.name,
        "thresholds": {"min_text_match": MIN_TEXT_MATCH, "max_step_drift_s": MAX_STEP_DRIFT_S,
                       "max_duration_delta_s": MAX_DURATION_DELTA_S},
        "ok": ok,
        "chunks": chunks_report,
    }
    (project_dir / REPORT_FILE).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report, ok


def print_report(report: dict) -> None:
    print("=" * 70)
    print(f"  QA DE CLIPS GENERADOS — {report['project']}")
    print("=" * 70)
    for c in report["chunks"]:
        head = f"Clip {c['chunk_id']}"
        if c.get("real_duration_s") is not None:
            match = f"{c['text_match']:.0%}" if c.get("text_match") is not None else "n/a"
            head += (f": {c['real_duration_s']}s (plan {c.get('planned_duration_s')}s) | texto {match} "
                     f"| habla {c.get('speech_start_s')}-{c.get('speech_end_s')}s")
        print(("[OK]   " if not c["issues"] else "[FAIL] ") + head)
        for s in c.get("steps", []):
            if s.get("drift_s") is not None:
                print(f"         paso {s['planned_t0']:g}-{s['planned_t1']:g}s -> voz en {s['heard_at']}s (desfase {s['drift_s']:+.1f}s)")
        for issue in c["issues"]:
            print(f"         ! {issue}")
    clips_bad = [c["chunk_id"] for c in report["chunks"] if c["issues"]]
    print("-" * 70)
    print("  RESULTADO: todos los clips OK" if report["ok"] else f"  RESULTADO: revisar/regenerar clips {clips_bad}")
    print("  (Mide solo audio; la acción visual debe revisarse a ojo.)")


def _resolve_project(name_or_path: str, base_dir: Path) -> Path:
    p = Path(name_or_path)
    if p.is_absolute() and p.exists():
        return p
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from tools.checkpoint1 import find_project
    try:
        return find_project(name_or_path, base_dir)
    except FileNotFoundError:
        for root in (Path.cwd(), base_dir, base_dir.parent):
            found = list(root.glob(f"**/06_ARCHIVE/{p.name}"))
            if found:
                return found[0]
        raise


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="QA de clips generados: texto, duración y desfase de voz vs plan")
    parser.add_argument("--project", required=True, help="Nombre o ruta del proyecto (04_IN_PRODUCTION o 06_ARCHIVE)")
    parser.add_argument("--language", default="en", help="Idioma hablado en los clips (en, es, pt, auto). Por defecto: en")
    parser.add_argument("--model", default="base", help="Modelo Whisper (tiny, base, small...)")
    parser.add_argument("--workspace", default=None, help="Carpeta del avatar (por defecto, el directorio actual)")
    args = parser.parse_args(argv)
    base_dir = Path(args.workspace) if args.workspace else Path.cwd()
    try:
        project_dir = _resolve_project(args.project, base_dir)
        report, ok = run_qa(project_dir, language=args.language, model_size=args.model)
    except FileNotFoundError as e:
        print(f"[ERROR] {e}")
        return 2
    print_report(report)
    print(f"\n  Reporte guardado en: {project_dir / REPORT_FILE}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
