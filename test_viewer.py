#!/usr/bin/env python3
"""
Test script for FlowState viewer functionality.
Generates test data and validates the viewer setup.
"""

import json
import sys
from pathlib import Path
import subprocess
import time
import requests
import webbrowser
from typing import Dict, Any, List
import numpy as np


class ViewerTester:
    """Test the FlowState viewer functionality."""
    
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.viewer_dir = self.root_dir / "viewer"
        self.template_dir = self.viewer_dir / "template"
        self.test_output_dir = self.root_dir / "test_output" / "viewer"
        
    def generate_test_pose_data(self, num_frames: int = 120) -> Dict[str, Any]:
        """Generate realistic test pose data."""
        print("Generating test pose data...")
        
        # MediaPipe has 33 pose landmarks
        num_landmarks = 33
        pose_landmarks = []
        
        for frame in range(num_frames):
            frame_landmarks = []
            t = frame / num_frames * 2 * np.pi
            
            for landmark_id in range(num_landmarks):
                # Create smooth, realistic movement patterns
                base_x = 0.5 + 0.3 * np.sin(t + landmark_id * 0.1)
                base_y = 0.5 + 0.2 * np.cos(t * 0.5 + landmark_id * 0.1)
                base_z = 0.1 * np.sin(t * 2 + landmark_id * 0.05)
                
                # Add some noise for realism
                noise_scale = 0.02
                x = base_x + np.random.normal(0, noise_scale)
                y = base_y + np.random.normal(0, noise_scale)
                z = base_z + np.random.normal(0, noise_scale * 0.5)
                
                frame_landmarks.append({
                    "x": float(x),
                    "y": float(y),
                    "z": float(z),
                    "visibility": float(0.8 + 0.2 * np.random.random())
                })
            
            pose_landmarks.append(frame_landmarks)
        
        # Generate scores
        scores = {
            "flow": float(75 + 20 * np.random.random()),
            "balance": float(70 + 25 * np.random.random()),
            "smoothness": float(80 + 15 * np.random.random()),
            "energy": float(65 + 30 * np.random.random())
        }
        
        return {
            "poseData": {
                "pose_landmarks": pose_landmarks,
                "overall_scores": scores,
                "frame_scores": {
                    "flow": [float(scores["flow"] + np.random.normal(0, 5)) for _ in range(num_frames)],
                    "balance": [float(scores["balance"] + np.random.normal(0, 5)) for _ in range(num_frames)]
                }
            },
            "videoInfo": {
                "title": "Test Dance Performance",
                "uploader": "FlowState Tester",
                "uploadDate": time.strftime("%Y-%m-%d"),
                "thumbnail": "",
                "webpageUrl": "https://github.com/yourusername/flowstate-music"
            },
            "settings": {
                "quality": "high",
                "theme": "dark",
                "enableParticles": True,
                "enableShadows": True,
                "frameRate": 30
            }
        }
    
    def setup_test_viewer(self):
        """Set up a test viewer directory with generated data."""
        print(f"Setting up test viewer in {self.test_output_dir}")
        
        # Create output directory
        self.test_output_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy template files
        for template_file in self.template_dir.glob("*"):
            if template_file.is_file():
                dest_file = self.test_output_dir / template_file.name
                dest_file.write_bytes(template_file.read_bytes())
                print(f"  Copied {template_file.name}")
        
        # Generate test data
        test_data = self.generate_test_pose_data()
        data_js_path = self.test_output_dir / "data.js"
        
        with open(data_js_path, 'w', encoding='utf-8') as f:
            f.write(f"const flowStateData = {json.dumps(test_data, indent=2)};")
        
        print(f"  Generated test data: {data_js_path}")
        return self.test_output_dir
    
    def test_viewer_files(self) -> bool:
        """Test that all required viewer files exist."""
        print("\nTesting viewer file structure...")
        
        required_files = [
            self.viewer_dir / "builder.py",
            self.viewer_dir / "dev_server.py",
            self.template_dir / "index.html",
            self.template_dir / "enhanced_viewer.html",
            self.template_dir / "enhanced_viewer.js"
        ]
        
        all_exist = True
        for file_path in required_files:
            if file_path.exists():
                print(f"  ✓ {file_path.relative_to(self.root_dir)}")
            else:
                print(f"  ✗ {file_path.relative_to(self.root_dir)} - MISSING")
                all_exist = False
        
        return all_exist
    
    def test_dev_server(self, port: int = 8081) -> bool:
        """Test the development server."""
        print(f"\nTesting development server on port {port}...")
        
        # Start the server
        server_cmd = [
            sys.executable,
            str(self.viewer_dir / "dev_server.py"),
            "--port", str(port),
            "--directory", str(self.test_output_dir),
            "--no-browser"
        ]
        
        try:
            # Start server process
            process = subprocess.Popen(
                server_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Give server time to start
            time.sleep(2)
            
            # Test server is responding
            try:
                response = requests.get(f"http://localhost:{port}/", timeout=5)
                if response.status_code == 200:
                    print(f"  ✓ Server responding on http://localhost:{port}")
                    
                    # Test specific files
                    test_urls = [
                        "/index.html",
                        "/enhanced_viewer.html",
                        "/enhanced_viewer.js",
                        "/data.js"
                    ]
                    
                    for url in test_urls:
                        response = requests.get(f"http://localhost:{port}{url}", timeout=5)
                        if response.status_code == 200:
                            print(f"  ✓ {url} - OK")
                        else:
                            print(f"  ✗ {url} - Status {response.status_code}")
                    
                    return True
                else:
                    print(f"  ✗ Server returned status {response.status_code}")
                    return False
                    
            except requests.exceptions.RequestException as e:
                print(f"  ✗ Failed to connect to server: {e}")
                return False
                
        finally:
            # Clean up server process
            process.terminate()
            time.sleep(1)
            if process.poll() is None:
                process.kill()
    
    def test_docker_build(self) -> bool:
        """Test Docker build process."""
        print("\nTesting Docker build...")
        
        try:
            # Check if Docker is available
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print("  ✗ Docker not available")
                return False
            
            print(f"  ✓ Docker available: {result.stdout.strip()}")
            
            # Try building the image
            print("  Building Docker image (this may take a while)...")
            result = subprocess.run(
                ["docker", "build", "-t", "flowstate-test:latest", "."],
                cwd=self.root_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("  ✓ Docker image built successfully")
                return True
            else:
                print(f"  ✗ Docker build failed:")
                print(result.stderr)
                return False
                
        except FileNotFoundError:
            print("  ✗ Docker not installed")
            return False
    
    def run_all_tests(self):
        """Run all viewer tests."""
        print("FlowState Viewer Test Suite")
        print("=" * 50)
        
        results = {
            "File Structure": self.test_viewer_files(),
            "Test Viewer Setup": self.setup_test_viewer() is not None,
            "Development Server": self.test_dev_server(),
            "Docker Build": self.test_docker_build() if "--docker" in sys.argv else None
        }
        
        print("\n" + "=" * 50)
        print("Test Results:")
        print("-" * 50)
        
        passed = 0
        failed = 0
        skipped = 0
        
        for test_name, result in results.items():
            if result is None:
                print(f"  {test_name}: SKIPPED")
                skipped += 1
            elif result:
                print(f"  {test_name}: PASSED ✓")
                passed += 1
            else:
                print(f"  {test_name}: FAILED ✗")
                failed += 1
        
        print("-" * 50)
        print(f"Total: {passed} passed, {failed} failed, {skipped} skipped")
        
        if failed == 0:
            print("\nAll tests passed! The viewer is ready to use.")
            print(f"\nTest viewer available at: {self.test_output_dir}")
            
            # Offer to open browser
            if "--no-browser" not in sys.argv:
                response = input("\nOpen test viewer in browser? (y/n): ")
                if response.lower() == 'y':
                    viewer_path = self.test_output_dir / "enhanced_viewer.html"
                    webbrowser.open(f"file://{viewer_path}")
        else:
            print("\nSome tests failed. Please check the errors above.")
            sys.exit(1)


def main():
    """Main entry point."""
    print("FlowState Viewer Test Tool")
    print("Usage: python test_viewer.py [--docker] [--no-browser]")
    print()
    
    tester = ViewerTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()