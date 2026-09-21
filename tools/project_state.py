"""Estado por proyecto (state.json): fase actual y gates aprobados, para retomar una producción."""
import sys
import json
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

STATE_FILE = "state.json"
PHASES = ("fase1_ingesta", "fase2_keyframes", "checkpoint1", "fase3_prompts", "fase4_ensamblaje", "certificado")


def load_state(project_dir: Path) -> dict:
    path = Path(project_dir) / STATE_FILE
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return {"phase": PHASES[0], "gates": {}, "updated_at": None}


def save_state(project_dir: Path, **updates) -> dict:
    if "phase" in updates and updates["phase"] not in PHASES:
        raise ValueError(f"phase debe ser una de {PHASES}")
    state = load_state(project_dir)
    state.update(updates)
    state["updated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    Path(project_dir, STATE_FILE).write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    return state


def record_gates(project_dir: Path, gates: list, precheck: bool = False) -> dict:
    """Guarda el resultado de cada gate; avanza la fase solo si todos pasan."""
    results = {g["gate_id"]: bool(g["passed"]) for g in gates}
    state = load_state(project_dir)
    merged = {**state.get("gates", {}), **results}
    updates = {"gates": merged}
    if not precheck and len(merged) == 7 and all(merged.values()):
        updates["phase"] = "certificado"
    return save_state(project_dir, **updates)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Muestra el estado de un proyecto")
    ap.add_argument("project_dir")
    print(json.dumps(load_state(Path(ap.parse_args().project_dir)), ensure_ascii=False, indent=2))
