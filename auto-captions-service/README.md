# Auto-Captions Animated Service (Estilo CapCut / Submagic) 🎬⚡

Sistema automatizado end-to-end de generación y quemado de subtítulos animados palabra por palabra sobre videos verticales (Reels, TikTok, Shorts), diseñado para operar de forma desatendida vía API REST, carpeta watch o integrado con pipelines de **n8n**.

---

## Características Principales

- 🎙️ **ASR con Timestamps por Palabra**: Transcripción de alta precisión en español e inglés mediante `faster-whisper` (local, sin coste por video) o fallback a OpenAI Whisper API.
- ✨ **Animaciones Estilo CapCut**:
  - **Pop-Scale & Highlight (`hype_yellow`)**: La palabra activa hace zoom/pop (120% -> 100%) en amarillo vibrante mientras se pronuncia.
  - **Minimalista Clean (`clean_white`)**: Fuente elegante, fondo suave tipo caja/pill semitransparente y transiciones fade fluidas.
  - **Karaoke Dinámico (`karaoke_highlight`)**: Barrido progresivo de color palabra por palabra mediante tags `\k` de ASS.
  - **Personalizable al 100%**: Añade o ajusta estilos directamente en `templates.json` sin tocar código.
- 🔥 **Emojis Contextuales Automáticos**: Detección inteligente de palabras clave (dinero -> 💰, fuego -> 🔥, cohete -> 🚀, etc.) con toggle on/off.
- ⚡ **Quemado Hardsub Rápido con FFmpeg**: Mantiene resolución nativa (9:16, 1:1, 16:9), fps y calidad de audio original sin pérdida.
- 🔄 **Revisión y Corrección Manual Opcional**: Pausa el flujo antes de renderizar para editar el transcript JSON (`GET /caption/{id}/transcript` -> `POST /caption/{id}/render`).
- 📁 **Carpeta Watch**: Monitorea `watch/input` y quema automáticamente cualquier video depositado, guardándolo en `watch/output`.
- 🔗 **Webhooks & n8n Ready**: Notificaciones HTTP automáticas al completar el render y workflow de n8n listo para importar.
- 🐳 **Docker & Docker Compose**: Empaquetado listo para producción con fuentes tipográficas y `libass`.

---

## Estructura del Proyecto

```
auto-captions-service/
├── app/
│   ├── main.py                  # FastAPI API y endpoints
│   ├── config.py                # Configuración y variables de entorno
│   ├── core/
│   │   ├── audio_extractor.py   # Extracción de audio y sondeo de video (FFmpeg)
│   │   ├── asr_engine.py        # Motor ASR (faster-whisper / OpenAI)
│   │   ├── cue_segmenter.py     # Agrupador de palabras en cues visuales
│   │   ├── emoji_tagger.py      # Diccionario y detector de emojis contextuales
│   │   ├── ass_generator.py     # Generador de subtítulos .ass con animaciones
│   │   ├── srt_generator.py     # Generador de subtítulos .srt estándar
│   │   ├── ffmpeg_burner.py     # Quemador de subtítulos con libass
│   │   └── pipeline.py          # Orquestador del pipeline end-to-end
│   ├── services/
│   │   ├── job_queue.py         # Manejador de tareas y cola asíncrona
│   │   ├── template_manager.py  # Gestor de templates.json
│   │   ├── webhook_client.py    # Envío de notificaciones a n8n
│   │   └── watch_folder.py      # Observador de carpeta watch
│   ├── schemas/
│   │   ├── job.py               # Modelos Pydantic para jobs y transcripts
│   │   └── template.py          # Esquema de validación de plantillas
│   └── templates/
│       └── templates.json       # Plantillas de estilo preconfiguradas
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── examples/
│   ├── n8n_workflow_example.json # Flujo n8n listo para importar
│   └── curl_examples.sh         # Ejemplos de peticiones cURL
├── scripts/
│   ├── generate_sample_video.py # Generador de videos sintéticos de prueba
│   └── run_batch_test.py        # Procesador por lotes
├── tests/
│   ├── test_ass_generator.py
│   └── test_pipeline.py
├── requirements.txt
├── .env.example
└── README.md
```

---

## Inicio Rápido con Docker

```bash
cd auto-captions-service

# 1. Copiar variables de entorno
cp .env.example .env

# 2. Levantar el servicio
docker compose -f docker/docker-compose.yml up -d --build

# 3. Verificar salud
curl http://localhost:8000/health
```

La documentación Swagger / OpenAPI estará disponible de inmediato en:
👉 `http://localhost:8000/docs`

---

## Inicio Local (Desarrollo en Python)

### Prerrequisitos
- Python 3.11+
- FFmpeg con soporte `libass` instalado y en el PATH del sistema.

```bash
cd auto-captions-service

# 1. Crear entorno virtual
python -m venv .venv
# En Windows:
.venv\Scripts\activate
# En Linux/macOS:
source .venv/bin/activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Iniciar servidor
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## Uso de la API REST

### 1. Iniciar subtitulado vía JSON (`POST /caption`)
```bash
curl -X POST "http://localhost:8000/caption" \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
    "language": "es",
    "template": "hype_yellow",
    "max_words_per_cue": 3,
    "highlight_active_word": true,
    "auto_emoji": true,
    "export_srt": true,
    "export_ass": true
  }'
```
**Respuesta:**
```json
{
  "job_id": "cap_9f21a3",
  "status": "queued",
  "message": "Job successfully queued"
}
```

### 2. Iniciar subtitulado subiendo un archivo de video (`multipart/form-data`)
```bash
curl -X POST "http://localhost:8000/caption" \
  -F "file=@mi_video_vertical.mp4" \
  -F "template=hype_yellow" \
  -F "language=es" \
  -F "auto_emoji=true"
```

### 3. Consultar Estado y URLs de Descarga (`GET /caption/{job_id}`)
```bash
curl -X GET "http://localhost:8000/caption/cap_9f21a3"
```
**Respuesta cuando está completado:**
```json
{
  "job_id": "cap_9f21a3",
  "status": "completed",
  "progress_percentage": 100,
  "stage": "Finalizado exitosamente",
  "output_video_url": "http://localhost:8000/caption/cap_9f21a3/download/video",
  "srt_url": "http://localhost:8000/caption/cap_9f21a3/download/srt",
  "ass_url": "http://localhost:8000/caption/cap_9f21a3/download/ass",
  "transcript_url": "http://localhost:8000/caption/cap_9f21a3/transcript",
  "duration_seconds": 24.5,
  "processing_time_seconds": 12.3
}
```

### 4. Flujo de Corrección Manual de Transcripción
1. Envía el video con `"pause_before_render": true`. El job transcribirá y se detendrá en estado `waiting_for_review`.
2. Obtén el transcript editable: `GET /caption/{job_id}/transcript`.
3. Corrige ortografía, marcas o jerga en el JSON.
4. Envía el transcript corregido para renderizar:
```bash
curl -X POST "http://localhost:8000/caption/cap_9f21a3/render" \
  -H "Content-Type: application/json" \
  -d '{
    "template": "hype_yellow",
    "transcript": {
      "language": "es",
      "words": [
        {"word": "Aprende", "start": 0.1, "end": 0.4},
        {"word": "a", "start": 0.42, "end": 0.55},
        {"word": "vender", "start": 0.58, "end": 1.1}
      ]
    }
  }'
```

---

## Plantillas de Estilo (`templates.json`)

Puedes agregar o modificar plantillas en cualquier momento editando `app/templates/templates.json`:

```json
{
  "name": "hype_yellow",
  "font_family": "Montserrat Bold",
  "font_size_pct_of_height": 7.5,
  "primary_color": "#FFFFFF",
  "highlight_color": "#FFD400",
  "outline_color": "#000000",
  "outline_width": 4.5,
  "position": "bottom_center",
  "vertical_margin_pct": 18.0,
  "animation": "pop_scale",
  "pop_scale_from": 120.0,
  "pop_scale_duration_ms": 120,
  "uppercase": true,
  "max_words_per_cue": 3
}
```

---

## Integración con n8n

1. Abre n8n y ve a **Workflows** -> **Import from File**.
2. Selecciona `examples/n8n_workflow_example.json`.
3. El workflow incluye:
   - Webhook trigger para recibir URLs de video de tus fuentes (Google Drive, Veo, Telegram).
   - Nodo HTTP Request que llama a `POST /caption`.
   - Bucle de espera y consulta `GET /caption/{job_id}` hasta obtener `completed`.
   - Descarga y reenvío del video final listo a tus redes sociales o almacenamiento en la nube.

---

## Ejecutar Pruebas Automatizadas

```bash
cd auto-captions-service
python -m unittest discover -s tests
```
