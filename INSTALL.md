# 📦 Instalación y Versionado

Esta guía cubre cómo descargar el proyecto, cómo elegir una versión (tag) específica, y cómo volver a una versión anterior si algo se rompe. Para el instalador de dependencias (`install_and_setup.bat`) y el uso diario del sistema, ver el [README](README.md).

---

## 1. Cómo está versionado este repo

Cada versión estable se marca con un **tag Git anotado** siguiendo [SemVer](https://semver.org/lang/es/): `vMAJOR.MINOR.PATCH`.

- **PATCH** (`v1.0.1`): fix de un gate/script, sin romper compatibilidad.
- **MINOR** (`v1.1.0`): feature nueva retrocompatible (ej. un gate nuevo, un tool nuevo).
- **MAJOR** (`v2.0.0`): rompe compatibilidad (ej. cambia el schema de `production_package.json` o el formato del ledger).

Cada tag tiene un [Release en GitHub](https://github.com/rvelillag/ugc-ai-production-engine/releases) con el changelog de qué cambió.

Ver los tags disponibles:
```bash
git tag -l -n9        # -n9 muestra también el mensaje del tag
```

> **Nota (2026-09-22):** `v1.0.0` es hoy el único tag — es la primera versión etiquetada del pipeline. Todavía no hay versiones anteriores a las que volver vía tags; los pasos de esta guía quedan listos para cuando existan `v1.1.0`, `v2.0.0`, etc.

---

## 2. Cómo descargar el proyecto

### Opción A — Clon completo (recomendado)
Trae **todo el historial de commits**, no solo el snapshot de una versión. Permite moverse libremente entre tags más adelante sin pasos extra.

```bash
git clone https://github.com/rvelillag/ugc-ai-production-engine.git
cd ugc-ai-production-engine
git checkout v1.0.0     # (opcional) ubicarse en una versión concreta
```

Usa esta opción si vas a **actualizar** el sistema cuando salgan nuevas versiones.

### Opción B — Clon superficial (`--depth 1`)
Trae solo el commit de la versión pedida, sin el historial anterior. Más rápido/liviano, pero deja el repo en modo "shallow": no podrás saltar a otro tag sin primero traer el historial completo (`git fetch --unshallow`).

```bash
git clone --branch v1.0.0 --depth 1 https://github.com/rvelillag/ugc-ai-production-engine.git
cd ugc-ai-production-engine
```

Usa esta opción si solo vas a **usar esa versión puntual**, sin planes de actualizar después.

| | Clon completo | Clon `--depth 1` |
|---|---|---|
| Historial de commits | Completo | Solo el commit de la versión pedida |
| Código final en esa versión | Idéntico | Idéntico |
| Cambiar de tag después | Libre (`git checkout <otro-tag>`) | Requiere `git fetch --unshallow` primero |
| Velocidad/peso de descarga | Más pesado | Más liviano |

Después de clonar (cualquiera de las dos opciones), instala las dependencias con `install_and_setup.bat` (ver [README](README.md#-instalación-rápida-windows)).

---

## 3. Cómo cambiar a otra versión ya con el repo clonado

Traer los tags nuevos que no tenías (por si clonaste hace tiempo):
```bash
git fetch --tags
```

Moverte a una versión específica **sin tocar tu rama de trabajo** (deja el repo en `detached HEAD`, ideal solo para probar/usar):
```bash
git checkout v1.0.0
```

Si además quieres seguir trabajando desde ahí, crea una rama:
```bash
git checkout -b mi-rama-desde-v1.0.0 v1.0.0
```

Volver a la última versión de desarrollo:
```bash
git checkout main
git pull origin main
```

---

## 4. Cómo volver a una versión anterior si algo se rompió

- **Solo quieres revisar/usar la versión vieja**, sin perder tus cambios actuales:
  ```bash
  git checkout v1.0.0
  ```
- **Quieres que TU rama actual (ej. `main`) vuelva exactamente a ese estado**, descartando todo lo posterior:
  ```bash
  git reset --hard v1.0.0
  ```
  ⚠️ Esto es destructivo: borra commits locales no respaldados en otro lado. Si ya lo pusheaste, necesitarás `git push --force` (avisa a cualquiera que también tenga el repo clonado antes de hacerlo).
- **Quieres deshacer un cambio puntual sin perder el historial posterior**:
  ```bash
  git revert <hash-del-commit-problemático>
  ```

---

## 5. Para quien mantiene el repo: cómo etiquetar una nueva versión

```bash
git tag -a v1.1.0 -m "Descripción corta de qué cambió"
git push origin v1.1.0
gh release create v1.1.0 --title "v1.1.0" --notes "Changelog detallado aquí"
```
