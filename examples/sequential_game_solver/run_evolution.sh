#!/bin/bash
# Convenience script to run sequential game solver evolution

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Sequential Game Solver Evolution${NC}"
echo "=================================="
echo

# Check if API key is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "Warning: OPENAI_API_KEY environment variable is not set"
    echo "Please set it before running evolution:"
    echo "  export OPENAI_API_KEY='your-key-here'"
    echo
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
OPENEVOLVE_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"

echo -e "${GREEN}[1/3] Testing initial program...${NC}"
cd "$SCRIPT_DIR"
python initial_program.py > /dev/null 2>&1 && echo "  ✓ Initial program works" || echo "  ✗ Initial program failed"

echo
echo -e "${GREEN}[2/3] Running evaluator test...${NC}"
python evaluator.py initial_program.py

echo
echo -e "${GREEN}[3/3] Starting evolution...${NC}"
cd "$OPENEVOLVE_ROOT"

# Default to 50 iterations, but allow override
ITERATIONS=${1:-50}

python openevolve-run.py \
  "$SCRIPT_DIR/initial_program.py" \
  "$SCRIPT_DIR/evaluator.py" \
  --config "$SCRIPT_DIR/config.yaml" \
  --iterations "$ITERATIONS"

echo
echo -e "${BLUE}Evolution complete!${NC}"
echo "Check results in: $SCRIPT_DIR/openevolve_output/"
echo
echo "To visualize results:"
echo "  python scripts/visualizer.py --path $SCRIPT_DIR/openevolve_output/checkpoints/checkpoint_$ITERATIONS/"
