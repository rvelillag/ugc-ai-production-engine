# ✅ LISTA DE CONTROL DE CALIDAD (QA CHECKLIST)

Antes de considerar listo un proyecto de video o enviarlo a renderizado final, debe auditarse contra esta lista ágil de 5 puntos.

---

## 1. CONTROL DE DURACIÓN Y CHUNKS
- [ ] **Techo Máximo:** Ningún chunk excede los **10.00 segundos**.
- [ ] **Rango Óptimo:** La mayoría de los chunks se encuentran entre **8.0s y 9.5s**.
- [ ] **Estructura:** Exactamente 5 chunks narrativos (o 3-4 si es video ultra-corto <30s).
- [ ] **Duración Total:** Entre 40 y 48 segundos (óptimo para retención en TikTok / Reels).

---

## 2. CONTROL DE NARRATIVA Y VOICEOVER
- [ ] **Script Continuo:** Existe el guion completo continuo al inicio del documento.
- [ ] **Pregunta Gancho:** El Chunk 1 comienza con una pregunta activa o frase de asombro (*"Did you know that if you squeeze...?"* / *"¿Sabías que...?"*).
- [ ] **Payoff Sensorial:** El Chunk 3 muestra claramente el producto terminado o la textura espesa/cremosa.
- [ ] **Mecanismo Fisiológico:** El Chunk 4 explica de forma sencilla qué ocurre en el cuerpo (hígado, metabolismo, glucosa, folículos).
- [ ] **Llamado a la Acción:** El Chunk 5 tiene un CTA claro y directo (ej. seguir la cuenta para no perderse más recetas naturales).

---

## 3. CONTROL DE CONSISTENCIA VISUAL
- [ ] **Avatar:** Cumple con el Character Lock del avatar asignado (Rachel Bennett o Carmen Del Valle).
- [ ] **Locación:** Se ajusta a los escenarios canónicos (Bennett Studio, Veranda Kitchen o Casa Del Valle).
- [ ] **Cámara:** Ángulo simulado de smartphone sostenido a pulso con micro-oscilación física (*handheld micro-jitter*), sin sensación de trípode estático.
- [ ] **First Frame:** Prompt de Midjourney/Flux conciso (3-4 líneas), enfocado en la acción física en mano y el ángulo de cámara.

---

## 4. CONTROL DE AUDIO Y SFX
- [ ] **Cero Música en SFX:** La sección `🔊 SFX:` contiene exclusivamente efectos foley de cocina/salón (goteo, corte, vertido, tintineo de vidrio) y sonido ambiente. **Prohibido incluir música en el prompt de video**.
- [ ] **Lip-Sync Phonemes:** Cada chunk contiene su desglose en 2 bloques cronometrados con la acción física y el diálogo correspondiente.

---

## 5. CONTROL DE ARCHIVOS
- [ ] El documento markdown del caso está guardado en:
  - `sistema_produccion_ugc/casos_de_estudio/<nombre_del_caso>.md`
  - Y reflejado en la carpeta del proyecto en `avatares/<Avatar>/04_IN_PRODUCTION/<PROD_XXX>/`
