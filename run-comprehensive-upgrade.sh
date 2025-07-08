#!/bin/bash
# FlowState Comprehensive Upgrade Script
# Executes the claude-flow swarm for full project analysis and upgrade

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
SWARM_CONFIG="flowstate-comprehensive-swarm.json"
PROJECT_NAME="FlowState"
OUTPUT_DIR="upgrade-output"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Functions
print_header() {
    echo -e "\n${BLUE}════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}    $1${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Main execution
main() {
    print_header "$PROJECT_NAME Comprehensive Upgrade"
    
    # Check prerequisites
    echo "Checking prerequisites..."
    
    if ! command -v claude-flow &> /dev/null; then
        print_error "claude-flow not found. Please install claude-flow first."
        exit 1
    fi
    
    if [ ! -f "$SWARM_CONFIG" ]; then
        print_error "Swarm configuration file not found: $SWARM_CONFIG"
        exit 1
    fi
    
    print_success "Prerequisites checked"
    
    # Create output directory
    mkdir -p "$OUTPUT_DIR/$TIMESTAMP"
    print_success "Created output directory: $OUTPUT_DIR/$TIMESTAMP"
    
    # Initialize claude-flow if needed
    if [ ! -d ".claude" ]; then
        print_warning "Initializing claude-flow..."
        claude-flow init --sparc
    fi
    
    # Display swarm configuration summary
    print_header "Swarm Configuration Summary"
    echo "Configuration: $SWARM_CONFIG"
    echo "Workers: 10 specialized agents"
    echo "Phases: 8 comprehensive phases"
    echo "Estimated Duration: 20 hours"
    echo "Output Directory: $OUTPUT_DIR/$TIMESTAMP"
    
    # Confirm execution
    echo -e "\n${YELLOW}This will run a comprehensive analysis and upgrade of the FlowState project.${NC}"
    echo -e "${YELLOW}The swarm will:${NC}"
    echo "  - Perform security audit and fix vulnerabilities"
    echo "  - Analyze and improve code quality"
    echo "  - Optimize performance and scalability"
    echo "  - Implement new features and enhancements"
    echo "  - Create comprehensive documentation"
    echo "  - Set up CI/CD and deployment infrastructure"
    
    read -p $'\nDo you want to proceed? (y/N): ' -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "Operation cancelled"
        exit 0
    fi
    
    # Execute the swarm
    print_header "Launching Claude-Flow Swarm"
    
    # Set environment variables for the swarm
    export FLOWSTATE_UPGRADE_OUTPUT="$OUTPUT_DIR/$TIMESTAMP"
    export FLOWSTATE_PROJECT_ROOT="$(pwd)"
    
    # Launch with appropriate options
    if claude-flow hive-mind spawn \
        "Execute comprehensive FlowState analysis, debugging, upgrade, and documentation" \
        --config "$SWARM_CONFIG" \
        --output-dir "$OUTPUT_DIR/$TIMESTAMP" \
        --verbose \
        --auto-scale \
        --checkpoint-interval 30m \
        --max-workers 10 \
        --claude; then
        
        print_success "Swarm execution completed successfully!"
        
        # Generate summary report
        print_header "Generating Summary Report"
        
        cat > "$OUTPUT_DIR/$TIMESTAMP/UPGRADE_SUMMARY.md" << EOF
# FlowState Comprehensive Upgrade Summary

**Date**: $(date)
**Duration**: Check swarm logs for actual duration

## Completed Phases

1. ✓ Analysis and Audit
2. ✓ Performance and Testing Assessment
3. ✓ Design and Planning
4. ✓ Implementation Sprint 1 - Core Improvements
5. ✓ Implementation Sprint 2 - Features and Infrastructure
6. ✓ Implementation Sprint 3 - UI and ML
7. ✓ Documentation and Finalization
8. ✓ Integration and Testing

## Key Deliverables

- Security audit report and fixes
- Performance optimization patches
- New feature implementations
- Comprehensive test suite
- CI/CD pipeline configuration
- Kubernetes deployment manifests
- Complete documentation set
- API specifications

## Next Steps

1. Review all generated reports in: $OUTPUT_DIR/$TIMESTAMP
2. Apply patches and implementations to the main codebase
3. Run the comprehensive test suite
4. Deploy to staging environment
5. Perform user acceptance testing
6. Deploy to production

## Files Generated

Check the output directory for all generated files and reports.
EOF
        
        print_success "Summary report generated"
        
        # Display results location
        print_header "Upgrade Complete!"
        echo "All output files are available in:"
        echo "  $OUTPUT_DIR/$TIMESTAMP/"
        echo
        echo "Key files to review:"
        echo "  - security_audit_report.md"
        echo "  - performance_profile.md"
        echo "  - feature_specifications.md"
        echo "  - DEPLOYMENT_GUIDE.md"
        echo "  - api_specification.yaml"
        
    else
        print_error "Swarm execution failed. Check logs for details."
        exit 1
    fi
}

# Handle script interruption
trap 'print_error "Script interrupted"; exit 1' INT TERM

# Run main function
main "$@"