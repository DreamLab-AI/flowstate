"""
Validation utilities for various inputs.
"""

import re
from ..core.exceptions import InvalidURLError, GitHubAuthError


def validate_youtube_url(url: str) -> str:
    """
    Validates if a given string is a valid YouTube video URL and extracts the video ID.
    """
    # Regex to find video ID from various YouTube URL formats
    youtube_regex = (
        r'(?:https?:\/\/)?(?:www\.)?'
        '(?:youtube\.com|youtu\.be)\/'
        '(?:watch\?v=|embed\/|v\/|.+\?v=)?([^"&?\/ ]{11})'
    )
    match = re.search(youtube_regex, url)
    if not match or not match.group(1):
        raise InvalidURLError(f"Could not extract a valid YouTube video ID from URL: {url}")

    return match.group(1)


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
