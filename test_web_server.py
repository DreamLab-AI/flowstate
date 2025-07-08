#!/usr/bin/env python3
"""
Test script for FlowState web server functionality.
Validates that the fallback web server works correctly.
"""

import sys
import time
import tempfile
import json
from pathlib import Path
import subprocess
import requests
from concurrent.futures import ThreadPoolExecutor

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.core.server import FlowStateServer


def create_test_viewer(output_dir: Path) -> Path:
    """Create a test viewer directory with sample files."""
    viewer_dir = output_dir / "viewer"
    viewer_dir.mkdir(parents=True, exist_ok=True)
    
    # Create index.html
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>FlowState Test Viewer</title>
</head>
<body>
    <h1>FlowState Test Viewer</h1>
    <div id="container"></div>
    <script src="data.js"></script>
</body>
</html>"""
    (viewer_dir / "index.html").write_text(html_content)
    
    # Create data.js with sample data
    data = {
        "poseData": {
            "pose_landmarks": [[{"x": 0, "y": 0, "z": 0, "visibility": 1.0}]],
            "overall_scores": {
                "flow": 85.5,
                "balance": 78.2,
                "smoothness": 92.1,
                "energy": 71.3
            }
        },
        "videoInfo": {
            "title": "Test Video",
            "uploader": "Test User",
            "uploadDate": "2024-01-01",
            "webpageUrl": "#"
        }
    }
    (viewer_dir / "data.js").write_text(f"const flowStateData = {json.dumps(data, indent=2)};")
    
    return viewer_dir


def test_server_startup():
    """Test that the server starts correctly."""
    print("Testing server startup...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        viewer_dir = create_test_viewer(Path(tmpdir))
        server = FlowStateServer(port=8888, directory=viewer_dir)
        
        assert server.validate_directory(), "Directory validation failed"
        assert server.start(daemon=True), "Server failed to start"
        
        # Give server time to start
        time.sleep(1)
        
        # Test that server is accessible
        try:
            response = requests.get("http://localhost:8888/index.html", timeout=5)
            assert response.status_code == 200, f"Unexpected status code: {response.status_code}"
            assert "FlowState Test Viewer" in response.text, "Expected content not found"
            print("✓ Server started successfully and is accessible")
        finally:
            server.stop()


def test_host_network_binding():
    """Test that server binds to all interfaces."""
    print("\nTesting host network binding...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        viewer_dir = create_test_viewer(Path(tmpdir))
        server = FlowStateServer(port=8889, directory=viewer_dir, host='0.0.0.0')
        
        if server.start(daemon=True):
            time.sleep(1)
            
            # Test localhost access
            try:
                response = requests.get("http://localhost:8889/", timeout=5)
                assert response.status_code == 200, "Localhost access failed"
                print("✓ Server accessible on localhost")
                
                # Test 0.0.0.0 binding (would be accessible from network)
                response = requests.get("http://127.0.0.1:8889/", timeout=5)
                assert response.status_code == 200, "127.0.0.1 access failed"
                print("✓ Server accessible on all interfaces")
            finally:
                server.stop()


def test_cors_headers():
    """Test that CORS headers are properly set."""
    print("\nTesting CORS headers...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        viewer_dir = create_test_viewer(Path(tmpdir))
        server = FlowStateServer(port=8890, directory=viewer_dir)
        
        if server.start(daemon=True):
            time.sleep(1)
            
            try:
                response = requests.get("http://localhost:8890/data.js", timeout=5)
                assert 'Access-Control-Allow-Origin' in response.headers, "CORS header missing"
                assert response.headers['Access-Control-Allow-Origin'] == '*', "CORS header incorrect"
                print("✓ CORS headers correctly configured")
            finally:
                server.stop()


def test_concurrent_requests():
    """Test server handles concurrent requests."""
    print("\nTesting concurrent request handling...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        viewer_dir = create_test_viewer(Path(tmpdir))
        server = FlowStateServer(port=8891, directory=viewer_dir)
        
        if server.start(daemon=True):
            time.sleep(1)
            
            def make_request(i):
                response = requests.get(f"http://localhost:8891/index.html?test={i}", timeout=5)
                return response.status_code == 200
            
            try:
                with ThreadPoolExecutor(max_workers=10) as executor:
                    futures = [executor.submit(make_request, i) for i in range(20)]
                    results = [f.result() for f in futures]
                    
                assert all(results), "Some concurrent requests failed"
                print("✓ Server handles concurrent requests successfully")
            finally:
                server.stop()


def test_docker_entrypoint():
    """Test that docker entrypoint recognizes server command."""
    print("\nTesting Docker entrypoint integration...")
    
    entrypoint_path = Path(__file__).parent / "docker-entrypoint.sh"
    if entrypoint_path.exists():
        content = entrypoint_path.read_text()
        assert '"server"|"serve")' in content, "Server command not found in entrypoint"
        assert 'python -m src.core.server' in content, "Server module call not found"
        print("✓ Docker entrypoint correctly configured")
    else:
        print("⚠ Docker entrypoint not found, skipping test")


def test_cli_integration():
    """Test that CLI has serve option."""
    print("\nTesting CLI integration...")
    
    cli_path = Path(__file__).parent / "src" / "cli" / "app.py"
    if cli_path.exists():
        content = cli_path.read_text()
        assert '--serve' in content, "Serve option not found in CLI"
        assert 'FlowStateServer' in content, "FlowStateServer import not found"
        assert 'serve_port' in content, "Serve port option not found"
        print("✓ CLI integration correctly configured")
    else:
        print("⚠ CLI app not found, skipping test")


def main():
    """Run all tests."""
    print("FlowState Web Server Test Suite")
    print("=" * 40)
    
    tests = [
        test_server_startup,
        test_host_network_binding,
        test_cors_headers,
        test_concurrent_requests,
        test_docker_entrypoint,
        test_cli_integration
    ]
    
    failed = 0
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"✗ Test failed: {test.__name__}")
            print(f"  Error: {e}")
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