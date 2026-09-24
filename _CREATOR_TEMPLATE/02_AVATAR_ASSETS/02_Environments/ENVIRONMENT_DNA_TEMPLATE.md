# [NOMBRE_MARCA] — ENVIRONMENT DNA (Fuente de Verdad de la Locación)

La locación principal de la marca es **constante entre todos los videos**, igual que el avatar. `prompt_compiler.py` lee el bloque
de la sección 1 y lo inyecta idéntico en cada prompt de video y de first frame. En cada video solo cambia el **área/ángulo** del set
que se encuadra (ej. estación de lavado, zona de espejos), nunca el set en sí.

## 1. ENVIRONMENT PROMPT ANCHOR VERBATIM

```text
[Describe el set con materiales, colores, iluminación y elementos fijos. Sin nombres de personas ni marcas.]
```

## 2. Áreas del set (encuadres permitidos)

- [Área 1: qué se ve, ángulo típico]
- [Área 2: ...]

## 3. Personajes secundarios y extras

Los clientes/extras **pueden variar de un video a otro**, pero dentro de cada video son fijos: se definen en `secondary_characters`
del `production_package_*.json`, no aquí.
