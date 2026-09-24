"""Genera el borrador del ledger de referencia: diálogo literal (Whisper) + frames de contacto para describir acciones."""
import argparse
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.checkpoint1 import find_project
from tools.ledger import LEDGER_FILE, Ledger, LedgerRow, build_draft_rows


def _duration(video: Path) -> float:
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(video)], text=True)
    return float(out.strip())


def backup_existing(ledger_path: Path) -> Path:
    """Copia el ledger existente al directorio temporal del sistema (nunca dentro de 01_Reference)."""
    dest = Path(tempfile.gettempdir()) / f"reference_ledger_backup_{time.strftime('%Y%m%d_%H%M%S')}.json"
    shutil.copy2(ledger_path, dest)
    return dest


def build_rows_from_script_beats(script_beats_file: Path) -> list[LedgerRow]:
    """Extrae las filas del ledger directamente de las tomas y beats semánticos de script_beats.txt."""
    import re
    content = script_beats_file.read_text(encoding="utf-8")
    pattern = r"\[([A-Z0-9_]+)\s*—\s*TOMA\s*(\d+)\]\s*\n\*\s*Timestamp:\s*([0-9\.]+)s\s*-\s*([0-9\.]+)s[^\n]*\n\*\s*Voiceover Segment:\s*\"([^\"]*)\""
    matches = re.findall(pattern, content)
    rows = []
    for beat_name, take_num, t_start, t_end, vo in matches:
        is_cta = "CTA" in beat_name.upper()
        rid = f"r{int(take_num):02d}"
        rows.append(LedgerRow(
            id=rid,
            t_start=float(t_start),
            t_end=float(t_end),
            dialogue_verbatim=vo.strip(),
            is_cta=is_cta
        ))
    return rows


def make_draft(project_dir: Path, language, model_size: str, fps: float, force: bool) -> Path:
    ref_dir = project_dir / "01_Reference"
    videos = sorted(ref_dir.glob("*.mp4"))
    if not videos:
        raise FileNotFoundError(f"No hay .mp4 en {ref_dir}")
    out = ref_dir / LEDGER_FILE
    if out.exists() and not force:
        raise FileExistsError(f"{out} ya existe (usa --force para sobrescribirlo; se guarda una copia de seguridad en el directorio temporal e invalida el Checkpoint 1)")
    if out.exists():
        print(f"Copia de seguridad del ledger anterior: {backup_existing(out)}")
    video = videos[0]
    duration = _duration(video)

    script_beats_files = sorted(ref_dir.glob("script_beats_*.txt"))
    if script_beats_files:
        print(f"Sincronizando ledger con tomas narrativas de: {script_beats_files[0].name}")
        rows = build_rows_from_script_beats(script_beats_files[0])
        lang = language or "en"
    else:
        from faster_whisper import WhisperModel
        model = WhisperModel(model_size, device="cpu", compute_type="int8")
        segments, info = model.transcribe(str(video), word_timestamps=True, language=language)
        words = [{"word": w.word.strip(), "start": round(w.start, 2), "end": round(w.end, 2)}
                 for s in segments for w in (s.words or [])]
        rows = build_draft_rows(words, duration)
        lang = info.language

    ledger = Ledger(reference_video=video.name, duration_s=round(duration, 2),
                    language=lang, rows=rows)
    out.write_text(ledger.model_dump_json(indent=2), encoding="utf-8")

    frames_dir = Path(tempfile.mkdtemp(prefix="ledger_frames_"))
    subprocess.run(["ffmpeg", "-y", "-i", str(video), "-vf", f"fps={fps}", "-q:v", "3",
                    str(frames_dir / "f_%04d.jpg")], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    print(f"Borrador del ledger: {out} ({len(ledger.rows)} filas narrativas completas)")
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
