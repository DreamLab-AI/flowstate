"""
Video downloading and frame extraction module.
Supports YouTube video downloads and frame extraction for pose analysis.
"""

import yt_dlp
import cv2
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
import shutil

from ..core.config import settings
from ..core.exceptions import VideoDownloadError, InvalidURLError


class YouTubeDownloader:
    """
    Handles downloading YouTube videos and extracting frames.
    """

    def __init__(self):
        self.temp_video_path: Optional[Path] = None

    def process_local_video(self, video_path: Path) -> Tuple[Path, Dict[str, Any]]:
        """
        Processes a local video file, returning its path and a metadata dictionary.

        Args:
            video_path: Path to the local video file.

        Returns:
            A tuple containing the path to the video and its info.

        Raises:
            VideoDownloadError: If the video file does not exist or is not a file.
        """
        if not video_path.is_file():
            raise VideoDownloadError(f"Local video file not found: {video_path}")

        # Extract video metadata using OpenCV
        cap = cv2.VideoCapture(str(video_path))
        try:
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps if fps > 0 else None
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        finally:
            cap.release()

        # Create a comprehensive video_info dictionary for local files
        video_info = {
            'id': video_path.stem,
            'title': f"Local Video: {video_path.stem}",
            'ext': video_path.suffix.lstrip('.'),
            'fulltitle': video_path.name,
            'webpage_url': f"file://{video_path.absolute()}",
            'duration': duration,
            'fps': fps,
            'width': width,
            'height': height,
            'uploader': 'Local File',
            'upload_date': 'N/A',
            'description': f'Local video file: {video_path.name}',
            'thumbnail': None,
        }
        
        # Copy to temp directory if needed (for Docker compatibility)
        temp_path = settings.temp_dir / video_path.name
        if not temp_path.exists():
            shutil.copy2(video_path, temp_path)
            self.temp_video_path = temp_path
        else:
            self.temp_video_path = video_path
            
        return self.temp_video_path, video_info

    def download_video(self, url: str) -> Tuple[Path, Dict[str, Any]]:
        """
        Downloads a YouTube video.

        Args:
            url: The YouTube URL of the video.

        Returns:
            A tuple containing the path to the downloaded video and its info.

        Raises:
            InvalidURLError: If the URL is not a valid YouTube URL.
            VideoDownloadError: If the video download fails.
        """
        if "youtube.com/watch?v=" not in url and "youtu.be/" not in url:
            raise InvalidURLError("Provided URL is not a valid YouTube video URL.")

        output_template = str(settings.temp_dir / "%(id)s.%(ext)s")
        ydl_opts = {
            'format': settings.video_download_quality,
            'outtmpl': output_template,
            'noplaylist': True,
            'retries': 3,
            'fragment_retries': 3,
            'quiet': not settings.debug,
            'no_warnings': not settings.debug,
            'cachedir': False,
            'extractor_args': {
                'youtube': {
                    'skip': ['dash_manifest', 'hls_playlist']
                }
            },
            'cookiefile': str(settings.yt_dlp_cookiefile) if settings.yt_dlp_cookiefile else None
        }

        video_info = None
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)
                video_info = ydl.sanitize_info(info_dict)

                # Find the actual downloaded file path
                downloaded_filepath = Path(ydl.prepare_filename(info_dict))

                # Ensure the file exists and is not a directory
                if not downloaded_filepath.is_file():
                    # This can happen if yt-dlp downloads multiple formats and then merges
                    # We need to find the merged file.
                    # A common pattern is that the merged file will have a common video extension
                    # and be in the same directory as the parts.
                    # For simplicity, we'll assume the main file is the one with the original ID
                    # and a common video extension (e.g., .mp4, .webm)

                    # Try to find a file matching the ID and a common video extension
                    video_id = video_info.get('id')
                    if video_id:
                        found_files = list(settings.temp_dir.glob(f"{video_id}.*"))
                        if found_files:
                            downloaded_filepath = found_files[0]
                            if not downloaded_filepath.is_file():
                                raise VideoDownloadError(f"Downloaded file not found at {downloaded_filepath}")
                        else:
                            raise VideoDownloadError(f"Could not find downloaded video file for ID {video_id}")
                    else:
                        raise VideoDownloadError("Could not determine video ID for downloaded file.")

                self.temp_video_path = downloaded_filepath
                return downloaded_filepath, video_info

        except yt_dlp.utils.DownloadError as e:
            if "Unsupported URL" in str(e):
                raise InvalidURLError(f"Unsupported YouTube URL: {url}") from e
            raise VideoDownloadError(f"Failed to download video: {e}") from e
        except Exception as e:
            raise VideoDownloadError(f"An unexpected error occurred during video download: {e}") from e

    def extract_frames(self, video_path: Path) -> Path:
        """
        Extracts frames from a video at a specified FPS and saves them to a temporary directory.

        Args:
            video_path: Path to the input video file.

        Returns:
            Path to the directory containing extracted frames.

        Raises:
            VideoDownloadError: If frame extraction fails.
        """
        frames_output_dir = settings.temp_dir / "frames"
        frames_output_dir.mkdir(parents=True, exist_ok=True)

        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise VideoDownloadError(f"Could not open video file: {video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps == 0:
            raise VideoDownloadError("Could not determine video FPS.")

        frame_interval = int(round(fps / settings.frame_extraction_fps))
        if frame_interval == 0:
            frame_interval = 1 # Ensure at least one frame is processed if FPS is very low

        frame_count = 0
        extracted_count = 0

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_count % frame_interval == 0:
                    frame_filename = frames_output_dir / f"frame_{extracted_count:05d}.jpg"
                    cv2.imwrite(str(frame_filename), frame)
                    extracted_count += 1
                frame_count += 1
        except Exception as e:
            raise VideoDownloadError(f"Error during frame extraction: {e}") from e
        finally:
            cap.release()

        if extracted_count == 0:
            raise VideoDownloadError("No frames were extracted. Video might be empty or corrupted.")

        return frames_output_dir

    def cleanup(self):
        """
        Cleans up temporary files and directories created during the process.
        """
        if self.temp_video_path and self.temp_video_path.exists():
            try:
                self.temp_video_path.unlink()  # Delete the video file
                if settings.debug:
                    print(f"Cleaned up video file: {self.temp_video_path}")
            except OSError as e:
                print(f"Warning: Could not delete temporary video file {self.temp_video_path}: {e}")

        frames_dir = settings.temp_dir / "frames"
        if frames_dir.exists() and frames_dir.is_dir():
            try:
                shutil.rmtree(frames_dir)
                if settings.debug:
                    print(f"Cleaned up frames directory: {frames_dir}")
            except OSError as e:
                print(f"Warning: Could not delete temporary frames directory {frames_dir}: {e}")

        # Optionally, clean the main temp_dir if it's empty or if we want to be aggressive
        if settings.temp_dir.exists() and settings.temp_dir.is_dir() and not list(settings.temp_dir.iterdir()):
            try:
                settings.temp_dir.rmdir()
                if settings.debug:
                    print(f"Cleaned up temporary directory: {settings.temp_dir}")
            except OSError as e:
                print(f"Warning: Could not delete temporary directory {settings.temp_dir}: {e}")