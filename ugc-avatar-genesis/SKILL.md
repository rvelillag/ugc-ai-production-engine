---
name: ugc-avatar-genesis
description: >-
  Guía y wizard integral para crear la identidad inmutable de nuevos avatares UGC AI (Character DNA, Character Sheets consistentes, entornos oficiales 9:16, perfiles de voz y catálogos de producto). Utilizar cuando se desee dar de alta a un nuevo creador o marca en el sistema de producción.
---

# UGC Avatar Genesis Engine (Guía de Onboarding de Nuevos Creadores)

## Propósito

Esta skill proporciona el procedimiento paso a paso para dar de alta a un nuevo avatar y marca en el sistema de producción UGC, asegurando que su identidad visual, perfil acústico, escenarios y productos propios queden blindados para garantizar resultados de máxima calidad y consistencia en cada video.

---

## 1. Flujo de Onboarding en 6 Pasos (0 a 5)

### Paso 0: Entrevista de Personaje

Antes de crear ningún archivo, pregunta al usuario cuál de las dos rutas quiere tomar:

- **Ruta A — Desde cero:** el agente conduce una entrevista para construir la ficha del personaje a partir del contexto de audiencia y marca.
- **Ruta B — Desde referencia:** el usuario aporta fotos o videos de un avatar real que ya convierte; el agente extrae la ficha directamente de esos materiales y la remodela con la identidad de la nueva marca.

---

#### Ruta A — Desde cero

Conduce esta entrevista conversacional, una pregunta a la vez:

1. **Contexto del video/audiencia.** Pregunta por el nicho/tema del video y la investigación de audiencia que ya tenga. Si no tiene nada, haz 2-3 preguntas rápidas (quién sufre qué, cuál es el gancho emocional) para esbozar una audiencia ligera.

2. **Tipo de personaje.** Propón uno de estos 5 arquetipos con una razón de una línea basada en el contexto del paso 1; el usuario puede aceptar o pedir otra opción:
   - **Especialista** — autoridad profesional, accesible, sin bata blanca ni lenguaje distante.
   - **Espejo** — idéntico a la audiencia, empieza escéptico, comparte un descubrimiento honesto.
   - **Familiar** — un par/amigo que comparte su rutina cotidiana sin esfuerzo.
   - **Insider** — habla desde dentro de la industria/empresa, "esto es lo que no te cuentan."
   - **Convertido** — un ex-escéptico/sufriente que encontró la solución y ahora la evangeliza.

3. **Ficha del personaje.** Completa lo siguiente, proponiendo sugerencias concretas cuando el usuario no tenga nada en mente:
   - Nombre, edad, género, apariencia general (clase social que transparece).
   - Jeito de ser: cómo habla, qué valora, energía (cansada, acogedora, animada, seria).
   - Apariencia física: cabello, piel, cuerpo, ropa, accesorios — anclados a parecerse a la audiencia, no a un modelo genérico.
   - Expresión de rostro en reposo.
   - Gancho de atención: qué hace que la persona no siga scrolleando.

4. **Confirmación.** Muestra la ficha completa al usuario para un sí/ajuste final antes de escribir nada a disco.

5. **Escritura de archivos** — ver sección común al final de este paso.

---

#### Ruta B — Desde referencia

Parte de materiales reales de un avatar que ya funciona con la audiencia objetivo:

1. **Pide nombre y marca.** Son los únicos datos necesarios para crear la carpeta antes de analizar los archivos.

2. **Crea la carpeta** ejecutando `python tools/init_creator.py --name "<Nombre>" --brand "<Marca>"` con solo esos dos campos. Esto genera `<Nombre>/02_AVATAR_ASSETS/00_Reference_Input/` donde el usuario colocará los archivos.

3. **Pide los archivos de referencia.** Indica al usuario que coloque fotos o videos del avatar de referencia en:
   ```
   <Nombre>/02_AVATAR_ASSETS/00_Reference_Input/
   ```
   Formatos aceptados: `.jpg`, `.jpeg`, `.png`, `.mp4`, `.mov`. Cuando el usuario confirme que los archivos están listos, léelos con la herramienta Read (imágenes) o analízalos visualmente.

4. **Extrae la ficha.** A partir de los materiales, documenta:
   - Apariencia física: cabello, piel, edad aparente, cuerpo, ropa, accesorios.
   - Energía y jeito de ser: cómo habla, ritmo, tono emocional.
   - Expresión en reposo y microexpresiones características.
   - Gancho de atención: qué hace en los primeros segundos que detiene el scroll.
   - Arquetipo que mejor describe a este avatar (propón uno con una razón de una línea).

5. **Remodela la ficha** para la nueva marca: mantén la apariencia y energía del avatar de referencia; ajusta solo lo que la identidad de marca requiera (nombre, keyword, nicho, outfit si aplica).

6. **Confirmación.** Muestra la ficha remodeada al usuario para un sí/ajuste final antes de escribir nada más a disco.

7. **Escritura de archivos** — ver sección común al final de este paso.

---

#### Escritura de archivos (común a Ruta A y Ruta B)

Solo ejecutar después de la confirmación del usuario:

- **Ruta A:** llama primero a `python tools/init_creator.py --name "<Nombre>" --brand "<Marca>" --archetype "<Tipo>" --target-audience "<Audiencia>" [--age N] [--gender ...] [--niche ...] [--keyword ...]`. `init_creator.py` aborta si la carpeta ya existe, así que ningún archivo puede crearse por adelantado.
- **Ruta B:** la carpeta ya existe desde el paso 2; actualiza `creator_profile.yaml` con los campos faltantes (archetype, target_audience, age, gender, niche, keyword) que no se pasaron en el `init_creator.py` inicial.

Una vez que la carpeta existe, escribe los siguientes archivos:

- `CHARACTER_BRIEF.md` en `<Nombre>/02_AVATAR_ASSETS/01_Character/CHARACTER_BRIEF.md`:

  ```markdown
  # Character Brief — <Nombre>

  ## Contexto de Audiencia
  <nicho, resumen de investigación de audiencia>

  ## Tipo de Personaje: <Especialista|Espejo|Familiar|Insider|Convertido>
  <por qué este tipo encaja con esta audiencia>

  ## Jeito de Ser
  <cómo habla, qué valora, energía>

  ## Apariencia Física
  <cabello, piel, cuerpo, ropa, accesorios — y por qué cada elección refleja a la audiencia>

  ## Expresión en Reposo
  <...>

  ## Gancho de Atención
  <qué hace que la persona no siga scrolleando>

  ## Fuente
  <"Construido desde cero" | "Extraído de referencia: [nombre del archivo]">
  ```

- El párrafo-ancla compacto para `*_CHARACTER_DNA.md` (Paso 4), sin nombre completo real en el descriptor visual.
- Los prompts de imagen desde `prompts_avatar_builder.md` (Retrato de Perfil, Hoja de Consistencia Facial, y — si hay imagen aprobada — Hoja de Referencia desde Imagen Subida), presentados como texto listo para copiar en Midjourney/Flux.

---

### Paso 1: Inicializar el Espacio de Trabajo

> **Nota:** Si ya completaste el Paso 0 (Entrevista de Personaje), este paso ya se ejecutó automáticamente como parte de la Escritura de Archivos del Paso 0. En ese caso, puedes omitir el comando siguiente — el espacio de trabajo ya está creado con el archetype y target-audience ya capturados. Este comando es solo necesario si creas el espacio de trabajo sin pasar por la entrevista guiada.

Ejecutar el script de inicialización para crear la estructura de carpetas a partir de la plantilla maestra:

```bash
python tools/init_creator.py --name "<Nombre_Creador>" --brand "<Nombre_Marca>"
```

Esto creará automáticamente la carpeta `<Nombre_Creador> - <Nombre_Marca>/` con sus 5 subdirectorios y archivos de configuración.

---

### Paso 2: Definir la Persona & Arquetipo en `creator_profile.yaml`
Completar las variables clave:
* **Arquetipo:**
  * `Especialista` — autoridad profesional, accesible, sin bata blanca ni lenguaje distante.
  * `Espejo` — idéntico a la audiencia, empieza escéptico, comparte un descubrimiento honesto.
  * `Familiar` — un par/amigo que comparte su rutina cotidiana sin esfuerzo.
  * `Insider` — habla desde dentro de la industria/empresa, "esto es lo que no te cuentan."
  * `Convertido` — un ex-escéptico/sufriente que encontró la solución y ahora la evangeliza.
* **Paleta de Vestuario:** 4 a 5 colores neutros/tierra para rotación sistemática.
* **Configuración de Voz:** ID de voz en ElevenLabs o especificación para TTS nativo (Veo3/Kling).

---

### Paso 3: Generar los Assets Visuales del Avatar (Midjourney / Flux)

Consultar [`prompts_avatar_builder.md`](file:///c:/Users/Asus/Downloads/DTC/ugc-avatar-genesis/prompts_avatar_builder.md) para copiar las fórmulas de prompts:

1. **Retrato de Perfil (`Profile Picture.jpeg`):**
   * Primer plano frontal con luz natural de ventana, piel humana real con poros visibles, líneas de expresión naturales y mirada despierta.
2. **Hoja de Consistencia Facial (`character_sheet.png`):**
   * Grilla multi-ángulo: Vista frontal, vista tres cuartos izquierda, vista tres cuartos derecha, perfil lateral, y expresiones (neutra, sonrisa honesta, preocupación por problema).
3. **Entornos Oficiales 9:16 (`02_Environments/`):**
   * `01_Kitchen_Main.jpg` (Cocina con encimera de madera y luz matutina).
   * `02_Bathroom_Mirror.jpg` (Baño limpio para aplicaciones de skincare).
   * `03_LivingRoom_Daylight.jpg` (Espacio cotidiano para testimonios).

Guardar todos los renders en `02_AVATAR_ASSETS/01_Character/` y `02_AVATAR_ASSETS/02_Environments/`.

---

### Paso 4: Redactar la Fuente de Verdad (`*_CHARACTER_DNA.md`)
Crear el archivo `02_AVATAR_ASSETS/01_Character/<NOMBRE>_CHARACTER_DNA.md` integrando:
* **Prompt Anchor Verbatim:** El párrafo descriptivo inmutable del avatar. Puede empezar con su nombre para uso interno del documento, pero **al copiarlo a `avatar_visual_descriptor` en Fase 3, se omite el nombre y apellido** — un prompt hiperrealista con el nombre completo de una persona dispara los filtros de "personas destacadas/reales" de Veo3/Kling (error real observado en producción, no teórico). El resto del descriptor físico se copia literal.
* **Audio & Voice Direction Anchor:** La definición acústica, tono, ritmo (~2.3 palabras/segundo) y acústica de habitación doméstica para generadores con audio integrado.

---

### Paso 5: Registrar el Catálogo de Productos (`PRODUCT_CATALOG.yaml`)
Registrar en `PRODUCT_CATALOG.yaml` los productos que la marca comercializa:
* Nombre del producto.
* Categoría (Limpiador, Esencia láctea, Serum reparador, Base fluida, etc.).
* **Descripción Visual para Prompts:** Forma del envase, color, gotero/bomba dosificadora para que la IA genere el frasco correcto en las manos del avatar.
* **Keyword ManyChat:** Palabra clave para automatización en Instagram/TikTok.

---

## 2. Checklist de Validación del Avatar

- [ ] Carpeta del creador creada con la estructura estándar (01 a 05).
- [ ] `creator_profile.yaml` configurado con paleta de vestuario y ManyChat.
- [ ] `CHARACTER_BRIEF.md` redactado en `01_Character/` con la ficha completa de la entrevista.
- [ ] `Profile Picture.jpeg` y `character_sheet.png` guardados en `01_Character/`.
- [ ] Fondos oficiales 9:16 guardados en `02_Environments/`.
- [ ] `*_CHARACTER_DNA.md` creado con Prompt Anchor y Audio Anchor probados.
- [ ] `PRODUCT_CATALOG.yaml` completado con los productos de la marca.
- [ ] Listo para recibir videos virales de referencia en `03_INBOX_REFERENCES/`.
