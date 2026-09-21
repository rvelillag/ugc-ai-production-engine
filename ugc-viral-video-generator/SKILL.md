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
2. **Insumos de Referencia & Ficha de Beats:** Desde `04_IN_PRODUCTION/PROD_<ID>_<video>/01_Reference/` (`script_beats_<video>.txt` y capturas `.jpg`).
3. **Catálogo de Producto Propio:** Desde `PRODUCT_CATALOG.yaml` para sustituir automáticamente marcas de terceros.
4. **Historial de Vestuario:** Revisar el atuendo usado en la producción previa para rotar la paleta de color.

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

## 3. Matriz de Control Temporal & Sub-Chunking (6s, 8s, 10s)

> **Constante de Locución:** $2.2 \text{ a } 2.4 \text{ palabras por segundo}$ (con margen de respiración para evitar cortes de audio en Veo3/Kling/Grok).

* **6 segundos:** Hasta 15 palabras.
* **8 segundos:** 16 a 20 palabras.
* **10 segundos:** 21 a 24 palabras (máximo por clip).

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

1. **Regla de Fidelidad Verbatim (≥85 %):** el diálogo de cada fila del ledger se conserva ≥85 % palabra por palabra; solo se permiten ajustes mínimos de voz del avatar y el cambio de marcas/CTA por las fórmulas seguras. Cadencia ≤ 2.4 WPS.

2. **Desacoplamiento de Marca y Venta (Venta en ManyChat, NO en el Video):**
   - **El video no menciona marcas comerciales específicas** (ni marcas de terceros ni venta directa agresiva en el diálogo del video).
   - Los ingredientes, problemas y productos se mencionan de forma genérica/educativa (*"bicarbonato con tu champú"*, *"hydrating essence"*, *"grip primer"*, *"serum foundation"*).
   - **La recomendación exacta de producto, enlaces y conversión se delegan al 100% a la automatización de ManyChat** cuando el usuario comenta la palabra clave.

3. **CTA Seguro y Anti-Filtros:**
   - Se adapta la palabra clave de ManyChat (ej. `LIFT`, `GLOW`, `HAIR`) aplicando las fórmulas seguras anti-filtros aprobadas (sin usar palabras censuradas como `age` o `DM`).

---

## 8. Estructura Canónica de Prompts de Video (I2V Motion con Timeline Forense y SFX)

Para garantizar sincronización de labios exacta, correlación 1:1 entre acciones y diálogos, y físicas de movimiento realistas en generadores de video (Veo3, Kling, Hailuo, Grok), **todos los Video Motion Prompts deben seguir estrictamente esta arquitectura de 4 bloques**. Los prompts se generan con `tools/prompt_compiler.py` a partir del `action_timeline`; la plantilla de abajo describe su salida.

### Plantilla Maestra de Video Motion Prompt:
```text
Hyper-realistic vertical 9:16 smartphone UGC video. Use the canonical [DETALLES DE ENTORNO/ESCENARIO CANÓNICO]. [IDENTIDAD DEL AVATAR, EDAD, VESTUARIO EXACTO]. Preserve her identity, clothing, lighting, environment, table position, props and camera style throughout the entire clip.

*ACTION:*
0–3s: [Tipo de encuadre / plano]. [Acción física y gesticulación con props]. She looks directly into the smartphone camera and says: "[TEXTO EXACTO DE DIÁLOGO DEL SEGMENTO 1]"

3–8s: [Acción física continua con props / demostración]. She [gesto] while continuing: "[TEXTO EXACTO DE DIÁLOGO DEL SEGMENTO 2]"

Natural realistic hand movements. No cuts. No exaggerated acting.

*SFX:* [ambience del entorno, sonido físico sutil de contacto con mesa/superficie, sonido natural de manipulación de props e ingredientes].
```

### Reglas Clave de Redacción de Video Prompts:
1. **Header de Consistencia Inmutable:** Define la relación de aspecto 9:16, escenario canónico y el candado de continuidad (*"Preserve her identity, clothing, lighting, environment, table position, props and camera style throughout the entire clip"*).
2. **Bloques `*ACTION:*` con Timestamps de Milisegundo:** Cada segundo de duración ($0\text{–}3\text{s}$, $3\text{–}8\text{s}$, etc.) tiene su acción física correspondiente y su fragmento de diálogo explícito entrecomillado (`says: "..."`, `while continuing: "..."`).
3. **Restricción de Realismo Cinematográfico:** Obligatorio incluir `"Natural realistic hand movements. No cuts. No exaggerated acting."` para evitar sobreactuación o cortes artificiales de cámara.
4. **Capa Acústica y Foley (`*SFX:*`):** Define el ruido de fondo del entorno doméstico/estudio y los sonidos dieléctricos reales de los objetos al ser manipulados (líquidos, vidrio, madera, cerámica).




