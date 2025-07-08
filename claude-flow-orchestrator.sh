#!/bin/bash
# Claude-Flow Orchestrator for FlowState Project
# Master script to run different swarm configurations

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
SWARM_CONFIGS=(
    "flowstate-comprehensive-swarm.json:Comprehensive Analysis and Upgrade (20h)"
    "flowstate-quick-improvements-swarm.json:Quick Improvements (2h)"
    "flowstate-debug-analysis-swarm.json:Debug and Analysis (2h)"
    "flowstate-upgrade-swarm.json:Web Server Upgrade (1h)"
)

# Functions
print_banner() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║          FlowState Claude-Flow Orchestrator              ║"
    echo "║                                                          ║"
    echo "║  Automated AI-Powered Project Analysis and Enhancement   ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo -e "${NC}\n"
}

print_menu() {
    echo -e "${BLUE}Available Swarm Configurations:${NC}\n"
    
    local i=1
    for config in "${SWARM_CONFIGS[@]}"; do
        IFS=':' read -r file desc <<< "$config"
        if [ -f "$file" ]; then
            echo -e "  ${GREEN}[$i]${NC} $desc"
            echo -e "      ${YELLOW}Config: $file${NC}"
        else
            echo -e "  ${RED}[$i]${NC} $desc ${RED}(FILE NOT FOUND)${NC}"
        fi
        echo
        ((i++))
    done
    
    echo -e "  ${GREEN}[A]${NC} Run ALL swarms sequentially"
    echo -e "  ${GREEN}[C]${NC} Create custom swarm configuration"
    echo -e "  ${GREEN}[S]${NC} Show swarm status"
    echo -e "  ${GREEN}[Q]${NC} Quit"
    echo
}

create_custom_swarm() {
    echo -e "${BLUE}Creating Custom Swarm Configuration${NC}\n"
    
    read -p "Enter swarm name: " swarm_name
    read -p "Enter description: " swarm_desc
    read -p "Enter estimated duration (e.g., 2h): " duration
    read -p "Enter primary objective: " objective
    
    # Create basic custom swarm template
    cat > "custom-${swarm_name// /-}-swarm.json" << EOF
{
  "name": "$swarm_name",
  "description": "$swarm_desc",
  "version": "1.0.0",
  "objective": "$objective",
  "duration": "$duration",
  "agents": [
    {
      "id": "analyzer",
      "name": "Code Analyzer",
      "role": "Analyze codebase",
      "tasks": ["Analyze code structure", "Identify improvements"]
    },
    {
      "id": "implementer",
      "name": "Implementation Agent",
      "role": "Implement improvements",
      "tasks": ["Apply fixes", "Add features"]
    }
  ],
  "phases": [
    {
      "name": "Analysis",
      "duration": "30m",
      "agents": ["analyzer"]
    },
    {
      "name": "Implementation",
      "duration": "1h",
      "agents": ["implementer"]
    }
  ]
}
EOF
    
    echo -e "\n${GREEN}✓ Custom swarm configuration created: custom-${swarm_name// /-}-swarm.json${NC}"
    echo -e "${YELLOW}Edit this file to add more agents and tasks${NC}"
}

run_swarm() {
    local config_file=$1
    local config_name=$2
    
    echo -e "\n${BLUE}══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}Running: $config_name${NC}"
    echo -e "${BLUE}══════════════════════════════════════════════════════════${NC}\n"
    
    # Check if claude-flow is available
    if ! command -v claude-flow &> /dev/null; then
        echo -e "${RED}Error: claude-flow not found in PATH${NC}"
        echo -e "${YELLOW}Please ensure claude-flow is installed and accessible${NC}"
        return 1
    fi
    
    # Create output directory
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local output_dir="swarm-output/${config_file%.json}/$timestamp"
    mkdir -p "$output_dir"
    
    echo -e "${YELLOW}Output directory: $output_dir${NC}"
    echo -e "${YELLOW}Starting swarm...${NC}\n"
    
    # Run the swarm
    if claude-flow hive-mind spawn \
        "Execute $config_name for FlowState project" \
        --config "$config_file" \
        --output-dir "$output_dir" \
        --verbose \
        --auto-scale \
        --claude \
        2>&1 | tee "$output_dir/swarm.log"; then
        
        echo -e "\n${GREEN}✓ Swarm completed successfully!${NC}"
        echo -e "${GREEN}Results saved to: $output_dir${NC}"
        
        # Generate summary
        generate_summary "$output_dir" "$config_name"
        
        return 0
    else
        echo -e "\n${RED}✗ Swarm execution failed${NC}"
        echo -e "${YELLOW}Check logs at: $output_dir/swarm.log${NC}"
        return 1
    fi
}

generate_summary() {
    local output_dir=$1
    local config_name=$2
    
    cat > "$output_dir/EXECUTION_SUMMARY.md" << EOF
# Swarm Execution Summary

**Configuration**: $config_name
**Date**: $(date)
**Output Directory**: $output_dir

## Execution Status
- Start Time: $(date)
- Status: Completed
- Log File: swarm.log

## Generated Files
$(ls -la "$output_dir" 2>/dev/null | grep -v "^total" | grep -v "EXECUTION_SUMMARY" || echo "No files generated yet")

## Next Steps
1. Review the generated files
2. Apply recommended changes
3. Run tests to validate improvements
4. Deploy updated version

## Notes
- Check swarm.log for detailed execution information
- Review any error messages or warnings
- Validate all changes before applying to production
EOF
}

show_status() {
    echo -e "${BLUE}Swarm Execution Status${NC}\n"
    
    if [ -d "swarm-output" ]; then
        echo -e "${GREEN}Recent Executions:${NC}"
        find swarm-output -name "EXECUTION_SUMMARY.md" -type f -exec dirname {} \; | sort -r | head -10 | while read dir; do
            echo -e "\n${YELLOW}$(basename $(dirname $dir))${NC} - $(basename $dir)"
            grep -E "^(\*\*Date\*\*:|Status:)" "$dir/EXECUTION_SUMMARY.md" 2>/dev/null || true
        done
    else
        echo -e "${YELLOW}No swarm executions found${NC}"
    fi
    
    # Check if any swarms are currently running
    echo -e "\n${GREEN}Active Swarms:${NC}"
    if pgrep -f "claude-flow.*hive-mind" > /dev/null; then
        ps aux | grep "claude-flow.*hive-mind" | grep -v grep
    else
        echo "No active swarms running"
    fi
}

# Main execution
main() {
    print_banner
    
    while true; do
        print_menu
        
        read -p "Select option: " choice
        
        case $choice in
            [1-9])
                # Run specific swarm
                index=$((choice-1))
                if [ $index -lt ${#SWARM_CONFIGS[@]} ]; then
                    IFS=':' read -r file desc <<< "${SWARM_CONFIGS[$index]}"
                    if [ -f "$file" ]; then
                        run_swarm "$file" "$desc"
                    else
                        echo -e "${RED}Error: Configuration file not found: $file${NC}"
                    fi
                else
                    echo -e "${RED}Invalid selection${NC}"
                fi
                ;;
            [Aa])
                # Run all swarms
                echo -e "${YELLOW}Running all swarms sequentially...${NC}"
                for config in "${SWARM_CONFIGS[@]}"; do
                    IFS=':' read -r file desc <<< "$config"
                    if [ -f "$file" ]; then
                        run_swarm "$file" "$desc"
                        echo -e "\n${CYAN}Pausing for 30 seconds before next swarm...${NC}"
                        sleep 30
                    fi
                done
                ;;
            [Cc])
                create_custom_swarm
                ;;
            [Ss])
                show_status
                ;;
            [Qq])
                echo -e "${GREEN}Exiting...${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}Invalid option${NC}"
                ;;
        esac
        
        echo -e "\n${CYAN}Press Enter to continue...${NC}"
        read
        clear
    done
}

# Handle interrupts
trap 'echo -e "\n${RED}Interrupted${NC}"; exit 1' INT TERM

# Check if running with arguments
if [ $# -gt 0 ]; then
    # Direct execution mode
    case "$1" in
        --comprehensive)
            run_swarm "flowstate-comprehensive-swarm.json" "Comprehensive Analysis and Upgrade"
            ;;
        --quick)
            run_swarm "flowstate-quick-improvements-swarm.json" "Quick Improvements"
            ;;
        --debug)
            run_swarm "flowstate-debug-analysis-swarm.json" "Debug and Analysis"
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --comprehensive  Run comprehensive analysis and upgrade"
            echo "  --quick         Run quick improvements"
            echo "  --debug         Run debug and analysis"
            echo "  --help          Show this help message"
            echo ""
            echo "Without options, interactive menu will be shown"
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
else
    # Interactive mode
    main
fi