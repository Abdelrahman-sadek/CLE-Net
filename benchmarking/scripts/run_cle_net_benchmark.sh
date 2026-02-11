#!/usr/bin/env bash
# CLE-Net Benchmarking Script
# Runs CLE-Net rule discovery on temporal graph datasets

set -e  # Exit on error

echo "========================================="
echo "CLE-Net Benchmarking"
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
    pip install -e .
    pip install numpy scipy scikit-learn tqdm
fi

# Set random seed
SEED=${SEED:-42}
export PYTHONHASHSEED=$SEED

# Create results directory
mkdir -p results/cle_net

# Function to run CLE-Net on a dataset
run_cle_net() {
    local dataset=$1
    local output=${2:-results/cle_net/${dataset}_eval.json}
    echo ""
    echo "-----------------------------------------"
    echo "Processing dataset: $dataset"
    echo "-----------------------------------------"
    
    # Preprocess data if needed
    if [ ! -f "benchmarking/data/${dataset}_temporal.pkl" ]; then
        echo "Preprocessing $dataset dataset..."
        python benchmarking/preprocess.py --dataset $dataset
    fi
    
    # Run CLE-Net evaluation
    echo "Running CLE-Net evaluation on $dataset..."
    python benchmarking/run_cle_net_eval.py \
        --dataset $dataset \
        --output $output \
        --seed $SEED
    
    echo "Results saved to $output"
}

# Run on all datasets
for dataset in cora reddit uci_message; do
    run_cle_net $dataset
done

echo ""
echo "========================================="
echo "CLE-Net benchmarking complete!"
echo "Results saved in results/cle_net/"
echo "========================================="
