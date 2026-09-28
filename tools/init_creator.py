import os
import re
import sys
import shutil
import argparse
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ARCHETYPES = ["Especialista", "Espejo", "Familiar", "Insider", "Convertido"]
PRODUCT_TYPES = ["physical", "digital", "none"]


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
    parser.add_argument("--product-type", choices=PRODUCT_TYPES, default=None, dest="product_type",
                         help="Tipo de producto: 'physical' (físico), 'digital' (ebooks/guías/cursos), 'none' (servicios/marca personal)")
    parser.add_argument("--no-product", action="store_true", dest="no_product",
                         help="Omitir producto físico (equivalente a --product-type none o digital)")
    parser.add_argument("--digital-product-name", default="", dest="digital_product_name",
                         help="Nombre del producto digital si aplica (ej: 'Guía de Recetas Naturales (PDF)')")
    parser.add_argument("--ethnicity", default="Caucasian", help="Etnia / rasgos visuales (ej: 'Caucasian', 'Latina / Hispanic', 'African American')")
    parser.add_argument("--avatar-prompt", default="", dest="avatar_prompt", help="Prompt canónico de imagen para el Character DNA")
    parser.add_argument("--environment-prompt", default="", dest="environment_prompt", help="Prompt canónico de locación para el Environment DNA")
    parser.add_argument("--environment-type", default="", dest="environment_type", help="Tipo de locación (ej: 'luxury salon', 'modern domestic kitchen', 'aesthetic clinic')")
    return parser


def build_character_dna_prompt(name: str, age: int, gender: str, archetype: str, niche: str,
                               ethnicity: str = "Caucasian", custom_style: str = "") -> str:
    """Construye el Master Image Prompt canónico de 9:16 para el Character DNA."""
    gen_noun = "woman" if gender == "female" else "man"
    pronoun = "She" if gender == "female" else "He"

    if archetype == "Especialista":
        hair = "a beautifully styled collarbone-length layered bob with soft controlled waves, natural ash-brown tones with subtle silver highlights" if gender == "female" else "well-groomed neat parted salt-and-pepper hair"
        wardrobe = "an elegant silk button-down blouse with rolled-up sleeves and delicate minimalist gold earrings" if gender == "female" else "a crisp linen button-down shirt with rolled sleeves"
        vibe = "Professional, confident, authoritative yet approachable expression"
    elif archetype == "Insider":
        hair = "a chic modern textured medium cut with natural highlights"
        wardrobe = "a stylish tailored blazer over a neutral silk top" if gender == "female" else "a tailored casual blazer over a fine knit crewneck"
        vibe = "Savvy, energetic, confident insider gaze"
    else:  # Espejo, Familiar, Convertido
        hair = "natural shoulder-length wavy hair loosely tied in a casual half-up style with soft framing strands" if gender == "female" else "casual neatly trimmed hair"
        wardrobe = "a comfortable high-quality neutral knit sweater in soft beige and delicate discrete earrings" if gender == "female" else "a comfortable neutral henley shirt in heather gray"
        vibe = "Warm, authentic, highly relatable and trustworthy friendly expression"

    if custom_style:
        wardrobe = custom_style

    prompt = (
        f"{name}, an authentic {age}-year-old {ethnicity} {gen_noun}. "
        f"{pronoun} has {hair}. "
        f"{pronoun} has realistic, radiant mature skin with subtle fine lines, natural skin texture, visible fine pores, and minimal flattering natural makeup. "
        f"Wearing {wardrobe}. "
        f"{vibe}. "
        f"Medium close-up portrait, high-end warm ambient lighting, 8k resolution, photorealistic portrait, shot on modern smartphone lens, zero CGI, zero plastic sheen."
    )
    return prompt


def build_environment_dna_prompt(brand_name: str, niche: str, env_type: str = "", env_style: str = "") -> str:
    """Construye el Master Environment Prompt canónico para el Environment DNA."""
    n_lower = niche.lower()
    if not env_type:
        if "hair" in n_lower or "capilar" in n_lower:
            env_type = "high-end luxury boutique hair salon interior"
            details = "warm beige plaster walls, fluted walnut wood styling counters with tall vertical oval mirrors edged in a soft golden backlit glow, cream styling chairs, brass globe chandeliers, polished cream marble floors"
        elif "skin" in n_lower or "derma" in n_lower or "belleza" in n_lower:
            env_type = "modern aesthetic dermatology clinic consultation studio"
            details = "warm limestone and white oak architectural elements, soft cove lighting, minimalist marble console with discreet frosted glass bottles, large arched window with natural diffused daylight"
        elif "receta" in n_lower or "cocina" in n_lower or "salud" in n_lower or "nutri" in n_lower:
            env_type = "warm, upscale domestic open-plan kitchen and dining area"
            details = "polished white quartzite countertops, warm natural oak wood cabinetry, subtle brass pendant lights, a bowl of fresh ingredients in background, soft morning natural window light"
        elif "finanza" in n_lower or "negocio" in n_lower or "marketing" in n_lower:
            env_type = "modern high-end home executive office"
            details = "fluted dark wood paneling, warm ambient library lighting, a sleek walnut desk with a notebook and brass reading lamp, large window overlooking garden"
        else:
            env_type = "contemporary minimalist lifestyle studio"
            details = "warm textured plaster walls, organic oak furniture, potted fiddle-leaf fig, soft linen drapes with warm morning sunlight"
    else:
        details = env_style or "clean architectural elements, warm ambient illumination, textured materials, elegant photorealistic interior"

    prompt = (
        f"{brand_name} Studio, a {env_type} with {details}. "
        f"Warm, soft, flattering ambient lighting, architectural interior photography, elegant cinematic depth of field, 8k resolution, zero people in frame."
    )
    return prompt


def substitute_profile_fields(content: str, *, name: str, brand: str, age: int, gender: str,
                               archetype: str, niche: str, keyword: str, target_audience: str,
                               product_type: str = "physical",
                               has_physical_product: bool = True,
                               digital_product_name: str = "") -> str:
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

    # Configurar product_type y has_physical_product
    prod_val = "true" if product_type == "physical" and has_physical_product else "false"
    if "has_physical_product:" in content:
        content = re.sub(r'(?m)^(\s*has_physical_product:\s*).+', rf'\g<1>{prod_val}', content)
    else:
        content = content.replace(f'niche: "{niche}"', f'niche: "{niche}"\n  has_physical_product: {prod_val}')

    if "product_type:" in content:
        content = re.sub(r'(?m)^(\s*product_type:\s*).+', rf'\g<1>"{product_type}"', content)
    else:
        content = re.sub(r'(?m)^(\s*has_physical_product:\s*.+)', rf'\g<1>\n  product_type: "{product_type}"', content)

    if product_type == "digital" and digital_product_name:
        if "digital_product_name:" in content:
            content = re.sub(r'(?m)^(\s*digital_product_name:\s*).+', rf'\g<1>"{digital_product_name}"', content)
        else:
            content = re.sub(r'(?m)^(\s*product_type:\s*.+)', rf'\g<1>\n  digital_product_name: "{digital_product_name}"', content)

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

    # Determine product type
    if args.product_type:
        product_type = args.product_type
    elif args.no_product:
        product_type = "none"
    else:
        product_type = "physical"

    has_physical_product = (product_type == "physical")

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

    # Asegurar explícitamente la creación de todos los directorios 01 a 06
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
            name=args.name,
            brand=brand_name,
            age=args.age,
            gender=args.gender,
            archetype=args.archetype,
            niche=args.niche,
            keyword=args.keyword,
            target_audience=args.target_audience,
            product_type=product_type,
            has_physical_product=has_physical_product,
            digital_product_name=args.digital_product_name,
        )
        profile_file.write_text(content, encoding="utf-8")

    # Personalizar PRODUCT_CATALOG.yaml según tipo de producto
    cat_file = target_dir / "PRODUCT_CATALOG.yaml"
    if cat_file.exists():
        if product_type == "digital":
            d_name = args.digital_product_name or f"Guía Digital / Recetario de {args.niche}"
            digital_content = f"""# =======================================================
# BRAND PRODUCT CATALOG (MODO PRODUCTO DIGITAL)
# =======================================================
# Este avatar vende/ofrece productos digitales (Ebooks, Guías PDF, Cursos, Recetarios, Suscripciones).
# Los prompts de video NO muestran frascos físicos en mano; la conversión se hace vía ManyChat
# para enviar el link de acceso o descarga del recurso digital.

product_type: digital
has_physical_product: false
has_digital_product: true

digital_products:
  - id: "DIGITAL_001"
    name: "{d_name}"
    format: "PDF / Guía Digital"
    manychat_keyword: "{args.keyword}"
    delivery_message: "¡Aquí tienes tu {d_name}! Haz clic en el enlace para descargar."
"""
            cat_file.write_text(digital_content, encoding="utf-8")
        elif product_type == "none":
            no_prod_content = """# =======================================================
# BRAND PRODUCT CATALOG (MODO SIN PRODUCTO FÍSICO)
# =======================================================
# Este avatar opera en modo sin producto físico (marca personal, educación, servicios o recetas).
# Los prompts I2V y de imagen omiten frascos, empaques o aplicaciones de producto.

product_type: none
has_physical_product: false
has_digital_product: false
products: []
"""
            cat_file.write_text(no_prod_content, encoding="utf-8")

    # Generar Prompts Canónicos
    char_prompt = args.avatar_prompt or build_character_dna_prompt(
        name=args.name,
        age=args.age,
        gender=args.gender,
        archetype=args.archetype,
        niche=args.niche,
        ethnicity=args.ethnicity,
    )

    env_prompt = args.environment_prompt or build_environment_dna_prompt(
        brand_name=brand_name,
        niche=args.niche,
        env_type=args.environment_type,
    )

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

        # Inyectar el Prompt Anchor Verbatim en la Sección 6
        section6_block = f"## 6. PROMPT ANCHOR (VERBATIM)\n\n```text\n{char_prompt}\n```"
        if re.search(r"##\s*6\..*?```text.*?```", dna_content, re.DOTALL):
            dna_content = re.sub(r"##\s*6\..*?```text.*?```", section6_block, dna_content, flags=re.DOTALL)
        else:
            dna_content += f"\n\n{section6_block}\n"

        new_dna.write_text(dna_content, encoding="utf-8")
        old_dna.unlink()

    # Personalizar y renombrar ENVIRONMENT_DNA_TEMPLATE.md (locacion constante de la marca)
    env_dir = target_dir / "02_AVATAR_ASSETS" / "02_Environments"
    old_env = env_dir / "ENVIRONMENT_DNA_TEMPLATE.md"
    new_env_name = f"{brand_name.upper().replace(' ', '_')}_ENVIRONMENT_DNA.md"
    new_env = env_dir / new_env_name

    if old_env.exists():
        env_content = old_env.read_text(encoding="utf-8")
        env_content = env_content.replace("[NOMBRE_MARCA]", brand_name)

        # Inyectar el Environment Prompt Anchor Verbatim en la Sección 1
        section1_env = f"## 1. ENVIRONMENT PROMPT ANCHOR VERBATIM\n\n```text\n{env_prompt}\n```"
        if re.search(r"##\s*1\..*?```text.*?```", env_content, re.DOTALL):
            env_content = re.sub(r"##\s*1\..*?```text.*?```", section1_env, env_content, flags=re.DOTALL)
        else:
            env_content += f"\n\n{section1_env}\n"

        new_env.write_text(env_content, encoding="utf-8")
        old_env.unlink()

    print(f"\n[OK] ¡Avatar '{creator_folder_name}' inicializado con éxito!")
    print(f"Ubicación: {target_dir}")
    print(f"Modalidad: {product_type.upper()} ({'Producto Físico' if product_type == 'physical' else 'Producto Digital (Ebook/PDF)' if product_type == 'digital' else 'Marca Personal / Servicios'})")
    print(f"\nDirectorios listos:")
    print(f"  📁 01_KNOWLEDGE_BASE/")
    print(f"  📁 02_AVATAR_ASSETS/ (01_Character, 02_Environments)")
    print(f"  📁 03_INBOX_REFERENCES/")
    print(f"  📁 04_IN_PRODUCTION/")
    print(f"  📁 05_PROCESSED_DELIVERABLES/")
    print(f"  📁 06_ARCHIVE/")
    print(f"  📄 creator_profile.yaml (product_type: {product_type})")
    print(f"  📄 PRODUCT_CATALOG.yaml")
    print(f"  📄 {new_dna_name} (Prompt Anchor Verbatim configurado)")
    print(f"  📄 {new_env_name} (Environment Anchor configurado)")

    print("\n" + "=" * 70)
    print("       🎨 PROMPTS MAESTROS GENERADOS PARA GENERACIÓN DE IMÁGENES")
    print("   (Compatibles con NanoBanana, Grok-2, ChatGPT/GPT-4o, Flux y Midjourney)")
    print("=" * 70)

    print(f"\n📸 [PROMPT 1: RETRATO CANÓNICO DEL AVATAR (9:16)]")
    print(f"   Destino: Guardar imagen(es) en -> {creator_folder_name}/02_AVATAR_ASSETS/01_Character/")
    print("-" * 70)
    print("👉 Para NanoBanana / Grok-2 / ChatGPT / Flux / Leonardo (Texto Puro):")
    print(f"Candid vertical 9:16 smartphone UGC photo. {char_prompt}")
    print("\n👉 Para Midjourney:")
    print(f"{char_prompt} --ar 9:16 --v 6.1")
    print("-" * 70)

    print(f"\n🏛️ [PROMPT 2: SET / LOCACIÓN CANÓNICA]")
    print(f"   Destino: Guardar imagen(es) en -> {creator_folder_name}/02_AVATAR_ASSETS/02_Environments/")
    print("-" * 70)
    print("👉 Para NanoBanana / Grok-2 / ChatGPT / Flux / Leonardo (Texto Puro):")
    print(f"Candid vertical 9:16 architectural interior photo. {env_prompt}")
    print("\n👉 Para Midjourney:")
    print(f"{env_prompt} --ar 9:16 --v 6.1")
    print("-" * 70)
    print("=" * 70)

    return {
        "target_dir": str(target_dir),
        "character_prompt": char_prompt,
        "environment_prompt": env_prompt,
        "product_type": product_type
    }


if __name__ == "__main__":
    init_creator()
