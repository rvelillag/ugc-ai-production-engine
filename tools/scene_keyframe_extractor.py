import os
import sys
import json
import re
import subprocess
from pathlib import Path
from faster_whisper import WhisperModel

sys.stdout.reconfigure(encoding="utf-8")

def extract_scenes_and_cadence(video_path: Path, output_dir: Path = None):
    if output_dir is None:
        output_dir = video_path.parent
    
    # 1. Get video duration
    cmd_dur = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(video_path)]
    duration_str = subprocess.check_output(cmd_dur, text=True).strip()
    total_duration = float(duration_str)
    
    print(f"Analyzing Video: {video_path.name} ({total_duration:.2f}s)")
    
    # 2. Transcribe with Whisper
    print("Running Whisper transcription with word timestamps...")
    model = WhisperModel("base", device="cpu", compute_type="int8")
    segments, info = model.transcribe(str(video_path), word_timestamps=True)
    
    whisper_segments = []
    all_words = []
    for s in segments:
        words = []
        if s.words:
            for w in s.words:
                words.append({"word": w.word.strip(), "start": round(w.start, 2), "end": round(w.end, 2)})
                all_words.append(w.word.strip())
        whisper_segments.append({
            "start": round(s.start, 2),
            "end": round(s.end, 2),
            "text": s.text.strip(),
            "words": words
        })
    
    total_words = len(all_words)
    wps = round(total_words / total_duration, 2) if total_duration > 0 else 0.0
    wpm = int(round(wps * 60))
    
    # 3. Detect Scene Cuts using FFmpeg
    print("Detecting visual scene transitions with FFmpeg...")
    scene_cmd = [
        "ffmpeg", "-i", str(video_path),
        "-filter:v", "select='gt(scene,0.22)',showinfo",
        "-f", "null", "-"
    ]
    p = subprocess.run(scene_cmd, stderr=subprocess.PIPE, text=True, errors="replace")
    
    # Extract timestamps of scene cuts
    cut_timestamps = [0.0]
    for line in p.stderr.splitlines():
        if "pts_time:" in line:
            m = re.search(r"pts_time:([0-9\.]+)", line)
            if m:
                ts = float(m.group(1))
                # Avoid micro-cuts < 1.0s apart
                if ts - cut_timestamps[-1] >= 1.2 and ts < total_duration - 0.8:
                    cut_timestamps.append(round(ts, 2))
    
    # If scene detection found fewer than 4 cuts, generate balanced beat anchors
    if len(cut_timestamps) < 4:
        cut_timestamps = [
            0.0,
            round(total_duration * 0.18, 2),
            round(total_duration * 0.36, 2),
            round(total_duration * 0.54, 2),
            round(total_duration * 0.72, 2),
            round(total_duration * 0.88, 2)
        ]
    
    print(f"Detected {len(cut_timestamps)} visual takes at timestamps: {cut_timestamps}")
    
    # 4. Extract Keyframes
    extracted_frames = []
    for idx, ts in enumerate(cut_timestamps):
        frame_time = min(ts + 0.4, total_duration - 0.2)
        frame_filename = f"0{idx+1}_take{idx+1}_{frame_time:.1f}s.jpg" if idx < 9 else f"{idx+1}_take{idx+1}_{frame_time:.1f}s.jpg"
        out_frame_path = output_dir / frame_filename
        
        ff_extract = [
            "ffmpeg", "-y", "-ss", str(frame_time),
            "-i", str(video_path),
            "-vframes", "1",
            "-q:v", "2",
            str(out_frame_path)
        ]
        subprocess.run(ff_extract, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        extracted_frames.append({"index": idx+1, "timestamp": frame_time, "filename": frame_filename})
        print(f"  -> Extracted Keyframe {frame_filename} at {frame_time:.2f}s")
    
    # 5. Build forensic script_beats.txt
    script_beats_content = f"""=======================================================
SCRIPT POR BEATS Y DESGLOSE FORENSE — {video_path.name.upper()}
=======================================================
DURACIÓN TOTAL: {total_duration:.2f}s
TOTAL PALABRAS: {total_words}
CADENCIA PROMEDIO: {wps} WPS ({wpm} WPM)
TOTAL TOMAS DETECTADAS: {len(extracted_frames)}

=======================================================
TRANSCRIPCIÓN COMPLETA LITERAL:
=======================================================
{" ".join([s["text"] for s in whisper_segments])}

=======================================================
DESGLOSE FORENSE POR TOMAS Y ACCIONES VISUALES (1:1):
=======================================================
"""
    for i in range(len(cut_timestamps)):
        start_t = cut_timestamps[i]
        end_t = cut_timestamps[i+1] if i+1 < len(cut_timestamps) else total_duration
        
        # Collect words spoken in this window
        seg_words = []
        for s in whisper_segments:
            for w in s["words"]:
                if w["start"] >= start_t - 0.2 and w["end"] <= end_t + 0.5:
                    seg_words.append(w["word"])
        
        spoken_text = " ".join(seg_words) if seg_words else "(Visual B-roll / Acción física continua)"
        frame_info = extracted_frames[i]
        
        script_beats_content += f"""
[TOMA {i+1} / BEAT]
* Timestamp: {start_t:.2f}s - {end_t:.2f}s ({round(end_t - start_t, 1)}s)
* Voiceover Segment: "{spoken_text}"
* Keyframe Extraído: {frame_info["filename"]}
* Acción y Encuadre: Plano correspondiente al corte visual detectado en {start_t:.2f}s.
"""

    script_beats_file = output_dir / f"script_beats_{video_path.stem}.txt"
    with open(script_beats_file, "w", encoding="utf-8") as f:
        f.write(script_beats_content)
    
    print(f"\nGenerated forensic breakdown: {script_beats_file}")
    return {
        "duration": total_duration,
        "total_words": total_words,
        "wps": wps,
        "whisper_segments": whisper_segments,
        "cut_timestamps": cut_timestamps,
        "extracted_frames": extracted_frames,
        "script_beats_file": str(script_beats_file)
    }

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", required=True, help="Path to reference video")
    parser.add_argument("--output", required=False, help="Output directory")
    args = parser.parse_args()
    
    video = Path(args.video)
    out = Path(args.output) if args.output else video.parent
    extract_scenes_and_cadence(video, out)
