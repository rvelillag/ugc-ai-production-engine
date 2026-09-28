"""Compila video_motion_prompt_i2v desde el action_timeline (plantilla canónica de CLAUDE.md, Fase 3 punto 6)."""
import argparse
import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REALISM = (
    "Natural realistic hand movements. No cuts. No exaggerated acting. "
    "Authentic unretouched smartphone UGC camera feel, natural room lighting, zero CGI or plastic sheen. "
    "Skin/Hair Condition Lock: The creator must always be depicted with healthy, glowing, flawless skin and hair in the aspirational after-state, preserving natural visible pore texture. "
    "Application Lock: Any product applied glides on invisibly and translucent, without artificial white cast, chalkiness, or cakey residue. "
    "UGC Realism: Phone propped at eye level with subtle natural handheld micro-shake, relaxed open-palm gestures, and unhurried tactile prop handling."
)
DEFAULT_SFX = "Natural room ambience with subtle sounds of the props being handled."

# ... helper functions ...


def _load_dna_descriptor(json_path: Path) -> str | None:
    """Read the PROMPT ANCHOR VERBATIM block from the brand's *_CHARACTER_DNA.md.

    Walks up from json_path until it finds 02_AVATAR_ASSETS/01_Character/. Strips the avatar's
    full name from the descriptor per CLAUDE.md anti-filter rule (Fase 3, punto 6 header).
    Raises ValueError if a DNA file exists but cannot be parsed, to prevent silent fallback bugs.
    Returns None only if no DNA directory or file exists.
    """
    for parent in json_path.resolve().parents:
        dna_dir = parent / "02_AVATAR_ASSETS" / "01_Character"
        if dna_dir.is_dir():
            dna_files = list(dna_dir.glob("*_CHARACTER_DNA.md"))
            if not dna_files:
                return None
            text = dna_files[0].read_text(encoding="utf-8")
            m = re.search(r"##\s*6\..*?VERBATIM.*?```text\s*\n(.*?)```", text, re.DOTALL | re.IGNORECASE)
            if not m:
                # Flexible fallback pattern for variations in heading
                m = re.search(r"##[^\n]*(?:VERBATIM|PROMPT ANCHOR)[^\n]*\n.*?```text\s*\n(.*?)```", text, re.DOTALL | re.IGNORECASE)
            if not m:
                raise ValueError(
                    f"[ERROR DNA] Archivo de Character DNA encontrado ({dna_files[0]}) "
                    "pero no contiene la sección canónica obligatoria con bloque de texto: "
                    "'## 6. PROMPT ANCHOR (VERBATIM)' con ```text ... ```. "
                    "Corrige el formato del archivo de DNA."
                )
            raw = m.group(1).strip()
            # Strip "First Last, " prefix — never inject full names into generative prompts
            stripped = re.sub(r"^[A-Z][a-zA-ZÀ-ÖØ-öø-ÿ]+(?:\s+[A-Z][a-zA-ZÀ-ÖØ-öø-ÿ]+)+,\s*", "", raw)
            return (stripped[0].upper() + stripped[1:]) if stripped else None
    return None


def _load_environment_descriptor(json_path: Path) -> str | None:
    """Read the ENVIRONMENT PROMPT ANCHOR VERBATIM block from the brand's *_ENVIRONMENT_DNA.md.

    The brand's location (e.g. the salon) is a constant across videos, like the avatar.
    Raises ValueError if an environment file exists but cannot be parsed.
    Returns None if the brand has no environment DNA (older creators): the chunk's own environment text is used.
    """
    for parent in json_path.resolve().parents:
        env_dir = parent / "02_AVATAR_ASSETS" / "02_Environments"
        if env_dir.is_dir():
            files = list(env_dir.glob("*_ENVIRONMENT_DNA.md"))
            if not files:
                return None
            pattern = r"##[^\n]*VERBATIM[^\n]*\n.*?```text\s*\n(.*?)```"
            text = files[0].read_text(encoding="utf-8")
            m = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if not m:
                # Flexible fallback
                m = re.search(r"##[^\n]*(?:VERBATIM|PROMPT ANCHOR|ENVIRONMENT ANCHOR)[^\n]*\n.*?```text\s*\n(.*?)```", text, re.DOTALL | re.IGNORECASE)
            if not m:
                raise ValueError(
                    f"[ERROR ENVIRONMENT DNA] Archivo encontrado ({files[0]}) pero no contiene "
                    "el bloque obligatorio ```text ... ``` bajo una cabecera VERBATIM."
                )
            return m.group(1).strip() if m else None
    return None


def _as_noun_phrase(outfit: str) -> str:
    """Make a free-text outfit read naturally after 'She is wearing': lowercase first word, add an article, join the last item with 'and'."""
    text = outfit.strip().rstrip(".")
    if not re.match(r"(?i)(a|an|the|her)\s", text):
        text = text[:1].lower() + text[1:]
        text = ("an " if text[:1] in "aeiou" else "a ") + text
    head, sep, last = text.rpartition(", ")
    if sep and " and " not in text:
        if len(last.split()) == 1:  # a lone noun such as "ring" needs its article
            last = "a " + last
        text = f"{head}, and {last}"
    return text


def _apply_outfit_override(descriptor: str, json_path: Path) -> str:
    """Replace the DNA's wardrobe/props sentences with the outfit confirmed in checkpoint1.json.

    The DNA block hard-codes a base wardrobe (blouse + apron + shears); the outfit chosen in
    Checkpoint 1.B must win. Looks for checkpoint1.json in the project dir (json_path's parent
    or grandparent). Returns the descriptor unchanged if there is no checkpoint/outfit or the
    DNA has no "She is wearing ..." sentence.
    """
    for base in (json_path.resolve().parent, json_path.resolve().parent.parent):
        cp_path = base / "checkpoint1.json"
        if cp_path.is_file():
            outfit = (json.loads(cp_path.read_text(encoding="utf-8")).get("outfit") or "").strip().rstrip(".")
            break
    else:
        return descriptor
    pattern = r"She is wearing[^.]*\.(?:\s*She is holding[^.]*\.)?"
    if outfit and re.search(pattern, descriptor):
        descriptor = re.sub(pattern, lambda _: f"She is wearing {_as_noun_phrase(outfit)}.", descriptor, count=1)
    # Remove any hardcoded salon background from avatar identity so the environment lock governs background
    descriptor = re.sub(r",?\s*high-end luxury hair salon background with warm lighting", "", descriptor, flags=re.IGNORECASE)
    return descriptor


def time_marker(t0: float, t1: float) -> str:
    return f"{t0:g}–{t1:g}s"


def compile_i2v_prompt(pkg: dict, chunk: dict) -> str:
    env = chunk["composition_audit"]["environment_background"].rstrip(".")
    if pkg.get("environment_descriptor"):
        # Brand-locked location; the chunk's environment text only says which area/angle of the set is framed.
        env = f"{pkg['environment_descriptor'].rstrip('.')}. In this clip, framed on: {env}"
    # No usar avatar_name (nombre y apellido) en el prompt literal: combinado con lenguaje
    # hiperrealista, dispara los filtros de "personas destacadas/reales" de Veo3/Kling. Se usa
    # el descriptor físico sin nombre; avatar_name queda solo para continuidad/documentación.
    identity = pkg.get("avatar_visual_descriptor") or f"a {pkg['avatar_age']}-year-old woman"
    identity = identity[:1].upper() + identity[1:] if identity else identity
    # If identity is a self-contained DNA block (ends with punctuation), it already carries
    # wardrobe info — appending ", wearing wardrobe_assigned" would be redundant.
    # Only add the wardrobe suffix for short descriptors that don't include clothing.
    if identity.rstrip().endswith((".", "!", "?")):
        identity_clause = identity.rstrip()
    else:
        identity_clause = f"{identity}, wearing {pkg['wardrobe_assigned']}"
    secondary = "".join(
        f" Secondary character ({c['role']}), identical in every clip: {c['descriptor'].rstrip('.')}."
        for c in pkg.get("secondary_characters", []))
    if chunk.get("secondary_state") and pkg.get("secondary_characters"):
        secondary += f" In this clip: {chunk['secondary_state'].rstrip('.')}."
    header = (
        f"Raw unedited vertical 9:16 smartphone UGC video recorded on iPhone 15 Pro 24mm f/1.8 main camera. Subtle natural handheld breathing motion, authentic natural lighting, no CGI. Use the canonical {env}. "
        f"{identity_clause.rstrip('.')}.{secondary} "
        "Preserve her identity, clothing, lighting, environment, table position, props and camera style "
        "throughout the entire clip, and keep every other person's face, hair and clothing identical."
    )
    lines = ["*ACTION:*"]
    spoke = False
    for step in chunk["action_timeline"]:
        line = f"{time_marker(step['t0'], step['t1'])}: {step['action'].rstrip('.')}"
        if step.get("dialogue"):
            line += f', {"while continuing" if spoke else "and says"}: "{step["dialogue"]}"'
            spoke = True
        lines.append(line)
    sfx = chunk.get("sfx") or DEFAULT_SFX
    return "\n\n".join([header, "\n\n".join(lines), REALISM, f"*SFX:* {sfx}"])


MJ_LOCK_MARKS = ("LOCKS (", "SECONDARY CHARACTERS (lock")


def lock_first_frame_prompt(pkg: dict, chunk: dict) -> str:
    """Append the identity locks to the Midjourney prompt (idempotent), before the --ar params.

    Avatar and environment are brand constants (from the DNA files); secondary characters are
    constant within this video. The hand-written prompt should only describe the scene.
    Enforces authentic iPhone raw candid parameters (--ar 9:16 --style raw --v 6.1).
    """
    prompt = chunk.get("midjourney_prompt_9_16", "")
    # Strip artificial AI buzzwords
    prompt = re.sub(r",?\s*(?:8k\s*resolution|photorealistic(?:\s*portrait)?|hyper-realistic)", "", prompt, flags=re.IGNORECASE)
    parts = []
    if pkg.get("avatar_visual_descriptor"):
        avatar_desc = re.sub(r",?\s*(?:8k\s*resolution|photorealistic(?:\s*portrait)?|hyper-realistic)", "", pkg['avatar_visual_descriptor'], flags=re.IGNORECASE)
        parts.append(f"AVATAR: {avatar_desc.rstrip('.')}.")
    if pkg.get("environment_descriptor"):
        parts.append(f"ENVIRONMENT: {pkg['environment_descriptor'].rstrip('.')}.")
    parts += [f"{c['role'].upper()}: {c['descriptor'].rstrip('.')}." for c in pkg.get("secondary_characters", [])]
    if chunk.get("secondary_state") and pkg.get("secondary_characters"):
        parts.append(f"State in this frame: {chunk['secondary_state'].rstrip('.')}.")
    if not parts or not prompt:
        return prompt
    for mark in MJ_LOCK_MARKS:
        prompt = re.sub(r"\s*" + re.escape(mark) + r".*?\.(?= --|$)", "", prompt, flags=re.DOTALL)
    # Strip existing flags if any to standardize
    head = re.sub(r"\s*--(?:ar\s+\d+:\d+|style\s+\w+|v\s+[\d.]+|s\s+\d+)\b.*", "", prompt).strip()
    return f"{head.rstrip()} LOCKS (identical in every frame and video): {' '.join(parts)} --ar 9:16 --style raw --v 6.1 --s 50"


def render_md(data: dict, json_path: Path) -> None:
    """Renders prompts_and_script_[ID].md alongside the JSON (Fase 3, CLAUDE.md)."""
    pid = data.get("project_id", json_path.stem)
    pc = data.get("post_copy", {})
    lines = [
        f"# {pid} — Prompts & Script",
        "",
        f"**Referencia:** {data.get('reference_video', '')} ({data.get('reference_duration_s', '')}s)  ",
        f"**Marca:** {data.get('brand', '')}  ",
        f"**Avatar:** {data.get('avatar_name', '')}, {data.get('avatar_age', '')}yo  ",
        f"**Tema:** {data.get('topic', '')}  ",
        f"**Wardrobe:** {data.get('wardrobe_assigned', '')}",
        "",
        "---",
        "",
        "## Audio Voice Direction Anchor",
        "",
        data.get("audio_voice_direction_anchor", ""),
        "",
        "---",
        "",
        "## Guion Completo (TTS — una sola pasada)",
        "",
        "> " + " ".join(c.get("voiceover_clean_tts", "") for c in data.get("chunks", [])),
        "",
        "---",
        "",
    ]
    for chunk in data.get("chunks", []):
        cid = chunk.get("chunk_id", "?")
        ref = chunk.get("ref_window", [0, 0])
        lines += [
            f"## Chunk {cid} — {chunk.get('beat_name', '')}",
            "",
            f"**Duración:** {chunk.get('recommended_duration_s')}s | **Palabras:** {chunk.get('word_count')} | "
            f"**Ref window:** {ref[0]}s – {ref[1]}s | **Ledger rows:** {', '.join(chunk.get('ledger_rows', []))}",
            "",
            "### Voiceover (TTS)",
            "",
            f"> {chunk.get('voiceover_clean_tts', '')}",
            "",
            "### 📸 First Frame Prompt (Midjourney / Imagen — 9:16)",
            "",
            "```text",
            chunk.get("midjourney_prompt_9_16", "").strip(),
            "```",
            "",
            f"### 🎬 Video Motion Prompt I2V (Veo3 / Kling) — ⏱️ Tiempo sugerido: {chunk.get('recommended_duration_s')}s",
            "",
            "> ⏱️ **Tiempo sugerido del video:** `" + str(chunk.get('recommended_duration_s', 5)) + " segundos`",
            "",
            "```text",
            chunk.get("video_motion_prompt_i2v", "").strip(),
            "```",
            "",
            "---",
            "",
        ]
    lines += [
        "## Post Copy",
        "",
        f"**Cover Headline:** {pc.get('cover_headline', '')}",
        "",
        f"**Title:** {pc.get('title', '')}",
        "",
        "**Caption:**",
        "",
        pc.get("caption", ""),
        "",
        f"**Hashtags:** {' '.join(pc.get('hashtags', []))}",
        "",
    ]
    md_path = json_path.parent / f"prompts_and_script_{pid}.md"
    md_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Rendered: {md_path.name}")


def compile_package(json_path: Path) -> int:
    path = Path(json_path)
    data = json.loads(path.read_text(encoding="utf-8"))

    # Sync avatar_visual_descriptor from the brand's Character DNA file.
    # The DNA is the single source of truth for visual identity across all projects;
    # whatever was hand-written in the JSON is overridden on every compile run.
    dna_descriptor = _load_dna_descriptor(path)
    if dna_descriptor:
        dna_descriptor = _apply_outfit_override(dna_descriptor, path)
        if data.get("avatar_visual_descriptor") != dna_descriptor:
            print(f"  [DNA sync] avatar_visual_descriptor updated from *_CHARACTER_DNA.md")
        data["avatar_visual_descriptor"] = dna_descriptor

    env_descriptor = _load_environment_descriptor(path)
    if env_descriptor and not data.get("environment_descriptor"):
        data["environment_descriptor"] = env_descriptor

    count = 0
    for chunk in data.get("chunks", []):
        if chunk.get("action_timeline"):
            chunk["video_motion_prompt_i2v"] = compile_i2v_prompt(data, chunk)
            chunk["midjourney_prompt_9_16"] = lock_first_frame_prompt(data, chunk)
            count += 1
    if count > 0:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        if (path.parent / "02_First_Frames").is_dir():
            (path.parent / "02_First_Frames" / path.name).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        elif path.parent.name == "02_First_Frames":
            (path.parent.parent / path.name).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        render_md(data, path)
    return count


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Compila los prompts I2V desde el action_timeline de cada chunk")
    ap.add_argument("--json", required=True, help="production_package_PROD_XXX.json")
    n = compile_package(Path(ap.parse_args().json))
    print(f"Prompts I2V compilados: {n}")
