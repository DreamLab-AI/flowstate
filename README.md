# FlowState-CLI v2.0

FlowState-CLI is a command-line interface tool designed to analyze Tai Chi and other movement videos from YouTube or local files. It uses an **OpenPose-compatible** pose estimation model with **NVIDIA GPU acceleration** to generate interactive 3D visualizations, which can be viewed locally or published to GitHub Pages.

## Key Features

- **High-Quality Pose Estimation**: Utilizes a powerful pose detection model (based on YOLOv8-Pose) for accurate analysis.
- **Full Body Analysis**: Detects keypoints for the entire body, including **hands, feet, and face**.
- **GPU Accelerated**: Leverages NVIDIA GPUs via Docker for high-performance analysis.
- **Enhanced Temporal Analysis**: Increases temporal granularity by **10x** and uses **motion interpolation** to produce smooth, fluid animations.
- **Download Flexibility**: Analyzes videos directly from YouTube or local `*.mp4` files.
- **Interactive 3D Viewer**: Generates a self-contained web-based viewer with playback controls and motion trails.
- **Deployment Options**:
    - Serve the viewer locally for private analysis.
    - Publish the interactive 3D visualization to GitHub Pages.

## Installation

### Prerequisites

- **Git**
- **Docker**
- **NVIDIA GPU** with the latest drivers.
- **NVIDIA Container Toolkit**: Essential for providing GPU access to Docker containers. Follow the [official installation guide](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html).

### Using Docker (Recommended)

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-repo/flowstate-cli.git
    cd flowstate-cli
    ```

2.  **Build the Docker image:**
    This command builds the `flowstate:2.0-openpose` image, which includes all dependencies.
    ```bash
    docker build -t flowstate:2.0-openpose .
    ```

3.  **Verify the setup:**
    Run the help command to ensure the image is built correctly.
    ```bash
    docker run --rm -it --gpus all flowstate:2.0-openpose --help
    ```

## Usage

### Analyze a YouTube Video (with GPU)

To analyze a YouTube video and generate a local 3D visualization, run the following command. The `--gpus all` flag is **required** for the analysis to work.

```bash
docker run --rm -it --gpus all \
  flowstate:2.0-openpose \
  --url "YOUR_YOUTUBE_URL" \
  --skip-publish
```

Replace `"YOUR_YOUTUBE_URL"` with the video link. The `--skip-publish` flag prevents publishing to GitHub Pages. The output will be saved in the `./output` directory on your host machine if you mount it (see below).

### Analyze a Local Video File (with GPU)

FlowState-CLI can analyze local `*.mp4` files. Mount your video file to `/app/input.mp4` inside the container.

```bash
# Mount your video as input.mp4
docker run --rm -it --gpus all \
  -v /path/to/your/video.mp4:/app/input.mp4:ro \
  flowstate:2.0-openpose \
  --skip-publish
```

### Serving the Viewer Locally

Add the `--serve` flag to host the interactive viewer on a local web server (default port: 8080).

```bash
docker run --rm -it --gpus all -p 8080:8080 \
  flowstate:2.0-openpose \
  --url "YOUR_YOUTUBE_URL" \
  --serve
```

### Using Docker Compose (Easiest Method)

Docker Compose is the simplest way to run the application, as it automatically handles GPU runtime configuration and volume mounts.

1.  **Place your local video** (if any) in the project root and name it `input.mp4`.
2.  **Run the analysis:**
    ```bash
    docker-compose run --rm flowstate
    ```
    This command will analyze `input.mp4` (if it exists) or you can pass a URL:
    ```bash
    docker-compose run --rm flowstate --url "YOUR_YOUTUBE_URL"
    ```

### Publishing to GitHub Pages

To publish the interactive 3D visualization to GitHub Pages:

1.  **Generate a GitHub Personal Access Token (PAT)** with `repo` and `workflow` scopes.
2.  **Create a `.env` file** in the project root with your token:
    ```
    FLOWSTATE_GITHUB_TOKEN=your_copied_github_pat
    ```
3.  **Run the analysis command without `--skip-publish`:**
    ```bash
    docker run --rm -it --gpus all flowstate:2.0-openpose --url "YOUR_YOUTUBE_URL"
    ```
    The CLI will use the token from the `.env` file to create a repository and deploy the viewer.

### Using a Cookie File for Authentication

For age-restricted or private YouTube videos, provide a `cookies.txt` file.

1.  **Generate `cookies.txt`** using a browser extension like "Get cookies.txt LOCALLY".
2.  **Run with the `--cookie-file` option:**
    ```bash
    docker run --rm -it --gpus all \
      -v /path/to/your/cookies.txt:/app/cookies.txt:ro \
      flowstate:2.0-openpose \
      --url "YOUTUBE_URL" \
      --cookie-file /app/cookies.txt
    ```

## Development

### Local Setup (Advanced)

Running locally without Docker is complex due to the CUDA and PyTorch dependencies. It is recommended to develop inside the container.

1.  **Start an interactive shell** in the container:
    ```bash
    docker run --rm -it --gpus all \
      -v $(pwd):/app \
      flowstate:2.0-openpose \
      shell
    ```
2.  **Inside the container**, you can run commands directly:
    ```bash
    # The project code is mounted at /app
    cd /app
    # Run the CLI
    flowstate --help
    ```

### Project Structure

-   `src/cli/app.py`: Main CLI application entry point.
-   `src/core/analyzer.py`: Core logic for pose analysis using the OpenPose-compatible model.
-   `src/core/downloader.py`: Handles video downloading.
-   `src/core/publisher.py`: Manages GitHub publishing.
-   `src/viewer/`: Contains the logic and templates for the 3D viewer.
-   `requirements.txt`: Python dependencies.
-   `Dockerfile`: Defines the GPU-enabled Docker image.
-   `docker-compose.yml`: Defines services for easy development and deployment.

## Contributing

Contributions are welcome! Please see the `CONTRIBUTING.md` for guidelines.

## License

This project is licensed under the MIT License.