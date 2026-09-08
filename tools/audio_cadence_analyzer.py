import sys
from pathlib import Path
from typing import List, Dict, Any

class AudioCadenceAnalyzer:
    """
    Analiza la velocidad, cadencia, ritmo de pausas y perfil tonal de una locución
    a partir de marcas de tiempo de Whisper (faster-whisper) para generar configuraciones
    exactas de replicación en ElevenLabs y directivas de voz en prompts de video (Veo3/Kling/Grok).
    """

    @staticmethod
    def analyze_transcript(words_with_timestamps: List[Dict[str, Any]], total_audio_duration_s: float = None) -> Dict[str, Any]:
        if not words_with_timestamps:
            return {
                "total_words": 0,
                "speech_duration_s": 0.0,
                "wps": 2.4,
                "wpm": 144,
                "cadence_tier": "Dynamic UGC (2.4 - 2.9 WPS)",
                "average_pause_s": 0.25,
                "elevenlabs_settings": {
                    "speed": 1.0,
                    "stability": 0.45,
                    "similarity_boost": 0.80,
                    "style": 0.20
                },
                "voice_prompt_direction": "Natural conversational 47yo female voice at 145 WPM with authentic breathing pauses."
            }

        total_words = len(words_with_timestamps)
        first_word_start = words_with_timestamps[0].get("start", 0.0)
        last_word_end = words_with_timestamps[-1].get("end", total_audio_duration_s or 0.0)
        speech_duration_s = max(last_word_end - first_word_start, 1.0)

        wps = round(total_words / speech_duration_s, 2)
        wpm = int(round(wps * 60))

        # Calculate average pause between consecutive words
        pauses = []
        for i in range(len(words_with_timestamps) - 1):
            gap = words_with_timestamps[i+1].get("start", 0.0) - words_with_timestamps[i].get("end", 0.0)
            if gap > 0.05: # ignore micro-syllabic transitions
                pauses.append(gap)

        avg_pause_s = round(sum(pauses) / len(pauses), 2) if pauses else 0.15

        # Cadence classification
        if wps >= 3.0:
            cadence_tier = "⚡ Hyper-Fast Hook (3.0+ WPS / 180+ WPM)"
            el_speed = round(min(wps / 2.5, 1.20), 2)
            el_stability = 0.35
            el_style = 0.30
            pacing_desc = f"Rapid-fire, high-urgency hook tempo at {wpm} WPM ({wps} words/sec) with minimal pauses"
        elif wps >= 2.4:
            cadence_tier = "🔥 Dynamic UGC (2.4 - 2.9 WPS / 145 - 175 WPM)"
            el_speed = round(wps / 2.4, 2)
            el_stability = 0.42
            el_style = 0.20
            pacing_desc = f"Engaging, dynamic UGC conversational pacing at {wpm} WPM ({wps} words/sec) with snappy sentence transitions"
        else:
            cadence_tier = "🌿 Relaxed Conversational (1.8 - 2.3 WPS / 110 - 140 WPM)"
            el_speed = round(max(wps / 2.3, 0.85), 2)
            el_stability = 0.60
            el_style = 0.10
            pacing_desc = f"Grounded, unhurried, reassuring cadence at {wpm} WPM ({wps} words/sec) with relaxed natural pauses"

        # Tone analysis based on lexical keywords
        all_text = " ".join([w.get("word", "") for w in words_with_timestamps]).lower()
        
        has_urgency = any(k in all_text for k in ["never", "stop", "mistake", "warning", "ugly", "tired", "old", "fail"])
        has_conspiracy = any(k in all_text for k in ["secret", "nobody tells you", "they don't want", "truth", "20 years younger", "actually"])
        has_empathy = any(k in all_text for k in ["not your fault", "i used to", "we all", "wonder why", "receptive", "comfort"])
        
        tone_profile = []
        if has_urgency:
            tone_profile.append("High-Alert Urgency & Direct Warning")
        if has_conspiracy:
            tone_profile.append("Confidential Discovery / Insider Secret")
        if has_empathy:
            tone_profile.append("Empathetic & Relatable Mirror")
        if not tone_profile:
            tone_profile.append("Authentic Everyday UGC Confidence")

        tone_str = " + ".join(tone_profile)

        voice_prompt_direction = (
            f"[AUDIO & VOICE CADENCE]: Pacing calibrated at {wpm} WPM ({wps} WPS, avg pause: {avg_pause_s}s). "
            f"Vocal Tone: {tone_str}. "
            f"Inflection: Crisp American pronunciation with natural dynamic emphasis on operative solution words, "
            f"zero studio reverb, domestic ambient room acoustics, natural breathing sync."
        )

        return {
            "total_words": total_words,
            "speech_duration_s": round(speech_duration_s, 2),
            "wps": wps,
            "wpm": wpm,
            "cadence_tier": cadence_tier,
            "average_pause_s": avg_pause_s,
            "tone_profile": tone_str,
            "elevenlabs_settings": {
                "speed": el_speed,
                "stability": el_stability,
                "similarity_boost": 0.80,
                "style": el_style
            },
            "voice_prompt_direction": voice_prompt_direction
        }
