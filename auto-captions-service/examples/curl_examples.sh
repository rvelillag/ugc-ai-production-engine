#!/bin/bash

# ==============================================================================
# Ejemplos de uso cURL para Auto-Captions Animated Service
# ==============================================================================

BASE_URL="http://localhost:8000"

echo "1. Healthcheck"
curl -X GET "$BASE_URL/health"
echo -e "\n"

echo "2. Listar Plantillas Disponibles"
curl -X GET "$BASE_URL/templates"
echo -e "\n"

echo "3. Crear Job vía URL (JSON Payload)"
JOB_RESP=$(curl -s -X POST "$BASE_URL/caption" \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
    "language": "es",
    "template": "hype_yellow",
    "max_words_per_cue": 3,
    "highlight_active_word": true,
    "auto_emoji": true,
    "position": "bottom_center",
    "export_srt": true,
    "export_ass": true
  }')

echo "Respuesta:" $JOB_RESP
JOB_ID=$(echo $JOB_RESP | grep -o '"job_id":"[^"]*' | cut -d'"' -f4)
echo "Job ID extraído:" $JOB_ID
echo -e "\n"

echo "4. Crear Job vía Subida de Archivo (Multipart Form)"
# curl -X POST "$BASE_URL/caption" \
#   -F "file=@/ruta/a/mi_video.mp4" \
#   -F "template=clean_white" \
#   -F "language=es" \
#   -F "max_words_per_cue=4" \
#   -F "auto_emoji=true"

echo "5. Consultar Estado del Job"
if [ ! -z "$JOB_ID" ]; then
  curl -X GET "$BASE_URL/caption/$JOB_ID"
  echo -e "\n"

  echo "6. Obtener Transcript para Revisión Manual"
  curl -X GET "$BASE_URL/caption/$JOB_ID/transcript"
  echo -e "\n"

  echo "7. Descargar Video Subtitulado"
  # curl -O -J "$BASE_URL/caption/$JOB_ID/download/video"
fi
