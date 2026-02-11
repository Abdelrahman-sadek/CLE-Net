#!/usr/bin/env bash
# VGRNN Benchmarking Script
# Runs VGRNN on temporal graph datasets

set -e  # Exit on error

echo "========================================="
echo "VGRNN Baseline Benchmarking"
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
    pip install torch torch-geometric torch-scatter torch-sparse numpy scipy scikit-learn tqdm
fi

# Set random seed
SEED=${SEED:-42}
export PYTHONHASHSEED=$SEED

# Create results directory
mkdir -p results/vgrnn

# Function to run VGRNN on a dataset
run_vgrnn() {
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
    
    # Run VGRNN
    echo "Training VGRNN on $dataset..."
    python benchmarking/vgrnn/train.py \
        --dataset $dataset \
        --output results/vgrnn/${dataset}_embeddings.json \
        --epochs 100 \
        --hidden-dim 64 \
        --num-layers 2 \
        --lr 0.01
    
    echo "Results saved to results/vgrnn/${dataset}_embeddings.json"
}

# Run on all datasets
for dataset in cora reddit uci_message; do
    run_vgrnn $dataset
done

echo ""
echo "========================================="
echo "VGRNN benchmarking complete!"
echo "Results saved in results/vgrnn/"
echo "========================================="
