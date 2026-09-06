import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from app.config import settings
from app.schemas.template import TemplateConfig

logger = logging.getLogger(__name__)

class TemplateManager:
    """Manages subtitle style templates loaded from JSON."""

    _templates: Dict[str, TemplateConfig] = {}

    @classmethod
    def load_templates(cls, templates_path: Optional[Path] = None) -> Dict[str, TemplateConfig]:
        """Loads and parses templates from templates.json."""
        target_path = templates_path or settings.TEMPLATES_FILE
        if not target_path.exists():
            logger.warning(f"Templates file not found at {target_path}. Using fallback templates.")
            return cls._load_fallback_templates()

        try:
            with open(target_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            templates_list = data.get("templates", [])
            cls._templates = {}
            for item in templates_list:
                cfg = TemplateConfig(**item)
                cls._templates[cfg.name] = cfg

            logger.info(f"Loaded {len(cls._templates)} templates from {target_path}")
            return cls._templates
        except Exception as e:
            logger.error(f"Failed to load templates: {e}")
            return cls._load_fallback_templates()

    @classmethod
    def _load_fallback_templates(cls) -> Dict[str, TemplateConfig]:
        fallback = {
            "hype_yellow": TemplateConfig(
                name="hype_yellow",
                description="Default CapCut pop style",
                font_family="Montserrat Bold",
                font_size_pct_of_height=7.5,
                primary_color="#FFFFFF",
                highlight_color="#FFD400",
                secondary_color="#CCCCCC",
                outline_color="#000000",
                outline_width=4.5,
                animation="pop_scale",
                pop_scale_from=120.0,
                uppercase=True,
                max_words_per_cue=3
            ),
            "clean_white": TemplateConfig(
                name="clean_white",
                description="Minimalist pill style",
                font_family="Roboto",
                font_size_pct_of_height=6.0,
                primary_color="#FFFFFF",
                highlight_color="#00E5FF",
                box_color="#80000000",
                animation="fade",
                uppercase=False,
                max_words_per_cue=4
            ),
            "karaoke_highlight": TemplateConfig(
                name="karaoke_highlight",
                description="Karaoke fill style",
                font_family="Montserrat Bold",
                font_size_pct_of_height=7.0,
                primary_color="#FFFFFF",
                highlight_color="#00FF66",
                animation="karaoke",
                uppercase=True,
                max_words_per_cue=4
            )
        }
        cls._templates = fallback
        return cls._templates

    @classmethod
    def get_template(cls, name: str) -> TemplateConfig:
        """Retrieves template by name or returns default hype_yellow."""
        if not cls._templates:
            cls.load_templates()
        return cls._templates.get(name) or cls._templates.get("hype_yellow")

    @classmethod
    def list_templates(cls) -> List[TemplateConfig]:
        """Returns all registered templates."""
        if not cls._templates:
            cls.load_templates()
        return list(cls._templates.values())

    @classmethod
    def save_template(cls, template: TemplateConfig) -> None:
        """Adds or updates a template in memory and persists to templates.json."""
        if not cls._templates:
            cls.load_templates()
        cls._templates[template.name] = template

        # Persist
        target_path = settings.TEMPLATES_FILE
        target_path.parent.mkdir(parents=True, exist_ok=True)
        data = {"templates": [t.dict() for t in cls._templates.values()]}
        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
