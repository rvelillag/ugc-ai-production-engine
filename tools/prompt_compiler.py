"""Compila video_motion_prompt_i2v desde el action_timeline (plantilla canónica de CLAUDE.md, Fase 3 punto 6)."""
import argparse
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REALISM = "Natural realistic hand movements. No cuts. No exaggerated acting."
DEFAULT_SFX = "Natural room ambience with subtle sounds of the props being handled."


def time_marker(t0: float, t1: float) -> str:
    return f"{t0:g}–{t1:g}s"


def compile_i2v_prompt(pkg: dict, chunk: dict) -> str:
    env = chunk["composition_audit"]["environment_background"].rstrip(".")
    # No usar avatar_name (nombre y apellido) en el prompt literal: combinado con lenguaje
    # hiperrealista, dispara los filtros de "personas destacadas/reales" de Veo3/Kling. Se usa
    # el descriptor físico sin nombre; avatar_name queda solo para continuidad/documentación.
    identity = pkg.get("avatar_visual_descriptor") or f"a {pkg['avatar_age']}-year-old woman"
    identity = identity[:1].upper() + identity[1:] if identity else identity
    header = (
        f"Hyper-realistic vertical 9:16 smartphone UGC video. Use the canonical {env}. "
        f"{identity}, wearing {pkg['wardrobe_assigned']}. "
        "Preserve her identity, clothing, lighting, environment, table position, props and camera style "
        "throughout the entire clip."
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
            "### First Frame Prompt (Midjourney / Imagen — 9:16)",
            "",
            chunk.get("midjourney_prompt_9_16", ""),
            "",
            "### Video Motion Prompt I2V (Veo3 / Kling)",
            "",
            chunk.get("video_motion_prompt_i2v", ""),
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
    count = 0
    for chunk in data.get("chunks", []):
        if chunk.get("action_timeline"):
            chunk["video_motion_prompt_i2v"] = compile_i2v_prompt(data, chunk)
            count += 1
    if count > 0:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        render_md(data, path)
    return count


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Compila los prompts I2V desde el action_timeline de cada chunk")
    ap.add_argument("--json", required=True, help="production_package_PROD_XXX.json")
    n = compile_package(Path(ap.parse_args().json))
    print(f"Prompts I2V compilados: {n}")
