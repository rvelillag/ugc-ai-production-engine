import sys
import json
import argparse
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.project_state import save_state
from tools.ledger import LEDGER_FILE, ledger_hash, load_ledger

CHECKPOINT_FILE = "checkpoint1.json"
SCENE_MODES = ("replicate_1to1", "adapt_to_brand")
REQUIRED_FIELDS = ("scene_mode", "outfit", "manychat_keyword", "cover_headline")


def find_project(name_or_path: str, base_dir: Path) -> Path:
    p = Path(name_or_path)
    if p.is_absolute() and p.exists():
        return p
    found = list(base_dir.glob(f"*/04_IN_PRODUCTION/{p.name}"))
    if not found:
        raise FileNotFoundError(f"Proyecto no encontrado: {name_or_path}")
    return found[0]


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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Registra la confirmación del Checkpoint 1 (solo tras confirmar con el usuario)")
    parser.add_argument("--project", required=True, help="Nombre o ruta del proyecto PROD_XXX_ref")
    parser.add_argument("--scene", required=True, choices=SCENE_MODES, help="replicate_1to1 (escenario de la referencia) o adapt_to_brand")
    parser.add_argument("--outfit", required=True)
    parser.add_argument("--keyword", required=True, help="Keyword de ManyChat")
    parser.add_argument("--headline", required=True, help="Cover headline (máx 7 palabras)")
    parser.add_argument("--confirmed-by-user", action="store_true", required=True,
                        help="Obligatorio: certifica que el usuario confirmó estos 4 puntos")
    parser.add_argument("--ledger-confirmed", action="store_true",
                        help="El usuario confirmó el reference_ledger.json (guarda su hash)")
    parser.add_argument("--hook-exaggeration", action="store_true",
                        help="Opt-in: el usuario pidió exagerar el disparador del hook (por defecto: acción idéntica a la referencia)")
    args = parser.parse_args()

    base = Path(__file__).resolve().parent.parent
    path = write_checkpoint(find_project(args.project, base), args.scene, args.outfit, args.keyword, args.headline,
                            ledger_confirmed=args.ledger_confirmed, hook_exaggeration=args.hook_exaggeration)
    print(f"Checkpoint 1 registrado: {path}")
