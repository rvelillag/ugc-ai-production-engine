# Fórmulas Maestras de Prompts para Creación de Avatares (Midjourney / Flux)

Utiliza estas fórmulas para generar los assets fundacionales del nuevo personaje con máxima consistencia y realismo humano.

---

## 1. Prompt Maestro para Retrato de Perfil (`Profile Picture.jpeg`)

```text
A candid portrait photograph of [Nombre], an authentic [Edad]-year-old [Etnia/Género] with natural [Color/Tipo de cabello] showing subtle natural roots and texture. Realistic human skin with visible pores, soft fine lines around the eyes and forehead, natural skin undertones with zero heavy makeup or artificial airbrushing. Bright, warm, open and well-rested eyes. Wearing a simple everyday neutral ribbed cotton top and small discreet stud earrings. Soft natural morning daylight entering through a home window, domestic kitchen or living space in the background with subtle bokeh. Photographed on a modern smartphone camera, unfiltered UGC social media aesthetic, 8k photorealistic. --ar 1:1 --v 6.1 --style raw
```

---

## 2. Prompt Maestro para Hoja de Consistencia Facial (`character_sheet.png`)

```text
Character sheet turnaround grid featuring the same authentic [Edad]-year-old [Género], [Nombre]. Multiple angles and expressions of the same character: front view smiling warmly, three-quarter view speaking candidly, three-quarter view with concerned listening expression, and side profile. Consistent shoulder-length [Cabello] in a loose casual low ponytail, realistic skin texture with fine lines, pores, and natural skin tone. Wearing a simple neutral top and small gold earrings. Clean neutral daylight studio backdrop for reference, photorealistic 8k, consistent facial geometry and facial symmetry across all views. --ar 16:9 --v 6.1 --style raw
```

---

## 3. Prompts Maestros para Entornos Oficiales 9:16 (`02_Environments/`)

### A. Cocina Doméstica con Encimera de Madera (`01_Kitchen_Main.jpg`)
```text
A candid 9:16 vertical eye-level interior photograph of a warm, cozy modern domestic kitchen. Clean wooden butcher-block countertop in the foreground with a modern matte black faucet and small sink basin. In the background are open wooden shelves with neat glass spice jars, potted fresh green herbs, and soft morning window sunlight illuminating the room with an honest, inviting home atmosphere. Unfiltered everyday social media aesthetic, photorealistic 8k. --ar 9:16 --v 6.1
```

### B. Tocador / Baño de Skincare (`02_Bathroom_Mirror.jpg`)
```text
A candid 9:16 vertical eye-level photograph of a clean, bright, modern home bathroom vanity. Smooth neutral countertop in the foreground, sleek minimalist mirror frame, soft diffused morning window light, small potted green plant on the side shelf, and a warm tidy domestic bathroom setting ideal for skincare routines. Photorealistic 8k, unfiltered aesthetic. --ar 9:16 --v 6.1
```

---

## 4. Prompt Maestro para Hoja de Referencia desde Imagen Subida (`character_reference_sheet.png`)

Usar este prompt una vez que el `Profile Picture.jpeg` del personaje ya fue aprobado, subiéndolo como imagen de referencia:

```text
Create a professional character reference sheet based strictly on the uploaded reference image. Use a clean, neutral plain background and present the sheet as a technical model turnaround while matching the exact visual style of the reference (same realism level, rendering approach, texture, color treatment, and overall aesthetic). Arrange the composition into two horizontal rows. Top row: four full-body standing views placed side-by-side in this order: front view, left profile view (facing left), right profile view (facing right), back view. Bottom row: three highly detailed close-up portraits aligned beneath the full-body row in this order: front portrait, left profile portrait (facing left), right profile portrait (facing right). Maintain perfect identity consistency across every panel. Keep the subject in a relaxed A-pose and with consistent scale and alignment between views, accurate anatomy, and clear silhouette; ensure even spacing and clean panel separation, with uniform framing and consistent head height across the full-body lineup and consistent facial scale across the portraits. Lighting should be consistent across all panels (same direction, intensity, and softness), with natural, controlled shadows that preserve detail without dramatic mood shifts. Output a crisp, print-ready reference sheet look, sharp details.
```
