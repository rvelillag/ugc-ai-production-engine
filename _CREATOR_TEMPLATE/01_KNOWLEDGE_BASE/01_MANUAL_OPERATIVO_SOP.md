# 📋 MANUAL OPERATIVO ESTÁNDAR (SOP): PASO A PASO
**Procedimiento Operativo para la Creación de Videos UGC Ágiles**

Este manual describe el flujo de trabajo directo de 6 etapas para producir videos UGC de alta retención orgánica bajo la arquitectura de 5 Beats y Chunks <= 10s.

---

## ETAPA 1: DEFINICIÓN DE LA RECETA O REPLICACIÓN

1. **Si es Replicación de Video Existente (1:1):**
   * Extraer metadatos con `ffprobe` (duración exacta, resolución y framerate).
   * Transcribir audio de referencia con `whisper`.
   * Identificar los 5 momentos clave del video original.
   * Extraer fotogramas de referencia de cada beat.
2. **Si es Concepto Original de la Marca:**
   * Definir el dolor/problema principal que resuelve (caída de cabello, retención de líquidos, inflamación, pesadez).
   * Identificar los 2 o 3 ingredientes botánicos clave.
   * Definir la acción visual impactante del Hook (exprimir, partir, gotear, verter).

---

## ETAPA 2: REDACCIÓN DEL GUION EN PROSA CONTINUA

* Escribir el guion completo continuo (de 100 a 125 palabras para videos de ~45 segundos).
* **Cadencia objetivo:** Calcular a ~2.4 palabras por segundo para sincronizar con la duración objetivo.
* **Estructura en 5 Partes:**
  1. **Frase gancho (0 a 3s):** *"Did you know that if you squeeze fresh lime over a ripe banana...?"* / *"¿Sabías que si mezclas...?"*
  2. **Proceso rápido:** *"Toss it into your blender with cinnamon and water..."*
  3. **Payoff / Pregunta de dolor:** *"If you wake up feeling heavy or bloated, drink a glass before bed..."*
  4. **Mecanismo:** *"It cleanses your liver and resets your metabolism overnight—you'll feel the difference in seven days..."*
  5. **Cierre / Follow CTA:** *"Follow my profile right here so you don't miss my next natural recipes!"*

---

## ETAPA 3: SUBDIVISIÓN EN 5 CHUNKS (ESTRICTO <= 10.0 SEGUNDOS)

* Aplicar la matriz de duración: dividir el video completo en **5 chunks de 8.0 a 10.0 segundos** (ningún clip puede superar los 10.00s).
* Asignar a cada chunk su beat correspondiente:
  * Chunk 1: Beat 1 (Hook Sensorial)
  * Chunk 2: Beat 2 (Proceso Dinámico)
  * Chunk 3: Beat 3 (Payoff Sensorial)
  * Chunk 4: Beat 4 (Mecanismo Fisiológico)
  * Chunk 5: Beat 5 (Cierre / Follow CTA)

---

## ETAPA 4: GENERACIÓN DEL FIRST FRAME DEL HOOK (MIDJOURNEY / FLUX)

* Generar una imagen vertical 9:16 fotorrealista para el Chunk 1.
* **Parámetros obligatorios en el prompt:**
  * Avatar canónico (Rachel Bennett o Carmen Del Valle).
  * Locación canónica (Veranda Kitchen, Bennett Studio, o Casa Del Valle).
  * Ingrediente activo en primer plano con interacción física en mano (sosteniendo, exprimiendo, goteando).
  * Ángulo picado a pulso (20° a 35°) simulando smartphone handheld UGC, luz natural matutina.

---

## ETAPA 5: REDACCIÓN DE PROMPTS DE VIDEO (KLING / VEO / RUNWAY)

Para cada uno de los 5 chunks del proyecto, redactar el prompt con la plantilla canónica:
1. `VOICE LOCK` (Perfil vocal y cadencia ~2.4 WPS).
2. `SPOKEN DIALOGUE` (Texto exacto del fragmento).
3. `LIP-SYNC & PHONEME TIMESTAMPS` (Desglose en 2 bloques cronometrados).
4. `TIMED MICRO-STEPS & HANDHELD CAMERA MOVEMENTS` (Acción física y ángulo de smartphone).
5. `🔊 SFX:` (Foley fotorrealista exclusivo; cero música de fondo).

---

## ETAPA 6: REVISIÓN DE CALIDAD Y EXPORTACIÓN

1. Guardar el caso de estudio en:
   * `sistema_produccion_ugc/casos_de_estudio/<nombre_del_caso>.md`
   * Y dentro de la carpeta del proyecto en `avatares/<Avatar>/04_IN_PRODUCTION/<PROD_XXX>/`
2. Validar con [`04_CHECKLIST_DE_CALIDAD.md`](file:///C:/Users/Asus/Downloads/DTC/sistema_produccion_ugc/04_CHECKLIST_DE_CALIDAD.md).
3. Listo para generar clips sin fricción técnica.
