# FlowState Docker Commands Reference

## Image Name
The Docker image is built as: `flowstate:2.0-openpose`

## Common Commands

### 1. Build the Docker Image
```bash
docker build -t flowstate:2.0-openpose .
```

### 2. Analyze YouTube Video (with GPU)
To leverage NVIDIA GPU acceleration, you must add the `--gpus all` flag.

```bash
# Basic analysis with GPU
docker run --rm -it --gpus all flowstate:2.0-openpose --url "https://youtube.com/watch?v=VIDEO_ID"

# Skip GitHub publishing
docker run --rm -it --gpus all flowstate:2.0-openpose --url "https://youtube.com/watch?v=VIDEO_ID" --skip-publish

# Analyze and serve locally
docker run --rm -it --gpus all -p 8080:8080 flowstate:2.0-openpose --url "https://youtube.com/watch?v=VIDEO_ID" --serve
```

### 3. Analyze Local Video (input.mp4, with GPU)
```bash
# Mount local video as input.mp4 (no URL needed)
docker run --rm -it --gpus all -v $(pwd)/your-video.mp4:/app/input.mp4:ro flowstate:2.0-openpose --skip-publish

# Analyze and serve
docker run --rm -it --gpus all -v $(pwd)/your-video.mp4:/app/input.mp4:ro -p 8080:8080 flowstate:2.0-openpose --serve
```

### 4. Run Web Server Only
The web server does not require GPU resources.

```bash
# Serve existing analysis results
docker run --rm -it -p 8080:8080 --network host flowstate:2.0-openpose server

# With custom port
docker run --rm -it -p 3000:3000 --network host flowstate:2.0-openpose server --port 3000
```

### 5. Using Docker Compose
Docker Compose is the recommended way to run the application as it handles GPU settings automatically.

```bash
# Build the image
docker-compose build

# Analyze with input.mp4 (place file in project root first)
# The 'flowstate' service is configured to use the NVIDIA runtime
docker-compose run --rm flowstate --serve

# Start web server (production profile)
docker-compose --profile production up web-server

# Development viewer
docker-compose --profile dev up viewer
```

### 6. Interactive Shell (with GPU)
```bash
# Access container shell for debugging, with GPUs available
docker run --rm -it --gpus all flowstate:2.0-openpose shell
```

### 7. Volume Mounting for Output
```bash
# Save output to host directory
docker run --rm -it --gpus all \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/input.mp4:/app/input.mp4:ro \
  flowstate:2.0-openpose --skip-publish
```

## Important Notes

1. The new image name is `flowstate:2.0-openpose`.
2. **GPU is required for analysis.** Use the `--gpus all` flag with `docker run` or use Docker Compose, which is pre-configured.
3. When using `--serve`, make sure to expose port 8080 with `-p 8080:8080`.
4. For host network access, add `--network host`.
5. Always use `:ro` (read-only) when mounting input videos for security.

## Troubleshooting

### NVIDIA Container Toolkit Not Found
If you see an error like `docker: Error response from daemon: unknown runtime specified 'nvidia'`, you need to install the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html).

### Wrong Image Name Error
If you see: `Unable to find image 'flowstate:1.0'`
Solution: Use `flowstate:2.0-openpose` instead.

### Port Already in Use
If port 8080 is taken:
```bash
docker run --rm -it --gpus all -p 8888:8080 flowstate:2.0-openpose --url VIDEO_URL --serve --serve-port 8080
```
Note: The internal port stays 8080, but it's mapped to 8888 on the host.

### Input Video Not Found
Make sure to use absolute paths or `$(pwd)` for volume mounts:
```bash
# Good
docker run --gpus all -v $(pwd)/input.mp4:/app/input.mp4:ro flowstate:2.0-openpose analyze --serve

# Bad (relative path without $(pwd))
docker run --gpus all -v ./input.mp4:/app/input.mp4:ro flowstate:2.0-openpose analyze --serve