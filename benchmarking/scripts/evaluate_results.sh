#!/usr/bin/env bash
# Evaluation Results Comparison Script
# Compares results from all models and generates comparison tables

set -e  # Exit on error

echo "========================================="
echo "Benchmark Results Evaluation"
echo "========================================="

# Activate virtual environment
if [ -d "env" ]; then
    source env/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Create results directory
mkdir -p results

# Default dataset
DATASET=${1:-cora}

echo ""
echo "-----------------------------------------"
echo "Evaluating results for dataset: $DATASET"
echo "-----------------------------------------"

# Check if results exist
CLE_NET_RESULT="results/cle_net/${DATASET}_eval.json"
TRIAD_RESULT="results/dynamic_triad/${DATASET}_embeddings.json"
VGRNN_RESULT="results/vgrnn/${DATASET}_embeddings.json"

# Build command based on available results
CMD="python benchmarking/evaluate.py --dataset $DATASET --output results/${DATASET}_comparison.csv"

if [ -f "$CLE_NET_RESULT" ]; then
    CMD="$CMD --cle-net $CLE_NET_RESULT"
fi

if [ -f "$TRIAD_RESULT" ]; then
    CMD="$CMD --triad $TRIAD_RESULT"
fi

if [ -f "$VGRNN_RESULT" ]; then
    CMD="$CMD --vgrnn $VGRNN_RESULT"
fi

# Run evaluation
echo ""
echo "Running comparison evaluation..."
eval $CMD

echo ""
echo "========================================="
echo "Evaluation complete!"
echo "Results saved in results/${DATASET}_comparison.csv"
echo "========================================="

# Display summary if csv is generated
if [ -f "results/${DATASET}_comparison.csv" ]; then
    echo ""
    echo "Comparison Summary:"
    cat results/${DATASET}_comparison.csv
fi
