# Multi-stage Dockerfile for FlowState-CLI
# Optimized for size and build speed

# Stage 1: Python dependencies builder
FROM tensorflow/tensorflow:latest-gpu AS python-builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Add user bin to PATH
ENV PATH="/root/.local/bin:${PATH}"

# Copy requirements and install Python packages
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Final runtime image
FROM tensorflow/tensorflow:latest-gpu

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgirepository-1.0-1 \
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
    CMD python -c "import mediapipe, cv2, numpy; import src.core.pose_analyzer; print('OK')" || exit 1

# Copy entrypoint script
COPY --chown=flowstate:flowstate docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Entry point
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]

# Default command (can be overridden)
CMD ["--help"]