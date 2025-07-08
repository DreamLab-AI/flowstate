# FlowState Claude-Flow Swarm Guide

## Overview

This guide explains how to use Claude-Flow swarms to analyze, debug, upgrade, and document the FlowState project. We've created multiple swarm configurations for different purposes and scales.

## Available Swarm Configurations

### 1. **Comprehensive Analysis and Upgrade** (`flowstate-comprehensive-swarm.json`)
- **Duration**: ~20 hours
- **Workers**: 10 specialized agents
- **Purpose**: Complete project overhaul with security, performance, features, and documentation
- **Best for**: Major version releases or complete refactoring

### 2. **Quick Improvements** (`flowstate-quick-improvements-swarm.json`)
- **Duration**: ~2 hours
- **Workers**: 5 focused agents
- **Purpose**: High-impact improvements without major refactoring
- **Best for**: Sprint updates or quick fixes

### 3. **Debug and Analysis** (`flowstate-debug-analysis-swarm.json`)
- **Duration**: ~2 hours
- **Workers**: 5 analysis specialists
- **Purpose**: Deep debugging and issue identification
- **Best for**: Troubleshooting or pre-release validation

### 4. **Web Server Upgrade** (`flowstate-upgrade-swarm.json`)
- **Duration**: ~1 hour
- **Workers**: 5 implementation agents
- **Purpose**: Specific feature implementation
- **Best for**: Adding new features or modules

## Quick Start

### Interactive Mode (Recommended)
```bash
./claude-flow-orchestrator.sh
```

This opens an interactive menu where you can:
- Select specific swarms to run
- Run all swarms sequentially
- Create custom swarm configurations
- Check swarm execution status

### Command Line Mode
```bash
# Run comprehensive upgrade
./claude-flow-orchestrator.sh --comprehensive

# Run quick improvements
./claude-flow-orchestrator.sh --quick

# Run debug analysis
./claude-flow-orchestrator.sh --debug
```

### Direct Claude-Flow Usage
```bash
# Run a specific swarm
claude-flow hive-mind spawn "Upgrade FlowState" \
  --config flowstate-comprehensive-swarm.json \
  --verbose \
  --auto-scale \
  --claude
```

## Swarm Agent Roles

### Comprehensive Swarm Agents

1. **Security Auditor**
   - Scans for vulnerabilities
   - Reviews authentication flows
   - Validates input sanitization

2. **Code Quality Analyst**
   - Assesses code maintainability
   - Identifies technical debt
   - Suggests refactoring

3. **Performance Optimizer**
   - Profiles bottlenecks
   - Optimizes algorithms
   - Improves resource usage

4. **Architecture Reviewer**
   - Evaluates system design
   - Suggests structural improvements
   - Creates documentation

5. **Feature Engineer**
   - Implements new capabilities
   - Enhances existing features
   - Adds API endpoints

6. **Testing Specialist**
   - Creates test suites
   - Implements CI/CD
   - Validates coverage

7. **DevOps Engineer**
   - Optimizes deployment
   - Sets up monitoring
   - Creates infrastructure

8. **Documentation Expert**
   - Writes user guides
   - Creates API docs
   - Documents architecture

9. **UX Designer**
   - Improves interfaces
   - Enhances visualizations
   - Creates responsive designs

10. **ML Enhancer**
    - Optimizes pose detection
    - Improves algorithms
    - Adds new ML features

## Output Structure

All swarm executions create outputs in:
```
swarm-output/
├── flowstate-comprehensive-swarm/
│   └── 20240708_143022/
│       ├── swarm.log
│       ├── EXECUTION_SUMMARY.md
│       ├── security_audit_report.md
│       ├── performance_profile.html
│       ├── patches/
│       ├── docs/
│       └── ...
```

## Best Practices

### 1. **Pre-Swarm Checklist**
- [ ] Commit current changes
- [ ] Create a backup branch
- [ ] Ensure sufficient disk space
- [ ] Check system resources

### 2. **During Execution**
- Monitor swarm.log for progress
- Don't interrupt unless necessary
- Keep system resources available

### 3. **Post-Swarm Actions**
- Review all generated reports
- Test changes in isolation
- Apply patches incrementally
- Run validation tests

## Customizing Swarms

### Creating Custom Swarms

1. Use the orchestrator:
   ```bash
   ./claude-flow-orchestrator.sh
   # Select 'C' for custom swarm
   ```

2. Or create manually:
   ```json
   {
     "name": "Custom FlowState Swarm",
     "agents": [...],
     "phases": [...],
     "deliverables": [...]
   }
   ```

### Modifying Existing Swarms

1. Copy an existing configuration
2. Adjust agents, tasks, or phases
3. Update duration and resources
4. Test with dry-run first

## Troubleshooting

### Common Issues

1. **"claude-flow not found"**
   ```bash
   # Install claude-flow
   npm install -g claude-flow@alpha
   ```

2. **"Insufficient resources"**
   - Reduce max-workers
   - Run smaller swarms
   - Free up system memory

3. **"Swarm timeout"**
   - Check swarm.log
   - Increase timeout limits
   - Break into smaller swarms

### Debug Commands

```bash
# Check active swarms
ps aux | grep claude-flow

# Monitor resource usage
docker stats

# View recent logs
tail -f swarm-output/*/swarm.log
```

## Integration with Development Workflow

### 1. **Development Phase**
- Run quick improvements swarm
- Apply patches
- Test changes

### 2. **Pre-Release**
- Run debug analysis swarm
- Fix identified issues
- Generate reports

### 3. **Major Updates**
- Run comprehensive swarm
- Review all deliverables
- Plan implementation

### 4. **Documentation**
- Use documentation expert outputs
- Update README files
- Generate API docs

## Advanced Usage

### Parallel Swarm Execution
```bash
# Run multiple swarms in parallel
claude-flow hive-mind spawn "Quick Fixes" --config quick.json &
claude-flow hive-mind spawn "Documentation" --config docs.json &
wait
```

### Checkpoint and Resume
```bash
# Run with checkpoints
claude-flow hive-mind spawn "Large Upgrade" \
  --config comprehensive.json \
  --checkpoint-interval 1h \
  --resume-on-failure
```

### Resource Limits
```bash
# Limit resource usage
claude-flow hive-mind spawn "Analysis" \
  --config analysis.json \
  --max-workers 5 \
  --memory-limit 8G
```

## Results Interpretation

### Security Reports
- **Critical**: Fix immediately
- **High**: Fix before release
- **Medium**: Plan for next sprint
- **Low**: Track in backlog

### Performance Metrics
- **Green**: Optimal performance
- **Yellow**: Acceptable but improvable
- **Red**: Needs immediate attention

### Code Quality Scores
- **9-10**: Excellent, maintain standards
- **7-8**: Good, minor improvements needed
- **5-6**: Fair, refactoring recommended
- **<5**: Poor, major refactoring required

## Next Steps

1. Start with the debug analysis swarm to understand current state
2. Run quick improvements for immediate wins
3. Plan comprehensive upgrade for major release
4. Use custom swarms for specific needs

Remember: Swarms are powerful but review all changes before applying to production!