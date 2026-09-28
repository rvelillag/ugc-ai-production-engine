"""UGC AI Video Production Engine - Master CLI.

Command-line interface to execute the decoupled production engine across any creator workspace.
Usage:
  ugc new --name "Sofia Torres" --brand "GlowLab" [--niche "..."] [--dest "..."]
  ugc ingest --video "path/to/video.mp4" [--project PROD_XXX]
  ugc ledger --project PROD_XXX [--language en|es]
  ugc checkpoint1 --project PROD_XXX --scene adapt_to_brand --outfit "..." --keyword KEYWORD --headline "..."
  ugc compile --project PROD_XXX
  ugc assemble --project PROD_XXX [--language auto|es|en]
  ugc certify --project PROD_XXX [--deliverable ID] [--precheck]
  ugc status
  ugc setup-path
"""
import os
import re
import sys
import subprocess
import argparse
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ENGINE_ROOT = Path(__file__).resolve().parent
TOOLS_DIR = ENGINE_ROOT / "tools"

sys.path.insert(0, str(ENGINE_ROOT))
sys.path.insert(0, str(ENGINE_ROOT / "auto-captions-service"))


def detect_workspace(explicit_path: str = None) -> Path:
    if explicit_path:
        p = Path(explicit_path).resolve()
        if p.is_dir():
            return p
        raise FileNotFoundError(f"Workspace no encontrado: {explicit_path}")

    cwd = Path.cwd().resolve()
    for candidate in [cwd] + list(cwd.parents):
        if candidate == ENGINE_ROOT:
            break
        if (candidate / "creator_profile.yaml").exists() or (candidate / "04_IN_PRODUCTION").exists():
            return candidate

    return cwd


def run_tool(script_name: str, args: list[str], cwd: Path = None):
    script_path = TOOLS_DIR / script_name
    if not script_path.exists():
        print(f"[ERROR] Script no encontrado: {script_path}")
        sys.exit(1)

    cmd = [sys.executable, str(script_path)] + args
    result = subprocess.run(cmd, cwd=str(cwd or Path.cwd()))
    return result.returncode


def suggest_avatar_names(niche: str, gender: str) -> list[str]:
    """Genera sugerencias de nombres con alta recordación acordes al nicho."""
    niche_lower = niche.lower()
    if gender.lower() == "male":
        if any(w in niche_lower for w in ["hair", "capilar", "barba"]):
            return ["Marcus Bennett", "Julian Vance", "Mateo Silva", "Liam Ross"]
        elif any(w in niche_lower for w in ["tech", "ia", "crypto", "business", "finan"]):
            return ["David Mercer", "Adrian Holt", "Lucas Vance", "Gabriel Rios"]
        else:
            return ["Mateo Vargas", "Lucas Silva", "Daniel Rios", "Julian Vance"]
    else:
        if any(w in niche_lower for w in ["hair", "capilar", "cabello"]):
            return ["Rachel Bennett", "Camila Vega", "Chloe Mercier", "Elena Rostova"]
        elif any(w in niche_lower for w in ["skin", "piel", "glow", "dermo"]):
            return ["Sofia Torres", "Elena Rostova", "Camila Vega", "Clara Lindqvist"]
        elif any(w in niche_lower for w in ["home", "organiz", "hogar", "receta", "cocina"]):
            return ["Laura Morales", "Elena Rostova", "Valentina Rios", "Camila Vega"]
        else:
            return ["Sofia Torres", "Camila Vega", "Elena Rostova", "Valeria Silva"]


def evaluate_name(name: str, niche: str) -> str:
    """Evalúa el nombre propuesto y retorna una sugerencia optimizada si aplica."""
    clean = re.sub(r'[^a-zA-ZáéíóúÁÉÍÓÚñÑ\s]', '', name).strip()
    words = clean.split()
    if len(words) == 1:
        first = words[0].capitalize()
        return f"{first} Bennett" if "hair" in niche.lower() else f"{first} Torres"
    return clean.title()


def cmd_new(args):
    """Crear un nuevo avatar / workspace de marca."""
    tool_args = [
        "--name", args.name,
    ]
    if args.brand:
        tool_args.extend(["--brand", args.brand])
    if args.age:
        tool_args.extend(["--age", str(args.age)])
def cmd_new(args):
    """Crear un nuevo avatar / creador en avatares/ a partir de la plantilla oficial."""
    tool_args = ["--name", args.name]
    if args.brand:
        tool_args.extend(["--brand", args.brand])
    if args.age:
        tool_args.extend(["--age", str(args.age)])
    if args.gender:
        tool_args.extend(["--gender", args.gender])
    if args.niche:
        tool_args.extend(["--niche", args.niche])
    if args.keyword:
        tool_args.extend(["--keyword", args.keyword])
    if args.archetype:
        tool_args.extend(["--archetype", args.archetype])
    if args.dest:
        tool_args.extend(["--dest", args.dest])
    if args.target_audience:
        tool_args.extend(["--target-audience", args.target_audience])
    if getattr(args, "product_type", None):
        tool_args.extend(["--product-type", args.product_type])
    elif getattr(args, "no_product", False):
        tool_args.append("--no-product")
    if getattr(args, "digital_product_name", None):
        tool_args.extend(["--digital-product-name", args.digital_product_name])
    if getattr(args, "ethnicity", None):
        tool_args.extend(["--ethnicity", args.ethnicity])
    if getattr(args, "avatar_prompt", None):
        tool_args.extend(["--avatar-prompt", args.avatar_prompt])
    if getattr(args, "environment_prompt", None):
        tool_args.extend(["--environment-prompt", args.environment_prompt])
    if getattr(args, "environment_type", None):
        tool_args.extend(["--environment-type", args.environment_type])

    return run_tool("init_creator.py", tool_args)


def cmd_onboard(args):
    """Asistente interactivo guiado para dar de alta un nuevo Avatar con prompts canónicos completos."""
    print("=" * 70)
    print("      🎬 ASISTENTE DE ONBOARDING - UGC AI PRODUCTION ENGINE")
    print("=" * 70)
    print("Este asistente te guiará paso a paso para configurar tu Avatar,\n"
          "definir su producto (Físico/Digital/Servicio) y generar sus prompts maestros.\n")

    # Paso 1: Definición del Personaje
    print("\n--- PASO 1: DEFINICIÓN DEL PERSONAJE ---")
    print("  [1] Ya tengo un personaje en mente (nombre, nicho o referencias)")
    print("  [2] Deseo crear un personaje nuevo desde cero (asistencia con nombre y arquetipo)")

    choice = input("\nElige una opción [1 o 2, default: 1]: ").strip() or "1"

    name = ""
    brand = ""
    niche = ""
    archetype = "Espejo"
    age = 45
    gender = "female"
    ethnicity = "Caucasian"

    if choice == "2":
        print("\n--- CREACIÓN DESDE CERO ---")
        niche = input("¿Cuál es el nicho o temática principal? (ej: Cuidado capilar, Skincare, Finanzas, Recetas): ").strip()
        if not niche:
            niche = "Estilo de vida y bienestar"

        print("\nArquetipos disponibles:")
        for idx, arc in enumerate(["Especialista", "Espejo", "Familiar", "Insider", "Convertido"], 1):
            print(f"  [{idx}] {arc}")
        arc_choice = input("Selecciona arquetipo [1-5, default: 2 (Espejo)]: ").strip() or "2"
        arc_map = {"1": "Especialista", "2": "Espejo", "3": "Familiar", "4": "Insider", "5": "Convertido"}
        archetype = arc_map.get(arc_choice, "Espejo")

        gender_in = input("Género del avatar ('female' / 'male', default: female): ").strip().lower() or "female"
        gender = "male" if "m" in gender_in and "fe" not in gender_in else "female"

        age_in = input("Edad aproximada (default: 42): ").strip()
        age = int(age_in) if age_in.isdigit() else 42

        suggestions = suggest_avatar_names(niche, gender)
        print(f"\nSugerencias de nombres de alto impacto para nicho '{niche}':")
        for idx, s in enumerate(suggestions, 1):
            print(f"  [{idx}] {s}")
        print(f"  [{len(suggestions)+1}] Escribir otro nombre personalizado")

        name_choice = input(f"Selecciona opción [1-{len(suggestions)+1}, default: 1]: ").strip() or "1"
        if name_choice.isdigit() and 1 <= int(name_choice) <= len(suggestions):
            name = suggestions[int(name_choice) - 1]
        else:
            name = input("Ingresa el nombre deseado para el avatar: ").strip()
            if not name:
                name = suggestions[0]

        brand = input(f"Nombre de la marca o proyecto (opcional, default: '{name}'): ").strip() or name
    else:
        print("\n--- PERSONAJE EN MENTE ---")
        name = input("Ingresa el nombre del avatar (ej: Sofia Torres, Rachel Bennett): ").strip()
        while not name:
            name = input("El nombre es obligatorio. Por favor ingrésalo: ").strip()

        niche = input("¿Cuál es el nicho o temática? (default: Skincare / Cuidado de la piel): ").strip() or "Skincare / Cuidado de la piel"
        brand = input(f"Nombre de la marca o proyecto (opcional, default: '{name}'): ").strip() or name

        age_in = input("Edad aproximada (default: 45): ").strip()
        age = int(age_in) if age_in.isdigit() else 45

        gender_in = input("Género ('female' / 'male', default: female): ").strip().lower() or "female"
        gender = "male" if "m" in gender_in and "fe" not in gender_in else "female"

        print("\nArquetipos disponibles:")
        for idx, arc in enumerate(["Especialista", "Espejo", "Familiar", "Insider", "Convertido"], 1):
            print(f"  [{idx}] {arc}")
        arc_choice = input("Selecciona arquetipo [1-5, default: 2 (Espejo)]: ").strip() or "2"
        arc_map = {"1": "Especialista", "2": "Espejo", "3": "Familiar", "4": "Insider", "5": "Convertido"}
        archetype = arc_map.get(arc_choice, "Espejo")

    # Rasgos visuales / Etnia
    print("\nRasgos visuales / Etnia:")
    print("  [1] Caucasian (Piel clara, castaño/rubio/gris)")
    print("  [2] Latina / Hispanic (Piel trigueña o cálida, cabello castaño u oscuro)")
    print("  [3] African American / Black")
    print("  [4] Asian")
    print("  [5] Personalizado")
    eth_choice = input("Selecciona opción [1-5, default: 1]: ").strip() or "1"
    eth_map = {"1": "Caucasian", "2": "Latina / Hispanic", "3": "African American", "4": "Asian"}
    if eth_choice in eth_map:
        ethnicity = eth_map[eth_choice]
    elif eth_choice == "5":
        ethnicity = input("Ingresa la etnia / rasgos deseados: ").strip() or "Caucasian"
    else:
        ethnicity = "Caucasian"

    # Paso 2: Requisitos de Producto (Físico, Digital o Servicio)
    print("\n--- PASO 2: MODALIDAD DE PRODUCTO ---")
    print("Selecciona el tipo de oferta o producto que promocionará el avatar:")
    print("  [1] Producto Físico (Cosméticos, goteros, cremas, botellas, packaging visible en mano)")
    print("  [2] Producto Digital (Ebook, Guía PDF, Curso online, Recetario digital, Suscripción)")
    print("  [3] Sin Producto / Marca Personal & Servicios (Educación pura, tips, recetas caseras)")

    prod_choice = input("\nElige una opción [1, 2 o 3, default: 1]: ").strip() or "1"
    product_type = "physical"
    digital_product_name = ""

    if prod_choice == "2":
        product_type = "digital"
        default_dig = f"Guía Digital de {niche} (PDF)"
        digital_product_name = input(f"Nombre del producto digital (default: '{default_dig}'): ").strip() or default_dig
        print(f"  -> Modo PRODUCTO DIGITAL configurado: '{digital_product_name}'. Los videos enfocarán valor educativo y la conversión será vía ManyChat.")
    elif prod_choice == "3":
        product_type = "none"
        print("  -> Modo SIN PRODUCTO configurado: los prompts omitirán frascos, botellas y empaques físicos.")
    else:
        product_type = "physical"
        print("  -> Modo PRODUCTO FÍSICO configurado: se generará plantilla de catálogo para cosméticos / envases.")

    # Paso 3: Entorno / Set de Grabación
    print("\n--- PASO 3: ENTORNO & LOCACIÓN CANÓNICA ---")
    print("Selecciona el set principal donde grabará el avatar:")
    print("  [1] Salón de Belleza / Studio de Peluquería Boutique (Fluted walnut wood, golden mirrors, marble)")
    print("  [2] Cocina Moderna y Elegante (Open-plan, quartzite counters, natural oak, warm window light)")
    print("  [3] Consultorio Médico / Clínica Estética Minimalista (Warm limestone, white oak, soft cove lights)")
    print("  [4] Oficina Ejecutiva / Estudio Profesional (Fluted dark wood, sleek desk, warm reading lamp)")
    print("  [5] Estudio Minimalista de Lifestyle (Textured plaster, organic oak, warm linen drapes)")
    print("  [6] Personalizado (Escribir descripción personalizada)")

    env_choice = input("\nElige una opción [1-6, default según nicho]: ").strip()
    environment_type = ""
    if env_choice == "1":
        environment_type = "high-end luxury boutique hair salon interior"
    elif env_choice == "2":
        environment_type = "warm, upscale domestic open-plan kitchen and dining area"
    elif env_choice == "3":
        environment_type = "modern aesthetic dermatology clinic consultation studio"
    elif env_choice == "4":
        environment_type = "modern high-end home executive office"
    elif env_choice == "5":
        environment_type = "contemporary minimalist lifestyle studio"
    elif env_choice == "6":
        environment_type = input("Describe el set de grabación deseado: ").strip()

    keyword = input(f"\nPalabra clave predeterminada para ManyChat (default: 'INFO' o 'GUIA'): ").strip().upper() or ("GUIA" if product_type == "digital" else "INFO")

    # Resumen y Confirmación
    avatares_root = ENGINE_ROOT.parent / "avatares"
    dest_path = (avatares_root / name) if avatares_root.is_dir() else (Path.cwd() / name)
    print("\n" + "=" * 70)
    print("RESUMEN DE CREACIÓN DEL AVATAR:")
    print(f"  Avatar:               {name} ({age} años, {gender}, {ethnicity})")
    print(f"  Marca / Proyecto:     {brand}")
    print(f"  Nicho:                {niche}")
    print(f"  Arquetipo:            {archetype}")
    print(f"  Modalidad Producto:   {product_type.upper()} {f'({digital_product_name})' if digital_product_name else ''}")
    print(f"  Keyword ManyChat:     {keyword}")
    print(f"  Carpeta destino:      {dest_path}")
    print("=" * 70)

    confirm = input("\n¿Proceder con la inicialización? [S/N, default: S]: ").strip().upper()
    if confirm == "N":
        print("Operación cancelada por el usuario.")
        return 0

    tool_args = [
        "--name", name,
        "--brand", brand,
        "--niche", niche,
        "--archetype", archetype,
        "--age", str(age),
        "--gender", gender,
        "--ethnicity", ethnicity,
        "--keyword", keyword,
        "--product-type", product_type,
    ]
    if digital_product_name:
        tool_args.extend(["--digital-product-name", digital_product_name])
    if environment_type:
        tool_args.extend(["--environment-type", environment_type])
    if avatares_root.is_dir():
        tool_args.extend(["--dest", str(avatares_root)])

    ret = run_tool("init_creator.py", tool_args)
    if ret == 0:
        print("\n" + "*" * 70)
        print(f"🎉 ¡ONBOARDING COMPLETADO CON ÉXITO!")
        print(f"Espacio de trabajo listo en: {dest_path}")
        print(f"Copia los prompts de arriba en Midjourney / Flux para generar tus retratos y fondos.")
        print("*" * 70)
    return ret


def cmd_rename(args):
    """Renombrar un avatar de forma consistente: carpeta, creator_profile.yaml y *_CHARACTER_DNA.md."""
    import re
    new_name = args.new.strip()
    if not new_name:
        print("[ERROR] El nuevo nombre no puede estar vacío.")
        return 1

    avatares_root = ENGINE_ROOT.parent / "avatares"
    old_folder = None

    if args.old:
        candidate = avatares_root / args.old.strip()
        if candidate.is_dir():
            old_folder = candidate
        else:
            candidate_cwd = Path.cwd() / args.old.strip()
            if candidate_cwd.is_dir():
                old_folder = candidate_cwd
            else:
                candidate_rel = Path(args.old.strip()).resolve()
                if candidate_rel.is_dir():
                    old_folder = candidate_rel
    else:
        ws = detect_workspace(args.workspace)
        if (ws / "creator_profile.yaml").exists():
            old_folder = ws

    if not old_folder or not old_folder.is_dir():
        print(f"[ERROR] No se pudo encontrar el directorio del avatar '{args.old or ''}'.")
        print("Usa: ugc rename --old \"Nombre Anterior\" --new \"Nuevo Nombre\" o ejecuta desde la carpeta del avatar.")
        return 1

    old_name = old_folder.name
    new_folder = old_folder.parent / new_name

    if new_folder.exists() and new_folder.resolve() != old_folder.resolve():
        print(f"[ERROR] La carpeta de destino ya existe: {new_folder}")
        return 1

    print(f"Renombrando avatar de '{old_name}' a '{new_name}'...")

    # 1. Actualizar creator_profile.yaml
    profile_p = old_folder / "creator_profile.yaml"
    if profile_p.is_file():
        text = profile_p.read_text(encoding="utf-8")
        text = re.sub(r'(?m)^(\s*name:\s*)".*"', rf'\g<1>"{new_name}"', text)
        profile_p.write_text(text, encoding="utf-8")
        print(f"  [OK] Actualizado creator_profile.yaml con nombre '{new_name}'")

    # 2. Renombrar y actualizar *_CHARACTER_DNA.md
    char_dir = old_folder / "02_AVATAR_ASSETS" / "01_Character"
    if char_dir.is_dir():
        dna_files = list(char_dir.glob("*_CHARACTER_DNA.md"))
        new_dna_file = char_dir / f"{new_name.upper().replace(' ', '_')}_CHARACTER_DNA.md"
        for df in dna_files:
            content = df.read_text(encoding="utf-8")
            # Word-boundary replacement to avoid replacing substrings (e.g. 'Banana' -> 'BNewName')
            content = re.sub(rf"\b{re.escape(old_name)}\b", new_name, content)
            content = re.sub(rf"\b{re.escape(old_name.upper())}\b", new_name.upper(), content)
            if df.name != new_dna_file.name:
                new_dna_file.write_text(content, encoding="utf-8")
                df.unlink()
                print(f"  [OK] Renombrado DNA a: {new_dna_file.name}")
            else:
                df.write_text(content, encoding="utf-8")

    # 3. Renombrar la carpeta si el nombre cambió
    if new_folder.resolve() != old_folder.resolve():
        try:
            is_cwd = Path.cwd().resolve() == old_folder.resolve()
            if is_cwd:
                os.chdir(str(old_folder.parent))
            old_folder.rename(new_folder)
            if is_cwd:
                os.chdir(str(new_folder))
            print(f"  [OK] Carpeta renombrada con éxito a: {new_folder.name}")
        except Exception as e:
            print(f"  [WARN] No se pudo renombrar la carpeta automáticamente ({e}). Renómbrala manualmente.")

    print(f"\n[OK] Avatar renombrado exitosamente a '{new_name}'.")
    return 0


def cmd_ingest(args):
    """Fase 1: Ingesta de video de referencia y extraccion de beats."""
    tool_args = ["--video", args.video]
    if args.model:
        tool_args.extend(["--model", args.model])
    if args.language:
        tool_args.extend(["--language", args.language])
    return run_tool("scene_keyframe_extractor.py", tool_args)


def cmd_ledger(args):
    """Fase 2: Generar o actualizar borrador de reference_ledger.json."""
    tool_args = ["--project", args.project]
    if args.language:
        tool_args.extend(["--language", args.language])
    if args.model:
        tool_args.extend(["--model", args.model])
    if args.force:
        tool_args.append("--force")
    return run_tool("reference_ledger.py", tool_args)


def cmd_checkpoint1(args):
    """Fase 2.5: Registrar y confirmar Checkpoint 1."""
    tool_args = [
        "--project", args.project,
        "--scene", args.scene,
        "--outfit", args.outfit,
        "--keyword", args.keyword,
        "--headline", args.headline,
        "--confirmed-by-user",
        "--ledger-confirmed",
    ]
    if args.fidelity_target:
        tool_args.extend(["--fidelity-target", args.fidelity_target])
    if args.wps_target is not None:
        tool_args.extend(["--wps-target", str(args.wps_target)])
    if args.hook_exaggeration:
        tool_args.append("--hook-exaggeration")
    return run_tool("checkpoint1.py", tool_args)


def cmd_compile(args):
    """Fase 3: Compilar prompts I2V y Markdown desde production_package.json."""
    ws = detect_workspace(args.workspace)
    json_path = None
    if args.json:
        json_path = Path(args.json)
    elif args.project:
        # Search in workspace
        candidates = list(ws.glob(f"**/04_IN_PRODUCTION/{args.project}/production_package_*.json"))
        if not candidates:
            candidates = list(ENGINE_ROOT.glob(f"**/04_IN_PRODUCTION/{args.project}/production_package_*.json"))
        if candidates:
            json_path = candidates[0]

    if not json_path or not json_path.exists():
        print(f"[ERROR] No se encontro production_package.json para '{args.project or args.json}'.")
        sys.exit(1)

    return run_tool("prompt_compiler.py", ["--json", str(json_path)])


def cmd_assemble(args):
    """Fase 4: Ensamblar clips con Smart Silence Trimming y subtitulos."""
    tool_args = ["--project", args.project]
    if args.language:
        tool_args.extend(["--language", args.language])
    if args.start_pad is not None:
        tool_args.extend(["--start-pad", str(args.start_pad)])
    if args.end_pad is not None:
        tool_args.extend(["--end-pad", str(args.end_pad)])
    if getattr(args, "archive", False):
        tool_args.append("--archive")
    return run_tool("assemble_project.py", tool_args)


def cmd_certify(args):
    """Fase 4: Auditar con QA Harness (8/8 Gates)."""
    tool_args = ["--project", args.project]
    if args.deliverable:
        tool_args.extend(["--deliverable", args.deliverable])
    if args.precheck:
        tool_args.append("--precheck")
    if args.workspace:
        tool_args.extend(["--workspace", args.workspace])
    return run_tool("ugc_harness.py", tool_args)


def cmd_status(args):
    """Consultar estado del workspace actual o creadores disponibles."""
    ws = detect_workspace(args.workspace)
    print("=" * 65)
    print("           UGC AI PRODUCTION ENGINE - STATUS")
    print("=" * 65)
    print(f"  Motor central: {ENGINE_ROOT}")
    print(f"  Workspace activo: {ws}")

    profile = ws / "creator_profile.yaml"
    if profile.exists():
        import yaml
        try:
            data = yaml.safe_load(profile.read_text(encoding="utf-8")) or {}
            c = data.get("creator", {})
            print(f"  Creador:       {c.get('name', 'N/A')}")
            print(f"  Marca:         {data.get('brand', {}).get('name', 'N/A')}")
            print(f"  Nicho:         {data.get('brand', {}).get('niche', 'N/A')}")
            print(f"  Arquetipo:     {c.get('archetype', 'N/A')}")
            print(f"  ManyChat KW:   {data.get('manychat', {}).get('default_keyword', 'N/A')}")
        except Exception:
            pass

    prod_dir = ws / "04_IN_PRODUCTION"
    if prod_dir.exists():
        prods = [p.name for p in prod_dir.iterdir() if p.is_dir()]
        print(f"\n  Proyectos en Produccion ({len(prods)}):")
        for p in prods:
            print(f"    * {p}")

    deliv_dir = ws / "05_PROCESSED_DELIVERABLES"
    if deliv_dir.exists():
        delivs = [d.name for d in deliv_dir.iterdir() if d.is_dir()]
        print(f"\n  Entregables Certificados ({len(delivs)}):")
        for d in delivs:
            print(f"    * {d}")

    archive_dir = ws / "06_ARCHIVE"
    if archive_dir.exists():
        archived = [a.name for a in archive_dir.iterdir() if a.is_dir()]
        if archived:
            print(f"\n  Proyectos Archivados ({len(archived)}):")
            for a in archived:
                print(f"    * {a}")

    print("=" * 65)
    return 0


def cmd_archive(args):
    """Mover proyectos completados desde 04_IN_PRODUCTION hacia 06_ARCHIVE."""
    ws = detect_workspace(args.workspace)
    in_prod_dir = ws / "04_IN_PRODUCTION"
    deliverables_dir = ws / "05_PROCESSED_DELIVERABLES"
    archive_dir = ws / "06_ARCHIVE"

    if not in_prod_dir.is_dir():
        print(f"[ERROR] No se encontró la carpeta 04_IN_PRODUCTION en {ws}")
        return 1

    archive_dir.mkdir(parents=True, exist_ok=True)
    target_project = args.project.strip() if args.project else None

    projects_to_check = []
    if target_project:
        candidate = in_prod_dir / target_project
        if not candidate.is_dir():
            print(f"[ERROR] Proyecto '{target_project}' no encontrado en {in_prod_dir}")
            return 1
        projects_to_check.append(candidate)
    else:
        projects_to_check = [d for d in in_prod_dir.iterdir() if d.is_dir()]

    if not projects_to_check:
        print("[INFO] No hay proyectos en 04_IN_PRODUCTION para archivar.")
        return 0

    print("=" * 65)
    print("        📦 ARCHIVADOR DE PROYECTOS UGC FINALIZADOS")
    print("=" * 65)
    print(f"Workspace: {ws.name}")
    print(f"Destino:   {archive_dir}\n")

    archived_count = 0
    for proj in sorted(projects_to_check, key=lambda x: x.name):
        prod_name = proj.name
        name_parts = prod_name.split("_")
        has_deliverable = False
        deliv_id = None
        if len(name_parts) >= 2 and name_parts[1]:
            from tools.deliverable_naming import resolve_deliverable_id
            try:
                deliv_id = resolve_deliverable_id(ws, name_parts[1])
                deliv_path = deliverables_dir / deliv_id
                if deliv_path.is_dir() and list(deliv_path.glob("*_Final_1080x1920.mp4")):
                    has_deliverable = True
            except Exception:
                has_deliverable = False

        if not has_deliverable and not getattr(args, "force", False):
            print(f"  [OMITIDO] {proj.name} (No tiene entregable final en 05_PROCESSED_DELIVERABLES; usa --force para forzar)")
            continue

        dest = archive_dir / proj.name
        if dest.exists():
            import shutil
            shutil.rmtree(dest, ignore_errors=True)
        try:
            import shutil
            shutil.move(str(proj), str(dest))
            print(f"  [ARCHIVADO] {proj.name} -> 06_ARCHIVE/{proj.name} (Entregable: {deliv_id or 'N/A'})")
            archived_count += 1
        except Exception as e:
            try:
                import shutil
                shutil.copytree(str(proj), str(dest), dirs_exist_ok=True)
                shutil.rmtree(str(proj), ignore_errors=True)
                print(f"  [ARCHIVADO] {proj.name} -> 06_ARCHIVE/{proj.name} (Entregable: {deliv_id or 'N/A'})")
                archived_count += 1
            except Exception as e2:
                print(f"  [ERROR] No se pudo mover {proj.name}: {e2}")

    print(f"\n[OK] Total de proyectos archivados: {archived_count}")
    return 0


def cmd_doctor(args):
    """Diagnostico de salud del motor y del avatar workspace."""
    ws = detect_workspace(args.workspace)
    print("=" * 65)
    print("           UGC AI PRODUCTION ENGINE - DIAGNOSTIC DOCTOR")
    print("=" * 65)

    # 1. System dependencies check
    print("\n[+] DIAGNOSTICO DEL MOTOR (SISTEMA):")
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    py_pass = sys.version_info >= (3, 10)
    print(f"  {'[PASS]' if py_pass else '[FAIL]'} Python {py_ver} (Requerido >= 3.10)")

    try:
        from app.core.ffmpeg_utils import FFmpegLocator
        ff_bin, pr_bin = FFmpegLocator.get_binaries()
        print(f"  [PASS] FFmpeg estatico detectado ({Path(ff_bin).name})")
    except Exception as e:
        print(f"  [FAIL] FFmpeg no disponible: {e}")

    try:
        from faster_whisper import WhisperModel
        print("  [PASS] Faster-Whisper disponible")
    except Exception as e:
        print(f"  [FAIL] Faster-Whisper no disponible: {e}")

    template_ok = (ENGINE_ROOT / "_CREATOR_TEMPLATE").is_dir()
    print(f"  {'[PASS]' if template_ok else '[FAIL]'} Plantilla _CREATOR_TEMPLATE presente")

    def _audit_single_workspace(w_path: Path):
        print(f"\n[+] DIAGNOSTICO DEL WORKSPACE ({w_path.name}):")
        profile_p = w_path / "creator_profile.yaml"
        has_product = True
        if profile_p.is_file():
            print("  [PASS] creator_profile.yaml encontrado")
            import yaml
            try:
                p_data = yaml.safe_load(profile_p.read_text(encoding="utf-8")) or {}
                brand_cfg = p_data.get("brand", {})
                if brand_cfg.get("has_physical_product") is False:
                    has_product = False
            except Exception:
                pass
        else:
            print("  [WARN] Falta creator_profile.yaml")

        cat_p = w_path / "PRODUCT_CATALOG.yaml"
        if cat_p.is_file():
            if not has_product:
                print("  [PASS] PRODUCT_CATALOG.yaml (Modo sin producto físico)")
            else:
                print("  [PASS] PRODUCT_CATALOG.yaml encontrado")
        else:
            if has_product:
                print("  [WARN] Falta PRODUCT_CATALOG.yaml")
            else:
                print("  [INFO] PRODUCT_CATALOG.yaml omitido (Modo sin producto físico)")

        char_dir = w_path / "02_AVATAR_ASSETS" / "01_Character"
        dna_files = list(char_dir.glob("*_CHARACTER_DNA.md")) if char_dir.is_dir() else []
        if dna_files:
            print(f"  [PASS] Character DNA configurado ({dna_files[0].name})")
        else:
            print("  [WARN] Falta *_CHARACTER_DNA.md en 02_AVATAR_ASSETS/01_Character")

        env_dir = w_path / "02_AVATAR_ASSETS" / "02_Environments"
        env_files = list(env_dir.glob("*_ENVIRONMENT_DNA.md")) if env_dir.is_dir() else []
        if env_files:
            print(f"  [PASS] Environment DNA configurado ({env_files[0].name})")
        else:
            print("  [WARN] Falta *_ENVIRONMENT_DNA.md en 02_AVATAR_ASSETS/02_Environments")

        for d in ["01_KNOWLEDGE_BASE", "03_INBOX_REFERENCES", "04_IN_PRODUCTION", "05_PROCESSED_DELIVERABLES"]:
            exists = (w_path / d).is_dir()
            print(f"  {'[PASS]' if exists else '[WARN]'} Directorio {d}/")

    # 2. Workspace check
    avatares_dir = ws / "avatares" if (ws / "avatares").is_dir() else (ENGINE_ROOT.parent / "avatares")
    if (ws / "creator_profile.yaml").exists() or (ws / "04_IN_PRODUCTION").exists():
        _audit_single_workspace(ws)
    elif avatares_dir and avatares_dir.is_dir():
        avatars = [d for d in avatares_dir.iterdir() if d.is_dir()]
        if avatars:
            for av in avatars:
                _audit_single_workspace(av)
        else:
            print(f"\n[INFO] No hay avatares creados en {avatares_dir}. Usa 'ugc new' para crear uno.")
    else:
        _audit_single_workspace(ws)

    print("\n" + "=" * 65)
    return 0


def cmd_prompt(args):
    """Ver o copiar prompts compilados de un proyecto."""
    ws = detect_workspace(args.workspace)
    proj_dir = None
    if (ws / "04_IN_PRODUCTION" / args.project).is_dir():
        proj_dir = ws / "04_IN_PRODUCTION" / args.project
    else:
        found = list(ws.glob(f"**/04_IN_PRODUCTION/{args.project}"))
        if not found:
            found = list(ENGINE_ROOT.parent.glob(f"**/04_IN_PRODUCTION/{args.project}"))
        if found:
            proj_dir = found[0]

    if not proj_dir:
        print(f"[ERROR] Proyecto no encontrado: {args.project}")
        sys.exit(1)

    pkg_files = list(proj_dir.glob("production_package_*.json"))
    if not pkg_files:
        print(f"[ERROR] No hay production_package.json en {proj_dir}")
        sys.exit(1)

    import json
    data = json.loads(pkg_files[0].read_text(encoding="utf-8"))
    chunks = data.get("chunks", [])
    if not chunks:
        print("[ERROR] Paquete sin chunks")
        sys.exit(1)

    chunk_idx = args.chunk - 1 if args.chunk and 1 <= args.chunk <= len(chunks) else 0
    target_chunk = chunks[chunk_idx]

    cid = target_chunk.get("chunk_id", f"chunk_{chunk_idx+1}")
    prompt_i2v = target_chunk.get("video_motion_prompt_i2v", "")
    prompt_mj = target_chunk.get("midjourney_prompt_9_16", "")

    selected_text = ""
    if args.type == "first-frame":
        selected_text = prompt_mj
        print(f"\n--- PROMPT FIRST FRAME (Midjourney) [{cid}] ---")
        print(prompt_mj)
    elif args.type == "i2v":
        selected_text = prompt_i2v
        print(f"\n--- PROMPT VIDEO MOTION I2V (Kling / Veo3) [{cid}] ---")
        print(prompt_i2v)
    else:
        selected_text = f"FIRST FRAME:\n{prompt_mj}\n\nVIDEO MOTION:\n{prompt_i2v}"
        print(f"\n--- PROMPT COMPLETO [{cid}] ---")
        print(f"\n[FIRST FRAME - Midjourney]:\n{prompt_mj}")
        print(f"\n[VIDEO MOTION - Kling / Veo3]:\n{prompt_i2v}")

    if args.copy and selected_text:
        try:
            import subprocess
            subprocess.run("clip", input=selected_text, text=True, check=True)
            print("\n[OK] Prompt copiado exitosamente al portapapeles de Windows!")
        except Exception as e:
            print(f"\n[AVISO] No se pudo copiar al portapapeles: {e}")

    return 0


def cmd_setup_path(args):
    """Registrar el motor UGC en el PATH de Windows para usarlo globalmente."""
    if os.name != "nt":
        print("Este comando es exclusivo para Windows.")
        return 0

    # 1. Instalar wrapper directo en Python Scripts (disponibilidad inmediata en toda la sesion)
    scripts_dir = Path(sys.executable).parent / "Scripts"
    if scripts_dir.is_dir():
        wrapper_file = scripts_dir / "ugc.cmd"
        wrapper_content = f'@echo off\n"{sys.executable}" "{ENGINE_ROOT / "ugc.py"}" %*\n'
        wrapper_file.write_text(wrapper_content, encoding="utf-8")
        print(f"[OK] Comando 'ugc' instalado inmediatamente en: {wrapper_file}")

    # 2. Agregar directorio del motor al PATH de Usuario (persistencia permanente)
    engine_str = str(ENGINE_ROOT)
    cmd = [
        "powershell",
        "-NoProfile",
        "-Command",
        f"""
        $current = [Environment]::GetEnvironmentVariable('Path', 'User')
        if ($current -notlike '*{engine_str}*') {{
            [Environment]::SetEnvironmentVariable('Path', "$current;{engine_str}", 'User')
            Write-Host '[OK] Directorio del motor agregado al PATH de Usuario con exito!'
        }} else {{
            Write-Host '[INFO] El motor ya se encuentra registrado en tu PATH de Usuario.'
        }}
        """
    ]
    subprocess.run(cmd)
    print("\nListo. Puedes escribir 'ugc --help' desde cualquier terminal o carpeta.")
    return 0


def cmd_update(args):
    """Actualizar el motor central a la última versión de Git y verificar dependencias."""
    print("=" * 65)
    print("        🔄 ACTUALIZADOR DEL MOTOR UGC PRODUCTION ENGINE")
    print("=" * 65)
    print(f"Motor central: {ENGINE_ROOT}\n")

    if not (ENGINE_ROOT / ".git").is_dir():
        print("[ERROR] El directorio del motor no es un repositorio Git.")
        return 1

    print("[1/3] Descargando últimas actualizaciones desde GitHub (git pull origin main)...")
    res = subprocess.run(["git", "pull", "origin", "main"], cwd=str(ENGINE_ROOT))
    if res.returncode != 0:
        print("[WARN] 'git pull' no pudo completarse limpiamente.")
        return res.returncode

    print("\n[2/3] Verificando dependencias en requirements.txt...")
    req_file = ENGINE_ROOT / "requirements.txt"
    if req_file.exists():
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(req_file), "--quiet"], cwd=str(ENGINE_ROOT))
        print("  [PASS] Dependencias al día.")

    print("\n[3/3] Verificando comando global 'ugc'...")
    cmd_setup_path(args)

    print("\n" + "=" * 65)
    print("  ¡MOTOR UGC ACTUALIZADO EXITOSAMENTE A LA ÚLTIMA VERSIÓN!")
    print("=" * 65)
    print("ℹ️ Tus avatares y entregables en 'avatares/' se mantienen 100% intactos.\n")
    return 0


def main():
    common_parser = argparse.ArgumentParser(add_help=False)
    common_parser.add_argument("--workspace", default=None, help="Ruta al workspace del avatar (auto-detectado si se omite)")

    parser = argparse.ArgumentParser(
        prog="ugc",
        description="🎬 UGC AI Video Production Engine - Master CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[common_parser],
    )
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponibles")

    # onboard (asistente guiado interactivo)
    p_onboard = subparsers.add_parser("onboard", parents=[common_parser], help="Asistente interactivo guiado para dar de alta un nuevo Avatar (Regla 1 y 2)")
    p_onboard.set_defaults(func=cmd_onboard)

    # new / init (creación directa por argumentos)
    p_new = subparsers.add_parser("new", aliases=["init"], parents=[common_parser], help="Inicializar un nuevo avatar / workspace de marca")
    p_new.add_argument("--name", required=True, help="Nombre del avatar / creador (ej: 'Sofia Torres')")
    p_new.add_argument("--brand", default="", help="Nombre de la marca (opcional, default: nombre del creador)")
    p_new.add_argument("--niche", default="Skincare / Cuidado de la piel", help="Nicho de la marca")
    p_new.add_argument("--age", type=int, default=45, help="Edad del avatar (default: 45)")
    p_new.add_argument("--gender", default="female", help="Genero ('female'/'male')")
    p_new.add_argument("--keyword", default="GLOW", help="Keyword ManyChat")
    p_new.add_argument("--archetype", default="Espejo", help="Arquetipo (Especialista, Espejo, Familiar, Insider, Convertido)")
    p_new.add_argument("--dest", default=None, help="Directorio destino donde crear la carpeta del avatar")
    p_new.add_argument("--target-audience", default="", help="Descripcion de audiencia objetivo")
    p_new.add_argument("--product-type", choices=["physical", "digital", "none"], default=None, help="Tipo de producto: 'physical' (físico), 'digital' (ebooks/guías/cursos), 'none' (servicios/marca personal)")
    p_new.add_argument("--no-product", action="store_true", help="Omitir producto físico (equivalente a --product-type none)")
    p_new.add_argument("--digital-product-name", default="", help="Nombre del producto digital si aplica (ej: 'Guía de Recetas Naturales (PDF)')")
    p_new.add_argument("--ethnicity", default="Caucasian", help="Etnia / rasgos visuales del avatar")
    p_new.add_argument("--avatar-prompt", default="", help="Prompt canónico de imagen para el Character DNA")
    p_new.add_argument("--environment-prompt", default="", help="Prompt canónico de locación para el Environment DNA")
    p_new.add_argument("--environment-type", default="", help="Tipo de locación (ej: 'luxury salon', 'modern domestic kitchen')")
    p_new.set_defaults(func=cmd_new)

    # rename (renombrado consistente de carpeta, perfiles y DNA)
    p_ren = subparsers.add_parser("rename", parents=[common_parser], help="Renombrar un avatar de forma consistente (carpeta, perfiles y DNA)")
    p_ren.add_argument("--new", required=True, help="Nuevo nombre para el avatar")
    p_ren.add_argument("--old", default=None, help="Nombre actual del avatar (si se omite, se usa el workspace activo)")
    p_ren.set_defaults(func=cmd_rename)

    # ingest
    p_ingest = subparsers.add_parser("ingest", parents=[common_parser], help="Fase 1: Ingestar video de referencia y extraer beats/keyframes")
    p_ingest.add_argument("--video", required=True, help="Ruta al video .mp4 de referencia")
    p_ingest.add_argument("--model", default="medium", help="Modelo Whisper (base/small/medium)")
    p_ingest.add_argument("--language", default=None, help="Idioma del audio (en/es/auto)")
    p_ingest.set_defaults(func=cmd_ingest)

    # ledger
    p_ledger = subparsers.add_parser("ledger", parents=[common_parser], help="Fase 2: Generar borrador de reference_ledger.json")
    p_ledger.add_argument("--project", required=True, help="Nombre de la carpeta del proyecto (ej: PROD_022_xxx)")
    p_ledger.add_argument("--language", default=None, help="Idioma del audio")
    p_ledger.add_argument("--model", default="medium", help="Modelo Whisper")
    p_ledger.add_argument("--force", action="store_true", help="Sobrescribir ledger existente")
    p_ledger.set_defaults(func=cmd_ledger)

    # checkpoint1
    p_cp1 = subparsers.add_parser("checkpoint1", parents=[common_parser], help="Fase 2.5: Registrar y confirmar Checkpoint 1")
    p_cp1.add_argument("--project", required=True, help="Nombre de la carpeta del proyecto")
    p_cp1.add_argument("--scene", required=True, choices=["replicate_1to1", "adapt_to_brand", "derivative_concept"], help="Modo de escena")
    p_cp1.add_argument("--outfit", required=True, help="Descripcion del vestuario")
    p_cp1.add_argument("--keyword", required=True, help="Keyword de ManyChat")
    p_cp1.add_argument("--headline", required=True, help="Headline de portada (<= 7 palabras)")
    p_cp1.add_argument("--fidelity-target", default="full_verbatim", choices=["full_verbatim", "trim_to_min"], help="Fidelidad de guion")
    p_cp1.add_argument("--wps-target", type=float, default=None, help="WPS objetivo medido de la referencia")
    p_cp1.add_argument("--hook-exaggeration", action="store_true", help="Activar exageracion visual en el hook")
    p_cp1.set_defaults(func=cmd_checkpoint1)

    # compile
    p_compile = subparsers.add_parser("compile", parents=[common_parser], help="Fase 3: Compilar prompts I2V y renderizar Markdown")
    p_compile.add_argument("--project", default=None, help="Nombre del proyecto en 04_IN_PRODUCTION")
    p_compile.add_argument("--json", default=None, help="Ruta directa a production_package_PROD_XXX.json")
    p_compile.set_defaults(func=cmd_compile)

    # assemble
    p_assemble = subparsers.add_parser("assemble", parents=[common_parser], help="Fase 4: Ensamblar video final con Smart Silence Trimming")
    p_assemble.add_argument("--project", required=True, help="Nombre del proyecto")
    p_assemble.add_argument("--language", default="auto", help="Idioma de subtitulos")
    p_assemble.add_argument("--start-pad", type=float, default=0.12, help="Padding de silencio inicial")
    p_assemble.add_argument("--end-pad", type=float, default=0.22, help="Padding de silencio final")
    p_assemble.add_argument("--archive", action="store_true", help="Mover automáticamente a 06_ARCHIVE tras el ensamblado exitoso")
    p_assemble.set_defaults(func=cmd_assemble)

    # certify / audit
    p_cert = subparsers.add_parser("certify", aliases=["audit"], parents=[common_parser], help="Fase 4: Certificar proyecto con 8/8 QA Gates")
    p_cert.add_argument("--project", required=True, help="Nombre del proyecto")
    p_cert.add_argument("--deliverable", default=None, help="Nombre del entregable canónico (ej: Rachel022)")
    p_cert.add_argument("--precheck", action="store_true", help="Precheck rapido sin clips de video")
    p_cert.set_defaults(func=cmd_certify)

    # status
    p_stat = subparsers.add_parser("status", parents=[common_parser], help="Consultar estado del workspace y proyectos")
    p_stat.set_defaults(func=cmd_status)

    # doctor / check
    p_doc = subparsers.add_parser("doctor", aliases=["check"], parents=[common_parser], help="Diagnosticar dependencias y salud del workspace")
    p_doc.set_defaults(func=cmd_doctor)

    # prompt
    p_prompt = subparsers.add_parser("prompt", parents=[common_parser], help="Ver o copiar prompts compilados (I2V / Midjourney)")
    p_prompt.add_argument("--project", required=True, help="Nombre del proyecto (ej: PROD_022_xxx)")
    p_prompt.add_argument("--chunk", type=int, default=1, help="Numero del chunk / clip a consultar (default: 1)")
    p_prompt.add_argument("--type", default="all", choices=["all", "i2v", "first-frame"], help="Tipo de prompt a consultar")
    p_prompt.add_argument("--copy", action="store_true", help="Copiar el prompt seleccionado directamente al portapapeles")
    p_prompt.set_defaults(func=cmd_prompt)

    # setup-path
    p_path = subparsers.add_parser("setup-path", parents=[common_parser], help="Registrar 'ugc' en el PATH de Windows para usarlo globalmente")
    p_path.set_defaults(func=cmd_setup_path)

    # archive
    p_arch = subparsers.add_parser("archive", parents=[common_parser], help="Mover proyectos completados desde 04_IN_PRODUCTION hacia 06_ARCHIVE")
    p_arch.add_argument("--project", default=None, help="Nombre de un proyecto especifico a archivar (si se omite, archiva todos los completados)")
    p_arch.add_argument("--force", action="store_true", help="Forzar archivado aunque no se detecte entregable final")
    p_arch.set_defaults(func=cmd_archive)

    # update
    p_update = subparsers.add_parser("update", parents=[common_parser], help="Actualizar el motor central a la última versión de Git y verificar dependencias")
    p_update.set_defaults(func=cmd_update)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    if hasattr(args, "func"):
        code = args.func(args)
        sys.exit(code or 0)


if __name__ == "__main__":
    main()
