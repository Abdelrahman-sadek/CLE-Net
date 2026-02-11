# Dynamic Triad Implementation for CLE-Net Benchmarking
# Based on "Dynamic Triad Closure Model for Predicting Temporal Networks"

## Overview
DynamicTriad extends the triad to model how triadic closure happens over time in evolving networks.

## Installation
```bash
pip install torch torch-geometric numpy scipy scikit-learn
```

## Usage
```python
from dynamic_triad import DynamicTriad

model = DynamicTriad(
    num_nodes=1000,
    embedding_dim=64,
    time_window=5,
    num_epochs=100,
    lr=0.01
)

model.train(edge_list_times, labels)
embeddings = model.get_embeddings()
```

## Key Parameters
- `num_nodes`: Number of nodes in the graph
- `embedding_dim`: Dimension of node embeddings
- `time_window`: Number of time steps to consider
- `num_epochs`: Training epochs
- `lr`: Learning rate
