"""
3D Viewer generation module.
Builds the interactive 3D visualization from pose analysis data.
"""

from pathlib import Path
from typing import Optional, Dict, Any
import json
import shutil

from ..core.config import settings
from ..core.exceptions import ViewerBuildError


class ViewerBuilder:
    """
    Generates the 3D interactive viewer.
    """

    def __init__(self):
        self.viewer_template_path = Path(__file__).parent / "template"
        if not self.viewer_template_path.is_dir():
            # This path might be different in a packaged environment
            # For now, assume it's relative to the current file.
            # In a real scenario, this would be handled by package data.
            print(f"Warning: Viewer template not found at {self.viewer_template_path}. "
                  "Viewer generation might fail.")

    def generate_viewer(self, pose_data: Dict[str, Any], video_info: Dict[str, Any]) -> Path:
        """
        Generates the 3D viewer with the provided pose data and video info.

        Args:
            pose_data: Dictionary containing pose analysis results.
            video_info: Dictionary containing video metadata.

        Returns:
            Path to the generated viewer directory.

        Raises:
            ViewerBuildError: If viewer generation fails.
        """
        output_viewer_dir = settings.output_dir / "viewer"
        output_viewer_dir.mkdir(parents=True, exist_ok=True)

        try:
            # Copy template files
            if self.viewer_template_path.is_dir():
                shutil.copytree(self.viewer_template_path, output_viewer_dir, dirs_exist_ok=True)
            else:
                raise ViewerBuildError(f"Viewer template directory not found at {self.viewer_template_path}")

            # Prepare data for JavaScript
            viewer_data = {
                "poseData": pose_data,
                "videoInfo": {
                    "title": video_info.get("title", "Untitled Video"),
                    "uploader": video_info.get("uploader", "Unknown"),
                    "uploadDate": video_info.get("upload_date", ""),
                    "thumbnail": video_info.get("thumbnail", ""),
                    "webpageUrl": video_info.get("webpage_url", "")
                },
                "settings": {
                    "quality": settings.viewer_quality,
                    "theme": settings.viewer_theme,
                    "enableParticles": settings.viewer_enable_particles,
                    "enableShadows": settings.viewer_enable_shadows
                }
            }

            # Save data to a JSON file in the viewer directory
            data_file_path = output_viewer_dir / "data.js"
            # We'll wrap it in a JS variable declaration for easy loading
            with open(data_file_path, "w", encoding="utf-8") as f:
                f.write(f"const flowStateData = {json.dumps(viewer_data, indent=2)};")

            return output_viewer_dir

        except Exception as e:
            raise ViewerBuildError(f"Failed to generate 3D viewer: {e}") from e
