---
name: ugc-viral-video-generator
description: >-
  Proceso JSON-First riguroso y repetible para replicar videos UGC virales (25-30s) para Instagram y Facebook con fidelidad visual 1:1,
  descomponiendo cada frame de referencia en capas técnicas (cámara, utilería, poses anatómicas X/Y y estado de piel), sustituyendo al personaje
  con el Character DNA verbatim, adaptando al catálogo de producto propio (PRODUCT_CATALOG.yaml) y autogenerando el production_package_PROD_<ID>.json y prompts_and_script_PROD_<ID>.md.
---

# Generación de Videos UGC Virales (Protocolo JSON-First con Fidelidad 1:1)

## Propósito

Esta skill define el proceso estricto y auditable para replicar videos UGC virales sustituyendo al creador original por un avatar consistente, garantizando **fidelidad visual 1:1 con respecto a las capturas de referencia**. Genera primero la fuente técnica estructurada `production_package_PROD_<ID>.json` validada con Pydantic y compila automáticamente el documento maestro `prompts_and_script_PROD_<ID>.md`.

---

## 1. Inputs Requeridos Obligatorios (Input Gate)

Antes de construir cualquier JSON o prompt, el sistema consulta obligatoriamente:

1. **Fuente de Verdad del Avatar (Inmutable):** Desde `02_AVATAR_ASSETS/01_Character/*_CHARACTER_DNA.md`.
   - Cargar edad, rasgos físicos inmutables, el **Prompt Anchor Verbatim** y el **Audio & Voice Direction Anchor**.
   - Al usar el Prompt Anchor Verbatim en `avatar_visual_descriptor`, elimina el nombre y apellido del avatar (ej. "Rachel Bennett, an authentic 47-year-old..." → "an authentic 47-year-old..."); copia el resto tal cual. Ver la nota en la sección 8.
2. **Insumos de Referencia & Ficha de Beats:** Desde `04_IN_PRODUCTION/PROD_<ID>_<video>/01_Reference/` (`script_beats_<video>.txt` y capturas `.jpg`).
3. **Catálogo de Producto Propio:** Desde `PRODUCT_CATALOG.yaml` para sustituir automáticamente marcas de terceros.
4. **Historial de Vestuario:** Revisar el atuendo usado en la producción previa para rotar la paleta de color.
5. **Ledger y Checkpoint 1:** `01_Reference/reference_ledger.json` (confirmado por el usuario) y `checkpoint1.json` (`scene_mode`, `hook_exaggeration`, `fidelity_target`) son insumos obligatorios.
6. **Tomas Reales (agrupación de chunks):** `01_Reference/script_beats_<video>.txt` — el número de TOMAS detectadas ahí (cortes de cámara genuinos) es la base para decidir cuántos chunks hay y dónde empiezan/terminan, NO las filas del ledger (ver sección 3).

---

## 2. Metodología de Desglose Fotográfico en 5 Capas & Regla de Escenario

### A. Escenario y Disparador de Hook (gobernados por Checkpoint 1)
* **Escenario:** lo decide `scene_mode` de `checkpoint1.json`: `replicate_1to1` replica el entorno de la referencia; `adapt_to_brand` usa el escenario canónico de la marca.
* **Acciones:** se replican idénticas, en orden, desde `01_Reference/reference_ledger.json`. La hiper-exageración del disparador visual solo se aplica si `hook_exaggeration` es `true`.

### B. Desglose en 5 Capas Técnicas:
Cada beat se audita obligatoriamente contra su captura `.jpg` correspondiente (`01_` a `06_`):

1. **Capa 1: Cámara y Óptica:** Distancia focal (24mm ultra-wide para perspectiva forzada en hooks, 28mm, 35mm, 50mm, macro), tipo de plano (9:16 vertical, plano medio, plano detalle) y ángulo de cámara.
2. **Capa 2: Primer Plano, Props y Disparadores Stop-Scroll:** Objetos exactos y utilería de choque en la mesa/isla de mármol o en las manos del avatar (maqueta colosal de boca/lengua, frascos estéticos, ingredientes, vertido activo).
3. **Capa 3: Poses Anatómicas y Orientación:**
   * **Sujeto Izquierdo (Avatar):** Orientación de torso, ángulo de brazos, interacción física con los props y dirección fija de la mirada hacia el lente del smartphone.
   * **Sujeto Derecho (si aplica):** Orientación, postura de brazos, qué sostiene y síntoma exagerado.
4. **Capa 4: Inyección del Character Sheet & DNA Verbatim:** Inserción íntegra de los descriptores físicos del avatar (`CHARACTER_DNA.md`), peinado inmutable y vestuario asignado.
5. **Capa 5: Limpieza Visual Absoluta:**
   * **Cero Textos, Cero Overlays, Cero Subtítulos Quemados, Cero Marcas de Agua, Cero Logos de Redes Sociales.**

---

## 3. Agrupación de Chunks por Toma Real & Sub-Chunking (6s, 8s, 10s)

> **Constante de Locución (sin techo artificial, variable por proyecto):** `wps_target` en `checkpoint1.json` = el WPS real medido en `script_beats_<video>.txt` (`CADENCIA PROMEDIO`), usado tal cual, sin recortarlo a ningún máximo. `ugc_harness.py` (GATE_2) lee ese valor (default 2.4 solo si el campo falta) y calcula el máximo real como `int(duración_s * wps_target)`. Los límites `[0.5, 10.0]` en el código son solo un guardarraíl de cordura contra datos corruptos (ej. WPS mal calculado en un video casi mudo), no una política de velocidad máxima — si Fase 4 detecta audio/lip-sync forzado a ese ritmo, se baja `wps_target` para ese chunk y se regenera, no se limita de antemano.

Ejemplo de topes por duración con distintos `wps_target` (calcula el que corresponda a TU referencia):

| Duración | wps_target 2.4 | wps_target 3.5 | wps_target 4.1 |
|---|---|---|---|
| 6s | 14 palabras | 21 palabras | 24 palabras |
| 8s | 19 palabras | 28 palabras | 32 palabras |
| 10s (máx clip) | 24 palabras | 35 palabras | 41 palabras |

**Regla de agrupación (evita cortar diálogo a mitad de frase):**
1. Parte de las TOMAS reales de `script_beats_<video>.txt`, no de las filas del ledger — las filas se generan por pausas acústicas de Whisper (`build_draft_rows`), sin relación con los cortes de cámara ni con la gramática.
2. Si una TOMA completa cabe en ≤`10 × wps_target` palabras/≤10s, es un solo chunk. Con `wps_target` igual al ritmo real de la referencia, es común que TOMAS que antes requerían dividirse ahora quepan enteras en un solo chunk.
3. Si excede el límite, divide esa TOMA en el final de una de sus oraciones internas; si una sola oración de la TOMA ya excede el límite, divide en su único conector de respiración natural (ej. "...follicles **and** | the natural moisture...", nunca a mitad de una frase nominal como "...that | thin and middle part...").
4. Una fila del ledger puede quedar repartida entre dos chunks consecutivos sin problema — GATE_7 evalúa la fidelidad acumulando el diálogo de todos los pasos que referencian esa fila, en cualquier chunk.

**Duración total variable (dos palancas independientes, ninguna es un múltiplo fijo):** cuánto crece el video frente a la referencia depende de (a) `wps_target` — al ser el WPS real de la referencia, el crecimiento residual es solo por redondeo de cada chunk al segundo entero y por diferencias de longitud del CTA reescrito — y de (b) `fidelity_target` en `checkpoint1.json`: `full_verbatim` (duración = palabras totales ÷ `wps_target`) o `trim_to_min` (recorta además dentro del ≥85% por fila si aun así se quiere acortar más).

---

## 4. Pipeline de Generación (JSON-First -> Markdown)

1. **Generar JSON Validado:** Crear `04_IN_PRODUCTION/PROD_<ID>_<nombre>/02_First_Frames/production_package_PROD_<ID>.json`.
2. **Rellenar por chunk** `ledger_rows`, `ref_window`, `voiceover_reference` y `action_timeline`; luego compilar los prompts I2V:
   ```bash
   python tools/prompt_compiler.py --json "04_IN_PRODUCTION/PROD_<ID>_<nombre>/02_First_Frames/production_package_PROD_<ID>.json"
   ```
3. **Compilar Markdown:** Ejecutar el conversor oficial:
   ```bash
   python tools/render_package_markdown.py --json "04_IN_PRODUCTION/PROD_<ID>_<nombre>/02_First_Frames/production_package_PROD_<ID>.json"
   ```
4. El script creará automáticamente `prompts_and_script_PROD_<ID>.md` formateado con tablas y bloques de código listos para copiar.

---

## 5. Política de Seguridad y Moderación en Guiones & CTAs (Anti-Filter Standard)

Para prevenir bloqueos automáticos en generadores de voz/video (ElevenLabs, Kling, Veo3, Grok) y plataformas sociales (Meta/TikTok):

* **Términos Sensibles a Evitar:**
  * ❌ `age` (edad) $\rightarrow$ Activa filtros de privacidad, discriminación y protección de menores.
  * ❌ `DM` (direct message / mensaje directo) $\rightarrow$ Activa filtros de spam y automatizaciones no deseadas.

* **Fórmulas Aprobadas de Alta Conversión (Lipsync 10s Safe):**
  1. **Enfoque en Tipo de Piel (Belleza/Skincare):**
     > *"Comment [KEYWORD] and your skin type below for my complete routine. Make sure you follow so I can send you the guide!"*
  2. **Enfoque en Objetivos:**
     > *"Comment [KEYWORD] and your main skin goal below for my complete routine. Make sure you're following, or I can't share the guide with you!"*
  3. **Enfoque Directo y Seguro:**
     > *"Drop the word [KEYWORD] below for my complete routine. You must be following so I can send the guide your way!"*
  4. **Enfoque Casual y Amigable:**
     > *"Comment [KEYWORD] below to get my complete routine. Just make sure you follow so I have a way to send you the guide!"*

---

## 6. Estándar de Guión (Fidelidad Verbatim ≥85 %) & Desacoplamiento ManyChat

1. **Regla de Fidelidad Verbatim (≥85 %):** el diálogo de cada fila del ledger se conserva ≥85 % palabra por palabra; solo se permiten ajustes mínimos de voz del avatar y el cambio de marcas/CTA por las fórmulas seguras. Cadencia ≤ `wps_target` (= WPS real de la referencia, sin techo, ver Checkpoint 1.G). Como `wps_target` iguala el ritmo real de la referencia, la duración total del video resultante queda muy cerca de la original salvo que el usuario haya pedido recortar dentro del margen ≥85% (`trim_to_min`) para acortarla aún más — ambos valores son una decisión por video, no un múltiplo universal.

2. **Desacoplamiento de Marca y Venta (Venta en ManyChat, NO en el Video):**
   - **El video no menciona marcas comerciales específicas** (ni marcas de terceros ni venta directa agresiva en el diálogo del video).
   - Los ingredientes, problemas y productos se mencionan de forma genérica/educativa (*"bicarbonato con tu champú"*, *"hydrating essence"*, *"grip primer"*, *"serum foundation"*).
   - **La recomendación exacta de producto, enlaces y conversión se delegan al 100% a la automatización de ManyChat** cuando el usuario comenta la palabra clave.

3. **CTA Seguro y Anti-Filtros:**
   - Se adapta la palabra clave de ManyChat (ej. `LIFT`, `GLOW`, `HAIR`) aplicando las fórmulas seguras anti-filtros aprobadas (sin usar palabras censuradas como `age` o `DM`).

---

## 8. Estructura Canónica de Prompts de Video (I2V Motion con Timeline Forense y SFX)

Para garantizar sincronización de labios exacta, correlación 1:1 entre acciones y diálogos, y físicas de movimiento realistas en generadores de video (Veo3, Kling, Hailuo, Grok), **todos los Video Motion Prompts deben seguir estrictamente esta arquitectura de 4 bloques**. Los prompts se generan con `tools/prompt_compiler.py` a partir del `action_timeline`; la plantilla de abajo describe su salida.

> **⚠️ Nunca el nombre propio del avatar en el prompt:** `prompt_compiler.py` usa `avatar_visual_descriptor` (descriptor físico, ej. "a 47-year-old woman with a collarbone-length layered bob..."), no `avatar_name`. Un prompt hiperrealista con nombre y apellido de una persona específica dispara los filtros de "personas destacadas/reales" de Veo3/Kling — error real observado en producción. Lo mismo aplica a `midjourney_prompt_9_16`: redáctalo con el descriptor físico, nunca con "[Nombre Avatar], a sophisticated...". `avatar_name`/`*_CHARACTER_DNA.md` quedan solo para continuidad interna (documentación, asset_tags).

> **Qué es constante y qué varía:** el avatar y la locación son constantes entre todos los videos de la marca (`*_CHARACTER_DNA.md` y `02_Environments/*_ENVIRONMENT_DNA.md`, sincronizados por `prompt_compiler.py`; el `environment_background` de cada chunk solo nombra el área/ángulo del set). Clientes y extras pueden cambiar de un video a otro, pero son fijos dentro de cada video. Redacta `midjourney_prompt_9_16` solo con la escena: el compilador añade los locks de avatar, locación y secundarios.

> **Consistencia de personajes secundarios:** la consistencia no aplica solo al avatar. Toda otra persona recurrente (clienta, paciente, extras de fondo) se define una vez en `secondary_characters` (`role` + `descriptor` sin nombre propio). `prompt_compiler.py` lo inyecta idéntico en el header de cada prompt I2V y en cada `midjourney_prompt_9_16`; el campo `secondary_state` de cada chunk solo describe qué cambia (ej. cabello mojado → seco). GATE_1 falla si hay `right_subject` sin `secondary_characters`. Tip: reutiliza el primer frame del personaje secundario como imagen de referencia en los demás chunks.

### Plantilla Maestra de Video Motion Prompt (Compilada por tools/prompt_compiler.py):
```text
Raw unedited vertical 9:16 smartphone UGC video recorded on iPhone 15 Pro 24mm f/1.8 main camera. Subtle natural handheld breathing motion, authentic natural lighting, no CGI. Use the canonical [DETALLES DE ENTORNO/ESCENARIO CANÓNICO]. [DESCRIPTOR FÍSICO DEL AVATAR — NUNCA nombre y apellido, ver nota abajo —, AÑOS APARENTES (ej. 47yo, nunca 'age'/'edad': GATE_3), VESTUARIO EXACTO]. Preserve her identity, clothing, lighting, environment, table position, props and camera style throughout the entire clip.

*ACTION:*
0–3s: [Spatial Grounding inicial de objetos sobre superficie]. [Acción física y mecánica táctil detallada: posición de manos/dedos con prop A]. She looks directly into the smartphone camera and says: "[TEXTO EXACTO DE DIÁLOGO DEL SEGMENTO 1]"

3–8s: [Explicit Release de prop A si aplica y manipulación táctil pausada de prop B]. She [gesto de palma abierta / micro-expresión] while continuing: "[TEXTO EXACTO DE DIÁLOGO DEL SEGMENTO 2]"

Natural realistic hand movements. No cuts. No exaggerated acting. Authentic unretouched smartphone UGC camera feel, natural room lighting, zero CGI or plastic sheen. Skin/Hair Condition Lock: The creator must always be depicted with healthy, glowing, flawless skin and hair in the aspirational after-state, preserving natural visible pore texture. Application Lock: Any product applied glides on invisibly and translucent, without artificial white cast, chalkiness, or cakey residue. UGC Realism: Phone propped at eye level with subtle natural handheld micro-shake, relaxed open-palm gestures, and unhurried tactile prop handling.

*SFX:* [ambience del entorno, sonido físico sutil de contacto con mesa/superficie, foley natural de manipulación de props e ingredientes].
```

### Reglas Clave de Redacción de Video Prompts (UGC Script Writing System v2):
1. **Los 4 Bloques Universales de Dirección:**
   - **Skin/Hair Condition Lock:** El avatar presente SIEMPRE se muestra en el estado aspiracional posterior (*after-state* con piel y cabello radiantes, textura natural visible). Nunca se muestra el síntoma/problema previo sobre el avatar actual.
   - **Application Direction Lock:** Los productos tópicos aplicados se deslizan de forma transparente/invisible y se absorben con textura natural, sin residuos blancos ni rayas pastosas.
   - **B-Roll Sequencing Block:** El producto de solución NO aparece en cámara antes de que el guion lo nombre/justifique. Chunks tempranos usan gestos y props cotidianos de problema.
   - **UGC Realism Direction Block:** Teléfono a la altura de los ojos con micro-movimiento natural sutil, luz natural de ventana, gestos de palma abierta y postura relajada. Cero rigidez (nunca manos congeladas detrás de la espalda ni en los bolsillos).
2. **Reglas de Acción a Prueba de Balas (Visual-to-Voiceover Sync & Biomecánica):**
   - **Visual-to-Voiceover Sync:** La acción física descrita en cada segundo DEBE corresponder en detalle exacto a lo que el avatar dice en ese preciso instante.
   - **Mecánica Táctil Explícita:** Se debe describir la interacción física precisa (yemas de los dedos, rotación de tapa, presión del gotero, textura). Cero acciones genéricas como `"talks to camera"`.
   - **Spatial Grounding Inicial:** En el primer beat (`0–3s:`), declarar la disposición física de los objetos sobre la mesa antes de manipularlos.
   - **Biomechanical Phasing & Explicit Release:** Solo UN objeto activo manipulado a la vez; soltar explícitamente el objeto anterior antes de tomar el siguiente.
   - **Cero B-Roll Decorativo:** Todo cambio de encuadre o movimiento está motivado por acción física o revelación; prohibidos planos vacíos de muebles o paredes.
3. **Bloques `*ACTION:*` con Timestamps de Milisegundo:** Cada segmento temporal ($0\text{–}3\text{s}$, $3\text{–}8\text{s}$, etc.) tiene su acción física correspondiente y su fragmento de diálogo explícito entrecomillado.
4. **Capa Acústica y Foley (`*SFX:*`):** Define el ambiente de sala y los sonidos táctiles de contacto con superficies y props.




