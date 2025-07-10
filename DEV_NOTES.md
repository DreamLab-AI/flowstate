# Developer Notes & Known Issues

This document outlines the current state of the implementation, including known stubs, inconsistencies, and areas for future improvement. It is intended to guide developers who are contributing to the project.

## 1. Core Analyzer Implementation (`src/core/analyzer.py`)

### "OpenPose" vs. YOLOv8-Pose

-   **Inconsistency**: The project is described as using an "OpenPose" implementation, and the output data is "OpenPose-compatible." However, the underlying model is `yolov8n-pose.pt` from the Ultralytics library.
-   **Reasoning**: This was a pragmatic choice. YOLOv8-Pose provides an excellent, pre-trained model that detects a rich set of keypoints (including hands and feet) with high performance. Building a full OpenPose implementation from source is significantly more complex. We use the term "OpenPose-compatible" to describe the *output format* and *feature set*, not the model architecture itself.
-   **Future Work**: We could explore fine-tuning the YOLO model or integrating a true OpenPose implementation if specific features (like the original OpenPose PAFs - Part Affinity Fields) are needed.

### Hand and Face Detection are Stubs

-   **Stub**: The `_detect_hands` and `_detect_face` methods in the `OpenPoseDetector` class are currently stubs.
    -   `_detect_face` simply reuses the head keypoints already detected by the main YOLO model.
    -   `_extract_hand_keypoints` does **not** run a separate hand detection model. Instead, it generates **synthetic/dummy keypoints** with random offsets around the detected wrist positions.
-   **Reasoning**: This was done to quickly build out the full data pipeline and viewer without getting blocked on training or integrating a specialized hand model. The current implementation provides the correct *data structure* for the viewer, even if the data itself is not yet real.
-   **Immediate Priority for Future Work**:
    1.  Integrate a dedicated hand-pose estimation model (e.g., the MediaPipe Hands model, or a fine-tuned YOLO model).
    2.  The hand model should be run on cropped image regions around the wrists detected by the main body-pose model for efficiency.
    3.  Replace the synthetic keypoint generation with the actual model output.

### Smoothing and Interpolation

-   **Simplification**: The `_gaussian_smooth_pose` method is currently a placeholder. It identifies the correct window of frames but simply returns the center frame without applying a weighted Gaussian average.
-   **Reasoning**: The primary smoothing effect currently comes from the `interpolate_poses` method, which already provides a significant improvement. A true Gaussian filter was deferred to a future optimization step.
-   **Future Work**: Implement a proper Gaussian or Savitzky-Golay filter over the temporal window of keypoints to further reduce high-frequency jitter. This should be applied to the `(x, y)` coordinates of each keypoint independently.

## 2. Docker and Dependencies

-   **CUDA Version**: The Dockerfile is pinned to `nvidia/cuda:11.8.0`. This is a stable, widely-supported version. If newer PyTorch or TensorFlow versions require a newer CUDA toolkit, this will need to be updated, and potential compatibility issues will need to be tested.
-   **Python Dependencies**: The `requirements.txt` file contains a mix of specific and broad version pins. For more reproducible builds, we should consider using a dependency management tool like Poetry or `pip-tools` to lock all transitive dependencies.

## 3. Viewer and Frontend

-   **Data Loading**: The viewer currently loads all pose data at once from `data.js`. For very long videos with high temporal granularity, this could lead to high memory usage in the browser.
-   **Future Work**: Implement a streaming data loader in the viewer. The frontend could fetch pose data frame-by-frame or in chunks from a local API endpoint (if served) or from a set of smaller JSON files, rather than one monolithic file.
-   **Stick Figure Rendering**: The `stick_figure_data` is generated in the Python backend. This is efficient but tightly couples the backend data format to the frontend rendering logic. A more flexible approach might be to send only the raw keypoints and have the frontend determine the connections based on a configuration.

## 4. Testing

-   **Current State**: The project has a few high-level tests but lacks comprehensive unit and integration tests for the new analysis pipeline.
-   **Future Work**:
    -   Add unit tests for the `PoseAnalyzer`, mocking the YOLO model to test the interpolation and smoothing logic.
    -   Add integration tests that run a small video through the entire pipeline and verify the output JSON structure.
    -   Create regression tests with known input videos and expected keypoint outputs to prevent future model changes from breaking results.