---
name: ugc-video-beat-extractor
description: >-
  Analiza videos UGC de referencia (.mp4), transcribe el guion literal mediante Whisper ASR, identifica cambios de cámara y acciones físicas por beat, extrae screenshots de alta resolución para cada corte usando FFmpeg dinámico y organiza todo dentro de 04_IN_PRODUCTION/PROD_<ID>_<nombre>/01_Reference/ junto al archivo script_beats_<nombre>.txt.
---

# UGC Reference Video Analyzer & Beat Extractor

## Propósito

Automatizar el análisis técnico de videos UGC de referencia: transcripción literal con marcas de tiempo mediante Whisper ASR, mapeo de beats, descripción de acciones físicas, captura de frames clave en alta resolución con FFmpeg y aislamiento de videos procesados.

---

## Flujo de Trabajo Paso a Paso

### 1. Detección y Análisis del Archivo
- **Ubicación de Entrada:** Localizar el video dentro de `03_INBOX_REFERENCES/<canal>/<nombre_video>.mp4`.
- **Clasificación del Formato de Personajes en el Hook:**
  - **Unipersonal (1 Sujeto):** El creador se graba a sí mismo y demuestra la acción/problema en su propio cuerpo/rostro.
  - **Multi-Personaje (2 Sujetos - Especialista + Paciente/Modelo):** El creador actúa como especialista/evaluador examinando a otra persona (paciente/modelo) que presenta el problema (Día 1) y muestra la transformación (Día 7).
- **Auditoría de Intensidad del Problema en el Hook:**
  - Evaluar si el problema mostrado en pantalla (ojeras, manchas, acné, hinchazón) es *Sutil, Moderado o Exagerado*.

---

### 2. Creación del Directorio de Staging
- Crear la estructura de producción del proyecto dentro de `04_IN_PRODUCTION/`:
  - `04_IN_PRODUCTION/PROD_<ID>_<nombre_video>/`
    - `📁 01_Reference/` (donde vivirán el video base, los screenshots y el script)
    - `📁 02_First_Frames/` (para los renders 9:16)
    - `📁 03_Raw_Clips/` (para los clips de video falado)
    - `📁 04_Audio/` (para locuciones o audios nativos)
- Copiar el archivo de video `.mp4` a `01_Reference/<nombre_video>.mp4`.

---

### 3. Transcripción ASR Automática (Whisper)
- Ejecutar la extracción de audio y transcripción palabra por palabra usando el motor `ASREngine` (faster-whisper) de Python (`auto-captions-service`):

```python
import sys
from pathlib import Path
sys.path.insert(0, 'auto-captions-service')
from app.core.audio_extractor import AudioExtractor
from app.core.asr_engine import ASREngine

video_path = Path("04_IN_PRODUCTION/PROD_<ID>_<nombre_video>/01_Reference/<nombre_video>.mp4")
temp_wav = Path("auto-captions-service/temp_extract.wav")
AudioExtractor.extract_audio(video_path, temp_wav)
transcript_data = ASREngine.transcribe(temp_wav, language="en")
```

---

### 4. Extracción de Keyframes en Alta Resolución (FFmpeg)
- Extraer los 6 fotogramas clave de cada beat usando el ejecutable resuelto por `FFmpegLocator`:

```python
from app.core.ffmpeg_utils import FFmpegLocator
import subprocess

ffmpeg_bin, _ = FFmpegLocator.get_binaries()
# Extraer frames con calidad -q:v 2
# 01_beat1_hook.jpg, 02_beat2_reframe.jpg, 03_beat3_ingredients.jpg...
```

---

### 5. Generación del Archivo de Beats (`script_beats_<nombre_video>.txt`)
- Guardar el archivo en `04_IN_PRODUCTION/PROD_<ID>_<nombre_video>/01_Reference/script_beats_<nombre_video>.txt`.
- **Estructura Requerida:**

```text
=======================================================
SCRIPT POR BEATS Y MARCAS DE TIEMPO — <NOMBRE_VIDEO>.MP4
=======================================================
FORMATO: [Unipersonal / Multi-Personaje (Especialista + Paciente)]
INTENSIDAD DEL PROBLEMA EN HOOK: [Sutil / Moderado / Exagerado]
DIAGNÓSTICO DE ENTORNO / BACKGROUND:
- Entorno de Referencia: [Descripción forense del fondo en el video original, ej: Tienda boutique de cosméticos con iluminación de retail y displays]
- Assets de Entorno Disponibles del Creador: [Listar imágenes de 02_AVATAR_ASSETS/02_Environments/]
- Opciones de Checkpoint:
  1. Replicación 1:1 del Entorno de Referencia
  2. Asset Canónico 1 (ej: Cocina 1.jpeg)
  3. Asset Canónico 2 (ej: Cuarto.jpeg)
  4. Custom / Personalizado

[BEAT 1: HOOK]
Timestamp: 0:00 - 0:06
Voiceover: "..."
Acción física y encuadre: ...
Screenshots / Keyframes: 01_beat1_hook.jpg

[BEAT 2: REFRAME]
Timestamp: 0:06 - 0:12
Voiceover: "..."
Acción física y encuadre: ...
Screenshots / Keyframes: 02_beat2_reframe.jpg

[BEAT 3: MECHANISM - RECETA Y PREPARACIÓN]
Timestamp: 0:12 - 0:24
Voiceover: "..."
Acción física y encuadre: ...
Screenshots / Keyframes: 03_beat3_ingredients.jpg, 04_beat3_application.jpg

[BEAT 4: PAYOFF]
Timestamp: 0:24 - 0:32
Voiceover: "..."
Acción física y encuadre: ...
Screenshots / Keyframes: 05_beat4_payoff.jpg

[BEAT 5: CTA]
Timestamp: 0:32 - 0:40
Voiceover: "..."
Acción física y encuadre: ...
Screenshots / Keyframes: 06_beat5_cta.jpg

=======================================================
SCRIPT COMPLETO CONTINUO (VOICEOVER ORIGINAL LITERAL)
=======================================================
"..."
```

---

### 6. Aislamiento y Archivo del Video en Inbox
- Mover físicamente el video original desde `03_INBOX_REFERENCES/<canal>/<nombre_video>.mp4` a la subcarpeta `03_INBOX_REFERENCES/<canal>/_PROCESSED/` para mantener el inbox libre de duplicados.

---

### 7. Checklist de Validación
- [ ] Carpeta de staging creada en `04_IN_PRODUCTION/PROD_<ID>_<nombre_video>/`.
- [ ] Transcripción literal palabra por palabra obtenida con Whisper.
- [ ] Screenshots `.jpg` nítidos presentes en `01_Reference/`.
- [ ] Diagnóstico de formato e intensidad del Hook documentados.
- [ ] Video original archivado en `_PROCESSED/`.
- [ ] Archivo `script_beats_<nombre_video>.txt` generado y listo para la Fase 3.
