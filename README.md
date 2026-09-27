# 🎬 UGC AI Production Engine (Turnkey Multi-Avatar Studio)

Un sistema integral, modular y escalable para la producción automatizada de videos UGC AI virales de alta conversión para Instagram Reels, TikTok y Facebook.

---

## 🌟 Características Principales

* **Arquitectura de 5 Beats Calibrada:** Hook con problema visual exagerado, Reframe de giro narrativo, Mechanism en dos sub-chunks (3A/3B), Payoff de transformación y CTA con Follow-Gate.
* **Extracción Técnica de Beats:** Transcripción palabra por palabra con Whisper ASR y extracción automática de fotogramas clave con FFmpeg.
* **Recorte Inteligente de Silencios (*Smart Silence Trimming*):** Detección automática de pausas muertas entre clips de IA mediante Whisper, eliminando silencios iniciales y finales para garantizar un ritmo publicitario continuo y ágil.
* **Sustitución Automática de Marcas Terceras:** Mapeo inteligente hacia tu catálogo de producto propio (`PRODUCT_CATALOG.yaml`).
* **Subtitulado Dinámico CapCut/Hormozi (`viral_yellow_highlight`):** Montserrat Bold en mayúsculas, tamaño compacto (4.5% de altura), palabra activa en Amarillo Viral (`#FFD400`), palabras inactivas en Blanco Puro y margen seguro al **18% de altura** (libre de botones de Reels/TikTok). Es la plantilla que ejecuta `tools/assemble_project.py`; `auto-captions-service` incluye otras plantillas alternativas (ej. `capcut_italic_yellow`) para uso manual vía su propio servicio.
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
├── 📁 tools/                             # Utilidades del motor (harness, compiler, etc.)
├── 📄 ugc.cmd                            # Lanzador global CLI de Windows
├── 📄 ugc.py                             # Master CLI Engine runner
├── 📄 install_and_setup.bat              # Instalador automático 1-Click (Windows)
├── 📄 ugc_studio.bat                     # Centro de control interactivo (Windows)
└── 📄 requirements.txt                   # Dependencias Python
```

---

## 🚀 Instalación Rápida (Windows)

### 1. Clonar el motor
```bash
git clone https://github.com/rvelillag/ugc-ai-production-engine.git
cd ugc-ai-production-engine
```

### 2. Ejecutar el Instalador 1-Click
Haz doble clic en **`install_and_setup.bat`** (o ejecuta en consola):
```cmd
install_and_setup.bat
```
Esto instalará todas las librerías (*faster-whisper, PyTorch, FFmpeg estático, PyYAML, etc.*) y registrará el comando global **`ugc`** en tu sistema.

---

## 🎮 Arquitectura Desacoplada (Un Solo Motor, Múltiples Avatares)

El motor vive **una sola vez** en tu máquina. Tus marcas o avatares pueden estar en cualquier carpeta de tu disco o en repositorios Git separados (pesan solo 500 KB y no duplican librerías):

### 1. Crear un Nuevo Avatar en Cualquier Ubicación
Abre cualquier terminal y ejecuta:
```bash
ugc new --name "Sofia Torres" --brand "GlowLab" --niche "Skincare" [--dest "D:\Mis_Marcas"]
```
Esto creará el workspace `Sofia Torres - GlowLab/` con su plantilla completa y sus instrucciones para agentes de IA (`CLAUDE.md`).

### 2. Operar desde la Carpeta del Avatar
Entra a la carpeta de tu marca:
```bash
cd "D:\Mis_Marcas\Sofia Torres - GlowLab"
```
El comando `ugc` detectará automáticamente tu avatar y marca:

| Fase | Comando | Descripción |
| :--- | :--- | :--- |
| **Status** | `ugc status` | Muestra estado del avatar, proyectos activos y entregables |
| **Fase 1** | `ugc ingest --video "03_INBOX_REFERENCES/ref.mp4"` | Ingesta de video viral y extracción de beats/keyframes |
| **Fase 2** | `ugc ledger --project PROD_001 [--language es]` | Genera borrador del reference ledger |
| **Fase 2.5** | `ugc checkpoint1 --project PROD_001 --scene adapt_to_brand --outfit "..." --keyword KEYWORD --headline "..."` | Registra Checkpoint 1 |
| **Fase 3** | `ugc compile --project PROD_001` | Compila prompts I2V con gatillos ópticos iPhone 15 Pro |
| **Fase 4** | `ugc assemble --project PROD_001` | Ensambla con Smart Silence Trimming y subtítulos virales |
| **Fase 4** | `ugc certify --project PROD_001` | Audita y certifica calidad de agencia (8/8 QA Gates) |
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
