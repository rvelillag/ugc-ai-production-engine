import sys
from pathlib import Path

file_path = Path("Rachel Bennett - Botanique/04_IN_PRODUCTION/PROD_011_elainevanhausen_4/02_First_Frames/prompts_and_script_PROD_011.md")

with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

# Replace Chunk 1 with hyper-exaggerated hook
old_chunk1_start = "### **Chunk 1: Hook (Coca-Cola en Raya Media en Lavacabezas)**"
old_chunk2_start = "### **Chunk 2: Protocol (De Raíz a Puntas y 10 Minutos)**"

new_chunk1 = """### **Chunk 1: Hook (Coca-Cola en Raya Media — Ángulo Picado Exagerado)**
* **Beat:** Beat 1 — Hook (Coca-Cola en Raya Media — Ángulo Picado Exagerado & Alto Impacto Visual)
* **Word Count:** 21 palabras
* **Recommended Clip Duration:** **8 Segundos**
* **Voiceover (Clean TTS):**
  `I know this looks absolutely insane, but pour a glass bottle of Coca-Cola right onto that thin middle part and watch what happens.`
* **Visual Direction:** Plano picado cenital/inmersivo 9:16 vertical (steep high-angle POV) mirando directamente hacia abajo. En primer plano macro y extremo, una raya media visiblemente despoblada en el cuero cabelludo que recibe un chorro continuo y efervescente de Coca-Cola oscura con burbujas y espuma blanca densa activa. Rachel Bennett inclinada sobre el encuadre mirando hacia arriba directamente al lente del smartphone con ojos abiertos, cejas arqueadas y una expresión de asombro/intriga cómplice total que congela el scroll. Fondo de salón de lujo con lavacabezas cerámico negro y luces cálidas difuminadas.

> **📐 Desglose Forense de Composición (Exageración de Alto Impacto 1:1):**
> * **Cámara:** Vertical 9:16 steep high-angle POV / extreme close-up looking directly down at scalp parting, 24mm wide smartphone lens creating immersive proximity
> * **Primer Plano / Props:** Wide thinning middle scalp part line receiving a continuous bubbling dark soda stream from the tilted mouth of a vintage glass bottle; active fizzy carbonation foam spreading across hair roots
> * **Sujeto Izquierdo (Rachel Bennett (Host Stylist)):** Leaning dramatically forward over the top-half of frame, looking up directly into the overhead camera | Pose: Tilted vintage glass Coca-Cola bottle in right hand pouring fizzy stream onto scalp; left hand holding hair open at parting; wide expressive eyes, raised eyebrows, intense stop-scroll conspiratorial shock expression
> * **Sujeto Derecho (Client in Wash Basin):** Head tilted back in black basin, wide visible thinning part line receiving the dramatic fizzy dark liquid and foaming bubbles

* **Prompt de Imagen (First Frame en Midjourney/Flux — 9:16):**
  ```text
  A dramatic, high-retention candid 9:16 vertical smartphone UGC video first frame shot from a steep high-angle looking directly down. In the intense foreground close-up, a woman's dark wet hair has an exaggerated, clearly visible wide thinning middle part line on her scalp. Leaning directly over the frame into the lens is Rachel Bennett, a gorgeous 47-year-old female salon owner with layered wavy bob and platinum highlights, wearing a crisp white silk blouse under a black canvas apron with gold cursive embroidery 'Bennett Studio'. Rachel is holding a vintage glass Coca-Cola bottle tilted steeply downward, pouring an effervescent, bubbling dark fizzy soda stream with visible micro-bubbles and white foam splashing directly onto the scalp parting line. Rachel looks intensely up into the camera with wide eyes, raised eyebrows, and a shocked, conspiratorial expression. Luxury modern salon background with glossy black ceramic wash basin and glowing warm vanity lights in soft bokeh. Extreme macro hair texture, fizzy foam details, hyper-realistic skin pores, candid smartphone quality, zero text, zero overlays, photorealistic 8k --ar 9:16 --v 6.1 --style raw
  ```
* **Prompt de Video / Animación (Image-to-Video para Kling / Veo3 / Grok / Luma):**
  ```text
  Steep high-angle vertical 9:16 UGC video, 8 seconds duration. Seamless dynamic action from Hook First Frame. Rachel Bennett tilts the glass Coca-Cola bottle, pouring a continuous fizzy dark stream onto the scalp part line with active bubbling foam, speaking with intense, high-urgency facial expressions and wide eyes directly into the high-angle smartphone camera. Dramatic head tilt, expressive eyebrow raises, conversational hand movements. Warm luxury salon lighting. Strictly zero on-screen text, zero subtitles, zero icons, zero watermarks. [AUDIO & VOICE DIRECTION ANCHOR]: Polished, confident, and warm 47-year-old American female speaking voice. Urgent, high-hook pacing with clear articulation, luxury salon acoustics, natural lipsync matching the spoken script: "I know this looks absolutely insane, but pour a glass bottle of Coca-Cola right onto that thin middle part and watch what happens." Hyper-realistic fluid motion, 4k.
  ```
* **Asset Tags:** `@rachel_bennett_47yo`, `@hook_picado_cenital`, `@coca_cola_espuma_efervescente`, `@raya_media_despoblada`, `@delantal_bennett_studio`, `@stop_scroll_exaggerated`
* **Continuity Notes:** Ángulo cenital picado exagerado para máximo impacto visual en los primeros 3 segundos. Espuma y burbujas de Coca-Cola activas sobre el cuero cabelludo.

---
"""

parts = text.split(old_chunk2_start)
prefix = text.split(old_chunk1_start)[0]

updated_text = prefix + new_chunk1 + "\n" + old_chunk2_start + parts[1]

with open(file_path, "w", encoding="utf-8") as f:
    f.write(updated_text)

print("Updated Hook in prompts_and_script_PROD_011.md successfully!")
