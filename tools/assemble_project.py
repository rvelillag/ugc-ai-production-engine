import os
import sys
import re
import json
import shutil
import argparse
import subprocess
from pathlib import Path
from faster_whisper import WhisperModel

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Add project root and auto-captions-service to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "auto-captions-service"))

from app.core.ffmpeg_utils import FFmpegLocator
from app.core.pipeline import CaptionPipeline
from tools.cover_generator import generate_cover_advanced
from tools.deliverable_naming import resolve_deliverable_id

def probe_fps(ffprobe_bin: str, clip: Path) -> str:
    out = subprocess.check_output(
        [ffprobe_bin, "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=avg_frame_rate",
         "-of", "default=noprint_wrappers=1:nokey=1", str(clip)], text=True).strip()
    num, _, den = out.partition("/")
    return f"{num}/{den}" if den and den != "0" else "30"

def build_trim_concat_cmd(ffmpeg_bin: str, segments, output_path: Path, fps: str = "30", width: int = 1080, height: int = 1920):
    """Single-pass trim + concat: segments is [(clip_path, start_s, end_s)]. One encode instead of one per clip plus one for the join."""
    cmd = [ffmpeg_bin, "-y"]
    for clip, _, _ in segments:
        cmd += ["-i", str(clip)]
    parts = []
    for i, (_, start, end) in enumerate(segments):
        parts.append(
            f"[{i}:v]trim=start={start:.3f}:end={end:.3f},setpts=PTS-STARTPTS,"
            f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
            f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={fps}[v{i}]"
        )
        fade_d = min(0.03, max(0.005, (end - start) / 4.0))
        fade_out_st = max(0.0, (end - start) - fade_d)
        parts.append(
            f"[{i}:a]atrim=start={start:.3f}:end={end:.3f},asetpts=PTS-STARTPTS,"
            f"afade=t=in:ss=0:d={fade_d:.3f},afade=t=out:st={fade_out_st:.3f}:d={fade_d:.3f},"
            f"aresample=48000,aformat=channel_layouts=stereo[a{i}]"
        )
    joined = "".join(f"[v{i}][a{i}]" for i in range(len(segments)))
    parts.append(f"{joined}concat=n={len(segments)}:v=1:a=1[outv][outa]")
    cmd += [
        "-filter_complex", ";".join(parts),
        "-map", "[outv]", "-map", "[outa]",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k",
        str(output_path),
    ]
    return cmd

def assemble_project(project_path_str: str, brand_dir_str: str = None, silence_padding_start: float = 0.12, silence_padding_end: float = 0.22, language: str = "auto", archive: bool = False, no_video_headline: bool = False, template: str = "poppins_yellow"):
    ffmpeg_bin, ffprobe_bin = FFmpegLocator.get_binaries()
    project_path = Path(project_path_str)
    
    engine_root = Path(__file__).resolve().parent.parent
    if not project_path.is_absolute():
        # Try finding it in current directory or brand workspace
        cwd = Path.cwd()
        if (cwd / project_path).exists():
            project_path = cwd / project_path
        elif (cwd / "04_IN_PRODUCTION" / project_path.name).exists():
            project_path = cwd / "04_IN_PRODUCTION" / project_path.name
        else:
            # Search in subfolders of cwd, engine_root, or parent (avatares)
            found = []
            for root in (cwd, engine_root, engine_root.parent):
                found = list(root.glob(f"**/04_IN_PRODUCTION/{project_path.name}"))
                if found:
                    break
            if found:
                project_path = found[0]
            else:
                raise FileNotFoundError(f"Project folder not found: {project_path_str}")

    brand_dir = Path(brand_dir_str) if brand_dir_str else project_path.parent.parent
    prod_name = project_path.name
    name_parts = prod_name.split("_")
    if len(name_parts) < 2 or not name_parts[1]:
        raise ValueError(f"Nombre de proyecto inválido '{prod_name}': se espera PROD_[XXX]_[referencia]")
    deliv_id = resolve_deliverable_id(brand_dir, name_parts[1])

    raw_clips_dir = project_path / "03_Raw_Clips"
    montage_dir = project_path / "05_Montage"
    first_frames_dir = project_path / "02_First_Frames"
    
    montage_dir.mkdir(parents=True, exist_ok=True)
    
    job_dir = engine_root / "scratch" / f"{prod_name}_assembly"
    job_dir.mkdir(parents=True, exist_ok=True)

    deliv_dir = brand_dir / "05_PROCESSED_DELIVERABLES" / deliv_id
    deliv_dir.mkdir(parents=True, exist_ok=True)

    # 1. Detect Raw Clips (robust numeric sorting: supports 1.mp4, 01.mp4, clip_1.mp4, etc.)
    def _clip_sort_key(p: Path):
        m = re.search(r'\d+', p.stem)
        return (int(m.group(0)) if m else 999, p.stem)

    raw_clips = sorted(list(raw_clips_dir.glob("*.mp4")), key=_clip_sort_key)
    if not raw_clips:
        raise FileNotFoundError(f"No raw clips found in {raw_clips_dir}")

    print(f"=== Assembling {prod_name} ({len(raw_clips)} clips detected) ===")

    # 2. Smart Silence Trimming using Faster-Whisper
    print("Stage 1: Performing Smart Silence Trimming on individual clips...")
    whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
    cuts = []

    for idx, clip in enumerate(raw_clips, 1):
        cmd_dur = [ffprobe_bin, "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(clip)]
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

        cuts.append((clip, start_trim, end_trim))
        print(f"  [Trim] {clip.name}: {start_trim:.2f}s -> {end_trim:.2f}s (Dur: {end_trim - start_trim:.2f}s, Cut: {dur - (end_trim - start_trim):.2f}s dead silence)")

    # 3. Single-pass trim + concatenation (one encode)
    print("\nStage 2: Trimming and concatenating in a single pass...")
    concat_video_path = job_dir / "concatenated_tight.mp4"
    cmd_concat = build_trim_concat_cmd(ffmpeg_bin, cuts, concat_video_path, fps=probe_fps(ffprobe_bin, raw_clips[0]))
    subprocess.run(cmd_concat, check=True)
    print(f"Seamless video created: {concat_video_path}")

    # 4. Auto-Captions Pipeline (dynamic highlight)
    print(f"\nStage 3: Burning synchronized dynamic viral captions (template: {template})...")
    pipeline = CaptionPipeline(job_dir=job_dir)
    asr_data = pipeline.process_stage_asr(input_video_path=concat_video_path, language=language)
    words = asr_data.get("words", [])

    render_result = pipeline.process_stage_render(
        input_video_path=concat_video_path,
        words=words,
        template_name=template,
        auto_emoji=True,
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
    headline_overlay_path = job_dir / "headline_overlay.png"
    generate_cover_advanced(
        input_image_path=raw_frame_path,
        headline=cover_headline,
        output_image_path=cover_badge_path,
        output_overlay_path=headline_overlay_path
    )

    # 5.5 Overlay hook headline sticker badge during first 3 seconds (0.0s - 3.0s)
    if not no_video_headline and headline_overlay_path.exists() and cover_headline.strip():
        print(f"\nStage 4.5: Overlaying hook headline badge ('{cover_headline}') for first 3 seconds...")
        video_with_hook = job_dir / "output_captioned_with_hook.mp4"
        cmd_hook = [
            ffmpeg_bin, "-y",
            "-i", str(output_burned_video),
            "-i", str(headline_overlay_path),
            "-filter_complex", "[0:v][1:v]overlay=0:0:enable='between(t,0,3)'[v]",
            "-map", "[v]",
            "-map", "0:a?",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "18",
            "-pix_fmt", "yuv420p",
            "-c:a", "copy",
            str(video_with_hook)
        ]
        subprocess.run(cmd_hook, check=True)
        output_burned_video = video_with_hook
    else:
        print("\nStage 4.5: Skipping video hook headline overlay (clean video requested).")

    # 6. Deliverables Export
    print("\nStage 5: Exporting canonical deliverable packages...")
    # 05_Montage
    shutil.copy(output_burned_video, montage_dir / f"{prod_name.split('_')[0]}_{deliv_id}_Final_Master.mp4")
    if output_srt and output_srt.exists():
        shutil.copy(output_srt, montage_dir / f"{prod_name.split('_')[0]}_{deliv_id}_Subtitles.srt")
    shutil.copy(cover_badge_path, montage_dir / "Cover.jpg")

    # Canonical deliverables
    shutil.copy(output_burned_video, deliv_dir / f"{deliv_id}_Final_1080x1920.mp4")
    if output_srt and output_srt.exists():
        shutil.copy(output_srt, deliv_dir / f"{deliv_id}_Subtitles.srt")
    shutil.copy(cover_badge_path, deliv_dir / f"{deliv_id}_Cover.jpg")
    shutil.copy(cover_badge_path, deliv_dir / f"{deliv_id}_Cover_Headline.jpg")
    if raw_frame_path.exists():
        shutil.copy(raw_frame_path, deliv_dir / f"{deliv_id}_Cover_Clean.jpg")
        shutil.copy(raw_frame_path, montage_dir / "Cover_Clean.jpg")
    with open(deliv_dir / "post_copy_title_and_caption.txt", "w", encoding="utf-8") as f:
        f.write(copy_content)

    print(f"\n[SUCCESS] Project {prod_name} assembled with Smart Silence Trimming!")

    if archive:
        archive_dir = brand_dir / "06_ARCHIVE"
        archive_dir.mkdir(parents=True, exist_ok=True)
        dest_archive = archive_dir / prod_name
        if dest_archive.exists():
            shutil.rmtree(dest_archive, ignore_errors=True)
        try:
            shutil.move(str(project_path), str(dest_archive))
            print(f"  [ARCHIVADO] Carpeta de producción movida a: 06_ARCHIVE/{prod_name}")
        except Exception:
            try:
                shutil.copytree(str(project_path), str(dest_archive), dirs_exist_ok=True)
                shutil.rmtree(str(project_path), ignore_errors=True)
                print(f"  [ARCHIVADO] Carpeta de producción movida a: 06_ARCHIVE/{prod_name}")
            except Exception as e2:
                print(f"  [WARN] No se pudo archivar automáticamente ({e2}). Usa 'ugc archive'.")

    return {
        "burned_video": str(output_burned_video),
        "srt": str(output_srt),
        "cover": str(cover_badge_path),
        "deliverables_dir": str(deliv_dir)
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Assemble raw clips with Smart Silence Trimming into canonical deliverable.")
    parser.add_argument("--project", required=True, help="Project directory name or path (e.g., PROD_001_cuenta_1)")
    parser.add_argument("--language", default="auto", help="Caption language code (es, en, ...) or 'auto' to detect")
    parser.add_argument("--start-pad", type=float, default=0.12, help="Silence padding start (seconds)")
    parser.add_argument("--end-pad", type=float, default=0.22, help="Silence padding end (seconds)")
    parser.add_argument("--archive", action="store_true", help="Mover automáticamente a 06_ARCHIVE tras el ensamblado exitoso")
    parser.add_argument("--no-video-headline", action="store_true", help="Omitir el sticker del headline en el video")
    parser.add_argument("--template", default="poppins_yellow", help="Subtitle template name (e.g. poppins_yellow, viral_yellow_highlight)")
    args = parser.parse_args()
    assemble_project(
        args.project,
        silence_padding_start=args.start_pad,
        silence_padding_end=args.end_pad,
        language=args.language,
        archive=args.archive,
        no_video_headline=args.no_video_headline,
        template=args.template
    )
