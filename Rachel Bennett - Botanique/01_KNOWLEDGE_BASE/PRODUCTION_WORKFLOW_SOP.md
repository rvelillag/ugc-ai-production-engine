# Standard Operating Procedure (SOP) — Flujo de Producción UGC AI

Este documento define el procedimiento estándar oficial para la ingesta, análisis, generación y entrega de videos virales UGC para los avatares y marcas del sistema DTC.

---

## 1. Arquitectura de Carpetas y Rutas Oficiales

```
Rachel Bennett - Botanique/
├── 📁 01_KNOWLEDGE_BASE/          # Documentación, Playbooks, este SOP y frameworks
├── 📁 02_AVATAR_ASSETS/            # Identidad inmutable del avatar y escenarios
│   ├── 📁 01_Character/            # Fotos, Character Sheet y RACHEL_BENNETT_CHARACTER_DNA.md (Fuente de Verdad)
│   └── 📁 02_Environments/         # Cocina, cuarto, fondos validados
├── 📁 03_INBOX_REFERENCES/         # Ingesta de videos descargados (por procesar)
│   └── 📁 <cuenta_origen>/         # Ej: koreansecrets7/, choi.koreanskin/
│       └── 📁 _PROCESSED/          # Videos ya extraídos y archivados
├── 📁 04_IN_PRODUCTION/            # Proyectos en curso (Work In Progress)
│   └── 📁 PROD_<ID>_<video_name>/
│       ├── 📁 01_Reference/        # Video base, screenshots .jpg y script_beats.txt
│       ├── 📁 02_First_Frames/     # Documento maestro prompts_and_script_*.md y renders 9:16
│       ├── 📁 03_Raw_Clips/        # Clips generados de Veo3/Kling/Grok/Luma
│       └── 📁 04_Audio/            # Locuciones ElevenLabs (si aplica)
└── 📁 05_PROCESSED_DELIVERABLES/   # Videos finales listos para publicar
    └── 📁 <Avatar_Project_ID>/     # Ej: Rachel001, Rachel002, Rachel005
        ├── <Project_ID>_Final_1080x1920.mp4
        ├── <Project_ID>_Subtitles.srt
        ├── <Project_ID>_Cover.jpg
        └── post_copy_title_and_caption.txt
```

---

## 2. Ciclo de Vida de un Video (Paso a Paso)

### Fase 1: Ingesta (Humano / Scraper)
1. Descargar el video viral `.mp4` de referencia.
2. Guardarlo en `03_INBOX_REFERENCES/<cuenta>/<nombre_video>.mp4`.

---

### Fase 2: Extracción y Diagnóstico (`ugc-video-beat-extractor`)
1. El sistema detecta el video en `03_INBOX_REFERENCES/`.
2. Crea la carpeta del proyecto en `04_IN_PRODUCTION/PROD_<ID>_<nombre_video>/01_Reference/`.
3. Ejecuta FFmpeg para extraer los 6 screenshots clave (`01_hook.jpg` a `06_cta.jpg`).
4. Clasifica el formato:
   * **Unipersonal:** 1 persona demostrando en sí misma.
   * **Multi-Personaje:** Especialista diagnosticando a un Paciente/Modelo.
5. Audita la intensidad del problema en el hook (*Sutil, Moderado o Exagerado*).
6. Genera el archivo `script_beats_<nombre_video>.txt` con marcas de tiempo y transcripción literal.
7. Mueve el video de origen a `03_INBOX_REFERENCES/<cuenta>/_PROCESSED/`.

> [!IMPORTANT]
> **Punto de Control:** El orquestador presenta el diagnóstico de beats, el formato y la propuesta de vestuario al usuario antes de proceder con la generación.

---

### Fase 3: Generación de Guion, Prompts de Imagen y Prompts de Video (`ugc-viral-video-generator`)

1. **Lectura Obligatoria de `*_CHARACTER_DNA.md`:**
   * Cargar `02_AVATAR_ASSETS/01_Character/RACHEL_BENNETT_CHARACTER_DNA.md`.
   * Bloqueo inmutable: Rachel Bennett (47 años, cabello castaño con canas sutiles en coleta baja, arquetipo *Mirror + Convert*).
2. **Traslación de Arquetipo de Roles:**
   * Si la referencia es clínica (médico/guantes), se traduce a un formato testimonial de confianza: **"Anfitriona de cocina compartiendo su descubrimiento con una amiga/invitada"** (sin bata médica ni luces de estudio).
3. **Control y Rotación de Vestuario:**
   * Auditar el color de prenda usado en la producción anterior y rotar la paleta (ej. Terracota Cálido, Verde Salvia, Azul Pizarra, Lino Beige).
4. **Regla de Exageración Forzada en el Hook:**
   * En el Chunk 1 / Prompt 1, usar descriptores visuales de alta intensidad (*severe, prominent, high-contrast dark patches, pronounced swelling*) para detener el scroll en los primeros 2 segundos.
5. **Fidelidad Textual Literal 1:1 & Desacoplamiento ManyChat:**
   * El guión hablado es **100% fiel al video viral de referencia (palabra por palabra)**, conservando la cadencia, los ganchos y las frases retóricas del creador original (*"sliding off by lunch"*, *"it's not your fault"*, *"tested on 22-year-olds"*).
   * **Cero Marcas en el Diálogo del Video:** Los productos se tratan de forma genérica y educativa (*"hydrating milky essence"*, *"featherlight grip primer"*, *"age-defying serum foundation"*). La venta y la recomendación de marca específica se delegan al 100% a la automatización de ManyChat.
   * **Única Modificación:** La frase final del CTA para insertar la palabra clave segura de ManyChat (ej. `LIFT`, `GLOW`) evitando términos sensibles como `age` o `DM`.
6. **Entrega Doble Obligatoria en `prompts_and_script_PROD_<ID>.md`:**
   * **Standard Production Skeleton** (Toma continua 25-30s).
   * **Chunked Production Skeleton (5-6 Chunks)** con:
     * **First Frame Prompt (9:16 vertical en prosa continua para Midjourney/Flux)** con replicación compositiva 1:1.
     * **Video Motion Prompt (I2V para Kling/Veo3/Grok/Luma)** con físicas de movimiento y lipsync verbatim.
   * **Título + Caption con Follow-Gate y Keyword ManyChat**.

---

### Fase 4: Producción Audiovisual (Midjourney / Kling / Veo3 / ElevenLabs)
1. Generar los 5 First Frames en la herramienta de imagen y guardarlos en `02_First_Frames/`.
2. Animar los 5 clips `.mp4` usando los Video Generation Prompts y guardarlos en `03_Raw_Clips/` (`1.mp4` a `5.mp4`).
3. Generar la locución limpia con ElevenLabs en `04_Audio/` si aplica.

---

### Fase 5: Montaje y Subtítulos Dinámicos (`auto-captions-service` / CapCut)
1. Concatenar los 5 clips validados de `03_Raw_Clips/`.
2. **Estándar Oficial de Subtítulos (`capcut_italic_yellow`):**
   * **Tipografía & Estilo:** Sans-Serif Italic Bold en minúsculas naturales (*sentence case*).
   * **Color Bicolor Dinámico:** Palabra activa en **Amarillo Neón (`#FFE500`)** y palabras secundarias en **Blanco Puro (`#FFFFFF`)**.
   * **Contorno:** Borde negro nítido de **4.5px** de alto contraste.
   * **Cadencia:** 2 a 3 palabras por bloque de pantalla.
3. **Zona Segura Oficial (Reels / TikTok Safe Zone):**
   * **Ubicación:** Margen inferior estricto al **18% de la altura del video** (`vertical_margin_pct: 18.0%`).
   * **Regla de interfaz:** Se sitúa en el tercio inferior seguro, por encima de la barra de descripción/audio de Instagram/TikTok y por debajo del pecho/rostro del creador, completamente libre de los botones laterales de interacción (like, comment, share).
4. Exportar el video final con subtítulos quemados en 1080x1920.

---

### Fase 6: Entrega Final y Registro
1. Exportar el video final y copy a `05_PROCESSED_DELIVERABLES/<Avatar_ID>/`.
2. Registrar enlace y métricas en `01_KNOWLEDGE_BASE/Botanique AI Creator Playbook.xlsx`.
