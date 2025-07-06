"""
GitHub Pages publishing module.
Handles creating GitHub repositories, pushing content, and enabling GitHub Pages.
"""

from github import Github, GithubException
from pathlib import Path
from typing import Optional, Callable, Dict, Any
import base64
import time

from ..core.config import settings
from ..core.exceptions import GitHubAuthError, GitHubPublishError


class GitHubPublisher:
    """
    Manages publishing analysis results to GitHub Pages.
    """

    def __init__(self):
        self.github_client: Optional[Github] = None

    def _get_github_client(self, token: str) -> Github:
        """
        Initializes and returns a GitHub client.
        """
        if not self.github_client:
            try:
                self.github_client = Github(
                    login_or_token=token,
                    timeout=settings.github_api_timeout,
                    retry=settings.github_retry_attempts,
                    per_page=100
                )
                # Test authentication
                self.github_client.get_user().login
            except GithubException as e:
                raise GitHubAuthError(f"Invalid GitHub token or API error: {e.data.get('message', str(e))}") from e
            except Exception as e:
                raise GitHubAuthError(f"Failed to initialize GitHub client: {e}") from e
        return self.github_client

    def deploy(self, token: str, repo_name: str, viewer_dir: Path,
             progress_callback: Optional[Callable[[int], None]] = None) -> Dict[str, str]:
        """
        Deploys the viewer to GitHub Pages.

        Args:
            token: GitHub Personal Access Token.
            repo_name: Name of the GitHub repository to create/use.
            viewer_dir: Path to the directory containing the viewer files.
            progress_callback: Optional callback for progress updates.

        Returns:
            A dictionary containing deployment information (e.g., pages_url).

        Raises:
            GitHubPublishError: If deployment fails.
        """
        g = self._get_github_client(token)
        user = g.get_user()

        try:
            # 1. Create or get repository
            if progress_callback: progress_callback(1)
            try:
                repo = user.get_repo(repo_name)
                print(f"Repository '{repo_name}' already exists. Using existing repository.")
            except GithubException as e:
                if e.status == 404:
                    print(f"Creating new repository: '{repo_name}'...")
                    repo = user.create_repo(
                        name=repo_name,
                        description=f"FlowState-CLI analysis for {repo_name}",
                        private=False,
                        has_issues=False,
                        has_projects=False,
                        has_wiki=False,
                        auto_init=True
                    )
                    # Give GitHub some time to initialize the repo
                    time.sleep(settings.github_retry_delay * 2)
                else:
                    raise GitHubPublishError(f"Failed to create or get repository: {e.data.get('message', str(e))}") from e

            # 2. Upload files
            if progress_callback: progress_callback(2)
            print("Uploading viewer files...")
            self._upload_directory_to_repo(repo, viewer_dir)

            # 3. Enable GitHub Pages
            if progress_callback: progress_callback(3)
            print("Enabling GitHub Pages...")
            try:
                # Ensure the 'gh-pages' branch exists and is the default for Pages
                # First, create gh-pages branch if it doesn't exist
                try:
                    source_branch = repo.get_branch("main")
                    repo.create_git_ref(ref=f"refs/heads/gh-pages", sha=source_branch.commit.sha)
                except GithubException as e:
                    if e.status == 422 and "Reference already exists" in str(e):
                        pass # gh-pages branch already exists
                    else:
                        raise GitHubPublishError(f"Failed to create gh-pages branch: {e.data.get('message', str(e))}") from e

                # Update Pages settings to use gh-pages branch
                pages = repo.get_pages()
                pages.update(branch="gh-pages", path="/")

            except GithubException as e:
                raise GitHubPublishError(f"Failed to enable GitHub Pages: {e.data.get('message', str(e))}") from e

            # 4. Get Pages URL
            if progress_callback: progress_callback(4)
            # GitHub Pages can take a moment to become active
            pages_url = None
            for _ in range(settings.github_retry_attempts):
                try:
                    pages = repo.get_pages()
                    pages_url = pages.html_url
                    if pages_url:
                        break
                except GithubException:
                    pass
                time.sleep(settings.github_retry_delay)

            if not pages_url:
                raise GitHubPublishError("Could not retrieve GitHub Pages URL after deployment.")

            return {"pages_url": pages_url, "repo_url": repo.html_url}

        except GitHubException as e:
            raise GitHubPublishError(f"GitHub API error during deployment: {e.data.get('message', str(e))}") from e
        except Exception as e:
            raise GitHubPublishError(f"An unexpected error occurred during deployment: {e}") from e

    def _upload_directory_to_repo(self, repo, directory_path: Path, path_in_repo: str = ""):
        """
        Recursively uploads files from a local directory to a GitHub repository.
        """
        for item in directory_path.iterdir():
            if item.is_file():
                file_content = item.read_bytes()
                encoded_content = base64.b64encode(file_content).decode('utf-8')
                repo_file_path = f"{path_in_repo}/{item.name}".lstrip('/')

                try:
                    # Check if file exists to decide between create or update
                    contents = repo.get_contents(repo_file_path, ref="gh-pages")
                    repo.update_file(
                        path=repo_file_path,
                        message=f"Update {repo_file_path}",
                        content=encoded_content,
                        sha=contents.sha,
                        branch="gh-pages"
                    )
                    print(f"Updated: {repo_file_path}")
                except GithubException as e:
                    if e.status == 404: # File does not exist, create it
                        repo.create_file(
                            path=repo_file_path,
                            message=f"Add {repo_file_path}",
                            content=encoded_content,
                            branch="gh-pages"
                        )
                        print(f"Created: {repo_file_path}")
                    else:
                        raise GitHubPublishError(f"Failed to upload file {repo_file_path}: {e.data.get('message', str(e))}") from e
            elif item.is_dir():
                self._upload_directory_to_repo(repo, item, f"{path_in_repo}/{item.name}")
