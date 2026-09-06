import os
import sys
import shutil
import argparse
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def init_creator():
    parser = argparse.ArgumentParser(description="Inicializador de Nuevo Creador / Avatar para UGC Production Engine")
    parser.add_argument("--name", required=True, help="Nombre del creador (ej: 'Sofia Torres')")
    parser.add_argument("--brand", required=True, help="Nombre de la marca (ej: 'GlowLab')")
    parser.add_argument("--age", type=int, default=45, help="Edad del avatar (default: 45)")
    parser.add_argument("--gender", default="female", help="Género del avatar ('female' / 'male')")
    parser.add_argument("--niche", default="Skincare / Cuidado de la piel", help="Nicho de la marca")
    parser.add_argument("--keyword", default="GLOW", help="Keyword predeterminada para ManyChat")

    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parent.parent
    template_dir = base_dir / "_CREATOR_TEMPLATE"
    
    if not template_dir.exists():
        print(f"Error: No se encontró la plantilla en {template_dir}")
        sys.exit(1)

    creator_folder_name = f"{args.name} - {args.brand}"
    target_dir = base_dir / creator_folder_name

    if target_dir.exists():
        print(f"Aviso: El directorio '{creator_folder_name}' ya existe en {target_dir}")
        sys.exit(1)

    print(f"--> Creando espacio de trabajo para '{args.name}' ({args.brand})...")
    shutil.copytree(template_dir, target_dir)

    # Personalizar creator_profile.yaml
    profile_file = target_dir / "creator_profile.yaml"
    if profile_file.exists():
        content = profile_file.read_text(encoding="utf-8")
        content = content.replace('"Nombre del Creador"', f'"{args.name}"')
        content = content.replace("age: 47", f"age: {args.age}")
        content = content.replace('"female"', f'"{args.gender}"')
        content = content.replace('"Nombre de la Marca"', f'"{args.brand}"')
        content = content.replace('"Skincare / Cuidado de la piel"', f'"{args.niche}"')
        content = content.replace('"YOUTHFUL"', f'"{args.keyword}"')
        profile_file.write_text(content, encoding="utf-8")

    # Personalizar y renombrar CHARACTER_DNA_TEMPLATE.md
    char_dir = target_dir / "02_AVATAR_ASSETS" / "01_Character"
    old_dna = char_dir / "CHARACTER_DNA_TEMPLATE.md"
    new_dna_name = f"{args.name.upper().replace(' ', '_')}_CHARACTER_DNA.md"
    new_dna = char_dir / new_dna_name

    if old_dna.exists():
        dna_content = old_dna.read_text(encoding="utf-8")
        dna_content = dna_content.replace("[NOMBRE_CREADOR]", args.name)
        dna_content = dna_content.replace("[Nombre Creador]", args.name)
        dna_content = dna_content.replace("[Nombre]", args.name)
        dna_content = dna_content.replace("[NOMBRE_MARCA]", args.brand)
        dna_content = dna_content.replace("[Edad]", str(args.age))
        dna_content = dna_content.replace("[Arquetipo]", "Mirror + Convert")
        new_dna.write_text(dna_content, encoding="utf-8")
        old_dna.unlink()

    print(f"\n[OK] ¡Creador '{creator_folder_name}' inicializado con éxito!")
    print(f"Ubicación: {target_dir}")
    print(f"\nSiguientes pasos recomendados:")
    print(f"1. Generar fotos de referencia y guardarlas en: '{creator_folder_name}/02_AVATAR_ASSETS/01_Character/'")
    print(f"2. Ajustar el catálogo propio en: '{creator_folder_name}/PRODUCT_CATALOG.yaml'")
    print(f"3. Colocar videos de referencia en: '{creator_folder_name}/03_INBOX_REFERENCES/'")

if __name__ == "__main__":
    init_creator()
