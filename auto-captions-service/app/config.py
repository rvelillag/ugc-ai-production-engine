import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    BASE_URL: str = "http://localhost:8000"

    # Base directories
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    STORAGE_DIR: Path = Path("./storage")
    WATCH_INPUT_DIR: Path = Path("./watch/input")
    WATCH_OUTPUT_DIR: Path = Path("./watch/output")
    TEMPLATES_FILE: Path = Path(__file__).resolve().parent / "templates" / "templates.json"

    # ASR Settings
    ASR_ENGINE: str = "faster-whisper"  # 'faster-whisper' or 'openai'
    WHISPER_MODEL_SIZE: str = "base"     # 'tiny', 'base', 'small', 'medium', 'large-v3'
    WHISPER_DEVICE: str = "auto"         # 'cuda', 'cpu', 'auto'
    WHISPER_COMPUTE_TYPE: str = "default" # 'float16', 'int8_float16', 'int8', 'default'
    OPENAI_API_KEY: str = ""

    # Defaults
    DEFAULT_LANGUAGE: str = "es"
    DEFAULT_TEMPLATE: str = "hype_yellow"
    DEFAULT_MAX_WORDS_PER_CUE: int = 3
    DEFAULT_AUTO_EMOJI: bool = True
    DEFAULT_PAUSE_THRESHOLD_MS: int = 450

    # Concurrency
    MAX_CONCURRENT_JOBS: int = 2
    ENABLE_WATCH_FOLDER: bool = True

    class Config:
        env_file = ".env"
        extra = "allow"

    def setup_directories(self):
        """Ensure all required directories exist."""
        self.STORAGE_DIR.mkdir(parents=True, exist_ok=True)
        self.WATCH_INPUT_DIR.mkdir(parents=True, exist_ok=True)
        self.WATCH_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        (self.STORAGE_DIR / "uploads").mkdir(parents=True, exist_ok=True)
        (self.STORAGE_DIR / "jobs").mkdir(parents=True, exist_ok=True)

settings = Settings()
settings.setup_directories()
