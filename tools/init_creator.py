import os
import re
import sys
import shutil
import argparse
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ARCHETYPES = ["Especialista", "Espejo", "Familiar", "Insider", "Convertido"]


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inicializador de Nuevo Creador / Avatar para UGC Production Engine")
    parser.add_argument("--name", required=True, help="Nombre del creador / avatar (ej: 'Sofia Torres')")
    parser.add_argument("--brand", default="", help="Nombre de la marca (ej: 'GlowLab', default: nombre del creador)")
    parser.add_argument("--age", type=int, default=45, help="Edad del avatar (default: 45)")
    parser.add_argument("--gender", default="female", help="Género del avatar ('female' / 'male')")
    parser.add_argument("--niche", default="Skincare / Cuidado de la piel", help="Nicho de la marca")
    parser.add_argument("--keyword", default="GLOW", help="Keyword predeterminada para ManyChat")
    parser.add_argument("--archetype", default="Espejo", choices=ARCHETYPES,
                         help="Tipo de personaje: " + ", ".join(ARCHETYPES))
    parser.add_argument("--dest", default=None, help="Directorio destino donde crear el espacio de trabajo (default: avatares/ o directorio actual)")
    parser.add_argument("--target-audience", default="", dest="target_audience",
                         help="Descripción de la audiencia objetivo (ej: 'Mujeres de 30 a 45 años')")
    parser.add_argument("--no-product", action="store_true", dest="no_product",
                         help="Omitir producto físico (para avatares de marca personal, servicios, educación o recetas)")
    return parser


def substitute_profile_fields(content: str, *, name: str, brand: str, age: int, gender: str,
                               archetype: str, niche: str, keyword: str, target_audience: str,
                               has_physical_product: bool = True) -> str:
    content = content.replace('"Nombre del Creador"', f'"{name}"')
    content = content.replace("age: 47", f"age: {age}")
    content = content.replace('"female"', f'"{gender}"')
    content = re.sub(r'(?m)^(\s*archetype:\s*)"[^"]*"', lambda m: f'{m.group(1)}"{archetype}"', content)
    if target_audience:
        content = re.sub(r'(?m)^(\s*target_audience:\s*)"[^"]*"', lambda m: f'{m.group(1)}"{target_audience}"', content)
    brand_val = brand if brand else name
    content = content.replace('"Nombre de la Marca"', f'"{brand_val}"')
    content = content.replace('"Skincare / Cuidado de la piel"', f'"{niche}"')
    content = content.replace('"YOUTHFUL"', f'"{keyword}"')

    # Configurar has_physical_product
    prod_val = "true" if has_physical_product else "false"
    if "has_physical_product:" in content:
        content = re.sub(r'(?m)^(\s*has_physical_product:\s*).+', rf'\g<1>{prod_val}', content)
    else:
        content = content.replace(f'niche: "{niche}"', f'niche: "{niche}"\n  has_physical_product: {prod_val}')

    return content


def init_creator():
    args = build_arg_parser().parse_args()

    base_dir = Path(__file__).resolve().parent.parent
    template_dir = base_dir / "_CREATOR_TEMPLATE"

    if not template_dir.exists():
        print(f"Error: No se encontró la plantilla en {template_dir}")
        sys.exit(1)

    brand_name = args.brand.strip() if args.brand else args.name.strip()
    creator_folder_name = args.name.strip()
    has_physical_product = not args.no_product

    # Resolver destino: priorizar avatares/ (existente o como carpeta hermana del motor)
    if args.dest:
        dest_dir = Path(args.dest)
    elif (base_dir.parent / "avatares").is_dir():
        dest_dir = base_dir.parent / "avatares"
    elif Path.cwd().name == "avatares":
        dest_dir = Path.cwd()
    elif (Path.cwd() / "avatares").is_dir():
        dest_dir = Path.cwd() / "avatares"
    elif base_dir.name.lower() in ["sistema", "ugc-ai-production-engine", "engine"]:
        dest_dir = base_dir.parent / "avatares"
        dest_dir.mkdir(parents=True, exist_ok=True)
    else:
        dest_dir = Path.cwd() / "avatares"
        dest_dir.mkdir(parents=True, exist_ok=True)

    target_dir = dest_dir / creator_folder_name

    if target_dir.exists():
        print(f"Aviso: El directorio '{creator_folder_name}' ya existe en {target_dir}")
        sys.exit(1)

    print(f"--> Creando espacio de trabajo para el avatar '{args.name}'...")
    shutil.copytree(template_dir, target_dir)

    # Asegurar explícitamente la creación de todos los directorios 01 a 05
    (target_dir / "01_KNOWLEDGE_BASE").mkdir(parents=True, exist_ok=True)
    (target_dir / "02_AVATAR_ASSETS" / "00_Reference_Input").mkdir(parents=True, exist_ok=True)
    (target_dir / "02_AVATAR_ASSETS" / "01_Character").mkdir(parents=True, exist_ok=True)
    (target_dir / "02_AVATAR_ASSETS" / "02_Environments").mkdir(parents=True, exist_ok=True)
    (target_dir / "03_INBOX_REFERENCES").mkdir(parents=True, exist_ok=True)
    (target_dir / "04_IN_PRODUCTION").mkdir(parents=True, exist_ok=True)
    (target_dir / "05_PROCESSED_DELIVERABLES").mkdir(parents=True, exist_ok=True)
    (target_dir / "06_ARCHIVE").mkdir(parents=True, exist_ok=True)

    # Personalizar creator_profile.yaml
    profile_file = target_dir / "creator_profile.yaml"
    if profile_file.exists():
        content = profile_file.read_text(encoding="utf-8")
        content = substitute_profile_fields(
            content,
            name=args.name, brand=brand_name, age=args.age, gender=args.gender,
            archetype=args.archetype, niche=args.niche, keyword=args.keyword,
            target_audience=args.target_audience,
            has_physical_product=has_physical_product,
        )
        profile_file.write_text(content, encoding="utf-8")

    # Personalizar PRODUCT_CATALOG.yaml si no muestra producto físico
    cat_file = target_dir / "PRODUCT_CATALOG.yaml"
    if not has_physical_product and cat_file.exists():
        no_prod_content = """# =======================================================
# BRAND PRODUCT CATALOG (MODO SIN PRODUCTO FÍSICO)
# =======================================================
# Este avatar opera en modo sin producto físico (marca personal, educación, servicios o recetas).
# Los prompts I2V y de imagen omiten frascos, empaques o aplicaciones de producto.

has_physical_product: false
products: []
"""
        cat_file.write_text(no_prod_content, encoding="utf-8")

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
        dna_content = dna_content.replace("[NOMBRE_MARCA]", brand_name)
        dna_content = dna_content.replace("[Edad]", str(args.age))
        dna_content = dna_content.replace("[Arquetipo]", args.archetype)
        new_dna.write_text(dna_content, encoding="utf-8")
        old_dna.unlink()

    # Personalizar y renombrar ENVIRONMENT_DNA_TEMPLATE.md (locacion constante de la marca)
    env_dir = target_dir / "02_AVATAR_ASSETS" / "02_Environments"
    old_env = env_dir / "ENVIRONMENT_DNA_TEMPLATE.md"
    if old_env.exists():
        env_slug = brand_name.upper().replace(' ', '_')
        (env_dir / f"{env_slug}_ENVIRONMENT_DNA.md").write_text(
            old_env.read_text(encoding="utf-8").replace("[NOMBRE_MARCA]", brand_name), encoding="utf-8")
        old_env.unlink()

    print(f"\n[OK] ¡Avatar '{creator_folder_name}' inicializado con éxito!")
    print(f"Ubicación: {target_dir}")
    print(f"\nDirectorios listos:")
    print(f"  📁 01_KNOWLEDGE_BASE/")
    print(f"  📁 02_AVATAR_ASSETS/ (01_Character, 02_Environments)")
    print(f"  📁 03_INBOX_REFERENCES/")
    print(f"  📁 04_IN_PRODUCTION/")
    print(f"  📁 05_PROCESSED_DELIVERABLES/")
    print(f"  📄 creator_profile.yaml (has_physical_product: {has_physical_product})")
    print(f"  📄 PRODUCT_CATALOG.yaml")
    print(f"\nSiguientes pasos recomendados:")
    print(f"1. Generar fotos de referencia y guardarlas en: '{creator_folder_name}/02_AVATAR_ASSETS/01_Character/'")
    if has_physical_product:
        print(f"2. Ajustar el catálogo propio en: '{creator_folder_name}/PRODUCT_CATALOG.yaml'")
    else:
        print("2. (Modo sin producto físico activo: prompts omitirán botellas/empaques)")
    print(f"3. Colocar videos de referencia en: '{creator_folder_name}/03_INBOX_REFERENCES/'")


if __name__ == "__main__":
    init_creator()
