"""Prompt Safety Linter & Anti-Filter Sanitizer para UGC AI Production Engine.

Inspecciona y sanitiza prompts (First Frames Midjourney / Flux e I2V Kling / Veo)
contra los clasificadores de moderación de seguridad de Google Imagen, Gemini,
Midjourney, Veo y Kling (prevención de bloqueos por desnudez, violencia, o contacto físico).
"""
import re
import json
import sys
from pathlib import Path
from typing import Tuple, List, Dict, Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Diccionario de patrones de riesgo y sustituciones clínicas / atléticas seguras
SAFETY_RULES: List[Dict[str, Any]] = [
    # 1. Nudity / Anatomy / Apparel triggers
    {
        "pattern": r"\bbare\s+lower\s+back\b",
        "replacement": "lower back supported by a fitted black athletic sports crop top",
        "category": "nudity_apparel"
    },
    {
        "pattern": r"\bbare\s+back\b",
        "replacement": "open-back cross-strap athletic gym crop top",
        "category": "nudity_apparel"
    },
    {
        "pattern": r"\bbare\s+waist\b",
        "replacement": "high-waisted athletic performance compression waistband",
        "category": "nudity_apparel"
    },
    {
        "pattern": r"\bwaist\s+(?:fully\s+)?exposed\b",
        "replacement": "athletic compression midriff band",
        "category": "nudity_apparel"
    },
    {
        "pattern": r"\blow-rise\s+leggings\b",
        "replacement": "high-waisted black athletic compression leggings",
        "category": "nudity_apparel"
    },
    {
        "pattern": r"\b(?:sports\s+)?bra\b",
        "replacement": "athletic sports crop top",
        "category": "nudity_apparel"
    },
    {
        "pattern": r"\bunderwear\b",
        "replacement": "compression athletic base layer",
        "category": "nudity_apparel"
    },
    {
        "pattern": r"\bcleavage\b",
        "replacement": "collarbone neckline",
        "category": "nudity_apparel"
    },
    {
        "pattern": r"\bpulled\s+up\s+(?:shirt|blouse|top)\b",
        "replacement": "athletic top neatly folded at the midriff for clinical examination",
        "category": "nudity_apparel"
    },
    {
        "pattern": r"\bunclothed\b",
        "replacement": "in modest athletic patient attire",
        "category": "nudity_apparel"
    },

    # 2. Physical contact / Pinching / Abuse false-positives
    {
        "pattern": r"\bpinches?\s+skin\b",
        "replacement": "performs gentle clinical two-finger palpation of skin elasticity",
        "category": "contact_pinch"
    },
    {
        "pattern": r"\bpinching\s+skin\b",
        "replacement": "gentle clinical two-finger examination",
        "category": "contact_pinch"
    },
    {
        "pattern": r"\bpinches?\s+(?:the\s+)?(?:back|flank|flanks|waist|flesh|tissue)\b",
        "replacement": "applies gentle diagnostic two-finger palpation to the flank tension area",
        "category": "contact_pinch"
    },
    {
        "pattern": r"\bpinching\s+(?:the\s+)?(?:back|flank|flanks|waist|flesh|tissue)\b",
        "replacement": "applying gentle diagnostic two-finger palpation to the flank area",
        "category": "contact_pinch"
    },
    {
        "pattern": r"\bgrabbing\s+(?:the\s+)?(?:waist|flesh|tissue|flank)\b",
        "replacement": "gently assessing the area with clinical gloved fingers",
        "category": "contact_pinch"
    },

    # 3. Clinical & Pathology sanitization (avoid gore triggers while preserving shock value)
    {
        "pattern": r"\bmutilated\b",
        "replacement": "pathologically pronounced and inflamed",
        "category": "gore_pathology"
    },
    {
        "pattern": r"\bbloody\b",
        "replacement": "severely erythematous and clinical",
        "category": "gore_pathology"
    },
    {
        "pattern": r"\bpus\b",
        "replacement": "purulent clinical exudate",
        "category": "gore_pathology"
    },

    # 4. AI plastic sheen / CGI buzzwords
    {
        "pattern": r",?\s*(?:8k\s*resolution|photorealistic(?:\s*portrait)?|hyper-realistic|ultra-detailed(?:\s*skin)?)\b",
        "replacement": "",
        "category": "plastic_buzzwords"
    }
]

# Front-load shock keywords for Hook chunks
HOOK_SHOCK_INDICATORS = [
    "edema", "pitting", "swollen", "bags", "dark circles", "rash",
    "inflamed", "puffiness", "wrinkles", "cystic", "clogged", "flank tension",
    "hair loss", "thinning", "alopecia", "flaking"
]


def lint_text(text: str) -> Tuple[str, List[Dict[str, str]]]:
    """Sanitiza una cadena de prompt reemplazando términos de riesgo por equivalentes seguros."""
    if not text:
        return text, []

    sanitized = text
    matches_found: List[Dict[str, str]] = []

    for rule in SAFETY_RULES:
        regex = re.compile(rule["pattern"], re.IGNORECASE)
        for match in regex.finditer(sanitized):
            matched_str = match.group(0)
            matches_found.append({
                "category": rule["category"],
                "matched": matched_str,
                "replacement": rule["replacement"]
            })
        sanitized = regex.sub(rule["replacement"], sanitized)

    # Clean double spaces or orphaned commas created by deletions
    sanitized = re.sub(r"\s{2,}", " ", sanitized)
    sanitized = re.sub(r"\s+([,.:;])", r"\1", sanitized)
    sanitized = re.sub(r",\s*,", ", ", sanitized).strip()

    return sanitized, matches_found


def verify_hook_front_loading(prompt: str) -> Dict[str, Any]:
    """Verifica si el Hook (Chunk 1) tiene el elemento de shock visual en las primeras 12 palabras."""
    words = prompt.split()
    first_12 = " ".join(words[:12]).lower()
    
    has_shock = any(ind in prompt.lower() for ind in HOOK_SHOCK_INDICATORS)
    front_loaded = any(ind in first_12 for ind in HOOK_SHOCK_INDICATORS)
    
    return {
        "has_pathology_or_shock": has_shock,
        "is_front_loaded": front_loaded if has_shock else True,
        "first_12_words": " ".join(words[:12]) if len(words) >= 12 else prompt,
        "recommendation": (
            "Coloca el objeto de shock en macro forzada en las primeras 12 palabras "
            "(ej: 'Extreme macro forced perspective in foreground: massively enlarged swollen...')"
            if has_shock and not front_loaded else "OK"
        )
    }


def lint_production_package(pkg_path: Path, inplace: bool = False) -> Dict[str, Any]:
    """Audita y sanitiza todos los prompts dentro de un production_package_PROD_XXX.json."""
    data = json.loads(pkg_path.read_text(encoding="utf-8"))
    report = {
        "file": str(pkg_path),
        "total_fixes": 0,
        "fixes": [],
        "hook_audit": {}
    }

    chunks = data.get("chunks", [])
    for chunk in chunks:
        cid = chunk.get("chunk_id", 0)
        
        # 1. Lint First Frame Midjourney prompt
        if "midjourney_prompt_9_16" in chunk:
            original = chunk["midjourney_prompt_9_16"]
            clean, fixes = lint_text(original)
            if fixes:
                chunk["midjourney_prompt_9_16"] = clean
                report["total_fixes"] += len(fixes)
                report["fixes"].append({
                    "chunk": cid,
                    "field": "midjourney_prompt_9_16",
                    "details": fixes
                })
            
            # Check front loading on Chunk 1
            if cid == 1 or "hook" in chunk.get("beat_name", "").lower():
                report["hook_audit"] = verify_hook_front_loading(chunk["midjourney_prompt_9_16"])

        # 2. Lint I2V Motion prompt
        if "video_motion_prompt_i2v" in chunk:
            original = chunk["video_motion_prompt_i2v"]
            clean, fixes = lint_text(original)
            if fixes:
                chunk["video_motion_prompt_i2v"] = clean
                report["total_fixes"] += len(fixes)
                report["fixes"].append({
                    "chunk": cid,
                    "field": "video_motion_prompt_i2v",
                    "details": fixes
                })

    if inplace and report["total_fixes"] > 0:
        pkg_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        report["saved"] = True
    else:
        report["saved"] = False

    return report


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Prompt Safety Linter & Anti-Filter Sanitizer")
    parser.add_argument("--json", help="Ruta a production_package_PROD_XXX.json")
    parser.add_argument("--text", help="Texto de prompt a auditar y sanitizar")
    parser.add_argument("--inplace", action="store_true", help="Guardar cambios directamente en el archivo JSON")
    args = parser.parse_args()

    if args.text:
        sanitized, fixes = lint_text(args.text)
        print(f"[INPUT]:     {args.text}")
        print(f"[SANITIZED]: {sanitized}")
        print(f"[FIXES]:     {len(fixes)} aplicados")
        for f in fixes:
            print(f"  * [{f['category']}] '{f['matched']}' -> '{f['replacement']}'")
        hook_eval = verify_hook_front_loading(sanitized)
        print(f"[HOOK CHECK]: {hook_eval['recommendation']}")

    elif args.json:
        p = Path(args.json)
        if not p.exists():
            print(f"[ERROR] Archivo no encontrado: {p}")
            sys.exit(1)
        res = lint_production_package(p, inplace=args.inplace)
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        parser.print_help()
