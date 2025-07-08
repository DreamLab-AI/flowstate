# FlowState Web Server Upgrade

## Overview

This upgrade adds a fallback web server to the FlowState project that ensures visualizations remain accessible even when GitHub Pages deployment fails. The server runs on the host network, making the visualization accessible from any device on the same network.

## Key Features Added

### 0. **Local Video Support (input.mp4)**
- Automatic detection of `input.mp4` when no URL provided
- Proper Docker volume mapping for local files
- Enhanced metadata extraction for local videos
- Seamless integration with existing workflow

### 1. **Production Web Server Module** (`src/core/server.py`)
- Robust HTTP server with CORS support
- Binds to all interfaces (0.0.0.0) for network accessibility
- Proper error handling and logging
- Thread-safe concurrent request handling
- Graceful shutdown support

### 2. **Docker Integration**
- New `web-server` service in docker-compose.yml
- Host network mode for direct network access
- Production profile for easy deployment
- Auto-restart policy for reliability

### 3. **CLI Enhancements**
- `--serve` flag to start web server directly
- `--serve-port` option to customize port (default: 8080)
- Automatic fallback when GitHub Pages fails
- Interactive prompts for better UX

### 4. **Docker Entrypoint Updates**
- New `server` and `serve` commands
- Seamless integration with existing workflow

## Usage Examples

### 1. Direct Web Server Mode
```bash
# Analyze video and host locally instead of GitHub Pages
flowstate analyze "https://youtube.com/watch?v=VIDEO_ID" --serve

# Custom port
flowstate analyze "https://youtube.com/watch?v=VIDEO_ID" --serve --serve-port 3000

# Analyze local input.mp4 file and serve
flowstate analyze --serve  # Will use input.mp4 if present
```

### 2. Docker Compose Production Mode
```bash
# Start the web server container
docker-compose --profile production up web-server

# The visualization will be available at:
# - http://localhost:8080 (from the host)
# - http://<host-ip>:8080 (from the network)
```

### 3. Docker Direct Server Mode
```bash
# Run container in server mode
docker run -p 8080:8080 --network host flowstate:1.0 server
```

### 4. Fallback Scenario
When GitHub Pages deployment fails, the CLI will automatically prompt:
```
GitHub Pages deployment failed.
Would you like to start a local web server instead? [Y/n]:
```

## Architecture Changes

### Workflow Enhancement
```
Original: Analyze → Generate Viewer → Publish to GitHub Pages
Updated:  Analyze → Generate Viewer → Publish to GitHub Pages
                                    ↓ (if fails)
                                    → Start Local Web Server
```

### Network Configuration
- The web server binds to `0.0.0.0:8080` by default
- Host network mode ensures accessibility from other devices
- CORS headers allow cross-origin requests

## Testing

Run the included test suite:
```bash
python test_web_server.py
```

Tests cover:
- Server startup and shutdown
- Host network binding
- CORS configuration
- Concurrent request handling
- Docker integration
- CLI integration

## Security Considerations

1. The web server is read-only (serves static files only)
2. No authentication required (suitable for local network use)
3. CORS is permissive (`*`) for ease of use
4. Runs as non-root user in Docker

## Troubleshooting

### Port Already in Use
If port 8080 is taken, use a different port:
```bash
flowstate analyze VIDEO_URL --serve --serve-port 8888
```

### Cannot Access from Network
Ensure your firewall allows incoming connections on the chosen port.

### Docker Host Network Issues
On some systems, use bridge network with port mapping:
```bash
docker run -p 8080:8080 flowstate:1.0 server
```

## Benefits

1. **Reliability**: Visualizations remain accessible even without GitHub
2. **Speed**: No internet required after analysis
3. **Privacy**: Keep analyses on your local network
4. **Flexibility**: Choose between cloud and local hosting
5. **Fallback**: Automatic failover when GitHub is unavailable

This upgrade ensures FlowState visualizations are always accessible, providing a seamless experience regardless of external service availability.