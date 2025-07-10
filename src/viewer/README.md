# FlowState 3D Viewer (v2.0)

Interactive 3D visualization for pose analysis results from FlowState, now powered by a high-fidelity, OpenPose-compatible data structure.

## Features

- **Real-time 3D Visualization**: View pose data in an interactive 3D environment.
- **Full Body Rendering**: Displays keypoints for the **body, hands, and face**.
- **Motion Trails**: Track movement patterns over time.
- **Performance Metrics**: Display flow, balance, smoothness, and energy scores.
- **Playback Controls**: Adjust speed, pause, and navigate through frames.
- **Enhanced Graphics**: Shadows, lighting, and ground plane for better depth perception.

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

## Data Format (v2.0)

The viewer expects a `data.js` file with the following **new** structure, which separates body, hand, and face keypoints.

```javascript
const flowStateData = {
  poseData: {
    // Array of pose frames, now with a more detailed structure
    pose_frames: [
      {
        timestamp: 0.033,
        frame_idx: 1,
        body_keypoints: [ // 17 COCO keypoints
          { x: 0.5, y: 0.5, confidence: 0.9, z: 0.0 },
          // ... 16 more keypoints
        ],
        hand_keypoints_left: [ // 21 hand keypoints
          { x: 0.4, y: 0.6, confidence: 0.8, z: 0.0 },
          // ... 20 more keypoints
        ],
        hand_keypoints_right: [ // 21 hand keypoints
          { x: 0.6, y: 0.6, confidence: 0.8, z: 0.0 },
          // ... 20 more keypoints
        ],
        face_keypoints: [ // 5 basic face keypoints
          { x: 0.5, y: 0.4, confidence: 0.95, z: 0.0 },
          // ... 4 more keypoints
        ]
      }
      // ... more frames
    ],
    // Stick figure data for drawing connections
    stick_figure_data: {
      frames: [
        {
          timestamp: 0.033,
          frame_idx: 1,
          body_connections: [
            { from: {x, y}, to: {x, y}, confidence: 0.85 }
          ],
          // ... connections for hands
        }
      ],
      keypoint_names: {
        body: ["nose", "left_eye", ...],
        hand: ["wrist", "thumb_cmc", ...]
      },
      connections: {
        body: [[0, 1], [0, 2], ...],
        hand: [[0, 1], [1, 2], ...]
      }
    },
    overall_scores: {
      flow: 85.5,
      balance: 78.2,
      smoothness: 92.1,
      energy: 71.3,
      hand_activity: 65.0,
      posture_stability: 88.0
    },
    features: {
        full_body_detection: true,
        hand_detection: true,
        face_detection: true,
        motion_interpolation: true,
        temporal_smoothing: true
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

Edit the color schemes in the JavaScript files. The viewer logic can now assign different colors to body, hands, and face.

```javascript
// Joint colors by body part
this.jointColors = {
    face: 0xff6b6b,
    torso: 0x4ecdc4,
    leftArm: 0x45b7d1,
    rightArm: 0x96ceb4,
    leftLeg: 0xf9ca24,
    rightLeg: 0xf0932b,
    hands: 0xffa502 // Orange for hands
};
```

## Troubleshooting

### Viewer Not Loading
- Check the browser console for errors.
- Ensure `data.js` exists and conforms to the new v2.0 format.
- Verify all CDN resources are accessible.

### Performance Issues
- Reduce trail length in settings.
- Disable shadows for better performance.
- The new high-granularity data can be demanding; ensure your browser is up-to-date.

## Future Enhancements

- [ ] Multiple person support.
- [ ] Advanced facial expression analysis.
- [ ] Fine-grained finger movement visualization.
- [ ] VR/AR viewing modes.