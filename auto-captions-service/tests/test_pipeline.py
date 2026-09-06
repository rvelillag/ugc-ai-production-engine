import unittest
from app.services.template_manager import TemplateManager
from app.schemas.job import CaptionRequest, JobStatus
from app.services.job_queue import JobManager

class TestPipelineAndAPI(unittest.TestCase):

    def test_template_manager_load(self):
        templates = TemplateManager.list_templates()
        self.assertGreaterEqual(len(templates), 3)
        template_names = [t.name for t in templates]
        self.assertIn("hype_yellow", template_names)
        self.assertIn("clean_white", template_names)
        self.assertIn("karaoke_highlight", template_names)

    def test_caption_request_schema(self):
        req = CaptionRequest(
            video_url="https://example.com/test.mp4",
            template="hype_yellow",
            language="es",
            max_words_per_cue=3,
            auto_emoji=True
        )
        self.assertEqual(req.template, "hype_yellow")
        self.assertEqual(req.max_words_per_cue, 3)
        self.assertTrue(req.auto_emoji)

if __name__ == "__main__":
    unittest.main()
