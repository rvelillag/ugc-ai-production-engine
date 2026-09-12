import json
from pathlib import Path

pkg_path = Path("Rachel Bennett - Botanique/04_IN_PRODUCTION/PROD_011_elainevanhausen_4/02_First_Frames/production_package_PROD_011.json")

with open(pkg_path, "r", encoding="utf-8") as f:
    data = json.load(f)

for ch in data["chunks"]:
    text = ch["voiceover_clean_tts"]
    words = text.split()
    print(f"Chunk {ch['chunk_id']}: {len(words)} words -> '{text}'")
