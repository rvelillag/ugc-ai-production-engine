import os
import sys
import json
import subprocess
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from faster_whisper import WhisperModel
from tools.audio_cadence_analyzer import AudioCadenceAnalyzer

sys.stdout.reconfigure(encoding="utf-8")

video_path = Path("Rachel Bennett - Botanique/04_IN_PRODUCTION/PROD_011_elainevanhausen_4/01_Reference/elainevanhausen_4.mp4")
ref_dir = video_path.parent

# 1. Get video duration
cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(video_path)]
duration_str = subprocess.check_output(cmd, text=True).strip()
duration = float(duration_str)
print(f"Video Duration: {duration:.2f}s")

# 2. Transcribe with Whisper
print("Transcribing with faster-whisper...")
model = WhisperModel("base", device="cpu", compute_type="int8")
segments, info = model.transcribe(str(video_path), word_timestamps=True)

words_list = []
full_transcript_text = []
for segment in segments:
    full_transcript_text.append(segment.text)
    if segment.words:
        for w in segment.words:
            words_list.append({"word": w.word, "start": w.start, "end": w.end, "probability": w.probability})

transcript_str = " ".join(full_transcript_text).strip()
print("\n--- FULL TRANSCRIPT ---")
print(transcript_str)

# 3. Analyze Cadence
analysis = AudioCadenceAnalyzer.analyze_transcript(words_list, duration)
print("\n--- CADENCE ANALYSIS ---")
print(json.dumps(analysis, indent=2, ensure_ascii=False))

# 4. Extract 6 Keyframes
timestamps = [
    ("01_beat1_hook.jpg", 1.0),
    ("02_beat2_problem.jpg", max(2.0, duration * 0.22)),
    ("03_beat3_reframe.jpg", duration * 0.42),
    ("04_beat4_mechanism.jpg", duration * 0.62),
    ("05_beat5_payoff.jpg", duration * 0.82),
    ("06_beat6_cta.jpg", min(duration - 0.8, duration * 0.94))
]

for name, ts in timestamps:
    out_file = ref_dir / name
    ff_cmd = [
        "ffmpeg", "-y", "-ss", str(round(ts, 2)),
        "-i", str(video_path),
        "-vframes", "1",
        "-q:v", "2",
        str(out_file)
    ]
    subprocess.run(ff_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"Extracted {name} at {ts:.2f}s")

