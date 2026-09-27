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
import sys
import subprocess
import argparse
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ENGINE_ROOT = Path(__file__).resolve().parent
TOOLS_DIR = ENGINE_ROOT / "tools"


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


def cmd_new(args):
    """Crear un nuevo avatar / workspace de marca."""
    tool_args = [
        "--name", args.name,
        "--brand", args.brand,
    ]
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

    return run_tool("init_creator.py", tool_args)


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

    print("=" * 65)
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

    # new / init
    p_new = subparsers.add_parser("new", aliases=["init"], parents=[common_parser], help="Inicializar un nuevo avatar / workspace de marca")
    p_new.add_argument("--name", required=True, help="Nombre del avatar / creador (ej: 'Sofia Torres')")
    p_new.add_argument("--brand", required=True, help="Nombre de la marca (ej: 'GlowLab')")
    p_new.add_argument("--niche", default="Skincare / Cuidado de la piel", help="Nicho de la marca")
    p_new.add_argument("--age", type=int, default=45, help="Edad del avatar (default: 45)")
    p_new.add_argument("--gender", default="female", help="Genero ('female'/'male')")
    p_new.add_argument("--keyword", default="GLOW", help="Keyword ManyChat")
    p_new.add_argument("--archetype", default="Espejo", help="Arquetipo (Especialista, Espejo, Familiar, Insider, Convertido)")
    p_new.add_argument("--dest", default=None, help="Directorio destino donde crear la carpeta del avatar")
    p_new.add_argument("--target-audience", default="", help="Descripcion de audiencia objetivo")
    p_new.set_defaults(func=cmd_new)

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

    # setup-path
    p_path = subparsers.add_parser("setup-path", parents=[common_parser], help="Registrar 'ugc' en el PATH de Windows para usarlo globalmente")
    p_path.set_defaults(func=cmd_setup_path)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    if hasattr(args, "func"):
        code = args.func(args)
        sys.exit(code or 0)


if __name__ == "__main__":
    main()
