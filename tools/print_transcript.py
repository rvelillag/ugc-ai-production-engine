import sys
from pathlib import Path
from faster_whisper import WhisperModel

sys.stdout.reconfigure(encoding="utf-8")
video_path = Path("Rachel Bennett - Botanique/04_IN_PRODUCTION/PROD_011_elainevanhausen_4/01_Reference/elainevanhausen_4.mp4")

model = WhisperModel("base", device="cpu", compute_type="int8")
segments, info = model.transcribe(str(video_path), word_timestamps=True)

for seg in segments:
    print(f"[{seg.start:.2f}s -> {seg.end:.2f}s] {seg.text}")
