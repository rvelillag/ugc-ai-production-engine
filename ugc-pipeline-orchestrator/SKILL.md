---
name: ugc-pipeline-orchestrator
description: >-
  Orquestador maestro del flujo de producción UGC AI de extremo a extremo. Gestiona el ciclo de vida completo de un video viral desde su ingesta en 03_INBOX_REFERENCES, coordina la extracción técnica con ugc-video-beat-extractor en 04_IN_PRODUCTION, guía la generación de prompts y guion con ugc-viral-video-generator, supervisa los assets generados y organiza la entrega final lista para publicar en 05_PROCESSED_DELIVERABLES. Utilizar para coordinar, auditar o ejecutar el pipeline completo de producción UGC.
---

# UGC Production Pipeline Orchestrator (SOP Maestro)

## Propósito

Esta skill actúa como el director de operaciones y orquestador maestro del sistema de producción UGC AI. Conecta y ejecuta en secuencia las skills especializadas, garantiza la gobernanza de archivos y asegura que ningún video pase a la siguiente etapa sin cumplir con los estándares de control de calidad.

---

## 1. Arquitectura del Espacio de Trabajo

El orquestador opera estrictamente sobre la siguiente estructura de carpetas:

```
<Creador>/ (ej. Rachel Bennett/ — solo el nombre del avatar, sin sufijo de marca)
├── 📁 01_KNOWLEDGE_BASE/          # Playbooks, frameworks de copy (fidelidad ≥85% vía ledger) y SOPs
├── 📁 02_AVATAR_ASSETS/            # Identidad inmutable del avatar y fondos validados
│   ├── 📁 01_Character/            # Fotos, Character Sheet y *_CHARACTER_DNA.md (Fuente de Verdad)
│   └── 📁 02_Environments/         # Cocina, dormitorio, fondos oficiales
├── 📁 03_INBOX_REFERENCES/         # Ingesta de videos descargados por procesar
│   └── 📁 <cuenta_origen>/         # Ej: cuenta_a/, cuenta_b/
│       └── 📁 _PROCESSED/          # Histórico de videos ya procesados
├── 📁 04_IN_PRODUCTION/            # Proyectos en curso (Work In Progress)
│   └── 📁 PROD_<ID>_<video_name>/
│       ├── 📁 01_Reference/        # Video base, screenshots .jpg y script_beats.txt
│       ├── 📁 02_First_Frames/     # Documento maestro prompts_and_script_*.md y renders 9:16
│       ├── 📁 03_Raw_Clips/        # Clips generados de Veo3/Kling/Grok/Luma
│       └── 📁 04_Audio/            # Locuciones ElevenLabs (si aplica)
└── 📁 05_PROCESSED_DELIVERABLES/   # Videos finales listos para publicar
    └── 📁 <Avatar_Project_ID>/     # Ej: Avatar001, Avatar002, Avatar005
        ├── <Project_ID>_Final_1080x1920.mp4
        ├── <Project_ID>_Subtitles.srt
        ├── <Project_ID>_Cover.jpg
        └── post_copy_title_and_caption.txt
```

---

## 2. Flujo de Ejecución Paso a Paso (Pipeline con Checkpoints)

### FASE 1: Ingesta y Selección
1. Localizar el video objetivo dentro de `03_INBOX_REFERENCES/<cuenta>/<nombre_video>.mp4`.
2. Asignar el siguiente identificador correlativo de producción (ej. `PROD_004`, `PROD_005`).

---

### FASE 2: Extracción y Diagnóstico Técnico (`ugc-video-beat-extractor`)
1. Crear la estructura en staging: `04_IN_PRODUCTION/PROD_<ID>_<nombre_video>/01_Reference/`.
2. Copiar el video original a `01_Reference/`.
3. Ejecutar FFmpeg para extraer los keyframes clave en alta resolución (`01_beat1_hook.jpg` en adelante); la cantidad no es fija, sigue los cortes de escena reales y las acciones del ledger, así que escala con la duración del video.
4. **Diagnóstico del Hook:**
   * **Clasificación de Formato:** Determinar si es **Unipersonal** (1 persona) o **Multi-Personaje** (Especialista + Paciente/Modelo).
   * **Auditoría de Intensidad del Problema:** Evaluar si el síntoma en el hook es *Sutil, Moderado o Exagerado*.
5. Generar `script_beats_<nombre_video>.txt` con transcripción literal y marcas de tiempo exactas.
6. Mover el video de origen a `03_INBOX_REFERENCES/<cuenta>/_PROCESSED/`.

> [!IMPORTANT]
> **CHECKPOINT 1:** El orquestador presenta el diagnóstico de beats, el formato detectado y la propuesta de vestuario al usuario antes de proceder a la Fase 3.

---

### FASE 3: Generación de Guion, Prompts y Video Prompts (`ugc-viral-video-generator`)

1. **Lectura Obligatoria de la Fuente de Verdad del Avatar:**
   * Cargar obligatoriamente `02_AVATAR_ASSETS/01_Character/*_CHARACTER_DNA.md`.
   * Extraer su **Prompt Anchor Verbatim** (edad, rasgos físicos, arquetipo psicológico).
   * Si no existe el archivo `*_CHARACTER_DNA.md`, el sistema se detiene y solicita la ficha de identidad al usuario antes de continuar.
2. **Traslación de Arquetipo de Personaje:**
   * Si el video de referencia es *Clínico/Médico* pero el avatar de la marca es *Mirror + Convert (Relatable Peer)*, traducir el rol de especialista clínico a **"Anfitriona de cocina compartiendo su descubrimiento con una amiga/invitada"** en un ambiente doméstico honesto.
   * **Límite:** esta traslación es de tono, encuadre narrativo y escenario (gobernada por `scene_mode` del Checkpoint 1) — **no** una licencia para reescribir diálogo ni acciones. El diálogo de cada fila del ledger sigue debiendo conservar ≥85% de las palabras literales (GATE_7) y las acciones físicas se mantienen en el mismo orden del ledger (GATE_8); solo cambian avatar, vestuario y, si aplica, el escenario.
3. **Control y Rotación de Vestuario:**
   * Auditar los entregables previos (`PROD_001`, `PROD_002`...) para identificar el color usado anteriormente.
   * Proponer y asignar un color diferenciado de la paleta permitida del avatar (ej. Terracota Cálido, Verde Salvia, Azul Pizarra) para evitar el look de "uniforme rígido" en el feed.
4. **Exageración del Hook (Opt-in, Parámetros Concretos si Aplica):**
   * Por defecto la acción del hook es idéntica a la referencia (sin exagerar), según el Checkpoint 1 (punto F). Solo si el usuario pidió `hook_exaggeration: true` en `checkpoint1.json`, el prompt del Chunk 1 usa descriptores de alta intensidad y contraste visual (*severe, prominent, high-contrast dark patches, pronounced swelling*) en lugar de términos tímidos (*slight, subtle*).
   * **WPS Objetivo y Estrategia de Duración (Checkpoint 1, punto G):** `wps_target` = el WPS real de ESA referencia (`CADENCIA PROMEDIO` en `script_beats_<video>.txt`), sin techo artificial — ya no un 2.4 fijo. GATE_2 valida contra este `wps_target` guardado en `checkpoint1.json`. Sobre esa base, `fidelity_target` decide el resto: `full_verbatim` (100% del guion, duración ≈ la original) o `trim_to_min` (recorta además dentro de ≥85% por fila si se quiere acortar aún más). Ninguno de los dos valores es un múltiplo fijo entre proyectos.
5. **Fidelidad al Guion de Referencia, Adaptación de Tono y Sustitución de Producto:**
   * **Estructura y Técnica Fieles:** Se respeta la estructura narrativa, los beats, la problemática y el orden de pasos del video original.
   * **Adaptación de Tono:** Se personaliza a la voz del avatar (**el avatar definido en `CHARACTER_DNA.md`**, p. ej. 45 años, estilo confesión doméstica de cocina, empática, honesta y natural).
   * **Regla de Producto Propio (Cero Marcas Terceras):** Queda prohibido incluir marcas o productos comerciales de terceros presentes en el video de referencia (ej. Rhode, NYX, Maybelline, etc.). Toda solución, mecanismo o paso de producto se **adapta e integra obligatoriamente hacia el producto de nuestra marca (la definida en `creator_profile.yaml`)**.
   * Formato de audio limpio: sin guiones largos (em dashes), sin negritas en texto para locución, ritmo natural fluido a `wps_target` (el WPS real de la referencia, de `checkpoint1.json`; si el lip-sync suena forzado a ese ritmo, se baja `wps_target` para ese chunk y se regenera).
6. **Composición Fiel y Prompts Limpios (Cero Overlays):**
   * Los prompts de imagen y video deben respetar la **composición y posiciones exactas de la referencia**, aplicando la regla de exageración en el Hook.
   * Queda estrictamente prohibido incorporar overlays de texto, marcas de agua o íconos de redes sociales en los prompts visuales.
7. **Entrega Doble Obligatoria en el Paquete de Producción:**
   * Guardar en `04_IN_PRODUCTION/PROD_<ID>_<nombre_video>/02_First_Frames/prompts_and_script_PROD_<ID>.md`:
     1. **Standard Production Skeleton** (Toma continua 25-30s).
     2. **Chunked Production Skeleton (N chunks, agrupados por tomas reales de `script_beats`, ≤10s cada uno)** con:
        * **Prompt de Imagen (First Frame en Midjourney/Flux)** (9:16 vertical, prosa continua, sin texto).
        * **Prompt de Video / Animación (I2V en Kling/Veo3/Grok/Luma)** con físicas de movimiento, micro-jitter de celular y lipsync.
     3. **Post Copy** (Título + Caption con Follow-gate y ManyChat Keyword).

---

### FASE 4: Producción Audiovisual (Generación Externa)
1. Generar los First Frames en la herramienta de imagen y guardarlos en `02_First_Frames/`.
2. Animar los clips `.mp4` usando los Video Generation Prompts en Kling / Veo3 / Grok y guardarlos en `03_Raw_Clips/` (`1.mp4` a `N.mp4`, uno por chunk del paquete).
3. Generar la locución limpia con ElevenLabs en `04_Audio/` si la herramienta de video no realiza TTS nativo.

---

### FASE 5: Recorte Inteligente de Silencios, Montaje y Subtítulos Dinámicos (`tools/assemble_project.py` + `auto-captions-service`)
1. **Recorte Inteligente de Silencios (Smart Silence Trimming Obligatorio):**
   * Antes de concatenar, se auditan con Whisper las marcas de tiempo exactas del primer y último instante de locución en cada clip crudo (`1.mp4` a `N.mp4`).
   * Se recortan automáticamente todos los silencios muertos iniciales y finales dejando únicamente un margen natural de respiración ($\approx 0.12\text{s}$ inicio, $\approx 0.22\text{s}$ fin) para evitar baches incómodos y garantizar un ritmo publicitario fluido y de alta retención.
2. **Concatenación y Subtitulado Dinámico Oficial (`poppins_yellow` por defecto; se cambia con `ugc assemble --template`):**
   * Poppins Black en minúsculas naturales, tamaño 6.0% de altura, palabra activa en Amarillo Neón (`#FFE600`), palabras inactivas en Blanco (`#FFFFFF`), borde negro de 4.5px. Alternativa: `viral_yellow_highlight` (Montserrat Bold mayúsculas, `#FFD400`).
   * **Zona Segura Inferior (Reels/TikTok Safe Zone):** Margen inferior fijo al **18% de la altura** (`vertical_margin_pct: 18.0%`) para garantizar que el texto nunca quede tapado por la interfaz o botones de Instagram y TikTok.
3. **Ejecución Unificada Automatizada:**
   ```bash
   python tools/assemble_project.py --project PROD_<ID>_<nombre>
   ```
4. Genera el archivo maestro `.mp4` con subtítulos quemados, archivo `.srt`, portada de alto impacto `Cover.jpg` y exportación canónica inmediata a `05_PROCESSED_DELIVERABLES/`.

---

### FASE 6: Entrega Final y Publicación
1. Exportar el paquete completo a `05_PROCESSED_DELIVERABLES/<Avatar_ID>/` conteniendo **estricta y exclusivamente los 4 archivos canónicos**:
   * `<Project_ID>_Final_1080x1920.mp4`
   * `<Project_ID>_Subtitles.srt`
   * `<Project_ID>_Cover.jpg`
   * `post_copy_title_and_caption.txt`
2. Registrar la entrega en `01_KNOWLEDGE_BASE/<Marca> AI Creator Playbook.xlsx`.

---

## 3. Checklist Maestro de Aprobación

- [ ] Video de referencia archivado en `03_INBOX_REFERENCES/.../_PROCESSED/`.
- [ ] Screenshots de keyframes y `script_beats_*.txt` presentes en `01_Reference/`.
- [ ] Ficha `*_CHARACTER_DNA.md` consultada y aplicada verbatim en los prompts.
- [ ] Arquetipo correctamente traducido (Clínico vs. Testimonial Mirror+Convert).
- [ ] Vestuario rotado respecto a la producción inmediata anterior.
- [ ] Hook con descriptores de problema visualmente exagerados (alto contraste).
- [ ] Standard Skeleton + N Chunked Skeletons (uno por chunk) con **First Frame Prompt** AND **Video Motion Prompt**.
- [ ] Copy con follow-gate y palabra clave ManyChat lista.
