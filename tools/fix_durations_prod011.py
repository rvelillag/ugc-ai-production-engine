import json
from pathlib import Path

pkg_path = Path("Rachel Bennett - Botanique/04_IN_PRODUCTION/PROD_011_elainevanhausen_4/02_First_Frames/production_package_PROD_011.json")

with open(pkg_path, "r", encoding="utf-8") as f:
    data = json.load(f)

for ch in data["chunks"]:
    cid = ch["chunk_id"]
    if cid == 1:
        ch["recommended_duration_s"] = 10
    else:
        ch["recommended_duration_s"] = 8

with open(pkg_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Updated production_package_PROD_011.json with calibrated chunk durations!")
