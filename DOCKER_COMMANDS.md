# FlowState Docker Commands Reference

## Image Name
The Docker image is built as: `flowstate:1.0`

## Common Commands

### 1. Build the Docker Image
```bash
docker build -t flowstate:1.0 .
```

### 2. Analyze YouTube Video
```bash
# Basic analysis (with 'analyze' for clarity, automatically removed)
docker run --rm -it flowstate:1.0 analyze --url "https://youtube.com/watch?v=VIDEO_ID"

# Or direct usage without 'analyze'
docker run --rm -it flowstate:1.0 --url "https://youtube.com/watch?v=VIDEO_ID"

# Skip GitHub publishing
docker run --rm -it flowstate:1.0 analyze --url "https://youtube.com/watch?v=VIDEO_ID" --skip-publish

# Analyze and serve locally
docker run --rm -it -p 8080:8080 flowstate:1.0 analyze --url "https://youtube.com/watch?v=VIDEO_ID" --serve
```

### 3. Analyze Local Video (input.mp4)
```bash
# Mount local video as input.mp4 (no URL needed)
docker run --rm -it -v $(pwd)/your-video.mp4:/app/input.mp4:ro flowstate:1.0 --skip-publish

# Or with 'analyze' prefix
docker run --rm -it -v $(pwd)/your-video.mp4:/app/input.mp4:ro flowstate:1.0 analyze --skip-publish

# Analyze and serve
docker run --rm -it -v $(pwd)/your-video.mp4:/app/input.mp4:ro -p 8080:8080 flowstate:1.0 --serve

# Or with 'analyze' prefix
docker run --rm -it -v $(pwd)/your-video.mp4:/app/input.mp4:ro -p 8080:8080 flowstate:1.0 analyze --serve
```

### 4. Run Web Server Only
```bash
# Serve existing analysis results
docker run --rm -it -p 8080:8080 --network host flowstate:1.0 server

# With custom port
docker run --rm -it -p 3000:3000 --network host flowstate:1.0 server --port 3000
```

### 5. Using Docker Compose
```bash
# Build the image
docker-compose build

# Analyze with input.mp4 (place file in project root first)
docker-compose run --rm flowstate --serve

# Or with 'analyze' prefix
docker-compose run --rm flowstate analyze --serve

# Start web server (production profile)
docker-compose --profile production up web-server

# Development viewer
docker-compose --profile dev up viewer
```

### 6. Interactive Shell
```bash
# Access container shell for debugging
docker run --rm -it flowstate:1.0 shell
```

### 7. Volume Mounting for Output
```bash
# Save output to host directory
docker run --rm -it \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/input.mp4:/app/input.mp4:ro \
  flowstate:1.0 --skip-publish
```

## Important Notes

1. The image name is `flowstate:1.0`, not `flowstate-cli:latest`
2. When using `--serve`, make sure to expose port 8080 with `-p 8080:8080`
3. For host network access, add `--network host`
4. Always use `:ro` (read-only) when mounting input videos for security
5. The `analyze` command is optional (automatically removed if present)

## Troubleshooting

### Wrong Image Name Error
If you see: `Unable to find image 'flowstate-cli:latest'`
Solution: Use `flowstate:1.0` instead

### Port Already in Use
If port 8080 is taken:
```bash
docker run --rm -it -p 8888:8080 flowstate:1.0 --url VIDEO_URL --serve --serve-port 8080
```
Note: The internal port stays 8080, but it's mapped to 8888 on the host

### Input Video Not Found
Make sure to use absolute paths or `$(pwd)` for volume mounts:
```bash
# Good
docker run -v $(pwd)/input.mp4:/app/input.mp4:ro flowstate:1.0 analyze --serve

# Bad (relative path without $(pwd))
docker run -v ./input.mp4:/app/input.mp4:ro flowstate:1.0 analyze --serve
```