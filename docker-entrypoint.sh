#!/bin/bash
# FlowState Docker Entrypoint Script
# Handles initialization and runtime configuration

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Initialize directories
init_directories() {
    log_info "Initializing directories..."
    
    # Create required directories if they don't exist
    mkdir -p "${FLOWSTATE_OUTPUT_DIR:-/app/output}"
    mkdir -p "${FLOWSTATE_LOG_DIR:-/app/logs}"
    mkdir -p "${FLOWSTATE_TEMP_DIR:-/tmp/flowstate}"
    mkdir -p "${FLOWSTATE_CACHE_DIR:-/tmp/flowstate/cache}"
    
    # Ensure proper permissions
    if [ -w "${FLOWSTATE_OUTPUT_DIR}" ]; then
        log_info "Output directory is writable"
    else
        log_error "Output directory is not writable: ${FLOWSTATE_OUTPUT_DIR}"
        exit 1
    fi
}

# Validate environment
validate_environment() {
    log_info "Validating environment..."
    
    # Check Python
    if ! python --version &> /dev/null; then
        log_error "Python is not available"
        exit 1
    fi
    
    # Check ffmpeg
    if ! ffmpeg -version &> /dev/null; then
        log_error "FFmpeg is not available"
        exit 1
    fi
    
    # Test imports
    if ! python -c "import mediapipe, cv2, numpy" &> /dev/null; then
        log_error "Required Python packages are not available"
        exit 1
    fi
    
    # Check flowstate command
    if ! command -v flowstate &> /dev/null; then
        log_error "flowstate command not found"
        exit 1
    fi
    
    log_info "Environment validation passed"
}

# Handle special commands
handle_special_commands() {
    case "$1" in
        "test"|"validate")
            log_info "Running validation tests..."
            python -m pytest /app/tests/ -v
            exit $?
            ;;
        "shell"|"bash")
            log_info "Starting interactive shell..."
            exec /bin/bash
            ;;
        "dev-server")
            log_info "Starting development viewer server..."
            cd "${FLOWSTATE_OUTPUT_DIR}/viewer" || exit 1
            exec python /app/viewer/dev_server.py --port 8080
            ;;
    esac
}

# Performance tuning
tune_performance() {
    log_info "Applying performance optimizations..."
    
    # Set OpenMP threads if not already set
    if [ -z "$OMP_NUM_THREADS" ]; then
        CORES=$(nproc --all)
        export OMP_NUM_THREADS=$((CORES > 4 ? 4 : CORES))
        log_info "Set OMP_NUM_THREADS to $OMP_NUM_THREADS"
    fi
    
    # Enable OpenCV optimizations
    export OPENCV_OPENCL_RUNTIME=1
    export OPENCV_OPENCL_DEVICE=disabled  # CPU-only for consistency
}

# Main execution
main() {
    log_info "FlowState Docker Container Starting..."
    log_info "Version: $(flowstate --version 2>/dev/null || echo 'unknown')"
    
    # Initialize
    init_directories
    validate_environment
    tune_performance
    
    # Handle special commands
    handle_special_commands "$1"
    
    # Check if no arguments provided
    if [ $# -eq 0 ]; then
        log_warn "No command provided. Showing help..."
        exec flowstate --help
    fi
    
    # Log the command being executed
    log_info "Executing: flowstate $*"
    
    # Execute flowstate with all arguments
    exec flowstate "$@"
}

# Run main function with all arguments
main "$@"