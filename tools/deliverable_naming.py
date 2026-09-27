"""Shared policy for naming deliverable folders/files.

Convention: deliverable IDs are `[AvatarFirstName][XXX]` (e.g. `Rachel013`),
matching the original `Rachel001`..`Rachel012` catalog. The avatar's first
name is derived from the brand folder name, which follows the
`[Avatar Full Name] - [Brand]` convention (e.g. `Rachel Bennett - Botanique`
-> `Rachel`). No extra confirmation step or checkpoint1.json field is
required: any brand folder that already follows this naming convention
gets the correct prefix automatically.
"""
from pathlib import Path


def avatar_prefix(brand_dir: Path) -> str:
    """Return the avatar's first name from creator_profile.yaml or brand folder name,
    or '' if it can't be determined (falls back to the bare numeric id)."""
    # 1. Check creator_profile.yaml
    profile_path = brand_dir / "creator_profile.yaml"
    if profile_path.is_file():
        try:
            import yaml
            data = yaml.safe_load(profile_path.read_text(encoding="utf-8")) or {}
            c_name = (data.get("creator") or {}).get("name", "")
            if c_name and c_name.strip():
                first = c_name.strip().split()[0]
                clean = "".join(ch for ch in first if ch.isalnum())
                if clean:
                    return clean
        except Exception:
            pass

    # 2. Fall back to brand folder name parsing
    first_word = brand_dir.name.split(" - ")[0].split()[0] if brand_dir.name.strip() else ""
    return "".join(ch for ch in first_word if ch.isalnum())


def resolve_deliverable_id(brand_dir: Path, xxx: str) -> str:
    """Build the canonical deliverable id, e.g. brand_dir='Rachel Bennett -
    Botanique', xxx='013' -> 'Rachel013'. Falls back to the bare xxx if no
    avatar name can be derived from the brand folder."""
    prefix = avatar_prefix(brand_dir)
    return f"{prefix}{xxx}" if prefix else xxx
