#!/usr/bin/env python3
"""
FlowState-CLI: YouTube to 3D Tai Chi Analysis & Publishing Tool
Refactored CLI interface with improved error handling and structure.
"""

import sys
import click
from pathlib import Path
from typing import Optional, Tuple
import re

from colorama import init, Fore, Style
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..core.config import settings
from ..core.exceptions import (
    FlowStateError, InvalidURLError, VideoDownloadError,
    PoseDetectionError, GitHubAuthError
)
from ..core.downloader import YouTubeDownloader
from ..core.analyzer import PoseAnalyzer
from ..core.publisher import GitHubPublisher
from ..viewer.builder import ViewerBuilder
from ..utils.validators import validate_youtube_url, validate_github_token
from ..core.server import FlowStateServer

# Initialize colorama for cross-platform color support
init(autoreset=True)
console = Console()


class FlowStateCLI:
    """Main CLI application class."""

    def __init__(self):
        self.downloader = YouTubeDownloader()
        self.analyzer = PoseAnalyzer()
        self.viewer_builder = ViewerBuilder()
        self.publisher = GitHubPublisher()

    def print_banner(self):
        """Display welcome banner."""
        console.print("\n[cyan]" + "="*60 + "[/cyan]")
        console.print("[cyan]      FlowState-CLI: Tai Chi Analysis & Publishing[/cyan]")
        console.print("[cyan]" + "="*60 + "[/cyan]\n")

    def run_analysis(self, youtube_url: str) -> Tuple[Optional[Path], Optional[dict]]:
        """
        Run the complete analysis pipeline.

        Args:
            youtube_url: YouTube video URL

        Returns:
            Tuple of (viewer_dir, video_info) or (None, None) on failure
        """
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:

                # Step 1: Download video
                task = progress.add_task("[cyan]Downloading video...", total=None)
                video_path, video_info = self.downloader.download_video(youtube_url)
                progress.update(task, completed=100)
                console.print(f"[green]✔ Video downloaded: '{video_info['title']}'[/green]")

                # Step 2: Extract frames
                task = progress.add_task("[cyan]Extracting frames...", total=None)
                frames_dir = self.downloader.extract_frames(video_path)
                progress.update(task, completed=100)
                console.print(f"[green]✔ Frames extracted successfully[/green]")

                # Step 3: Analyze poses
                task = progress.add_task("[cyan]Analyzing movement...", total=None)
                pose_data = self.analyzer.analyze_video(frames_dir)
                progress.update(task, completed=100)

                # Display analysis results
                overall_flow = pose_data['overall_scores']['flow']
                console.print(f"\n[green]✔ Analysis complete![/green]")
                console.print(f"[yellow]Overall Flow Score: {overall_flow:.1f}%[/yellow]")
                console.print(f"[dim]Detection Rate: {pose_data['detection_rate']:.1%}[/dim]")

                # Step 4: Generate viewer
                task = progress.add_task("[cyan]Generating 3D viewer...", total=None)
                viewer_dir = self.viewer_builder.generate_viewer(pose_data, video_info)
                progress.update(task, completed=100)
                console.print(f"[green]✔ 3D viewer generated[/green]")

                return viewer_dir, video_info

        except FlowStateError as e:
            console.print(f"[red]✖ {e.message}[/red]")
            if settings.debug and e.details:
                console.print(f"[dim]Details: {e.details}[/dim]")
            return None, None
        except Exception as e:
            console.print(f"[red]✖ Unexpected error: {str(e)}[/red]")
            if settings.debug:
                console.print_exception()
            return None, None
        finally:
            # Cleanup
            if hasattr(self, 'downloader'):
                self.downloader.cleanup()

    def github_deployment_wizard(self, viewer_dir: Path, video_info: dict) -> bool:
        """
        Interactive GitHub deployment wizard.

        Args:
            viewer_dir: Directory containing the viewer files
            video_info: Video metadata

        Returns:
            True if deployment successful, False otherwise
        """
        console.print("\n[cyan]GitHub Pages Deployment Wizard[/cyan]")
        console.print("[dim]Your analysis will be published to a public website.[/dim]\n")

        console.print("\n[cyan]GitHub Pages Deployment Wizard[/cyan]")
        console.print("[dim]Your analysis will be published to a public website.[/dim]\n")

        # Get token from environment or prompt
        if settings.github_token:
            console.print("[green]✔ Using GitHub token from environment[/green]")
            token = settings.github_token
        else:
            # Step-by-step guidance
            console.print("[yellow]Step 1:[/yellow] Generate a GitHub Personal Access Token")
            console.print("[blue]https://github.com/settings/tokens/new?scopes=repo,workflow[/blue]")
            console.print("[dim]Required scopes: repo, workflow[/dim]\n")

            # Get token
            token = console.input("[yellow]Paste your token here (hidden): [/yellow]", password=True)

        try:
            # Validate token only if it was manually entered (i.e., not from settings)
            if not settings.github_token and not validate_github_token(token):
                raise GitHubAuthError("Invalid token format")
            elif settings.github_token and not validate_github_token(token):
                # If token is from settings but still invalid, raise error
                raise GitHubAuthError("Invalid GitHub token from environment. Please check your .env file.")

            # Get repository name
            default_name = re.sub(r'[^a-zA-Z0-9-]', '-',
                                video_info['title'].lower())[:30].strip('-')
            repo_name = console.input(
                f"\n[yellow]Repository name[[/yellow][green]{default_name}[/green][yellow]]:[/yellow] "
            ) or default_name

            # Sanitize repo name
            repo_name = re.sub(r'[^a-zA-Z0-9-]', '-', repo_name).strip('-')

            console.print(f"\n[cyan]Deploying to GitHub Pages...[/cyan]")

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:

                task = progress.add_task("[cyan]Creating repository...", total=4)

                # Deploy
                deployment_info = self.publisher.deploy(
                    token=token,
                    repo_name=repo_name,
                    viewer_dir=viewer_dir,
                    progress_callback=lambda step: progress.update(task, advance=1)
                )

                progress.update(task, completed=4)

            # Success!
            console.print(f"\n[green]{'='*60}[/green]")
            console.print(f"[green]✨ Success! Your analysis is live at:[/green]")
            console.print(f"[blue][link={deployment_info['pages_url']}]{deployment_info['pages_url']}[/link][/blue]")
            console.print(f"[green]{'='*60}[/green]\n")

            return True

        except FlowStateError as e:
            console.print(f"\n[red]✖ Deployment failed: {e.message}[/red]")
            return False
        except Exception as e:
            console.print(f"\n[red]✖ Unexpected error: {str(e)}[/red]")
            if settings.debug:
                console.print_exception()
            return False


@click.command()
@click.option(
    '--url', '-u',
    help='YouTube URL to analyze'
)
@click.option(
    '--output', '-o',
    type=click.Path(path_type=Path),
    help='Output directory for analysis'
)
@click.option(
    '--cookie-file', '-c',
    type=click.Path(path_type=Path, exists=True, dir_okay=False),
    help='Path to a Netscape-format cookies file for yt-dlp authentication'
)
@click.option(
    '--skip-publish',
    is_flag=True,
    help='Skip GitHub publishing step'
)
@click.option(
    '--serve',
    is_flag=True,
    help='Start local web server to host visualization'
)
@click.option(
    '--serve-port',
    type=int,
    default=8080,
    help='Port for the web server (default: 8080)'
)
@click.option(
    '--debug',
    is_flag=True,
    help='Enable debug mode'
)
@click.version_option(version=settings.version)
def main(url: Optional[str], output: Optional[Path], cookie_file: Optional[Path],
         skip_publish: bool, serve: bool, serve_port: int, debug: bool):
    """
    FlowState-CLI: Transform Tai Chi videos into interactive 3D analyses.

    Analyze YouTube Tai Chi videos and publish them as interactive
    3D visualizations on GitHub Pages.
    """
    # Update settings
    if debug:
        settings.debug = True
    if output:
        settings.output_dir = output
        settings.create_directories()
    if cookie_file:
        settings.yt_dlp_cookiefile = cookie_file

    # Initialize CLI
    cli = FlowStateCLI()
    cli.print_banner()

    # Check for local input file first
    input_file_path = Path("input.mp4")
    video_path = None
    video_info = None

    if not url and input_file_path.exists() and input_file_path.is_file():
        console.print(f"[green]✔ Found local video: {input_file_path}[/green]")
        video_path, video_info = cli.downloader.process_local_video(input_file_path)
    elif url:
        # Process YouTube URL
        try:
            video_id = validate_youtube_url(url)
            video_path, video_info = cli.downloader.download_video(url)
        except InvalidURLError as e:
            console.print(f"[red]✖ {e.message}[/red]")
            console.print("[dim]Example: https://youtube.com/watch?v=VIDEO_ID[/dim]\n")
            return 1
    else:
        # No URL provided and no input.mp4 found - ask for URL
        console.print("[green]Welcome to FlowState-CLI![/green]")
        console.print("Please enter the YouTube URL of the Tai Chi video:\n")

        while True:
            url = console.input("[yellow]YouTube URL: [/yellow]").strip()

            try:
                video_id = validate_youtube_url(url)
                video_path, video_info = cli.downloader.download_video(url)
                break
            except InvalidURLError as e:
                console.print(f"[red]✖ {e.message}[/red]")
                console.print("[dim]Example: https://youtube.com/watch?v=VIDEO_ID[/dim]\n")

    if not video_path or not video_info:
        console.print("\n[red]Video processing failed. Exiting.[/red]")
        return 1

    # Step 2: Extract frames
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Extracting frames...", total=None)
            frames_dir = cli.downloader.extract_frames(video_path)
            progress.update(task, completed=100)
            console.print(f"[green]✔ Frames extracted successfully[/green]")

            # Step 3: Analyze poses
            task = progress.add_task("[cyan]Analyzing movement...", total=None)
            pose_data = cli.analyzer.analyze_video(frames_dir)
            progress.update(task, completed=100)

            # Display analysis results
            overall_flow = pose_data['overall_scores']['flow']
            console.print(f"\n[green]✔ Analysis complete![/green]")
            console.print(f"[yellow]Overall Flow Score: {overall_flow:.1f}%[/yellow]")
            console.print(f"[dim]Detection Rate: {pose_data['detection_rate']:.1%}[/dim]")

            # Step 4: Generate viewer
            task = progress.add_task("[cyan]Generating 3D viewer...", total=None)
            viewer_dir = cli.viewer_builder.generate_viewer(pose_data, video_info)
            progress.update(task, completed=100)
            console.print(f"[green]✔ 3D viewer generated[/green]")

    except FlowStateError as e:
        console.print(f"[red]✖ {e.message}[/red]")
        if settings.debug and e.details:
            console.print(f"[dim]Details: {e.details}[/dim]")
        return 1
    except Exception as e:
        console.print(f"[red]✖ Unexpected error: {str(e)}[/red]")
        if settings.debug:
            console.print_exception()
        return 1
    finally:
        if hasattr(cli, 'downloader'):
            cli.downloader.cleanup()

    viewer_dir, video_info = None, None # Reset for clarity, actual values come from above
    # Re-assign viewer_dir and video_info from the successful path
    if 'viewer_dir' in locals() and 'video_info' in locals():
        pass # Already assigned in the try block
    else:
        console.print("\n[red]Analysis failed. Please try with a different video.[/red]")
        return 1

    if not viewer_dir:
        console.print("\n[red]Analysis failed. Please try with a different video.[/red]")
        return 1

    # Publishing step
    if not skip_publish and not serve:
        console.print("\n[green]Analysis complete![/green]")
        if click.confirm("Would you like to publish to GitHub Pages?", default=True):
            success = cli.github_deployment_wizard(viewer_dir, video_info)
            if success:
                return 0
            else:
                # Offer to start local server as fallback
                console.print("\n[yellow]GitHub Pages deployment failed.[/yellow]")
                if click.confirm("Would you like to start a local web server instead?", default=True):
                    serve = True
                else:
                    return 1

    # Start local web server if requested or as fallback
    if serve:
        console.print(f"\n[yellow]Starting web server to host visualization...[/yellow]")
        server = FlowStateServer(port=serve_port, directory=viewer_dir)
        
        if server.start(daemon=False):
            console.print(f"\n[green]✔ Web server started successfully![/green]")
            console.print(f"[cyan]View your visualization at: http://localhost:{serve_port}[/cyan]")
            console.print("\n[dim]Press Ctrl+C to stop the server[/dim]\n")
            
            try:
                server.wait()
            except KeyboardInterrupt:
                console.print("\n[yellow]Shutting down server...[/yellow]")
                server.stop()
        else:
            console.print("[red]✖ Failed to start web server[/red]")
            return 1
    else:
        console.print(f"\n[yellow]Analysis saved to: {viewer_dir}[/yellow]")
        
    return 0


if __name__ == "__main__":
    sys.exit(main())