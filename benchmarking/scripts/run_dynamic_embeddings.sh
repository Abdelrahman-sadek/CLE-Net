#!/usr/bin/env bash
# DynamicTriad Benchmarking Script
# Runs DynamicTriad on temporal graph datasets

set -e  # Exit on error

echo "========================================="
echo "DynamicTriad Baseline Benchmarking"
echo "========================================="

# Activate virtual environment
if [ -d "env" ]; then
    source env/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "No virtual environment found. Creating one..."
    python -m venv env
    source env/bin/activate
    pip install --upgrade pip
    pip install torch torch-geometric numpy scipy scikit-learn tqdm
fi

# Set random seed
SEED=${SEED:-42}
export PYTHONHASHSEED=$SEED

# Create results directory
mkdir -p results/dynamic_triad

# Function to run DynamicTriad on a dataset
run_dynamic_triad() {
    local dataset=$1
    echo ""
    echo "-----------------------------------------"
    echo "Processing dataset: $dataset"
    echo "-----------------------------------------"
    
    # Preprocess data if needed
    if [ ! -f "benchmarking/data/${dataset}_temporal.pkl" ]; then
        echo "Preprocessing $dataset dataset..."
        python benchmarking/preprocess.py --dataset $dataset
    fi
    
    # Run DynamicTriad
    echo "Training DynamicTriad on $dataset..."
    python benchmarking/dynamic_triad/train.py \
        --dataset $dataset \
        --output results/dynamic_triad/${dataset}_embeddings.json \
        --epochs 100 \
        --embedding-dim 64 \
        --lr 0.01
    
    echo "Results saved to results/dynamic_triad/${dataset}_embeddings.json"
}

# Run on all datasets
for dataset in cora reddit uci_message; do
    run_dynamic_triad $dataset
done

echo ""
echo "========================================="
echo "DynamicTriad benchmarking complete!"
echo "Results saved in results/dynamic_triad/"
echo "========================================="
