import os
import sys
import json
import re
import subprocess
from pathlib import Path
from faster_whisper import WhisperModel

sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.ledger import LEDGER_FILE, anchor_times

def beat_label(idx: int, total: int) -> str:
    """Canonical beat name for keyframe idx (0-based). Middle 'action' slots should be renamed to the real verb."""
    if idx == 0:
        return "beat1_hook"
    if total > 1 and idx == total - 1:
        return "beat5_cta"
    if idx == 1:
        return "beat2_reframe"
    middle = total - 3
    pos = idx - 2
    if middle == 1:
        return "beat3_action"
    if pos < middle - 1:
        return f"beat3_{pos + 1}_action"
    return "beat4_action"

def extract_scenes_and_cadence(video_path: Path, output_dir: Path = None, model_size: str = "medium", language: str = None):
    if output_dir is None:
        output_dir = video_path.parent
    
    # 1. Get video duration
    cmd_dur = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(video_path)]
    duration_str = subprocess.check_output(cmd_dur, text=True).strip()
    total_duration = float(duration_str)
    
    print(f"Analyzing Video: {video_path.name} ({total_duration:.2f}s)")
    
    # 2. Transcribe with Whisper
    print("Running Whisper transcription with word timestamps...")
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    segments, info = model.transcribe(str(video_path), word_timestamps=True, language=language)
    
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
    
    # Few genuine cuts detected — cascade through smarter fallbacks before using percentages.
    if len(cut_timestamps) < 4:
        # Fallback 1: lower scene threshold (catches subtle same-room UGC cuts)
        scene_cmd2 = [
            "ffmpeg", "-i", str(video_path),
            "-filter:v", "select='gt(scene,0.10)',showinfo",
            "-f", "null", "-"
        ]
        p2 = subprocess.run(scene_cmd2, stderr=subprocess.PIPE, text=True, errors="replace")
        low_thresh_cuts = [0.0]
        for line in p2.stderr.splitlines():
            if "pts_time:" in line:
                m2 = re.search(r"pts_time:([0-9\.]+)", line)
                if m2:
                    ts2 = float(m2.group(1))
                    if ts2 - low_thresh_cuts[-1] >= 1.5 and ts2 < total_duration - 0.8:
                        low_thresh_cuts.append(round(ts2, 2))
        if len(low_thresh_cuts) >= 4:
            cut_timestamps = low_thresh_cuts
            print(f"  (low-threshold scene detection: {len(cut_timestamps)} cuts found)")

    if len(cut_timestamps) < 4:
        # Fallback 2: ledger action boundaries (if ledger was pre-built)
        anchors = anchor_times(output_dir / LEDGER_FILE)
        if len(anchors) >= 4:
            cut_timestamps = anchors
            print(f"  (ledger anchor fallback: {len(cut_timestamps)} cuts)")

    if len(cut_timestamps) < 4:
        # Fallback 3: Whisper sentence-end boundaries — far better than fixed percentages
        # because they align with natural speech pauses and action changes in UGC content.
        sentence_ends = []
        for seg in whisper_segments:
            end_t = seg["end"]
            if end_t > 0.5 and end_t < total_duration - 0.5:
                if not sentence_ends or end_t - sentence_ends[-1] >= 2.0:
                    sentence_ends.append(round(end_t, 2))
        if len(sentence_ends) >= 3:
            cut_timestamps = [0.0] + sentence_ends
            print(f"  (Whisper sentence-boundary fallback: {len(cut_timestamps)} cuts)")
        else:
            # Last resort: evenly spaced — only for very short or near-silent videos
            n_splits = max(3, round(total_duration / 8))
            cut_timestamps = [round(total_duration * i / n_splits, 2) for i in range(n_splits)]
            print(f"  (equidistant last-resort fallback: {len(cut_timestamps)} splits)")
    
    # No fixed cap: the number of genuine cuts scales with the video's length/edit density.
    # The >=1.2s de-dup above already keeps the count meaningful rather than exploding on noise.

    print(f"Detected {len(cut_timestamps)} visual takes at timestamps: {cut_timestamps}")

    # 4. Extract Keyframes
    extracted_frames = []
    for idx, ts in enumerate(cut_timestamps):
        frame_time = min(ts + 0.4, total_duration - 0.2)
        frame_filename = f"{idx+1:02d}_{beat_label(idx, len(cut_timestamps))}.jpg"
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
* Acción y Encuadre: (no se infiere del corte; se documenta en {LEDGER_FILE})
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
    parser.add_argument("--model", default="medium", help="Modelo faster-whisper (base/small/medium)")
    parser.add_argument("--language", default=None, help="Idioma del audio (en/es); auto si se omite")
    args = parser.parse_args()
    
    video = Path(args.video)
    out = Path(args.output) if args.output else video.parent
    extract_scenes_and_cadence(video, out, model_size=args.model, language=args.language)
