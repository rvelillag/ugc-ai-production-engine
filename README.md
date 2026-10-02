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

---

## 🎮 Arquitectura Desacoplada (2 Carpetas: Motor y Avatares)

El sistema opera bajo un desacoplamiento total en dos carpetas hermanas para mantener el repositorio limpio y permitir múltiples marcas/creadores sin duplicar código ni dependencias:

```
c:\...\DTC\
├── 📁 sistema/                 # El Motor Central (Git repo, scripts, auto-captions, tests)
└── 📁 avatares/                # Espacio de Trabajo de Creadores y Marcas
    ├── 📁 Rachel Bennett/      # Carpeta exclusiva con el nombre del avatar
    └── 📁 Carmen Del Valle/    # Carpeta exclusiva con el nombre del avatar
```

> **Regla de Nomenclatura de Carpetas:**  
> La carpeta de cada avatar lleva **únicamente el nombre del personaje** (ej: `avatares/Rachel Bennett/`, `avatares/Sofia Torres/`), nunca el sufijo de producto o marca (`- Botanique`). Si el nombre del avatar cambia en el futuro, se utiliza `ugc rename` para sincronizar la carpeta, perfiles y DNA sin errores.

---

## 🧭 Onboarding de Nuevos Avatares (`ugc onboard`)

El motor incluye un asistente guiado interactivo que garantiza la configuración perfecta de cada avatar siguiendo dos reglas fundamentales:

```bash
ugc onboard
```

### 1. Regla 1: Definición Inteligente del Personaje (Creación vs. Personaje en Mente)
* **Si ya tienes un personaje en mente:** Ingresas nombre, nicho y marca. El sistema analiza la sonoridad fonética y la memorabilidad del nombre para el nicho. Si detecta una optimización, te sugiere alternativas de alto impacto publicitario. Si decides adoptarla, la carpeta se crea inmediatamente con ese nombre optimizado.
* **Si creas un personaje desde cero:** El sistema te asiste seleccionando arquetipo publicitario (Especialista, Espejo, Familiar, Insider, Convertido), rango de edad, género y nicho, y genera un abanico de sugerencias de nombres con alta recordación para que elijas tu favorito.

### 2. Regla 2: Soporte para Avatares Sin Producto Físico
* Muchos creadores de contenido generan videos educativos, consejos prácticos, recetas caseras, estilo de vida o servicios sin manipular productos físicos.
* El asistente pregunta: *¿El avatar mostrará algún producto físico en video?*
  * **Caso Sí:** Configura el catálogo en `PRODUCT_CATALOG.yaml` para mapear envases, texturas y fórmulas.
  * **Caso No (`--no-product`):** Activa el modo `has_physical_product: false`. Los prompts generados omiten automáticamente frascos, goteros, botellas y empaques. `PRODUCT_CATALOG.yaml` queda limpio y `ugc doctor` certifica el workspace sin emitir advertencias de catálogo ausente.

---

## 🛠️ Guía Completa de Comandos Globales (`ugc`)

Una vez instalado, el comando `ugc` puede ejecutarse desde cualquier terminal o dentro de la carpeta de cualquier avatar:

| Comando | Descripción |
| :--- | :--- |
| `ugc onboard` | **Asistente interactivo guiado** para dar de alta nuevos avatares aplicando Regla 1 y Regla 2. |
| `ugc new` / `ugc init` | Inicializa un nuevo avatar por línea de comandos rápida (`--name "Sofia Torres"` `[--no-product]`). |
| `ugc rename` | **Renombra de forma consistente** un avatar (carpeta, `creator_profile.yaml` y Character DNA). |
| `ugc doctor` | **Diagnóstico de salud** del motor (FFmpeg, Whisper) y auditoría del workspace activo. |
| `ugc status` | Muestra el estado del avatar activo, nicho, ManyChat keyword, proyectos y entregables. |
| `ugc ingest` | **Fase 1:** Ingesta de video de referencia viral y extracción de transcripción + keyframes. |
| `ugc ledger` | **Fase 2:** Genera o actualiza el borrador del Reference Ledger estructurado. |
| `ugc checkpoint1` | **Fase 2.5:** Registra y confirma el Checkpoint 1 (escenario, vestuario, keyword y headline). |
| `ugc compile` | **Fase 3:** Compila los prompts de imagen y video I2V desde el action timeline. |
| `ugc prompt` | Consulta o copia al portapapeles de Windows prompts individuales listos para Kling / Veo3. |
| `ugc assemble` | **Fase 4:** Ensambla los clips generados con *Smart Silence Trimming* y subtítulos virales. |
| `ugc certify` | **Auditoría de Agencia:** Evalúa los 8 Gates de calidad de agencia con el QA Harness. |
| `ugc setup-path` | Registra el comando `ugc` en el PATH de Windows para uso global permanente. |
| `ugc update` | **Actualiza el motor** a la última versión de Git y sincroniza dependencias (sin tocar tus avatares). |

---

## 📦 Formato Canónico de Entrega

Cada video procesado en `05_PROCESSED_DELIVERABLES/[ID]/` contiene estrictamente los 4 archivos de certificación:
1. `[ID]_Final_1080x1920.mp4` (Video maestro ensamblado con audio original y subtítulos virales).
2. `[ID]_Subtitles.srt` (Subtítulos sincronizados palabra por palabra con Whisper).
3. `[ID]_Cover.jpg` (Portada optimizada con titular de curiosidad <= 7 palabras).
4. `post_copy_title_and_caption.txt` (Título gancho + Copy para redes con llamado a ManyChat).

---

## 📄 Licencia & Créditos

Desarrollado para la producción escalable de contenido UGC AI DTC de alta conversión.
