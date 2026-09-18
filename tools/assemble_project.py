import os
import sys
import json
import shutil
import argparse
import subprocess
from pathlib import Path
from faster_whisper import WhisperModel

# Add project root and auto-captions-service to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "auto-captions-service"))

from app.core.ffmpeg_utils import FFmpegLocator
from app.core.pipeline import CaptionPipeline
from tools.cover_generator import generate_cover_advanced

def assemble_project(project_path_str: str, brand_dir_str: str = None, silence_padding_start: float = 0.12, silence_padding_end: float = 0.22):
    ffmpeg_bin, _ = FFmpegLocator.get_binaries()
    project_path = Path(project_path_str)
    
    if not project_path.is_absolute():
        # Try finding it in brands
        base_dir = Path.cwd()
        if (base_dir / project_path).exists():
            project_path = base_dir / project_path
        else:
            # Search in subfolders
            found = list(base_dir.glob(f"*/04_IN_PRODUCTION/{project_path.name}"))
            if found:
                project_path = found[0]
            else:
                raise FileNotFoundError(f"Project folder not found: {project_path_str}")

    brand_dir = project_path.parent.parent
    prod_name = project_path.name
    deliv_id = prod_name.split("_")[1]

    raw_clips_dir = project_path / "03_Raw_Clips"
    montage_dir = project_path / "05_Montage"
    first_frames_dir = project_path / "02_First_Frames"
    
    montage_dir.mkdir(parents=True, exist_ok=True)
    
    job_dir = Path.cwd() / "scratch" / f"{prod_name}_assembly"
    job_dir.mkdir(parents=True, exist_ok=True)
    trimmed_dir = job_dir / "trimmed_clips"
    trimmed_dir.mkdir(parents=True, exist_ok=True)

    deliv_brand_folder = brand_dir / "05_PROCESSED_DELIVERABLES" / f"Avatar{deliv_id}"
    deliv_numeric_folder = brand_dir / "05_PROCESSED_DELIVERABLES" / deliv_id
    deliv_brand_folder.mkdir(parents=True, exist_ok=True)
    deliv_numeric_folder.mkdir(parents=True, exist_ok=True)

    # 1. Detect Raw Clips
    raw_clips = sorted(list(raw_clips_dir.glob("*.mp4")), key=lambda x: int(x.stem) if x.stem.isdigit() else 999)
    if not raw_clips:
        raise FileNotFoundError(f"No raw clips found in {raw_clips_dir}")

    print(f"=== Assembling {prod_name} ({len(raw_clips)} clips detected) ===")

    # 2. Smart Silence Trimming using Faster-Whisper
    print("Stage 1: Performing Smart Silence Trimming on individual clips...")
    whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
    trimmed_clips = []

    for idx, clip in enumerate(raw_clips, 1):
        cmd_dur = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(clip)]
        dur = float(subprocess.check_output(cmd_dur, text=True).strip())

        segments, info = whisper_model.transcribe(str(clip), word_timestamps=True)
        all_words = []
        for s in segments:
            if s.words:
                for w in s.words:
                    all_words.append((w.word, round(w.start, 2), round(w.end, 2)))

        if all_words:
            first_speech = all_words[0][1]
            last_speech = all_words[-1][2]

            start_trim = max(0.0, first_speech - silence_padding_start)
            if first_speech <= 0.1:
                start_trim = 0.0

            end_trim = min(dur, last_speech + silence_padding_end)
        else:
            start_trim = 0.0
            end_trim = dur

        trimmed_clip = trimmed_dir / f"trimmed_{clip.name}"
        trimmed_clips.append(trimmed_clip)

        cmd_cut = [
            ffmpeg_bin, "-y",
            "-ss", f"{start_trim:.3f}",
            "-to", f"{end_trim:.3f}",
            "-i", str(clip),
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "18",
            "-c:a", "aac",
            "-b:a", "192k",
            str(trimmed_clip)
        ]
        subprocess.run(cmd_cut, check=True)
        print(f"  [Trimmed] {clip.name}: {start_trim:.2f}s -> {end_trim:.2f}s (Dur: {end_trim - start_trim:.2f}s, Cut: {dur - (end_trim - start_trim):.2f}s dead silence)")

    # 3. Concatenation
    print("\nStage 2: Concatenating seamlessly trimmed clips...")
    concat_list_path = job_dir / "concat_list.txt"
    with open(concat_list_path, "w", encoding="utf-8") as f:
        for tc in trimmed_clips:
            f.write(f"file '{tc.resolve()}'\n")

    concat_video_path = job_dir / "concatenated_tight.mp4"
    cmd_concat = [
        ffmpeg_bin, "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_list_path),
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "192k",
        str(concat_video_path)
    ]
    subprocess.run(cmd_concat, check=True)
    print(f"Seamless video created: {concat_video_path}")

    # 4. Auto-Captions Pipeline (viral_yellow_highlight)
    print("\nStage 3: Burning synchronized dynamic viral captions...")
    pipeline = CaptionPipeline(job_dir=job_dir)
    asr_data = pipeline.process_stage_asr(input_video_path=concat_video_path, language="en")
    words = asr_data.get("words", [])

    render_result = pipeline.process_stage_render(
        input_video_path=concat_video_path,
        words=words,
        template_name="viral_yellow_highlight",
        auto_emoji=True,
        uppercase=True,
        export_srt=True,
        export_ass=True
    )
    output_burned_video = render_result["output_video_path"]
    output_srt = render_result["srt_path"]

    # 5. Extract Frame and Generate Cover Badge
    print("\nStage 4: Generating high-impact Cover...")
    json_path = first_frames_dir / f"production_package_{prod_name.split('_')[0]}_{prod_name.split('_')[1]}.json"
    if not json_path.exists():
        found_json = list(first_frames_dir.glob("*.json"))
        if found_json:
            json_path = found_json[0]

    cover_headline = "VIRAL UGC VIDEO"
    title = ""
    caption = ""
    hashtags = ""
    if json_path and json_path.exists():
        with open(json_path, "r", encoding="utf-8") as f:
            pkg = json.load(f)
            post_copy = pkg.get("post_copy", {})
            cover_headline = post_copy.get("cover_headline", cover_headline)
            title = post_copy.get("title", "")
            caption = post_copy.get("caption", "")
            hashtags = " ".join(post_copy.get("hashtags", []))

    copy_content = f"""HEADLINE DE PORTADA:
{cover_headline}

Title: {title}

Caption:
{caption}

{hashtags}
"""

    raw_frame_path = job_dir / "raw_first_frame.jpg"
    cmd_frame = [
        ffmpeg_bin, "-y",
        "-ss", "00:00:00.800",
        "-i", str(concat_video_path),
        "-frames:v", "1",
        "-q:v", "2",
        str(raw_frame_path)
    ]
    subprocess.run(cmd_frame, check=True)

    cover_badge_path = job_dir / "Cover_Badge.jpg"
    generate_cover_advanced(
        input_image_path=raw_frame_path,
        headline=cover_headline,
        output_image_path=cover_badge_path
    )

    # 6. Deliverables Export
    print("\nStage 5: Exporting canonical deliverable packages...")
    # 05_Montage
    shutil.copy(output_burned_video, montage_dir / f"{prod_name.split('_')[0]}_{deliv_id}_Final_Master.mp4")
    if output_srt and output_srt.exists():
        shutil.copy(output_srt, montage_dir / f"{prod_name.split('_')[0]}_{deliv_id}_Subtitles.srt")
    shutil.copy(cover_badge_path, montage_dir / "Cover.jpg")

    # Brand Deliv
    shutil.copy(output_burned_video, deliv_brand_folder / f"Avatar{deliv_id}_Final_1080x1920.mp4")
    if output_srt and output_srt.exists():
        shutil.copy(output_srt, deliv_brand_folder / f"Avatar{deliv_id}_Subtitles.srt")
    shutil.copy(cover_badge_path, deliv_brand_folder / f"Avatar{deliv_id}_Cover.jpg")
    with open(deliv_brand_folder / "post_copy_title_and_caption.txt", "w", encoding="utf-8") as f:
        f.write(copy_content)

    # Numeric Deliv
    shutil.copy(output_burned_video, deliv_numeric_folder / f"{deliv_id}_Final_1080x1920.mp4")
    if output_srt and output_srt.exists():
        shutil.copy(output_srt, deliv_numeric_folder / f"{deliv_id}_Subtitles.srt")
    shutil.copy(cover_badge_path, deliv_numeric_folder / f"{deliv_id}_Cover.jpg")
    with open(deliv_numeric_folder / "post_copy_title_and_caption.txt", "w", encoding="utf-8") as f:
        f.write(copy_content)

    print(f"\n[SUCCESS] Project {prod_name} assembled with Smart Silence Trimming!")
    return {
        "burned_video": str(output_burned_video),
        "srt": str(output_srt),
        "cover": str(cover_badge_path),
        "deliverables_dir": str(deliv_brand_folder)
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Assemble raw clips with Smart Silence Trimming into canonical deliverable.")
    parser.add_argument("--project", required=True, help="Project directory name or path (e.g., PROD_012_cuenta_a_6)")
    args = parser.parse_args()
    assemble_project(args.project)
