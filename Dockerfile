# Multi-stage Dockerfile for FlowState-CLI
# Optimized for size and build speed with OpenPose and GPU support

# Stage 1: Python dependencies builder
FROM nvidia/cuda:12.2-devel-ubuntu22.04 AS python-builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    python3 \
    python3-pip \
    python3-dev \
    cmake \
    libopencv-dev \
    libprotobuf-dev \
    protobuf-compiler \
    libgoogle-glog-dev \
    libgflags-dev \
    libhdf5-dev \
    libatlas-base-dev \
    libeigen3-dev \
    && rm -rf /var/lib/apt/lists/*

# Add user bin to PATH
ENV PATH="/root/.local/bin:${PATH}"

# Copy requirements and install Python packages
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Final runtime image
FROM nvidia/cuda:12.2-runtime-ubuntu22.04

# Install runtime dependencies including OpenPose requirements
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-dev \
    ffmpeg \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgirepository-1.0-1 \
    libopencv-dev \
    libprotobuf23 \
    libgoogle-glog0v5 \
    libgflags2.2 \
    libhdf5-103 \
    libatlas-base-dev \
    libeigen3-dev \
    wget \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 flowstate

# Copy Python packages from builder
COPY --from=python-builder /root/.local /home/flowstate/.local

# Copy application code
WORKDIR /app
COPY src/ ./src/
COPY src/viewer/ ./src/viewer/
COPY pyproject.toml .

# Set ownership of both /app and /home/flowstate/.local
RUN chown -R flowstate:flowstate /app /home/flowstate/.local

# Switch to non-root user
USER flowstate

# Install the CLI in editable mode to make 'flowstate' command available
RUN pip install --user -e .

# Update PATH
ENV PATH=/home/flowstate/.local/bin:$PATH
ENV PYTHONPATH=/app:$PYTHONPATH

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV FLOWSTATE_TEMP_DIR=/tmp/flowstate
ENV FLOWSTATE_OUTPUT_DIR=/app/output
ENV FLOWSTATE_LOG_DIR=/app/logs
ENV FLOWSTATE_CACHE_DIR=/tmp/flowstate/cache
ENV OPENCV_VIDEOIO_PRIORITY_FFMPEG=1

# Create necessary directories
RUN mkdir -p /tmp/flowstate /app/output /app/logs

# Health check - verify all critical components
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python3 -c "import cv2, numpy; import src.core.analyzer; print('OK')" || exit 1

# Copy entrypoint script
COPY --chown=flowstate:flowstate docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Entry point
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]

# Default command (can be overridden)
CMD ["--help"]