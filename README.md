# FlowState-CLI

FlowState-CLI is a command-line interface tool designed to analyze Tai Chi videos from YouTube and publish interactive 3D visualizations on GitHub Pages.

## Features

- Download YouTube videos.
- Extract frames from videos.
- Analyze human poses and movements using MediaPipe and TensorFlow.
- Calculate "flow" and "detection rate" scores for Tai Chi movements.
- Generate interactive 3D visualizations of pose data.
- Publish analysis results to GitHub Pages.

## Installation

### Prerequisites

- Docker (recommended for easy setup)
- Git

### Using Docker (Recommended)

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-repo/flowstate-cli.git
    cd flowstate-cli
    ```

2.  **Build the Docker image:**
    ```bash
    docker build -t flowstate:1.0 .
    ```

3.  **Run the CLI:**
    ```bash
    docker run --rm -it flowstate:1.0 --help
    ```

## Usage

### Analyze a YouTube Video

To analyze a YouTube video and generate a local 3D visualization:

```bash
docker run --rm -it flowstate:1.0 --url "YOUR_YOUTUBE_URL" --skip-publish
```

Replace `"YOUR_YOUTUBE_URL"` with the actual YouTube video link. The `--skip-publish` flag will prevent the tool from attempting to publish to GitHub Pages. The output will be saved in the `./output` directory.

### Analyze a Local Video File (input.mp4)

FlowState-CLI can also analyze local video files. If no URL is provided, it will automatically look for `input.mp4` in the current directory:

```bash
# Using Docker - mount your video as input.mp4
docker run --rm -it -v /path/to/your/video.mp4:/app/input.mp4:ro flowstate:1.0 --skip-publish

# Or using docker-compose (place input.mp4 in the project root)
docker-compose run flowstate analyze --skip-publish
```

The tool will automatically detect and process `input.mp4` when:
1. No YouTube URL is provided via the `--url` flag
2. The file `input.mp4` exists in the working directory (or is mounted in Docker)

### Analyze and Publish to GitHub Pages

To analyze a YouTube video and publish the interactive 3D visualization to GitHub Pages:

1.  **Generate a GitHub Personal Access Token (PAT):**
    - Go to [GitHub Developer Settings](https://github.com/settings/tokens/new?scopes=repo,workflow).
    - Click "Generate new token" (or "Generate new token (classic)").
    - Give your token a descriptive name (e.g., `flowstate-cli-deploy`).
    - **Crucially, grant the `repo` and `workflow` scopes.**
    - Click "Generate token" and **copy the token immediately**. You won't be able to see it again.

2.  **Set the GitHub Token as an Environment Variable:**
    It is highly recommended to set your GitHub token as an environment variable to avoid hardcoding it. You can do this by creating a `.env` file in the root of the `flowstate-cli` project:

    ```
    FLOWSTATE_GITHUB_TOKEN=your_copied_github_pat
    ```

    Replace `your_copied_github_pat` with the token you generated. Ensure `.env` is in your `.gitignore` file (it should be by default).

3.  **Run the analysis and publish command:**
    ```bash
    docker run --rm -it flowstate:1.0 --url "YOUR_YOUTUBE_URL"
    ```

    The CLI will automatically detect the `FLOWSTATE_GITHUB_TOKEN` environment variable from your `.env` file (if present) and use it for publishing. If the environment variable is not set, it will prompt you to paste the token.

    The tool will create a new GitHub repository (or use an existing one if the name matches) and publish your analysis to GitHub Pages. The URL to your live analysis will be displayed in the console.

### Using a Cookie File for Authentication

Some videos may require you to be logged into a YouTube account. If you encounter issues, you can use the `--cookie-file` option to provide a `cookies.txt` file for authentication.

**Generating a `cookies.txt` File**

You can use a browser extension to export your YouTube cookies in the required Netscape format. Here are a few options:

*   **Get cookies.txt LOCALLY:** [Chrome](https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc) | [Firefox](https://addons.mozilla.org/en-US/firefox/addon/get-cookies-txt-locally/)
*   **EditThisCookie:** [Chrome](https://chrome.google.com/webstore/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg)

**Instructions:**

1.  Install one of the recommended extensions.
2.  Navigate to [youtube.com](https://www.youtube.com) and log in to your account.
3.  Click the extension's icon in your browser's toolbar.
4.  Export your cookies in **Netscape** format and save the file as `cookies.txt`.
5.  Use the `--cookie-file` option to provide the path to your `cookies.txt` file when running the application:
    ```bash
    docker run --rm -it -v /path/to/your/cookies.txt:/app/cookies.txt flowstate:1.0 --url "YOUTUBE_URL" --cookie-file /app/cookies.txt
    ```

## Development

### Local Setup (without Docker)

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-repo/flowstate-cli.git
    cd flowstate-cli
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    pip install -e .
    ```

4.  **Run the CLI:**
    ```bash
    flowstate --help
    ```

### Project Structure

-   `src/cli/app.py`: Main CLI application entry point.
-   `src/core/`: Core logic for video downloading, pose analysis, and GitHub publishing.
-   `src/utils/`: Utility functions (e.g., validators).
-   `src/viewer/`: Logic for building the 3D visualization.
-   `requirements.txt`: Python dependencies.
-   `pyproject.toml`: Project metadata and build configuration.
-   `Dockerfile`: Docker build instructions.
-   `.env`: Environment variables (ignored by Git).

## Contributing

Contributions are welcome! Please see the `CONTRIBUTING.md` for guidelines.

## License

This project is licensed under the MIT License.