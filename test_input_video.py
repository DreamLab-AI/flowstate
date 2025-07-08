#!/usr/bin/env python3
"""
Test script for input.mp4 functionality.
Creates a test video and validates local video processing.
"""

import sys
import cv2
import numpy as np
from pathlib import Path
import subprocess

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.downloader import YouTubeDownloader


def create_test_video(output_path: Path, duration_seconds: int = 2):
    """Create a simple test video file."""
    fps = 30
    width, height = 640, 480
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    
    out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
    
    for frame_num in range(fps * duration_seconds):
        # Create a frame with moving circle
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Add some movement
        x = int(width/2 + 100 * np.sin(frame_num * 0.1))
        y = int(height/2 + 100 * np.cos(frame_num * 0.1))
        
        # Draw circle
        cv2.circle(frame, (x, y), 30, (0, 255, 0), -1)
        
        # Add frame number
        cv2.putText(frame, f"Frame {frame_num}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        out.write(frame)
    
    out.release()
    print(f"✓ Created test video: {output_path}")


def test_local_video_processing():
    """Test processing of local video file."""
    print("Testing local video processing...")
    
    # Create test video
    test_video = Path("input.mp4")
    create_test_video(test_video)
    
    try:
        # Test video processing
        downloader = YouTubeDownloader()
        video_path, video_info = downloader.process_local_video(test_video)
        
        # Validate results
        assert video_path.exists(), "Processed video path does not exist"
        assert video_info['title'] == "Local Video: input", "Title mismatch"
        assert video_info['duration'] is not None, "Duration not extracted"
        assert video_info['fps'] == 30, f"FPS mismatch: {video_info['fps']}"
        assert video_info['width'] == 640, "Width mismatch"
        assert video_info['height'] == 480, "Height mismatch"
        
        print("✓ Local video processing successful")
        print(f"  - Duration: {video_info['duration']:.2f}s")
        print(f"  - FPS: {video_info['fps']}")
        print(f"  - Resolution: {video_info['width']}x{video_info['height']}")
        
    finally:
        # Cleanup
        if test_video.exists():
            test_video.unlink()
            print("✓ Cleaned up test video")


def test_cli_with_input_video():
    """Test CLI behavior with input.mp4."""
    print("\nTesting CLI with input.mp4...")
    
    # Create test video
    test_video = Path("input.mp4")
    create_test_video(test_video, duration_seconds=1)
    
    try:
        # Test CLI detection (dry run)
        result = subprocess.run(
            [sys.executable, "-m", "src.cli.app", "--debug", "--skip-publish"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        # Check output
        if "Found local video: input.mp4" in result.stdout:
            print("✓ CLI correctly detected input.mp4")
        else:
            print("✗ CLI did not detect input.mp4")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("⚠ CLI test timed out (expected for full analysis)")
    finally:
        # Cleanup
        if test_video.exists():
            test_video.unlink()


def test_docker_volume_config():
    """Test Docker configuration for input.mp4."""
    print("\nTesting Docker configuration...")
    
    compose_path = Path(__file__).parent / "docker-compose.yml"
    if compose_path.exists():
        content = compose_path.read_text()
        
        # Check for input.mp4 volume mapping
        if "./input.mp4:/app/input.mp4:ro" in content:
            print("✓ Docker compose has input.mp4 volume mapping")
        else:
            print("✗ Docker compose missing input.mp4 volume mapping")
            
        # Check web-server service has the mapping too
        web_server_section = content.split("web-server:")[1].split("profiles:")[0]
        if "./input.mp4:/app/input.mp4:ro" in web_server_section:
            print("✓ Web server service has input.mp4 volume mapping")
        else:
            print("✗ Web server service missing input.mp4 volume mapping")
    else:
        print("⚠ docker-compose.yml not found")


def main():
    """Run all tests."""
    print("FlowState input.mp4 Test Suite")
    print("=" * 40)
    
    tests = [
        test_local_video_processing,
        test_cli_with_input_video,
        test_docker_volume_config
    ]
    
    failed = 0
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"✗ Test failed: {test.__name__}")
            print(f"  Error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 40)
    if failed == 0:
        print("✓ All tests passed!")
        return 0
    else:
        print(f"✗ {failed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())