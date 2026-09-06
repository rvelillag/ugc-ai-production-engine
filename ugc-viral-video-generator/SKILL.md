---
name: ugc-viral-video-generator
description: >-
  Proceso completo y repetible para replicar videos UGC virales de formato remedio o receta natural (25-30s) para Instagram y Facebook,
  sustituyendo al creador original por un avatar propio consistente mediante la arquitectura de 5 beats, skeletons de producción (standard y chunked),
  bloques universales de dirección, análisis de composición de hook, prompts de first frame, prompts de video/animación I2V y control de duración de clips (6s, 8s, 10s).
---

# Generación de Videos UGC Virales (Guion, First Frames, Video Motion Prompts & Timing)

## Propósito

Esta skill define el proceso completo, repetible y auditable para replicar videos UGC virales adaptando al avatar propio, manteniendo la arquitectura de guion (70% similitud), cámara y edición. Genera el paquete integral de producción: guion limpio para TTS, prompts de First Frame (Midjourney/Flux), prompts de Video/Animación (Kling/Veo3/Grok/Luma) con **Duración Recomendada por Clip (6s, 8s, 10s)** y regla de sub-chunking.

---

## 1. Inputs Requeridos Obligatorios (Input Gate)

Antes de construir cualquier skeleton o prompt, el sistema consulta obligatoriamente:

1. **Fuente de Verdad del Avatar (Inmutable):** Desde `02_AVATAR_ASSETS/01_Character/*_CHARACTER_DNA.md`.
   - Cargar edad, arquetipo psicológico (*Mirror + Convert*, etc.), rasgos físicos inmutables, el **Prompt Anchor Verbatim** y el **Audio & Voice Direction Anchor**.
   - > [!CAUTION]
     > Si el archivo `*_CHARACTER_DNA.md` no existe en `02_AVATAR_ASSETS/01_Character/`, detenerse inmediatamente y solicitar la ficha de identidad al usuario.
2. **Insumos de Referencia:** Desde `04_IN_PRODUCTION/PROD_<ID>_<video>/01_Reference/` (`script_beats_<video>.txt` y screenshots `.jpg`).
3. **Base de Conocimientos:** Desde `01_KNOWLEDGE_BASE/` (`PRODUCTION_WORKFLOW_SOP.md`, Playbooks).
4. **Historial de Vestuario:** Revisar el atuendo usado en la producción previa para rotar la paleta de color.

---

## 2. Diagnóstico de Arquitectura & Traslación de Roles

### 2.1 Formato de Personajes & Traslación de Arquetipo
* **Formato Unipersonal:** El creador se graba solo y demuestra la acción/problema en su propio cuerpo.
* **Formato Multi-Personaje (Host + Paciente/Amiga):**
  * Si la referencia es **Clínica/Médica** (doctor con bata/guantes examinando a un paciente) y el Avatar es de arquetipo **Mirror + Convert**, se realiza una **traslación de contexto**:
    * El avatar actúa como **Anfitriona de cocina compartiendo su descubrimiento con una amiga/invitada**.
    * La amiga/invitada asume el rol de quien sufre el problema en el Día 1 y muestra la transformación en el Día 7.

### 2.2 Arquitectura de 5 Beats & Regla de Sub-Chunking Temporal

| Beat | Función | Rango de Duración | Límite Máximo de Palabras |
|---|---|---|---|
| **1. Hook** | Disrupción física + problema exagerado + promesa rápida | 0:00–0:06 (6s) | Máx. 15 palabras |
| **2. Reframe** | Giro de autoridad/industria + revelación Día 7 | 0:06–0:12 (6s) | Máx. 15 palabras |
| **3. Mechanism** | Preparación en mesada + receta exacta con medidas | 0:12–0:24 (12s total) | *Sub-Chunking Obligatorio (3A: 6s / 3B: 6s)* |
| **4. Payoff** | Aplicación sensorial en piel + glow coreano | 0:24–0:32 (8s) | Máx. 20 palabras |
| **5. CTA** | Llamado a comentar con follow-gate | 0:32–0:40 (8s) | Máx. 20 palabras |

> [!IMPORTANT]
> **REGLA DURA DE SUB-CHUNKING TEMPORAL:**
> Las herramientas de generación de video IA operan en duraciones estándar de **6 segundos, 8 segundos o 10 segundos**.
> * **Nivel 1 (6 segundos):** Hasta 15 palabras de locución (ritmo natural: ~2.5 palabras/segundo).
> * **Nivel 2 (8 segundos):** 16 a 20 palabras de locución.
> * **Nivel 3 (10 segundos):** 21 a 24 palabras de locución (máximo absoluto por clip).
> * Si un beat supera las 24 palabras, **se divide obligatoriamente en Sub-Chunks (ej. Chunk 3A y Chunk 3B)**, cada uno con su propio First Frame y su propio Video Motion Prompt con su duración recomendada.

---

## 3. Character Lock & Matriz de Rotación de Vestuario

1. **Character Lock Verbatim:** Se extrae de `*_CHARACTER_DNA.md` y se inserta textualmente en cada prompt visual.
2. **Audio & Voice Direction Anchor:** Se extrae de `*_CHARACTER_DNA.md` y se inserta textualmente en cada Video Motion Prompt.
3. **Rotación de Vestuario:**
   * La prenda superior rota de color en cada producción dentro de la paleta permitida de la marca (ej. Terracota Cálido, Verde Salvia, Azul Pizarra, Lino Beige, Gris Carbón).
   * **Registro Obligatorio en el Encabezado:**
     `Outfit Anterior: [Color/Tipo] → Outfit Asignado Actual: [Color/Tipo]`.

---

## 4. Universal Direction Blocks (Bloques Fijos)

* **Skin Direction:** Describe piel real con micro-textura y poros visibles. En el Chunk 1 (Día 1) describe explícitamente el síntoma severo; en el Día 7 / Payoff describe piel uniforme, luminosa y recuperada.
* **Application / Action Direction:** Gestos cotidianos, fluidos y naturales (verter, batir, remover, aplicar con suavidad), nunca robóticos.
* **B-Roll Sequencing Block:** Ningún ingrediente aparece en cuadro antes de ser nombrado explícitamente. Cero tomas decorativas desvinculadas.
* **UGC Realism Direction:** Encuadre 9:16 de smartphone, luz natural de ventana, micro-movimiento de cámara en mano (handheld jitter) y confidencia no publicitaria.

---

## 5. Regla de Exageración Forzada en el Hook (Parámetros Obligatorios)

* El prompt de imagen del Chunk 1 **DEBE** emplear descriptores de alta intensidad y contraste:
  * *Vocabulario Requerido:* `severe`, `prominent`, `high-contrast dark melasma patches`, `deep sun damage`, `noticeable puffy swelling`, `marked uneven discoloration`.
  * *Términos Prohibidos en Hook:* `slight`, `subtle`, `mild`, `barely visible`.
* El punto de contacto (dedo señalando la zona afectada) debe situarse en el tercio superior-medio en foco nítido.

---

## 6. Producción de Skeletons (Estándar Obligatorio)

Todo paquete de entrega debe contener:

### 6.1 Standard Production Skeleton (Toma Única Continua 25-30s)
Un solo bloque integral para plataformas que generan tomas largas completas.

### 6.2 Chunked Production Skeleton (Chunks Operativos con Duración Recomendada)
Cada chunk debe contener obligatoriamente:
1. **Beat:** (Hook, Reframe, Mechanism 3A, Mechanism 3B, Payoff, CTA).
2. **Word Count & Recommended Clip Duration:** Especificar `Word Count: [N] palabras` y `Recommended Duration: [6s / 8s / 10s]`.
3. **Voiceover:** Texto limpio sin guiones largos (em dashes) ni negritas para TTS/ElevenLabs/Lipsync.
4. **Visual Direction & Movimiento de Cámara:** Encuadre, gesticulación y dinámica de cámara.
5. **Prompt de Imagen (First Frame en Midjourney/Flux/Imagen):** 9:16 vertical en prosa continua.
6. **Prompt de Video / Animación (I2V en Kling/Veo3/Grok/Luma):**
   * Incluye el `[AUDIO & VOICE DIRECTION ANCHOR]` de `*_CHARACTER_DNA.md`, físicas de movimiento, jitter de celular y lipsync.
7. **Asset Tags:** (`@objeto`).
8. **Continuity Notes & Bookend:** Simetría garantizada entre Chunk 1 y el Chunk final.

---

## 7. Cut Points y Fallback Cuts

* Documentar los puntos de corte naturales entre beats.
* **Regla de Fallback:** El Hook (Chunk 1) es intocable. Si el Chunk de aplicación presenta fallos, se fusiona con el de mezcla mostrando la consistencia en el cuenco.

---

## 8. Título + Caption con Follow-Gate

* **Título:** Corto (bajo 10 palabras), con emoji y gancho de curiosidad/resultado.
* **Caption:** 3-4 párrafos cortos: gancho de escepticismo personal, receta con medidas caseras exactas y llamado a la acción con **Follow-Gate** y palabra clave para automatización en ManyChat.

---

## 9. Checklist Final de Calidad

- [ ] `*_CHARACTER_DNA.md` consultado y aplicado verbatim (Visual + Audio Anchor).
- [ ] Arquetipo de personaje correctamente traducido (sin bata médica si es Mirror+Convert).
- [ ] Rotación de vestuario registrada respecto a la producción previa.
- [ ] Descriptores de alta intensidad aplicados en el Hook (Exageración forzada).
- [ ] Conteo de palabras y **Duración Recomendada (6s, 8s, 10s)** asignada por cada chunk.
- [ ] Sub-chunking aplicado si algún beat excede 24 palabras / 10s.
- [ ] Standard Production Skeleton + Chunked Skeletons con **First Frame Prompt** Y **Video Motion Prompt**.
- [ ] Caption con follow-gate y keyword ManyChat listo.
