import math
from pathlib import Path
from typing import List, Dict, Any, Optional
from app.schemas.template import TemplateConfig

class ASSGenerator:
    """Generates Advanced SubStation Alpha (.ass) subtitle files with rich CapCut style animations."""

    @staticmethod
    def hex_to_ass_color(hex_str: str, default_alpha: str = "00") -> str:
        """
        Converts hex color (#RRGGBB or #AARRGGBB) to ASS color format (&HAABBGGRR&).
        Note: ASS uses BGR ordering.
        """
        if not hex_str:
            return f"&H{default_alpha}FFFFFF&"
        clean_hex = hex_str.lstrip("#")
        if len(clean_hex) == 6:
            r = clean_hex[0:2]
            g = clean_hex[2:4]
            b = clean_hex[4:6]
            return f"&H{default_alpha}{b}{g}{r}&"
        elif len(clean_hex) == 8:
            a = clean_hex[0:2]
            r = clean_hex[2:4]
            g = clean_hex[4:6]
            b = clean_hex[6:8]
            return f"&H{a}{b}{g}{r}&"
        return f"&H{default_alpha}FFFFFF&"

    @staticmethod
    def format_timestamp(seconds: float) -> str:
        """Converts float seconds to ASS timestamp format: H:MM:SS.cc"""
        if seconds < 0:
            seconds = 0.0
        hrs = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        secs = seconds % 60
        centis = int(round((secs - int(secs)) * 100))
        if centis >= 100:
            centis = 99
        return f"{hrs}:{mins:02d}:{int(secs):02d}.{centis:02d}"

    @classmethod
    def generate_ass(
        cls,
        cues: List[Dict[str, Any]],
        template: TemplateConfig,
        video_width: int = 1080,
        video_height: int = 1920,
        output_file: Optional[Path] = None
    ) -> str:
        """
        Builds ASS script content with rich animation presets and styles.
        """
        font_size = int(video_height * (template.font_size_pct_of_height / 100.0))
        margin_v = int(video_height * (template.vertical_margin_pct / 100.0))
        margin_h = int(video_width * 0.10)  # 10% safe horizontal margin

        pri_color = cls.hex_to_ass_color(template.primary_color)
        sec_color = cls.hex_to_ass_color(template.secondary_color or "#E0E0E0")
        hl_color = cls.hex_to_ass_color(template.highlight_color)
        out_color = cls.hex_to_ass_color(template.outline_color)
        shd_color = cls.hex_to_ass_color(template.shadow_color or "#000000", "80")

        # Alignment: 2 = Bottom-Center, 5 = Middle-Center, 8 = Top-Center
        alignment = 2
        if template.position == "center":
            alignment = 5
        elif template.position == "top_center":
            alignment = 8

        # Border style: 1 = Outline + drop shadow, 3 = Opaque box
        border_style = 3 if template.box_color else 1
        back_color = cls.hex_to_ass_color(template.box_color) if template.box_color else shd_color
        is_italic = -1 if getattr(template, "italic", False) else 0

        lines = [
            "[Script Info]",
            "Title: Auto-Captions CapCut Style",
            "ScriptType: v4.00+",
            f"PlayResX: {video_width}",
            f"PlayResY: {video_height}",
            "WrapStyle: 0",
            "ScaledBorderAndShadow: yes",
            "",
            "[V4+ Styles]",
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
            f"Style: Default,{template.font_family},{font_size},{pri_color},{sec_color},{out_color},{back_color},-1,{is_italic},0,0,100,100,0,0,{border_style},{template.outline_width},{template.shadow_depth or 0},{alignment},{margin_h},{margin_h},{margin_v},1",
            "",
            "[Events]",
            "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"
        ]

        fade_ms = template.fade_duration_ms or 80
        pop_scale = template.pop_scale_from or 125.0
        pop_dur = template.pop_scale_duration_ms or 120
        anim_type = (template.animation or "pop_scale").lower()

        for cue in cues:
            words = cue.get("words", [])
            if not words:
                continue

            cue_start = cue["start"]
            cue_end = cue["end"]

            # Animation: Karaoke Progressive Sweep (\k)
            if anim_type == "karaoke":
                k_text_parts = []
                for w in words:
                    dur_cs = max(1, int(round((w["end"] - w["start"]) * 100)))
                    w_text = w["word"].upper() if template.uppercase else w["word"]
                    k_text_parts.append(f"{{\\k{dur_cs}}}{w_text}")
                
                dialogue_text = f"{{\\c{hl_color}\\2c{pri_color}\\fad({fade_ms},{fade_ms})}}{' '.join(k_text_parts)}"
                start_str = cls.format_timestamp(cue_start)
                end_str = cls.format_timestamp(cue_end)
                lines.append(f"Dialogue: 0,{start_str},{end_str},Default,,0,0,0,,{dialogue_text}")

            # Word-level highlight & active animation modes
            else:
                for idx, active_w in enumerate(words):
                    w_start = active_w["start"]
                    # Calculate end timing
                    if idx < len(words) - 1:
                        w_end = words[idx + 1]["start"]
                    else:
                        w_end = cue_end

                    if w_end <= w_start:
                        w_end = w_start + 0.2

                    word_tokens = []
                    for j, other_w in enumerate(words):
                        raw_w_text = other_w["word"].upper() if template.uppercase else other_w["word"]
                        
                        if j == idx:
                            # Active Word Animation Tags
                            if anim_type == "pop_scale":
                                # CapCut Pop: 125% -> 100%
                                anim_tag = f"\\fscx{int(pop_scale)}\\fscy{int(pop_scale)}\\t(0,{pop_dur},\\fscx100\\fscy100)"
                            elif anim_type == "elastic_bounce":
                                # Elastic bounce: 130% -> 95% -> 100%
                                anim_tag = f"\\fscx130\\fscy130\\t(0,70,\\fscx95\\fscy95)\\t(70,140,\\fscx100\\fscy100)"
                            elif anim_type == "glow_flash":
                                # Glow flash from pure white/cyan to highlight color
                                flash_col = "&H00FFFFFF&"
                                anim_tag = f"\\c{flash_col}\\t(0,90,\\c{hl_color})"
                            elif anim_type == "fade_in":
                                # Smooth appearance
                                anim_tag = f"\\alpha&HFF&\\t(0,{pop_dur},\\alpha&H00&)"
                            else:
                                anim_tag = ""

                            word_tokens.append(
                                f"{{\\c{hl_color}{anim_tag}}}{raw_w_text}{{\\c{pri_color}\\fscx100\\fscy100\\alpha&H00&}}"
                            )
                        else:
                            # Inactive words in current cue
                            word_tokens.append(f"{{\\c{sec_color}}}{raw_w_text}{{\\c{pri_color}}}")

                    fade_tag = f"\\fad({fade_ms if idx == 0 else 0},{fade_ms if idx == len(words)-1 else 0})"
                    rendered_text = f"{{{fade_tag}}}{' '.join(word_tokens)}"
                    start_str = cls.format_timestamp(w_start)
                    end_str = cls.format_timestamp(w_end)
                    lines.append(f"Dialogue: 0,{start_str},{end_str},Default,,0,0,0,,{rendered_text}")

        ass_content = "\n".join(lines) + "\n"

        if output_file:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(ass_content, encoding="utf-8")

        return ass_content
