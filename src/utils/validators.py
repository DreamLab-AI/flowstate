"""
Validation utilities for various inputs.
"""

import re
from ..core.exceptions import InvalidURLError, GitHubAuthError


def validate_youtube_url(url: str) -> str:
    """
    Validates if a given string is a valid YouTube video URL and extracts the video ID.

    Args:
        url: The URL string to validate.

    Returns:
        The extracted YouTube video ID.

    Raises:
        InvalidURLError: If the URL is not a valid YouTube video URL.
    """
    youtube_regex = (
        r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=|playlist\?list=|e/|f/|'
        'videos/|user/\S+|channel/\S+|'
        'ytscreeningroom\?v=|yt.be/|'
        'vi/|user/.+/videos/|'
        'embed/videoseries\?list=)'
        '([^"&?\/\s]{11})'
    )
    match = re.search(youtube_regex, url)
    if not match:
        raise InvalidURLError(f"Invalid YouTube URL format: {url}")

    video_id = match.group(4) # The 11-character video ID
    if not video_id:
        raise InvalidURLError(f"Could not extract video ID from URL: {url}")

    return video_id


def validate_github_token(token: str) -> bool:
    """
    Validates the format of a GitHub Personal Access Token.
    A valid token is typically 40 characters long and consists of hexadecimal characters.
    Newer tokens (fine-grained) can be longer and start with 'ghp_'.

    Args:
        token: The GitHub token string to validate.

    Returns:
        True if the token format is valid, False otherwise.

    Raises:
        GitHubAuthError: If the token format is invalid.
    """
    # Classic token: 40 hex characters
    if re.fullmatch(r'[0-9a-fA-F]{40}', token):
        return True
    # Fine-grained token: starts with ghp_ and is longer
    if token.startswith('ghp_') and len(token) > 40:
        return True

    raise GitHubAuthError("Invalid GitHub token format. Expected a 40-character hexadecimal string or a fine-grained token starting with 'ghp_'.")
