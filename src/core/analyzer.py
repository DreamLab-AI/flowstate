"""
Pose analysis module using MediaPipe.
Processes video frames to detect human poses and extract keypoint data.
"""

from pathlib import Path
from typing import Optional, Dict, Any, List
import cv2
import mediapipe as mp
import numpy as np
import json

from ..core.config import settings
from ..core.exceptions import PoseDetectionError


class PoseAnalyzer:
    """
    Analyzes video frames to detect human poses and calculate flow metrics.
    """

    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose_detector = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=settings.pose_model_complexity,
            min_detection_confidence=settings.pose_confidence_threshold,
            min_tracking_confidence=settings.pose_confidence_threshold
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

    def analyze_video(self, frames_dir: Path) -> Dict[str, Any]:
        """
        Analyzes a directory of video frames to detect poses and calculate metrics.

        Args:
            frames_dir: Path to the directory containing extracted video frames.

        Returns:
            A dictionary containing pose data, scores, and other analysis results.

        Raises:
            PoseDetectionError: If pose detection fails or no poses are detected.
        """
        if not frames_dir.is_dir():
            raise PoseDetectionError(f"Frames directory not found: {frames_dir}")

        image_files = sorted(list(frames_dir.glob("*.jpg")) + list(frames_dir.glob("*.png")))
        if not image_files:
            raise PoseDetectionError(f"No image files found in frames directory: {frames_dir}")

        all_pose_landmarks: List[List[Dict[str, float]]] = []
        detected_frames_count = 0

        for img_file in image_files:
            image = cv2.imread(str(img_file))
            if image is None:
                print(f"Warning: Could not read image {img_file}. Skipping.")
                continue

            # Convert the BGR image to RGB.
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # Process the image and find poses.
            results = self.pose_detector.process(image_rgb)

            frame_landmarks: List[Dict[str, float]] = []
            if results.pose_landmarks:
                detected_frames_count += 1
                for landmark in results.pose_landmarks.landmark:
                    frame_landmarks.append({
                        "x": landmark.x,
                        "y": landmark.y,
                        "z": landmark.z,
                        "visibility": landmark.visibility
                    })
            all_pose_landmarks.append(frame_landmarks)

        if detected_frames_count < settings.analysis_min_frames:
            raise PoseDetectionError(
                f"Too few frames with detected poses ({detected_frames_count}/{len(image_files)}). "
                f"Minimum required: {settings.analysis_min_frames}. "
                "Ensure the video clearly shows a person and try adjusting confidence threshold."
            )

        # Calculate metrics (simplified for example)
        overall_scores = self._calculate_overall_scores(all_pose_landmarks)
        detection_rate = detected_frames_count / len(image_files)

        return {
            "pose_landmarks": all_pose_landmarks,
            "overall_scores": overall_scores,
            "detection_rate": detection_rate,
            "frame_count": len(image_files),
            "detected_frames_count": detected_frames_count
        }

    def _calculate_overall_scores(self, all_pose_landmarks: List[List[Dict[str, float]]]) -> Dict[str, float]:
        """
        Calculates overall flow, balance, smoothness, and energy scores.
        This is a placeholder for actual sophisticated metric calculation.
        """
        # In a real application, this would involve complex algorithms
        # analyzing movement patterns, stability, velocity, etc.
        # For now, we'll return dummy values or simple averages.

        # Example: Simple "flow" score based on number of detected frames
        total_frames = len(all_pose_landmarks)
        if total_frames == 0:
            return {"flow": 0.0, "balance": 0.0, "smoothness": 0.0, "energy": 0.0}

        detected_frames = sum(1 for frame in all_pose_landmarks if frame)

        # Dummy scores for demonstration
        flow_score = (detected_frames / total_frames) * 100 * settings.analysis_flow_weight
        balance_score = np.random.uniform(70, 95) * settings.analysis_balance_weight
        smoothness_score = np.random.uniform(60, 90) * settings.analysis_smoothness_weight
        energy_score = np.random.uniform(50, 80) * (1 - settings.analysis_flow_weight - settings.analysis_balance_weight - settings.analysis_smoothness_weight)

        # Normalize to 100%
        total_weight = settings.analysis_flow_weight + settings.analysis_balance_weight + settings.analysis_smoothness_weight + (1 - settings.analysis_flow_weight - settings.analysis_balance_weight - settings.analysis_smoothness_weight)

        overall_flow = (flow_score + balance_score + smoothness_score + energy_score) / total_weight

        return {
            "flow": min(100.0, overall_flow),
            "balance": min(100.0, balance_score * (100/settings.analysis_balance_weight)), # Scale back for display
            "smoothness": min(100.0, smoothness_score * (100/settings.analysis_smoothness_weight)),
            "energy": min(100.0, energy_score * (100/(1 - settings.analysis_flow_weight - settings.analysis_balance_weight - settings.analysis_smoothness_weight)))
        }

    def __del__(self):
        """Release MediaPipe resources."""
        if hasattr(self, 'pose_detector'):
            self.pose_detector.close()
