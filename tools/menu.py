import os
import sys
import subprocess
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def list_creators(base_dir: Path):
    exclude = {"_CREATOR_TEMPLATE", "auto-captions-service", "tools", "ugc-avatar-genesis", "ugc-pipeline-orchestrator", "ugc-video-beat-extractor", "ugc-viral-video-generator", "scratch", "storage", "watch", ".git", ".gemini"}
    creators = []
    for d in base_dir.iterdir():
        if d.is_dir() and d.name not in exclude and not d.name.startswith("."):
            if (d / "01_KNOWLEDGE_BASE").exists() or (d / "03_INBOX_REFERENCES").exists():
                creators.append(d)
    return creators

def option_create_avatar(base_dir: Path):
    clear_screen()
    print("========================================================")
    print("     CREAR NUEVO AVATAR / CREADOR (WIZARD GUIADO)")
    print("========================================================\n")
    name = input("1. Nombre del Creador (ej: Sofia Torres): ").strip()
    if not name:
        print("El nombre no puede estar vacío.")
        input("\nPresiona ENTER para volver..."); return

    brand = input("2. Nombre de la Marca (ej: GlowLab): ").strip()
    if not brand:
        print("La marca no puede estar vacía.")
        input("\nPresiona ENTER para volver..."); return

    age_str = input("3. Edad del Avatar [default: 45]: ").strip()
    age = int(age_str) if age_str.isdigit() else 45

    niche = input("4. Nicho de la Marca [default: Skincare / Cuidado de la piel]: ").strip()
    if not niche: niche = "Skincare / Cuidado de la piel"

    keyword = input("5. Keyword ManyChat para CTA [default: GLOW]: ").strip()
    if not keyword: keyword = "GLOW"

    print("\n--> Inicializando nuevo espacio de trabajo...")
    cmd = [
        sys.executable,
        str(base_dir / "tools" / "init_creator.py"),
        "--name", name,
        "--brand", brand,
        "--age", str(age),
        "--niche", niche,
        "--keyword", keyword
    ]
    subprocess.run(cmd)
    input("\nPresiona ENTER para continuar...")

def option_assemble_project(base_dir: Path):
    clear_screen()
    print("========================================================")
    print("  ENSAMBLAJE AUTOMATICO + RECORTE INTELIGENTE DE SILENCIOS")
    print("========================================================\n")
    creators = list_creators(base_dir)
    all_prods = []
    for c in creators:
        prod_dir = c / "04_IN_PRODUCTION"
        if prod_dir.exists():
            for p in prod_dir.iterdir():
                if p.is_dir():
                    all_prods.append((c.name, p.name, p))

    if not all_prods:
        print("No se encontraron proyectos en producción (04_IN_PRODUCTION).")
        input("\nPresiona ENTER para volver..."); return

    print("Proyectos disponibles para ensamblar:")
    for idx, (cname, pname, _) in enumerate(all_prods, 1):
        print(f" [{idx}] {pname} ({cname})")

    choice = input(f"\nSelecciona el proyecto (1-{len(all_prods)}) o ingresa el nombre: ").strip()
    target_prod = None
    if choice.isdigit() and 1 <= int(choice) <= len(all_prods):
        target_prod = all_prods[int(choice) - 1][1]
    elif choice:
        target_prod = choice

    if not target_prod:
        input("\nOpción inválida. Presiona ENTER para volver..."); return

    print(f"\n--> Iniciando ensamblaje de {target_prod} con Smart Silence Trimming...")
    cmd = [
        sys.executable,
        str(base_dir / "tools" / "assemble_project.py"),
        "--project", target_prod
    ]
    subprocess.run(cmd)
    input("\nPresiona ENTER para continuar...")

def option_audit_qa(base_dir: Path):
    clear_screen()
    print("========================================================")
    print("        AUDITORIA DE CALIDAD QA HARNESS (7 GATES)")
    print("========================================================\n")
    creators = list_creators(base_dir)
    all_prods = []
    for c in creators:
        prod_dir = c / "04_IN_PRODUCTION"
        if prod_dir.exists():
            for p in prod_dir.iterdir():
                if p.is_dir():
                    all_prods.append((c.name, p.name, p))

    if not all_prods:
        print("No se encontraron proyectos en producción (04_IN_PRODUCTION).")
        input("\nPresiona ENTER para volver..."); return

    print("Proyectos disponibles para auditar:")
    for idx, (cname, pname, _) in enumerate(all_prods, 1):
        print(f" [{idx}] {pname} ({cname})")

    choice = input(f"\nSelecciona el proyecto (1-{len(all_prods)}) o ingresa el nombre: ").strip()
    target_prod = None
    if choice.isdigit() and 1 <= int(choice) <= len(all_prods):
        target_prod = all_prods[int(choice) - 1][1]
    elif choice:
        target_prod = choice

    if not target_prod:
        input("\nOpción inválida. Presiona ENTER para volver..."); return

    print(f"\n--> Ejecutando QA Harness para {target_prod}...")
    cmd = [
        sys.executable,
        str(base_dir / "tools" / "ugc_harness.py"),
        "--project", target_prod
    ]
    subprocess.run(cmd)
    input("\nPresiona ENTER para continuar...")

def option_list_status(base_dir: Path):
    clear_screen()
    print("========================================================")
    print("           ESTADO DE CREADORES Y PROYECTOS")
    print("========================================================\n")
    creators = list_creators(base_dir)
    if not creators:
        print("No se encontraron carpetas de creadores activas.")
    else:
        for idx, c in enumerate(creators, 1):
            inbox_dir = c / "03_INBOX_REFERENCES"
            prod_dir = c / "04_IN_PRODUCTION"
            deliv_dir = c / "05_PROCESSED_DELIVERABLES"

            inbox_vids = list(inbox_dir.glob("*/*.mp4")) if inbox_dir.exists() else []
            prods = [p for p in prod_dir.iterdir() if p.is_dir()] if prod_dir.exists() else []
            delivs = [d for d in deliv_dir.iterdir() if d.is_dir()] if deliv_dir.exists() else []

            print(f"[{idx}] {c.name}")
            print(f"    - Videos en Inbox pendientes: {len(inbox_vids)}")
            print(f"    - Proyectos en produccion:   {len(prods)}")
            print(f"    - Entregables completados:    {len(delivs)}")
            print("-" * 50)
    input("\nPresiona ENTER para volver...")

def main():
    base_dir = Path(__file__).resolve().parent.parent
    while True:
        clear_screen()
        print("========================================================")
        print("       UGC PRODUCTION STUDIO — CENTRO DE CONTROL")
        print("========================================================")
        print(" [1] Crear un nuevo Avatar / Creador")
        print(" [2] Ensamblar Video (Smart Silence Trimming + Subtitulado)")
        print(" [3] Auditar Proyecto con QA Harness (7 Gates)")
        print(" [4] Ver estado de Creadores y Proyectos")
        print(" [5] Abrir carpeta de Plantilla Maestra (_CREATOR_TEMPLATE)")
        print(" [6] Abrir carpeta de un Creador / Avatar")
        print(" [7] Salir")
        print("========================================================")
        choice = input("Selecciona una opcion (1-7): ").strip()

        if choice == "1":
            option_create_avatar(base_dir)
        elif choice == "2":
            option_assemble_project(base_dir)
        elif choice == "3":
            option_audit_qa(base_dir)
        elif choice == "4":
            option_list_status(base_dir)
        elif choice == "5":
            if os.name == "nt":
                os.startfile(str(base_dir / "_CREATOR_TEMPLATE"))
        elif choice == "6":
            creators = [d for d in base_dir.iterdir() if d.is_dir() and d.name != "_CREATOR_TEMPLATE" and (d / "01_KNOWLEDGE_BASE").exists()]
            if not creators:
                print("\nNo se encontraron carpetas de Creadores creadas.")
                input("Presiona ENTER...")
            elif len(creators) == 1:
                if os.name == "nt":
                    os.startfile(str(creators[0]))
            else:
                print("\nCreadores disponibles:")
                for i, c in enumerate(creators, 1):
                    print(f" [{i}] {c.name}")
                c_idx = input(f"Selecciona creador (1-{len(creators)}): ").strip()
                if c_idx.isdigit() and 1 <= int(c_idx) <= len(creators):
                    if os.name == "nt":
                        os.startfile(str(creators[int(c_idx) - 1]))
        elif choice == "7":
            print("\n¡Hasta luego!")
            break

if __name__ == "__main__":
    main()
