# VGRNN Implementation for CLE-Net Benchmarking
# Based on "Variational Graph Recurrent Neural Networks" (VGRNN)

## Overview
VGRNN combines variational inference with graph recurrent neural networks for dynamic graph embeddings.

## Installation
```bash
pip install torch torch-geometric torch-scatter torch-sparse
```

## Usage
```python
from vgrnn import VGRNN

model = VGRNN(
    input_dim=128,
    hidden_dim=64,
    num_layers=2,
    num_nodes=1000,
    num_epochs=100,
    lr=0.01
)

model.train(edge_index_list, node_features_list)
embeddings = model.get_embeddings()
```

## Key Parameters
- `input_dim`: Input feature dimension
- `hidden_dim`: Hidden dimension
- `num_layers`: Number of GNN layers
- `num_nodes`: Number of nodes
- `num_epochs`: Training epochs
- `lr`: Learning rate
