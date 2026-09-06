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
        print(" [2] Ver estado de Creadores y Proyectos")
        print(" [3] Abrir carpeta de Plantilla Maestra (_CREATOR_TEMPLATE)")
        print(" [4] Abrir carpeta del Creador de Referencia (Rachel Bennett)")
        print(" [5] Salir")
        print("========================================================")
        choice = input("Selecciona una opcion (1-5): ").strip()

        if choice == "1":
            option_create_avatar(base_dir)
        elif choice == "2":
            option_list_status(base_dir)
        elif choice == "3":
            os.startfile(str(base_dir / "_CREATOR_TEMPLATE"))
        elif choice == "4":
            os.startfile(str(base_dir / "Rachel Bennett - Botanique"))
        elif choice == "5":
            print("\n¡Hasta luego!")
            break

if __name__ == "__main__":
    main()
