"""
Configuration management for FlowState-CLI.
Uses pydantic for validation and environment variable support.
"""

from pathlib import Path
from typing import Optional, Literal
from pydantic import validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    FlowState configuration settings.
    All settings can be overridden via environment variables with FLOWSTATE_ prefix.
    """

    # Application settings
    app_name: str = "FlowState-CLI"
    version: str = "2.0.0"
    debug: bool = False

    # Video processing settings
    video_download_quality: str = "best"
    video_max_duration: int = 600  # 10 minutes
    frame_extraction_fps: int = 30
    yt_dlp_cookiefile: Optional[Path] = None

    # Pose detection settings
    pose_model: Literal["openpose", "yolov8"] = "openpose"
    pose_confidence_threshold: float = 0.7
    pose_model_complexity: int = 1  # 0, 1, or 2 for legacy compatibility

    # OpenPose specific settings
    openpose_hand_detection: bool = True
    openpose_face_detection: bool = True
    openpose_temporal_smoothing: bool = True
    openpose_interpolation_factor: int = 10  # 10x temporal granularity
    openpose_smoothing_window: int = 5

    # Analysis settings
    analysis_min_frames: int = 30
    analysis_flow_weight: float = 0.3
    analysis_balance_weight: float = 0.3
    analysis_smoothness_weight: float = 0.4

    # Viewer settings
    viewer_quality: Literal["low", "medium", "high"] = "high"
    viewer_theme: Literal["dark", "light"] = "dark"
    viewer_enable_particles: bool = True
    viewer_enable_shadows: bool = True

    # GitHub settings
    github_token: Optional[str] = None
    github_api_timeout: int = 30
    github_retry_attempts: int = 3
    github_retry_delay: float = 1.0

    # Storage settings
    temp_dir: Path = Path("/tmp/flowstate")
    output_dir: Path = Path("./output")
    cache_enabled: bool = True
    cache_ttl: int = 3600  # 1 hour

    # Performance settings
    use_gpu: bool = True
    num_workers: int = 4
    batch_size: int = 16

    @validator("temp_dir", "output_dir", pre=True)
    def ensure_path(cls, v):
        """Ensure paths are Path objects."""
        if isinstance(v, str):
            return Path(v)
        return v

    @validator("pose_confidence_threshold")
    def validate_confidence(cls, v):
        """Ensure confidence threshold is between 0 and 1."""
        if not 0 <= v <= 1:
            raise ValueError("Confidence threshold must be between 0 and 1")
        return v

    @validator("pose_model_complexity")
    def validate_complexity(cls, v):
        """Ensure model complexity is valid."""
        if v not in [0, 1, 2]:
            raise ValueError("Model complexity must be 0, 1, or 2")
        return v

    class Config:
        env_prefix = "FLOWSTATE_"
        env_file = ".env"
        env_file_encoding = "utf-8"

    def create_directories(self):
        """Create necessary directories."""
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()

# Create directories on import
settings.create_directories()