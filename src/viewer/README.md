# FlowState 3D Viewer

Interactive 3D visualization for pose analysis results from FlowState.

## Features

- **Real-time 3D Visualization**: View pose data in an interactive 3D environment
- **Motion Trails**: Track movement patterns over time
- **Performance Metrics**: Display flow, balance, smoothness, and energy scores
- **Playback Controls**: Adjust speed, pause, and navigate through frames
- **Enhanced Graphics**: Shadows, lighting, and ground plane for better depth perception

## Directory Structure

```
viewer/
├── README.md          # This file
├── builder.py         # Python module for generating viewer output
├── dev_server.py      # Development server for local testing
└── template/          # Viewer template files
    ├── index.html     # Basic viewer
    ├── enhanced_viewer.html  # Advanced viewer with controls
    └── enhanced_viewer.js    # Enhanced viewer JavaScript
```

## Development Server

The development server allows you to test the viewer locally before deployment.

### Starting the Server

```bash
# From the viewer directory
python dev_server.py

# Or specify a custom port
python dev_server.py --port 3000

# Serve a specific directory
python dev_server.py --directory ../output/viewer
```

### Features

- Automatic sample data generation if no data.js exists
- CORS support for local development
- Live reload by refreshing the browser
- Detailed logging of requests

## Using with Docker

### Development Mode

```bash
# Start both FlowState and viewer services
docker-compose --profile dev up

# Access viewer at http://localhost:8080
```

### Production Mode

```bash
# Build and run FlowState only
docker-compose up flowstate
```

## Viewer Types

### 1. Basic Viewer (`index.html`)
- Simple 3D skeleton visualization
- Automatic animation playback
- Basic information panel

### 2. Enhanced Viewer (`enhanced_viewer.html`)
- Advanced controls and settings
- Motion trails visualization
- Performance statistics
- Timeline scrubbing
- Adjustable visual parameters

## Data Format

The viewer expects a `data.js` file with the following structure:

```javascript
const flowStateData = {
  poseData: {
    pose_landmarks: [
      // Array of frames
      [
        // Array of 33 MediaPipe landmarks per frame
        { x: 0.5, y: 0.5, z: 0.0, visibility: 0.9 },
        // ... more landmarks
      ]
    ],
    overall_scores: {
      flow: 85.5,
      balance: 78.2,
      smoothness: 92.1,
      energy: 71.3
    }
  },
  videoInfo: {
    title: "Dance Video",
    uploader: "Creator Name",
    uploadDate: "2024-01-15",
    thumbnail: "url_to_thumbnail",
    webpageUrl: "https://youtube.com/..."
  },
  settings: {
    quality: "high",
    theme: "dark",
    enableParticles: true,
    enableShadows: true
  }
};
```

## Customization

### Modifying Colors

Edit the color schemes in the JavaScript files:

```javascript
// Joint colors by body part
this.jointColors = {
    face: 0xff6b6b,
    torso: 0x4ecdc4,
    leftArm: 0x45b7d1,
    rightArm: 0x96ceb4,
    leftLeg: 0xf9ca24,
    rightLeg: 0xf0932b
};
```

### Adding New Features

1. Modify the HTML to add UI controls
2. Update the JavaScript to handle new functionality
3. Test using the development server

## Deployment

### GitHub Pages

1. The viewer is automatically generated in the output directory
2. Commit and push to your GitHub repository
3. Enable GitHub Pages for the output branch

### Static Hosting

The viewer is completely static and can be hosted on any web server:
- Netlify
- Vercel
- AWS S3
- Nginx
- Apache

## Troubleshooting

### Viewer Not Loading
- Check browser console for errors
- Ensure `data.js` file exists and is valid
- Verify all CDN resources are accessible

### Performance Issues
- Reduce trail length in settings
- Disable shadows for better performance
- Lower the playback speed

### CORS Errors
- Use the development server for local testing
- Ensure proper CORS headers on production server

## Future Enhancements

- [ ] Multiple dancer support
- [ ] Export animations to video
- [ ] VR/AR viewing modes
- [ ] Real-time streaming support
- [ ] Performance comparison tools
- [ ] Social sharing features