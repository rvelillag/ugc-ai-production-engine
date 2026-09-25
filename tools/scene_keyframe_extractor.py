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
    output_dir.mkdir(parents=True, exist_ok=True)

    # Ensure full standard 5-folder project tree exists if inside a PROD directory
    proj_dir = output_dir if output_dir.name.startswith("PROD_") else (output_dir.parent if output_dir.parent.name.startswith("PROD_") else None)
    if proj_dir:
        for sub in ["01_Reference", "02_First_Frames", "03_Raw_Clips", "04_Audio", "05_Montage"]:
            (proj_dir / sub).mkdir(parents=True, exist_ok=True)
    
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
    
    # 3. Audio/Script-First Narrative & Semantic Segmentation (5 Canonical Beats)
    print("Analyzing narrative cadence, sentence boundaries, and natural pauses...")
    
    # Flatten word-level timestamps from all segments
    all_word_ts = []
    for seg in whisper_segments:
        for w in seg.get("words", []):
            if w.get("word", "").strip():
                all_word_ts.append(w)
    
    sentence_closing = {".", "!", "?", ":"}
    clause_conjunctions = {
        "and", "but", "or", "so", "then", "because", "after", "when", "while",
        "y", "pero", "o", "así", "entonces", "porque", "después", "luego", "cuando", "mientras"
    }

    # Detect visual cuts from FFmpeg for cross-reference and frame snapping
    print("Scanning visual scene transitions with FFmpeg for alignment...")
    scene_cmd = [
        "ffmpeg", "-i", str(video_path),
        "-filter:v", "select='gt(scene,0.18)',showinfo",
        "-f", "null", "-"
    ]
    p = subprocess.run(scene_cmd, stderr=subprocess.PIPE, text=True, errors="replace")
    raw_visual_cuts = []
    for line in p.stderr.splitlines():
        if "pts_time:" in line:
            m = re.search(r"pts_time:([0-9\.]+)", line)
            if m:
                ts = float(m.group(1))
                if 1.0 <= ts <= total_duration - 1.0:
                    raw_visual_cuts.append(round(ts, 2))

    # Identify semantic split points based on sentence endings, strong pauses, and sub-clause connectors
    MAX_TAKE_DURATION = 9.0  # Keep all generated clips safely <= 10s (Veo3/Kling limit)
    MIN_TAKE_DURATION = 2.0

    semantic_cuts = [0.0]
    last_cut = 0.0

    for i, w in enumerate(all_word_ts):
        word_raw = w["word"].strip()
        word_clean = word_raw.rstrip("\"')").lower()
        is_sentence_end = any(word_raw.endswith(p) for p in sentence_closing)
        end_t = w["end"]

        # Measure pause to next word
        pause = (all_word_ts[i + 1]["start"] - end_t) if (i + 1 < len(all_word_ts)) else (total_duration - end_t)
        current_dur = end_t - last_cut

        # Condition 1: Sentence closure with natural breathing pause (>= 0.15s) and sufficient take length
        is_strong_sentence_cut = is_sentence_end and (current_dur >= MIN_TAKE_DURATION) and (pause >= 0.12 or current_dur >= 4.0)

        # Condition 2: Long sub-beat take (> MAX_TAKE_DURATION - 2s) reaching a clause conjunction or pause >= 0.3s
        is_clause_split = (current_dur >= 5.5) and (word_clean in clause_conjunctions or is_sentence_end or pause >= 0.3)

        # Condition 3: Must split before exceeding MAX_TAKE_DURATION
        is_urgent_split = (current_dur >= MAX_TAKE_DURATION) and (pause >= 0.15 or is_sentence_end)

        if (is_strong_sentence_cut or is_clause_split or is_urgent_split) and (end_t < total_duration - 1.0):
            # Check if there is an FFmpeg visual cut nearby (+- 0.8s) to snap perfectly to the camera take
            candidate_ts = end_t
            for vcut in raw_visual_cuts:
                if abs(vcut - end_t) <= 0.85:
                    candidate_ts = vcut
                    break
            
            if candidate_ts - last_cut >= MIN_TAKE_DURATION:
                semantic_cuts.append(round(candidate_ts, 2))
                last_cut = candidate_ts

    # Ensure we cover the video adequately; if too few cuts, fallback to ledger anchors or proportional splits
    cut_timestamps = semantic_cuts
    if len(cut_timestamps) < 3:
        anchors = anchor_times(output_dir / LEDGER_FILE) if (output_dir / LEDGER_FILE).exists() else []
        if len(anchors) >= 3:
            cut_timestamps = anchors
            print(f"  (aligned to reference ledger anchors: {len(cut_timestamps)} takes)")
        else:
            n_splits = max(3, round(total_duration / 7.0))
            cut_timestamps = [round(total_duration * i / n_splits, 2) for i in range(n_splits)]
            print(f"  (distributed into {len(cut_timestamps)} balanced narrative takes)")

    # Deduplicate and sort as pure floats
    cut_timestamps = sorted([round(float(ts), 2) for ts in set(cut_timestamps)])
    if cut_timestamps[0] != 0.0:
        cut_timestamps.insert(0, 0.0)

    print(f"Constructed {len(cut_timestamps)} narrative takes at timestamps: {cut_timestamps}")

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
        
        # Collect words spoken in this window (disjoint partition by midpoint)
        seg_words = []
        for s in whisper_segments:
            for w in s["words"]:
                mid_t = (w["start"] + w["end"]) / 2.0
                if (i == 0 or mid_t >= start_t) and (i == len(cut_timestamps) - 1 or mid_t < end_t):
                    seg_words.append(w["word"])
        
        spoken_text = " ".join(seg_words) if seg_words else "(Visual B-roll / Acción física continua)"
        frame_info = extracted_frames[i]
        
        lbl = beat_label(i, len(cut_timestamps)).upper()
        script_beats_content += f"""
[{lbl} — TOMA {i+1}]
* Timestamp: {start_t:.2f}s - {end_t:.2f}s ({round(end_t - start_t, 1)}s)
* Voiceover Segment: "{spoken_text}"
* Keyframe Extraído: {frame_info["filename"]}
* Acción y Encuadre: (documentado en {LEDGER_FILE})
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
