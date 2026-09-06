import unittest
from pathlib import Path
from app.schemas.template import TemplateConfig
from app.core.ass_generator import ASSGenerator
from app.core.cue_segmenter import CueSegmenter
from app.core.emoji_tagger import EmojiTagger
from app.core.srt_generator import SRTGenerator

class TestASSGenerator(unittest.TestCase):

    def setUp(self):
        self.words = [
            {"word": "Gana", "start": 0.10, "end": 0.40, "score": 0.99},
            {"word": "mucho", "start": 0.45, "end": 0.70, "score": 0.98},
            {"word": "dinero", "start": 0.75, "end": 1.20, "score": 0.99},
            {"word": "con", "start": 1.40, "end": 1.60, "score": 0.95},
            {"word": "este", "start": 1.65, "end": 1.85, "score": 0.97},
            {"word": "truco", "start": 1.90, "end": 2.40, "score": 0.99}
        ]

    def test_cue_segmentation_and_emojis(self):
        tagger = EmojiTagger()
        cues = CueSegmenter.segment_words_into_cues(self.words, max_words_per_cue=3, uppercase=True)
        self.assertEqual(len(cues), 2)
        self.assertEqual(cues[0]["words"][0]["word"], "GANA")
        
        # Tag emojis
        cues = tagger.tag_cues(cues)
        self.assertTrue(any("💰" in w["word"] for w in cues[0]["words"]))

    def test_hype_yellow_template_generation(self):
        template = TemplateConfig(
            name="hype_yellow",
            font_family="Montserrat Bold",
            font_size_pct_of_height=7.5,
            primary_color="#FFFFFF",
            highlight_color="#FFD400",
            outline_color="#000000",
            outline_width=4.0,
            animation="pop_scale",
            pop_scale_from=120.0,
            uppercase=True,
            max_words_per_cue=3
        )
        cues = CueSegmenter.segment_words_into_cues(self.words, max_words_per_cue=3)
        ass_content = ASSGenerator.generate_ass(cues, template, video_width=1080, video_height=1920)
        
        self.assertIn("[Script Info]", ass_content)
        self.assertIn("PlayResX: 1080", ass_content)
        self.assertIn("PlayResY: 1920", ass_content)
        self.assertIn("\\fscx120\\fscy120", ass_content)  # Pop-scale tag
        self.assertIn("Dialogue: 0,", ass_content)

    def test_clean_white_template_generation(self):
        template = TemplateConfig(
            name="clean_white",
            font_family="Roboto",
            font_size_pct_of_height=6.0,
            primary_color="#FFFFFF",
            highlight_color="#00E5FF",
            box_color="#80000000",
            animation="fade",
            uppercase=False,
            max_words_per_cue=4
        )
        cues = CueSegmenter.segment_words_into_cues(self.words, max_words_per_cue=4, uppercase=False)
        ass_content = ASSGenerator.generate_ass(cues, template, video_width=1080, video_height=1920)
        self.assertIn("Style: Default,Roboto", ass_content)
        self.assertIn("\\fad(", ass_content)

    def test_karaoke_template_generation(self):
        template = TemplateConfig(
            name="karaoke_highlight",
            font_family="Montserrat Bold",
            font_size_pct_of_height=7.0,
            primary_color="#FFFFFF",
            highlight_color="#00FF66",
            animation="karaoke",
            uppercase=True,
            max_words_per_cue=4
        )
        cues = CueSegmenter.segment_words_into_cues(self.words, max_words_per_cue=4)
        ass_content = ASSGenerator.generate_ass(cues, template, video_width=1080, video_height=1920)
        self.assertIn("{\\k", ass_content)

    def test_srt_generation(self):
        cues = CueSegmenter.segment_words_into_cues(self.words, max_words_per_cue=3)
        srt_content = SRTGenerator.generate_srt(cues)
        self.assertIn("1\n00:00:00,100 -->", srt_content)
        self.assertIn("GANA MUCHO DINERO", srt_content)

if __name__ == "__main__":
    unittest.main()
