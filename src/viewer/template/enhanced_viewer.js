// Enhanced FlowState 3D Viewer
// Advanced visualization with motion trails, ground plane, and interactive controls

class FlowStateViewer {
    constructor() {
        // Three.js core components
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;
        this.stats = null;

        // Animation properties
        this.currentFrame = 0;
        this.frameRate = 30;
        this.playbackSpeed = 1.0;
        this.isPlaying = true;
        this.lastFrameTime = 0;

        // Data
        this.poseLandmarks = [];
        this.videoInfo = {};
        this.scores = {};

        // Visual elements
        this.skeletonLines = [];
        this.jointSpheres = [];
        this.motionTrails = [];
        this.groundPlane = null;

        // Settings
        this.settings = {
            showSkeleton: true,
            showJoints: true,
            showTrails: true,
            showGround: true,
            jointSize: 0.05,
            trailLength: 10
        };

        // MediaPipe pose connections
        this.skeletonConnections = [
            // Face
            [0, 1], [1, 2], [2, 3], [3, 7], [0, 4], [4, 5], [5, 6], [6, 8],
            [9, 10],
            // Torso
            [11, 12], [11, 23], [12, 24], [23, 24],
            // Arms
            [11, 13], [13, 15], [15, 17], [17, 19], [19, 15], [15, 21],
            [12, 14], [14, 16], [16, 18], [18, 20], [20, 16], [16, 22],
            // Legs
            [23, 25], [25, 27], [27, 29], [29, 31], [27, 31],
            [24, 26], [26, 28], [28, 30], [30, 32], [28, 32]
        ];

        // Colors for different body parts
        this.jointColors = {
            face: 0xff6b6b,
            torso: 0x4ecdc4,
            leftArm: 0x45b7d1,
            rightArm: 0x96ceb4,
            leftLeg: 0xf9ca24,
            rightLeg: 0xf0932b
        };
    }

    init() {
        this.setupScene();
        this.loadData();
        this.setupControls();
        this.animate();
        this.hideLoadingScreen();
    }

    setupScene() {
        // Scene
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x0a0a0a);
        this.scene.fog = new THREE.Fog(0x0a0a0a, 5, 50);

        // Camera
        const aspect = window.innerWidth / window.innerHeight;
        this.camera = new THREE.PerspectiveCamera(60, aspect, 0.1, 1000);
        this.camera.position.set(0, 1.5, 4);
        this.camera.lookAt(0, 1, 0);

        // Renderer
        this.renderer = new THREE.WebGLRenderer({ 
            antialias: true,
            alpha: true
        });
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.setPixelRatio(window.devicePixelRatio);
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        
        const container = document.getElementById('canvas-container');
        container.appendChild(this.renderer.domElement);

        // Controls
        this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.05;
        this.controls.screenSpacePanning = false;
        this.controls.minDistance = 1;
        this.controls.maxDistance = 20;
        this.controls.maxPolarAngle = Math.PI / 1.5;
        this.controls.target.set(0, 1, 0);

        // Lighting
        this.setupLighting();

        // Ground plane
        this.createGroundPlane();

        // Stats
        this.stats = new Stats();
        this.stats.showPanel(0); // FPS
        document.getElementById('stats').appendChild(this.stats.dom);

        // Handle window resize
        window.addEventListener('resize', () => this.onWindowResize(), false);
    }

    setupLighting() {
        // Ambient light
        const ambientLight = new THREE.AmbientLight(0x404040, 0.5);
        this.scene.add(ambientLight);

        // Directional light (sun)
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(5, 10, 5);
        directionalLight.castShadow = true;
        directionalLight.shadow.camera.near = 0.1;
        directionalLight.shadow.camera.far = 50;
        directionalLight.shadow.camera.left = -10;
        directionalLight.shadow.camera.right = 10;
        directionalLight.shadow.camera.top = 10;
        directionalLight.shadow.camera.bottom = -10;
        directionalLight.shadow.mapSize.width = 2048;
        directionalLight.shadow.mapSize.height = 2048;
        this.scene.add(directionalLight);

        // Rim light
        const rimLight = new THREE.DirectionalLight(0x64b5f6, 0.3);
        rimLight.position.set(-5, 5, -5);
        this.scene.add(rimLight);

        // Point lights for atmosphere
        const pointLight1 = new THREE.PointLight(0x4caf50, 0.3, 10);
        pointLight1.position.set(2, 3, 2);
        this.scene.add(pointLight1);

        const pointLight2 = new THREE.PointLight(0x64b5f6, 0.3, 10);
        pointLight2.position.set(-2, 3, -2);
        this.scene.add(pointLight2);
    }

    createGroundPlane() {
        const geometry = new THREE.PlaneGeometry(20, 20);
        const material = new THREE.MeshStandardMaterial({
            color: 0x1a1a1a,
            roughness: 0.8,
            metalness: 0.2
        });
        this.groundPlane = new THREE.Mesh(geometry, material);
        this.groundPlane.rotation.x = -Math.PI / 2;
        this.groundPlane.receiveShadow = true;
        this.scene.add(this.groundPlane);

        // Grid helper
        const gridHelper = new THREE.GridHelper(20, 20, 0x303030, 0x303030);
        this.scene.add(gridHelper);
    }

    loadData() {
        if (typeof flowStateData !== 'undefined') {
            this.poseLandmarks = flowStateData.poseData.pose_landmarks || [];
            this.videoInfo = flowStateData.videoInfo || {};
            this.scores = flowStateData.poseData.overall_scores || {};
            this.updateInfoPanel();
            
            // Update timeline
            document.getElementById('total-frames').textContent = this.poseLandmarks.length;
            
            // Draw first frame
            if (this.poseLandmarks.length > 0) {
                this.drawPose(this.poseLandmarks[0]);
            }
        } else {
            console.error("flowStateData not found!");
            alert("Analysis data could not be loaded.");
        }
    }

    updateInfoPanel() {
        document.getElementById('video-title').textContent = this.videoInfo.title || 'Unknown Video';
        document.getElementById('video-uploader').textContent = this.videoInfo.uploader || 'Unknown';
        document.getElementById('video-upload-date').textContent = this.videoInfo.uploadDate || '-';
        
        // Update scores with animation
        this.animateScore('flow-score', this.scores.flow);
        this.animateScore('balance-score', this.scores.balance);
        this.animateScore('smoothness-score', this.scores.smoothness);
        this.animateScore('energy-score', this.scores.energy);
        
        const videoLink = document.getElementById('video-link');
        if (this.videoInfo.webpageUrl) {
            videoLink.href = this.videoInfo.webpageUrl;
            videoLink.style.display = 'inline';
        } else {
            videoLink.style.display = 'none';
        }
    }

    animateScore(elementId, targetValue) {
        const element = document.getElementById(elementId);
        if (!element || !targetValue) {
            element.textContent = '-';
            return;
        }

        let currentValue = 0;
        const increment = targetValue / 30; // 30 frames
        const animate = () => {
            currentValue += increment;
            if (currentValue >= targetValue) {
                currentValue = targetValue;
                element.textContent = targetValue.toFixed(1) + '%';
            } else {
                element.textContent = currentValue.toFixed(1) + '%';
                requestAnimationFrame(animate);
            }
        };
        animate();
    }

    setupControls() {
        // Play/Pause button
        const playPauseBtn = document.getElementById('play-pause');
        playPauseBtn.addEventListener('click', () => {
            this.isPlaying = !this.isPlaying;
            playPauseBtn.textContent = this.isPlaying ? 'Pause' : 'Play';
        });

        // Reset view button
        document.getElementById('reset-view').addEventListener('click', () => {
            this.camera.position.set(0, 1.5, 4);
            this.controls.target.set(0, 1, 0);
            this.controls.update();
        });

        // Checkboxes
        document.getElementById('show-skeleton').addEventListener('change', (e) => {
            this.settings.showSkeleton = e.target.checked;
            this.updateVisibility();
        });

        document.getElementById('show-joints').addEventListener('change', (e) => {
            this.settings.showJoints = e.target.checked;
            this.updateVisibility();
        });

        document.getElementById('show-trails').addEventListener('change', (e) => {
            this.settings.showTrails = e.target.checked;
            this.updateVisibility();
        });

        document.getElementById('show-ground').addEventListener('change', (e) => {
            this.settings.showGround = e.target.checked;
            this.groundPlane.visible = e.target.checked;
        });

        // Sliders
        const speedSlider = document.getElementById('playback-speed');
        speedSlider.addEventListener('input', (e) => {
            this.playbackSpeed = parseFloat(e.target.value);
            document.getElementById('speed-value').textContent = this.playbackSpeed.toFixed(1) + 'x';
        });

        const jointSizeSlider = document.getElementById('joint-size');
        jointSizeSlider.addEventListener('input', (e) => {
            this.settings.jointSize = parseFloat(e.target.value);
            this.updateJointSizes();
        });

        const trailLengthSlider = document.getElementById('trail-length');
        trailLengthSlider.addEventListener('input', (e) => {
            this.settings.trailLength = parseInt(e.target.value);
        });

        // Timeline click
        const timeline = document.getElementById('timeline');
        timeline.addEventListener('click', (e) => {
            const rect = timeline.getBoundingClientRect();
            const progress = (e.clientX - rect.left) / rect.width;
            this.currentFrame = Math.floor(progress * this.poseLandmarks.length);
            this.updateTimeline();
        });
    }

    drawPose(landmarks) {
        if (!landmarks || landmarks.length === 0) return;

        // Clear previous pose
        this.clearPose();

        // Create joints
        if (this.settings.showJoints) {
            this.createJoints(landmarks);
        }

        // Create skeleton
        if (this.settings.showSkeleton) {
            this.createSkeleton(landmarks);
        }

        // Update motion trails
        if (this.settings.showTrails) {
            this.updateMotionTrails(landmarks);
        }
    }

    clearPose() {
        // Remove skeleton lines
        this.skeletonLines.forEach(line => {
            this.scene.remove(line);
            line.geometry.dispose();
            line.material.dispose();
        });
        this.skeletonLines = [];

        // Remove joint spheres
        this.jointSpheres.forEach(sphere => {
            this.scene.remove(sphere);
            sphere.geometry.dispose();
            sphere.material.dispose();
        });
        this.jointSpheres = [];
    }

    createJoints(landmarks) {
        landmarks.forEach((landmark, index) => {
            const geometry = new THREE.SphereGeometry(this.settings.jointSize, 16, 16);
            const color = this.getJointColor(index);
            const material = new THREE.MeshPhongMaterial({
                color: color,
                emissive: color,
                emissiveIntensity: 0.2,
                shininess: 100
            });
            
            const sphere = new THREE.Mesh(geometry, material);
            sphere.position.set(
                landmark.x * 2 - 1,
                -landmark.y * 2 + 2,
                landmark.z
            );
            sphere.castShadow = true;
            
            this.jointSpheres.push(sphere);
            this.scene.add(sphere);
        });
    }

    createSkeleton(landmarks) {
        this.skeletonConnections.forEach(connection => {
            const start = landmarks[connection[0]];
            const end = landmarks[connection[1]];

            if (start && end) {
                const material = new THREE.LineBasicMaterial({
                    color: 0x00ffff,
                    linewidth: 2,
                    opacity: 0.8,
                    transparent: true
                });

                const points = [
                    new THREE.Vector3(start.x * 2 - 1, -start.y * 2 + 2, start.z),
                    new THREE.Vector3(end.x * 2 - 1, -end.y * 2 + 2, end.z)
                ];

                const geometry = new THREE.BufferGeometry().setFromPoints(points);
                const line = new THREE.Line(geometry, material);
                
                this.skeletonLines.push(line);
                this.scene.add(line);
            }
        });
    }

    updateMotionTrails(landmarks) {
        // Add current position to trails
        if (this.motionTrails.length >= this.settings.trailLength) {
            const oldTrail = this.motionTrails.shift();
            oldTrail.forEach(trail => {
                this.scene.remove(trail);
                trail.geometry.dispose();
                trail.material.dispose();
            });
        }

        // Create trail for key joints (hands, feet, head)
        const keyJoints = [0, 15, 16, 27, 28]; // nose, left wrist, right wrist, left ankle, right ankle
        const trails = [];

        keyJoints.forEach(jointIndex => {
            if (landmarks[jointIndex]) {
                const geometry = new THREE.SphereGeometry(0.02, 8, 8);
                const material = new THREE.MeshBasicMaterial({
                    color: this.getJointColor(jointIndex),
                    opacity: 0.3,
                    transparent: true
                });

                const trail = new THREE.Mesh(geometry, material);
                trail.position.set(
                    landmarks[jointIndex].x * 2 - 1,
                    -landmarks[jointIndex].y * 2 + 2,
                    landmarks[jointIndex].z
                );

                trails.push(trail);
                this.scene.add(trail);
            }
        });

        this.motionTrails.push(trails);

        // Fade older trails
        this.motionTrails.forEach((trail, index) => {
            const opacity = (index + 1) / this.motionTrails.length * 0.3;
            trail.forEach(t => {
                t.material.opacity = opacity;
            });
        });
    }

    getJointColor(index) {
        if (index <= 10) return this.jointColors.face;
        if (index <= 12) return this.jointColors.torso;
        if (index === 13 || index === 15 || index === 17 || index === 19 || index === 21) 
            return this.jointColors.leftArm;
        if (index === 14 || index === 16 || index === 18 || index === 20 || index === 22) 
            return this.jointColors.rightArm;
        if (index === 23 || index === 25 || index === 27 || index === 29 || index === 31) 
            return this.jointColors.leftLeg;
        if (index === 24 || index === 26 || index === 28 || index === 30 || index === 32) 
            return this.jointColors.rightLeg;
        return 0xffffff;
    }

    updateVisibility() {
        this.jointSpheres.forEach(sphere => {
            sphere.visible = this.settings.showJoints;
        });

        this.skeletonLines.forEach(line => {
            line.visible = this.settings.showSkeleton;
        });

        this.motionTrails.forEach(trail => {
            trail.forEach(t => {
                t.visible = this.settings.showTrails;
            });
        });
    }

    updateJointSizes() {
        this.jointSpheres.forEach(sphere => {
            sphere.geometry.dispose();
            sphere.geometry = new THREE.SphereGeometry(this.settings.jointSize, 16, 16);
        });
    }

    updateTimeline() {
        const progress = (this.currentFrame / this.poseLandmarks.length) * 100;
        document.getElementById('timeline-progress').style.width = progress + '%';
        document.getElementById('current-frame').textContent = this.currentFrame;
    }

    animate(timestamp) {
        requestAnimationFrame((t) => this.animate(t));

        this.stats.begin();

        // Update controls
        this.controls.update();

        // Update animation
        if (this.isPlaying && this.poseLandmarks.length > 0) {
            const deltaTime = timestamp - this.lastFrameTime;
            const frameDuration = 1000 / (this.frameRate * this.playbackSpeed);

            if (deltaTime >= frameDuration) {
                this.currentFrame = (this.currentFrame + 1) % this.poseLandmarks.length;
                this.drawPose(this.poseLandmarks[this.currentFrame]);
                this.updateTimeline();
                this.lastFrameTime = timestamp;
            }
        }

        // Render
        this.renderer.render(this.scene, this.camera);

        this.stats.end();
    }

    onWindowResize() {
        this.camera.aspect = window.innerWidth / window.innerHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(window.innerWidth, window.innerHeight);
    }

    hideLoadingScreen() {
        const loadingScreen = document.getElementById('loading-screen');
        loadingScreen.style.opacity = '0';
        setTimeout(() => {
            loadingScreen.style.display = 'none';
        }, 500);
    }
}

// Initialize viewer when the page loads
window.addEventListener('DOMContentLoaded', () => {
    const viewer = new FlowStateViewer();
    viewer.init();
});