#!/usr/bin/env python3
"""
Simple test for input.mp4 functionality without OpenCV dependency.
"""

import sys
from pathlib import Path

# Test Docker configuration
def test_docker_config():
    """Check Docker configuration for input.mp4 support."""
    print("Testing Docker Configuration")
    print("=" * 40)
    
    compose_path = Path(__file__).parent / "docker-compose.yml"
    if not compose_path.exists():
        print("✗ docker-compose.yml not found")
        return False
    
    content = compose_path.read_text()
    checks_passed = 0
    
    # Check flowstate service
    if "./input.mp4:/app/input.mp4:ro" in content:
        print("✓ flowstate service has input.mp4 volume mapping")
        checks_passed += 1
    else:
        print("✗ flowstate service missing input.mp4 volume mapping")
    
    # Check web-server service
    web_server_start = content.find("web-server:")
    if web_server_start > 0:
        web_server_section = content[web_server_start:content.find("profiles:", web_server_start)]
        if "./input.mp4:/app/input.mp4:ro" in web_server_section:
            print("✓ web-server service has input.mp4 volume mapping")
            checks_passed += 1
        else:
            print("✗ web-server service missing input.mp4 volume mapping")
    
    return checks_passed == 2


def test_cli_code():
    """Check CLI code for input.mp4 handling."""
    print("\nTesting CLI Implementation")
    print("=" * 40)
    
    cli_path = Path(__file__).parent / "src" / "cli" / "app.py"
    if not cli_path.exists():
        print("✗ CLI app.py not found")
        return False
    
    content = cli_path.read_text()
    checks_passed = 0
    
    # Check for input.mp4 path definition
    if 'Path("input.mp4")' in content:
        print("✓ CLI defines input.mp4 path")
        checks_passed += 1
    else:
        print("✗ CLI missing input.mp4 path definition")
    
    # Check for local video processing
    if "process_local_video" in content:
        print("✓ CLI calls process_local_video method")
        checks_passed += 1
    else:
        print("✗ CLI missing process_local_video call")
    
    # Check for proper URL handling
    if "not url and input_file_path.exists()" in content:
        print("✓ CLI checks for input.mp4 when no URL provided")
        checks_passed += 1
    else:
        print("✗ CLI missing proper input.mp4 detection logic")
    
    return checks_passed == 3


def test_documentation():
    """Check if documentation includes input.mp4 usage."""
    print("\nTesting Documentation")
    print("=" * 40)
    
    checks_passed = 0
    
    # Check README
    readme_path = Path(__file__).parent / "README.md"
    if readme_path.exists():
        content = readme_path.read_text()
        if "input.mp4" in content:
            print("✓ README.md documents input.mp4 usage")
            checks_passed += 1
        else:
            print("✗ README.md missing input.mp4 documentation")
    
    # Check UPGRADE_NOTES
    upgrade_path = Path(__file__).parent / "UPGRADE_NOTES.md"
    if upgrade_path.exists():
        content = upgrade_path.read_text()
        if "input.mp4" in content:
            print("✓ UPGRADE_NOTES.md mentions input.mp4 support")
            checks_passed += 1
        else:
            print("✗ UPGRADE_NOTES.md missing input.mp4 information")
    
    return checks_passed == 2


def main():
    """Run all tests."""
    print("FlowState input.mp4 Configuration Test")
    print("=" * 40)
    
    results = []
    results.append(test_docker_config())
    results.append(test_cli_code())
    results.append(test_documentation())
    
    print("\n" + "=" * 40)
    print("Summary:")
    print(f"  Docker Config: {'PASS' if results[0] else 'FAIL'}")
    print(f"  CLI Implementation: {'PASS' if results[1] else 'FAIL'}")
    print(f"  Documentation: {'PASS' if results[2] else 'FAIL'}")
    
    if all(results):
        print("\n✓ All configuration tests passed!")
        print("\nUsage:")
        print("  1. Place your video file as 'input.mp4' in the project root")
        print("  2. Run: docker-compose run flowstate analyze --serve")
        print("  3. Or: docker run -v /path/to/video.mp4:/app/input.mp4:ro flowstate:1.0 analyze --serve")
        return 0
    else:
        print("\n✗ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())