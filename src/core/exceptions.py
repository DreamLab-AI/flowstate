"""
Custom exception classes for FlowState-CLI.
Provides a structured way to handle errors throughout the application.
"""

class FlowStateError(Exception):
    """Base exception for FlowState-CLI errors."""
    def __init__(self, message: str, details: str = None):
        self.message = message
        self.details = details
        super().__init__(self.message)

class InvalidURLError(FlowStateError):
    """Raised when a provided URL is invalid or unsupported."""
    def __init__(self, message: str = "Invalid or unsupported URL provided.", details: str = None):
        super().__init__(message, details)

class VideoDownloadError(FlowStateError):
    """Raised when there's an issue with video downloading or processing."""
    def __init__(self, message: str = "Failed to download or process video.", details: str = None):
        super().__init__(message, details)

class PoseDetectionError(FlowStateError):
    """Raised when pose detection fails or encounters an issue."""
    def __init__(self, message: str = "Pose detection failed.", details: str = None):
        super().__init__(message, details)

class GitHubAuthError(FlowStateError):
    """Raised when GitHub authentication fails."""
    def __init__(self, message: str = "GitHub authentication failed. Please check your token and permissions.", details: str = None):
        super().__init__(message, details)

class GitHubPublishError(FlowStateError):
    """Raised when publishing to GitHub Pages fails."""
    def __init__(self, message: str = "Failed to publish to GitHub Pages.", details: str = None):
        super().__init__(message, details)

class ViewerBuildError(FlowStateError):
    """Raised when there's an error building the 3D viewer."""
    def __init__(self, message: str = "Failed to build the 3D viewer.", details: str = None):
        super().__init__(message, details)
