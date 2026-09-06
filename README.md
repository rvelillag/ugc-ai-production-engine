# 🎬 UGC AI Production Engine (Turnkey Multi-Avatar Studio)

Un sistema integral, modular y escalable para la producción automatizada de videos UGC AI virales de alta conversión para Instagram Reels, TikTok y Facebook.

---

## 🌟 Características Principales

* **Arquitectura de 5 Beats Calibrada:** Hook con problema visual exagerado, Reframe de giro narrativo, Mechanism en dos sub-chunks (3A/3B), Payoff de transformación y CTA con Follow-Gate.
* **Extracción Técnica de Beats:** Transcripción palabra por palabra con Whisper ASR y extracción automática de fotogramas clave con FFmpeg.
* **Sustitución Automática de Marcas Terceras:** Mapeo inteligente hacia tu catálogo de producto propio (`PRODUCT_CATALOG.yaml`).
* **Subtitulado Dinámico CapCut (`capcut_italic_yellow`):** Estilo cursiva negrita en minúsculas, palabra activa en Amarillo Neón (`#FFE500`), palabras inactivas en Blanco Puro y margen seguro al **18% de altura** (libre de botones de Reels/TikTok).
* **Multi-Creador Plug & Play:** Crea nuevos personajes en 1 minuto usando el wizard guiado.

---

## 📁 Estructura del Repositorio

```
ugc-ai-production-engine/
├── 📁 _CREATOR_TEMPLATE/                # Plantilla maestra lista para clonar
│   ├── 📁 01_KNOWLEDGE_BASE/            # SOPs universales y frameworks de guion
│   ├── 📁 02_AVATAR_ASSETS/              # DNA inmutable del avatar y prompts de fondos
│   ├── 📁 03_INBOX_REFERENCES/           # Videos de referencia descargados (.mp4)
│   ├── 📁 04_IN_PRODUCTION/              # Proyectos en curso (Fases 2 a 5)
│   ├── 📁 05_PROCESSED_DELIVERABLES/     # Videos finales listos para publicar (4 archivos)
│   ├── 📄 creator_profile.yaml          # Variables de identidad, voz y paleta
│   └── 📄 PRODUCT_CATALOG.yaml          # Catálogo de producto de la marca
│
├── 📁 ugc-avatar-genesis/               # Skill de creación de nuevos avatares
├── 📁 ugc-pipeline-orchestrator/         # Skill orquestadora del ciclo de vida
├── 📁 ugc-video-beat-extractor/          # Skill de extracción técnica ASR + FFmpeg
├── 📁 ugc-viral-video-generator/         # Skill de generación de guiones y prompts I2V
├── 📁 auto-captions-service/             # Motor de subtitulado dinámico y quema FFmpeg
├── 📁 tools/                             # Utilidades CLI (init_creator.py, menu.py)
├── 📄 install_and_setup.bat              # Instalador automático 1-Click (Windows)
├── 📄 ugc_studio.bat                     # Centro de control interactivo (Windows)
└── 📄 requirements.txt                   # Dependencias Python
```

---

## 🚀 Instalación Rápida (Windows)

### 1. Clonar el repositorio
```bash
git clone https://github.com/TU_USUARIO/ugc-ai-production-engine.git
cd ugc-ai-production-engine
```

### 2. Ejecutar el Instalador 1-Click
Haz doble clic en **`install_and_setup.bat`** (o ejecuta en consola):
```cmd
install_and_setup.bat
```
Esto instalará automáticamente todas las librerías necesarias (*faster-whisper, PyTorch, FFmpeg estático, PyYAML, FastAPI, etc.*).

---

## 🎮 Cómo Usar el Sistema

### Paso 1: Abrir el Centro de Control
Haz doble clic en **`ugc_studio.bat`**:
* Selecciona **`[1] Crear un nuevo Avatar / Creador`**.
* Ingresa el nombre del creador (ej. *Sofia Torres*), la marca (ej. *GlowLab*), edad y nicho.
* El sistema creará automáticamente la carpeta `Sofia Torres - GlowLab/` con su ADN y configuración listos.

### Paso 2: Configurar tu Avatar y Catálogo
1. Genera los retratos y fondos en Midjourney/Flux usando las fórmulas de [`ugc-avatar-genesis/prompts_avatar_builder.md`](ugc-avatar-genesis/prompts_avatar_builder.md).
2. Ajusta tus productos propios en `<Tu_Creador>/PRODUCT_CATALOG.yaml`.

### Paso 3: Ingesta y Producción
1. Coloca los videos virales de TikTok/Reels en `<Tu_Creador>/03_INBOX_REFERENCES/<cuenta>/`.
2. El orquestador extraerá los beats técnicos, adaptará el guion a tu producto, generará los prompts de First Frame y Video Motion, y entregará el video final con subtítulos quemados en `<Tu_Creador>/05_PROCESSED_DELIVERABLES/<ID>/`.

---

## 📦 Formato Canónico de Entrega

Cada video procesado en `05_PROCESSED_DELIVERABLES/` contiene estrictamente:
1. `<ID>_Final_1080x1920.mp4` (Video maestro con subtítulos quemados a 18% de margen).
2. `<ID>_Subtitles.srt` (Subtítulos sincronizados palabra por palabra).
3. `<ID>_Cover.jpg` (Portada en alta resolución).
4. `post_copy_title_and_caption.txt` (Título gancho + Copy con Follow-Gate).

---

## 📄 Licencia & Créditos

Desarrollado para la producción escalable de contenido UGC AI DTC de alta conversión.
