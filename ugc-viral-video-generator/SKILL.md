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

## 2. Metodología de Desglose Fotográfico en 5 Capas (Fidelidad 1:1)

Cada beat se audita obligatoriamente contra su captura `.jpg` correspondiente (`01_` a `06_`):

1. **Capa 1: Cámara y Óptica:** Distancia focal (24mm, 28mm, 50mm, macro), tipo de plano (9:16 vertical, plano medio, plano detalle) y ángulo de cámara.
2. **Capa 2: Primer Plano y Utilería (Props):** Objetos exactos en la mesa, mostrador, fregadero o en las manos de los sujetos (ej. cesta gris con cosméticos, frascos, borlas, tubos).
3. **Capa 3: Poses Anatómicas y Orientación:**
   * **Sujeto Izquierdo (Avatar):** Orientación de torso (perfil 3/4 hacia la derecha), ángulo de brazos, interacción de manos y dirección de la mirada.
   * **Sujeto Derecho (Modelo/Amiga):** Orientación, postura de brazos, qué sostiene con las manos, expresión facial y síntoma exagerado.
4. **Capa 4: Inyección del Character Sheet & DNA Verbatim:** Inserción íntegra de los descriptores físicos del avatar y vestuario asignado.
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
2. **Compilar Markdown:** Ejecutar el conversor oficial:
   ```bash
   python tools/render_package_markdown.py --json "04_IN_PRODUCTION/PROD_<ID>_<nombre>/02_First_Frames/production_package_PROD_<ID>.json"
   ```
3. El script creará automáticamente `prompts_and_script_PROD_<ID>.md` formateado con tablas y bloques de código listos para copiar.
