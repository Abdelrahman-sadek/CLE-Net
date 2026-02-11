# CLE-Net Benchmarking Suite

This document describes the benchmarking framework for comparing CLE-Net's symbolic rule discovery against standard dynamic graph embedding baselines (DynamicTriad and VGRNN).

## Overview

The benchmarking suite evaluates:
- **Temporal Link Prediction**: How well each model predicts future edges
- **Embedding Stability**: Consistency of representations over time
- **Rule Discovery Quality**: CLE-Net's ability to extract meaningful symbolic rules
- **Efficiency**: Runtime and memory usage

## Datasets

### Supported Datasets

| Dataset | Description | Nodes | Temporal Splits |
|---------|-------------|-------|-----------------|
| Cora | Citation network (temporal splits) | ~2,700 | 10 |
| Reddit | Temporal user interactions | ~10,000 | 10 |
| UCI Message | Social interaction network | ~1,899 | 10 |

### Dataset Preparation

```bash
# Preprocess all datasets
python benchmarking/preprocess.py --dataset cora
python benchmarking/preprocess.py --dataset reddit
python benchmarking/preprocess.py --dataset uci_message

# Or preprocess a specific dataset
python benchmarking/preprocess.py --dataset <dataset_name>
```

Preprocessed data is saved to `benchmarking/data/<dataset>_temporal.pkl`

## Installation

### Prerequisites

```bash
# Create virtual environment
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate

# Install CLE-Net and dependencies
pip install -e .

# Install baseline dependencies
pip install torch torch-geometric torch-scatter torch-sparse numpy scipy scikit-learn tqdm
```

## Running Benchmarks

### Quick Start

```bash
# Run all benchmarks (CLE-Net, DynamicTriad, VGRNN)
bash benchmarking/scripts/run_all.sh

# Or run individually
bash benchmarking/scripts/run_dynamic_embeddings.sh   # DynamicTriad
bash benchmarking/scripts/run_vgrnn.sh                 # VGRNN
bash benchmarking/scripts/run_cle_net_benchmark.sh    # CLE-Net
```

### Individual Model Training

```bash
# Train DynamicTriad
python benchmarking/dynamic_triad/train.py \
    --dataset cora \
    --output results/dynamic_triad/cora.json \
    --epochs 100 \
    --embedding-dim 64

# Train VGRNN
python benchmarking/vgrnn/train.py \
    --dataset cora \
    --output results/vgrnn/cora.json \
    --epochs 100 \
    --hidden-dim 64

# Evaluate CLE-Net
python benchmarking/run_cle_net_eval.py \
    --dataset cora \
    --output results/cle_net/cora.json
```

### Compare Results

```bash
# Compare all model results
bash benchmarking/scripts/evaluate_results.sh cora

# Or with custom results
python benchmarking/evaluate.py \
    --cle-net results/cle_net/cora.json \
    --triad results/dynamic_triad/cora.json \
    --vgrnn results/vgrnn/cora.json \
    --dataset cora \
    --output results/comparison_cora.csv
```

## Evaluation Metrics

### Link Prediction Metrics

| Metric | Description | Interpretation |
|--------|-------------|----------------|
| AUC | Area Under ROC Curve | Higher is better (1.0 = perfect) |
| Average Precision | Precision-Recall Curve Area | Higher is better |
| Precision@K | Precision at top K predictions | Higher is better |
| Recall@K | Recall at top K predictions | Higher is better |

### CLE-Net Specific Metrics

| Metric | Description | Interpretation |
|--------|-------------|----------------|
| Rule Precision | Fraction of discovered rules that are true | Higher is better |
| Rule Recall | Coverage of ground-truth rules | Higher is better |
| Rule Stability CV | Coefficient of variation in rules over time | Lower is better |
| Avg Support | Average support of discovered rules | Higher = more general |
| Avg Confidence | Average confidence of discovered rules | Higher = more reliable |

### Temporal Stability Metrics

| Metric | Description | Interpretation |
|--------|-------------|----------------|
| Mean Drift | Average embedding change between timesteps | Lower is better |
| Std Drift | Variability in embedding changes | Lower is better |

## Expected Output

### Comparison CSV Format

```
Dataset,Model,Link Pred AUC,Avg Precision,Rule Precision,Rule Recall,Rule Stability
cora,CLE-Net,0.85,0.78,0.72,0.65,0.89
cora,DynamicTriad,0.82,0.75,N/A,N/A,0.85
cora,VGRNN,0.84,0.76,N/A,N/A,N/A
```

### Results Directory Structure

```
results/
├── cle_net/
│   ├── cora_eval.json
│   ├── reddit_eval.json
│   └── uci_message_eval.json
├── dynamic_triad/
│   ├── cora_embeddings.json
│   ├── reddit_embeddings.json
│   └── uci_message_embeddings.json
├── vgrnn/
│   ├── cora_embeddings.json
│   ├── reddit_embeddings.json
│   └── uci_message_embeddings.json
├── comparison_cora.csv
├── comparison_reddit.csv
└── comparison_uci_message.csv
```

## Configuration Options

### Common Options

| Option | Default | Description |
|--------|---------|-------------|
| `--seed` | 42 | Random seed for reproducibility |
| `--epochs` | 100 | Number of training epochs |
| `--batch-size` | 32/256 | Batch size for training |

### DynamicTriad Options

| Option | Default | Description |
|--------|---------|-------------|
| `--embedding-dim` | 64 | Dimension of node embeddings |
| `--lr` | 0.01 | Learning rate |
| `--time-window` | 5 | Number of timesteps in context window |

### VGRNN Options

| Option | Default | Description |
|--------|---------|-------------|
| `--hidden-dim` | 64 | Hidden dimension |
| `--num-layers` | 2 | Number of GNN layers |
| `--lr` | 0.01 | Learning rate |
| `--kl-weight` | 0.1 | Weight for KL divergence loss |

### CLE-Net Options

| Option | Default | Description |
|--------|---------|-------------|
| `--max-rules` | 50 | Maximum number of rules to extract |
| `--min-support` | 0.1 | Minimum support threshold |
| `--min-confidence` | 0.5 | Minimum confidence threshold |

## Interpreting Results

### When CLE-Net Outperforms Baselines

CLE-Net typically excels when:
1. **Semantic patterns are clear**: The underlying rules governing network evolution are discoverable
2. **Temporal consistency**: Rules remain stable across time windows
3. **Interpretability is required**: Need to understand why predictions are made

### When Baselines Outperform CLE-Net

Baselines typically excel when:
1. **Dense networks**: Many complex interactions that don't follow simple rules
2. **Short temporal sequences**: Not enough data for reliable rule extraction
3. **Noisy data**: Embedding methods are more robust to noise

## Reproducibility

All experiments use fixed random seeds (default: 42) for reproducibility. To change the seed:

```bash
SEED=123 bash benchmarking/scripts/run_all.sh
```

## Troubleshooting

### Common Issues

1. **PyTorch Geometric installation errors**
   ```bash
   # Install PyG separately with correct PyTorch version
   pip install torch-scatter torch-sparse -f https://data.pyg.org/whl/torch-${TORCH}.html
   ```

2. **Memory issues with large datasets**
   ```bash
   # Reduce batch size
   --batch-size 16
   ```

3. **CUDA out of memory**
   ```bash
   # Use CPU
   export CUDA_VISIBLE_DEVICES=""
   ```

## Citation

If you use this benchmarking suite in your research, please cite:

```bibtex
@article{cle-net-benchmarking,
  title={CLE-Net: Cognitive Logic Extraction Network Benchmarking},
  author={CLE-Net Contributors},
  year={2024}
}
```

## References

1. **DynamicTriad**: Zhou, L., et al. (2018). Dynamic Triad Closure Model for Predicting Temporal Networks.
2. **VGRNN**: Hajiramezanali, E., et al. (2019). Variational Graph Recurrent Neural Networks.
