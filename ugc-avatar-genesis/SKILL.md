---
name: ugc-avatar-genesis
description: >-
  Guía y wizard integral para crear la identidad inmutable de nuevos avatares UGC AI (Character DNA, Character Sheets consistentes, entornos oficiales 9:16, perfiles de voz y catálogos de producto). Utilizar cuando se desee dar de alta a un nuevo creador o marca en el sistema de producción.
---

# UGC Avatar Genesis Engine (Guía de Onboarding de Nuevos Creadores)

## Propósito

Esta skill proporciona el procedimiento paso a paso para dar de alta a un nuevo avatar y marca en el sistema de producción UGC, asegurando que su identidad visual, perfil acústico, escenarios y productos propios queden blindados para garantizar resultados de máxima calidad y consistencia en cada video.

---

## 1. Flujo de Onboarding en 5 Pasos

### Paso 1: Inicializar el Espacio de Trabajo
Ejecutar el script de inicialización para crear la estructura de carpetas a partir de la plantilla maestra:

```bash
python tools/init_creator.py --name "<Nombre_Creador>" --brand "<Nombre_Marca>"
```

Esto creará automáticamente la carpeta `<Nombre_Creador> - <Nombre_Marca>/` con sus 5 subdirectorios y archivos de configuración.

---

### Paso 2: Definir la Persona & Arquetipo en `creator_profile.yaml`
Completar las variables clave:
* **Arquetipo:**
  * `Mirror + Convert`: Persona idéntica a la audiencia, escéptica al inicio que comparte su descubrimiento honesto.
  * `Authority Expert`: Profesional accesible en entorno informal (sin bata blanca ni lenguaje distante).
  * `Lifestyle Peer`: Amiga/o que comparte su rutina cotidiana sin esfuerzo.
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
* **Prompt Anchor Verbatim:** El párrafo descriptivo inmutable del avatar que se copiará literalmente en cada First Frame.
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
- [ ] `Profile Picture.jpeg` y `character_sheet.png` guardados en `01_Character/`.
- [ ] Fondos oficiales 9:16 guardados en `02_Environments/`.
- [ ] `*_CHARACTER_DNA.md` creado con Prompt Anchor y Audio Anchor probados.
- [ ] `PRODUCT_CATALOG.yaml` completado con los productos de la marca.
- [ ] Listo para recibir videos virales de referencia en `03_INBOX_REFERENCES/`.
