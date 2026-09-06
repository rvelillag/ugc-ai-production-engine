import re
from typing import List, Dict, Any, Optional

class CueSegmenter:
    """Segments raw word timings into visual caption cues for TikTok/CapCut format."""

    @staticmethod
    def segment_words_into_cues(
        words: List[Dict[str, Any]],
        max_words_per_cue: int = 3,
        pause_threshold_s: float = 0.45,
        uppercase: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Groups words into compact cues respecting pause thresholds and punctuation.
        Returns:
            [
                {
                    "words": [{"word": "HOLA", "start": 0.1, "end": 0.35, "score": 1.0}, ...],
                    "start": 0.1,
                    "end": 0.95,
                    "text": "HOLA A TODOS"
                },
                ...
            ]
        """
        if not words:
            return []

        cues: List[Dict[str, Any]] = []
        current_cue_words: List[Dict[str, Any]] = []

        for i, w in enumerate(words):
            word_str = w["word"].strip()
            if not word_str:
                continue

            word_entry = {
                "word": word_str.upper() if uppercase else word_str,
                "start": w["start"],
                "end": w["end"],
                "score": w.get("score", 1.0)
            }

            if not current_cue_words:
                current_cue_words.append(word_entry)
                continue

            prev_word = current_cue_words[-1]
            gap = word_entry["start"] - prev_word["end"]

            # Conditions to flush current cue and start a new one:
            # 1. Exceeded max words
            is_full = len(current_cue_words) >= max_words_per_cue
            # 2. Significant pause between words (>0.55s)
            is_pause = gap >= max(pause_threshold_s, 0.55)
            # 3. Punctuation ending strong sentence boundary (., !, ?) only if at least 2 words
            prev_raw_word = words[i - 1]["word"].strip()
            is_sentence_end = bool(re.search(r"[.!?]$", prev_raw_word)) and len(current_cue_words) >= 2

            if is_full or is_pause or is_sentence_end:
                # Flush cue
                cue_start = current_cue_words[0]["start"]
                cue_end = max(current_cue_words[-1]["end"], cue_start + 0.25)
                cue_text = " ".join([cw["word"] for cw in current_cue_words])
                cues.append({
                    "words": current_cue_words,
                    "start": round(cue_start, 3),
                    "end": round(cue_end, 3),
                    "text": cue_text
                })
                current_cue_words = [word_entry]
            else:
                current_cue_words.append(word_entry)

        # Flush any remaining words in buffer
        if current_cue_words:
            cue_start = current_cue_words[0]["start"]
            cue_end = max(current_cue_words[-1]["end"], cue_start + 0.25)
            cue_text = " ".join([cw["word"] for cw in current_cue_words])
            cues.append({
                "words": current_cue_words,
                "start": round(cue_start, 3),
                "end": round(cue_end, 3),
                "text": cue_text
            })

        return cues
