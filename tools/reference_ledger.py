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
