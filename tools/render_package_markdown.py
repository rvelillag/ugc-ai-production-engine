import os
import sys
import json
import argparse
from pathlib import Path

def render_markdown(json_path: Path, output_md_path: Path = None):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if output_md_path is None:
        output_md_path = json_path.parent / f"prompts_and_script_{data.get('project_id', 'PACKAGE')}.md"

    md = []
    # Header
    md.append(f"# UGC VIRAL VIDEO PRODUCTION PACKAGE — {data.get('project_id')}")
    md.append(f"**Reference Video:** `{data.get('reference_video')}` ({data.get('reference_duration_s')}s)  ")
    md.append(f"**Topic:** {data.get('topic')}  ")
    md.append(f"**Brand:** {data.get('brand')}  ")
    md.append(f"**Avatar:** **{data.get('avatar_name')} ({data.get('avatar_age')} years old — {data.get('avatar_archetype')})**  ")
    md.append(f"**Outfit Tracking:** Outfit Previo: {data.get('wardrobe_previous')} $\\rightarrow$ **Outfit Asignado Actual: {data.get('wardrobe_assigned')}**.")
    md.append("\n---\n")

    # Timing Matrix Table
    md.append("## 1. Matriz de Control Temporal & Sub-Chunking Calibrado\n")
    md.append("> **Constante de Locución:** 2.2 a 2.4 palabras por segundo (con márgenes de respiración para evitar cortes de audio en Veo3/Kling/Grok).\n")
    md.append("| Chunk | Beat | Conteo Exacto | Duración Estimada | Clip IA Asignado | Margen de Seguridad |")
    md.append("|:---:|:---:|:---:|:---:|:---:|:---:|")
    
    for ch in data.get("chunks", []):
        dur = ch.get("recommended_duration_s", 8)
        wc = ch.get("word_count", 0)
        est_time = round(wc / 2.4, 1)
        margin = round(dur - est_time, 1)
        margin_str = f"✅ +{margin}s libre" if margin >= 0 else f"⚠️ {margin}s ajustado"
        md.append(f"| **Chunk {ch.get('chunk_id')}** | **{ch.get('beat_name')}** | {wc} palabras | {est_time}s | **{dur} Segundos** | {margin_str} |")

    md.append("\n---\n")

    # Audio Anchor
    md.append("## 2. Audio & Voice Direction Anchor (Inmutable)\n")
    md.append("```text")
    md.append(data.get("audio_voice_direction_anchor", "").strip())
    md.append("```\n")
    md.append("---\n")

    # Standard Skeleton
    md.append("## 3. Standard Production Skeleton (Toma Continua 25-30s)\n")
    md.append("```text")
    md.append(data.get("standard_skeleton_25_30s", "").strip())
    md.append("```\n")
    md.append("---\n")

    # Chunked Skeleton
    md.append("## 4. Chunked Production Skeleton (Desglose Fotográfico 1:1)\n")

    for ch in data.get("chunks", []):
        md.append(f"### **Chunk {ch.get('chunk_id')}: {ch.get('beat_name')}**")
        md.append(f"* **Beat:** Beat {ch.get('chunk_id')} — {ch.get('beat_name')}")
        md.append(f"* **Word Count:** {ch.get('word_count')} palabras")
        md.append(f"* **Recommended Clip Duration:** **{ch.get('recommended_duration_s')} Segundos**")
        md.append(f"* **Voiceover (Clean TTS):**\n  `{ch.get('voiceover_clean_tts')}`")
        md.append(f"* **Visual Direction:** {ch.get('visual_direction')}")
        
        # Composition Audit Breakdown
        comp = ch.get("composition_audit", {})
        md.append("\n> **📐 Desglose Forense de Composición (Match 1:1 con Referencia):**")
        md.append(f"> * **Cámara:** {comp.get('camera_shot_type')}")
        md.append(f"> * **Primer Plano / Props:** {comp.get('foreground_props')}")
        
        left = comp.get("left_subject", {})
        if left:
            md.append(f"> * **Sujeto Izquierdo ({left.get('name')}):** {left.get('orientation')} | Pose: {left.get('pose')}")
            
        right = comp.get("right_subject", {})
        if right:
            md.append(f"> * **Sujeto Derecho ({right.get('role')}):** {right.get('orientation')} | Pose: {right.get('pose')} | Síntoma: {right.get('skin_condition_exaggerated')}")
        
        md.append(f"\n* **Prompt de Imagen (First Frame en Midjourney/Flux — 9:16):**")
        md.append("  ```text")
        md.append(f"  {ch.get('midjourney_prompt_9_16', '').strip()}")
        md.append("  ```")

        md.append(f"* **Prompt de Video / Animación (Image-to-Video para Kling / Veo3 / Grok / Luma):**")
        md.append("  ```text")
        md.append(f"  {ch.get('video_motion_prompt_i2v', '').strip()}")
        md.append("  ```")

        tags_str = ", ".join([f"`{t}`" for t in ch.get("asset_tags", [])])
        md.append(f"* **Asset Tags:** {tags_str}")
        md.append(f"* **Continuity Notes:** {ch.get('continuity_notes')}")
        md.append("\n---\n")

    # Post Copy
    post = data.get("post_copy", {})
    md.append("## 5. Post Copy & Portada (ManyChat Automation)\n")
    if post.get("cover_headline"):
        md.append(f"> 🏷️ **HEADLINE DE PORTADA (Thumbnail — Máx 6-7 palabras):**\n> ### **\"{post.get('cover_headline')}\"**\n")
    md.append(f"### **Título / Hook de Post:**\n{post.get('title')}\n")
    md.append(f"### **Caption Completo (Instagram Reels / TikTok / Facebook):**\n{post.get('caption')}\n")
    
    tags = " ".join(post.get("hashtags", []))
    if tags:
        md.append(f"### **Hashtags:**\n{tags}\n")

    output_md_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))

    print(f"Rendered Markdown successfully to: {output_md_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Render JSON Production Package to Markdown")
    parser.add_argument("--json", required=True, help="Path to production_package_PROD_XXX.json")
    parser.add_argument("--out", required=False, help="Optional output markdown path")
    args = parser.parse_args()

    render_markdown(Path(args.json), Path(args.out) if args.out else None)
