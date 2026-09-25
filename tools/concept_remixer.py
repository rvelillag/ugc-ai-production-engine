"""
Concept Remixer (Derivative Creative Blueprint Engine).
Permite crear videos propios y originales basados en la estructura viral, cadencia y ritmo de tomas de un video de referencia.
"""
import sys
import json
import argparse
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.checkpoint1 import find_project, write_checkpoint
from tools.ledger import LEDGER_FILE, Ledger, LedgerRow


BEAT_ARCHETYPES = [
    ("HOOK", ["hook", "disruptivo", "scroll", "detencion", "problema"]),
    ("REFRAME", ["reframe", "contraste", "precio", "valor", "secreto", "work"]),
    ("RECIPE", ["receta", "ingredientes", "formula", "componentes", "honey", "aceite"]),
    ("TECHNIQUE", ["tecnica", "mezcla", "emulsion", "aplicacion", "conditioner", "stirring"]),
    ("MECHANISM", ["mecanismo", "biologia", "tiempo", "foliculo", "proteina", "nutricion", "circulacion"]),
    ("CTA", ["cta", "manychat", "keyword", "llamada", "seguimiento", "comenta"])
]

def classify_beat(name: str, index: int, total: int) -> str:
    name_lower = name.lower()
    for arch, keywords in BEAT_ARCHETYPES:
        if any(k in name_lower for k in keywords):
            return arch
    if index == 0:
        return "HOOK"
    elif index == total - 1:
        return "CTA"
    elif index == 1:
        return "REFRAME"
    elif index == total - 2:
        return "MECHANISM"
    return "TECHNIQUE"


def analyze_blueprint(ref_project_dir: Path) -> Dict[str, Any]:
    ref_dir = ref_project_dir / "01_Reference"
    ledger_path = ref_dir / LEDGER_FILE
    
    if not ledger_path.exists():
        raise FileNotFoundError(f"No se encontró {LEDGER_FILE} en {ref_dir}. Ejecuta reference_ledger.py primero.")
    
    ledger_data = json.loads(ledger_path.read_text(encoding="utf-8"))
    rows = ledger_data.get("rows", [])
    total_dur = ledger_data.get("duration_s", 0.0)
    
    beats = []
    total_words = 0
    for idx, r in enumerate(rows):
        t0 = r.get("t_start", 0.0)
        t1 = r.get("t_end", 0.0)
        dur = round(t1 - t0, 2)
        text = r.get("dialogue_verbatim", "")
        wc = len([w for w in text.split() if w])
        total_words += wc
        archetype = classify_beat(r.get("action", "") + " " + r.get("id", ""), idx, len(rows))
        
        beats.append({
            "take_id": r.get("id"),
            "t_start": t0,
            "t_end": t1,
            "duration_s": dur,
            "ref_word_count": wc,
            "archetype": archetype,
            "ref_action": r.get("action", ""),
            "ref_framing": r.get("framing", ""),
            "is_cta": r.get("is_cta", False)
        })
        
    measured_wps = round(total_words / total_dur, 2) if total_dur > 0 else 2.4
    
    return {
        "reference_video": ledger_data.get("reference_video"),
        "total_duration_s": total_dur,
        "total_words": total_words,
        "measured_wps": measured_wps,
        "total_takes": len(beats),
        "blueprint_beats": beats
    }


def print_blueprint_table(blueprint: Dict[str, Any]):
    print("\n" + "=" * 80)
    print(f"🎬 VIRAL BLUEPRINT ANALYSIS — {blueprint['reference_video']}")
    print(f"Duración: {blueprint['total_duration_s']}s | Tomas: {blueprint['total_takes']} | Cadencia: {blueprint['measured_wps']} WPS ({blueprint['total_words']} palabras)")
    print("=" * 80)
    print(f"{'Toma':<6} | {'Tiempo':<12} | {'Dur (s)':<8} | {'Arquetipo':<12} | {'Palabras Max':<14} | {'Función Psicológica'}")
    print("-" * 80)
    
    wps = blueprint["measured_wps"]
    for b in blueprint["blueprint_beats"]:
        max_words = int(round(b["duration_s"] * wps))
        print(f"{b['take_id']:<6} | {b['t_start']:>4.1f}s - {b['t_end']:>4.1f}s | {b['duration_s']:>6.1f}s | {b['archetype']:<12} | {max_words:>4} palabras    | {b['ref_action'][:35]}...")
    print("=" * 80 + "\n")


def scaffold_derivative_project(
    base_dir: Path,
    brand_folder_name: str,
    ref_project_name: str,
    new_project_id: str,
    topic: str,
    manychat_keyword: str,
    cover_headline: str,
    outfit: str = "Dark navy silk blouse, black canvas salon apron, gold hoop earrings"
) -> Path:
    brand_dir = base_dir / brand_folder_name
    if not brand_dir.exists():
        raise FileNotFoundError(f"Carpeta de marca no encontrada: {brand_dir}")
        
    ref_proj_dir = find_project(ref_project_name, base_dir)
    blueprint = analyze_blueprint(ref_proj_dir)
    
    new_proj_dir = brand_dir / "04_IN_PRODUCTION" / new_project_id
    
    for sub in ["01_Reference", "02_First_Frames", "03_Raw_Clips", "04_Audio", "05_Montage"]:
        (new_proj_dir / sub).mkdir(parents=True, exist_ok=True)
        
    # Copy reference assets to 01_Reference as structural guide
    ref_src = ref_proj_dir / "01_Reference"
    if ref_src.exists():
        for f in ref_src.glob("*"):
            if f.is_file():
                shutil.copy2(f, new_proj_dir / "01_Reference" / f.name)
                
    # Save structural blueprint
    blueprint_file = new_proj_dir / "01_Reference" / "viral_blueprint.json"
    blueprint_file.write_text(json.dumps(blueprint, ensure_ascii=False, indent=2), encoding="utf-8")
    
    # Pre-register checkpoint1
    write_checkpoint(
        project_dir=new_proj_dir,
        scene_mode="derivative_concept",
        outfit=outfit,
        keyword=manychat_keyword,
        headline=cover_headline,
        ledger_confirmed=False,
        hook_exaggeration=False,
        fidelity_target="full_verbatim",
        wps_target=blueprint["measured_wps"]
    )
    
    print(f"\n✅ Proyecto Creativo Derivado Creado: {new_proj_dir}")
    print(f"📊 Esqueleto Viral Copiado: {blueprint['total_takes']} tomas a {blueprint['measured_wps']} WPS")
    print(f"📌 Siguiente paso: Adaptar el guion en reference_ledger.json para el tema '{topic}'.\n")
    return new_proj_dir


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Concept Remixer: Creación de videos propios basados en esqueletos de referencia")
    parser.add_argument("--analyze", help="Analiza y muestra la estructura viral de un proyecto existente")
    parser.add_argument("--create", action="store_true", help="Crea un nuevo proyecto derivado")
    parser.add_argument("--brand", default="Rachel Bennett - Botanique", help="Nombre de la carpeta de marca")
    parser.add_argument("--ref", help="Nombre del proyecto de referencia (ej. PROD_017_skin.diaries.emma_9)")
    parser.add_argument("--project", help="ID del nuevo proyecto (ej. PROD_019_rosemary_oil)")
    parser.add_argument("--topic", help="Tema del nuevo video")
    parser.add_argument("--keyword", default="GROW", help="Keyword de ManyChat")
    parser.add_argument("--headline", default="The $3 Scalp Oil Trick", help="Cover headline (máx 7 palabras)")
    parser.add_argument("--outfit", default="Dark navy silk blouse, black canvas salon apron, gold hoop earrings")
    
    args = parser.parse_args()
    base = Path(__file__).resolve().parent.parent
    
    if args.analyze:
        proj = find_project(args.analyze, base)
        bp = analyze_blueprint(proj)
        print_blueprint_table(bp)
    elif args.create:
        if not args.ref or not args.project or not args.topic:
            print("Error: --ref, --project y --topic son obligatorios para crear un proyecto derivado.")
            sys.exit(1)
        scaffold_derivative_project(
            base_dir=base,
            brand_folder_name=args.brand,
            ref_project_name=args.ref,
            new_project_id=args.project,
            topic=args.topic,
            manychat_keyword=args.keyword,
            cover_headline=args.headline,
            outfit=args.outfit
        )
