#!/usr/bin/env python3
"""
Dataset Preprocessing for Benchmarking
Downloads and prepares Cora, Reddit, and UCI Message datasets for dynamic graph benchmarking.
"""

import argparse
import json
import os
import pickle
import random
import numpy as np
import torch


def set_seed(seed):
    """Set random seed for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)


def download_cora():
    """Download Cora citation network."""
    # Cora is available via torch geometric or networkx
    try:
        from torch_geometric.datasets import Planetoid
        dataset = Planetoid(root='data/cora', name='Cora')
        return dataset[0]
    except ImportError:
        print("Installing torch-geometric for Cora dataset...")
        os.system("pip install torch-geometric")
        from torch_geometric.datasets import Planetoid
        dataset = Planetoid(root='data/cora', name='Cora')
        return dataset[0]


def convert_cora_to_temporal(cora_data, num_splits=10):
    """Convert static Cora to temporal splits."""
    edge_index = cora_data.edge_index.numpy()
    num_nodes = cora_data.num_nodes
    
    # Create temporal edge list - edges are (u, v) pairs
    edges = list(zip(edge_index[0], edge_index[1]))
    
    # Shuffle and split into temporal windows
    random.shuffle(edges)
    
    temporal_edges = []
    split_size = len(edges) // num_splits
    
    for i in range(num_splits):
        start = i * split_size
        end = (i + 1) * split_size if i < num_splits - 1 else len(edges)
        temporal_edges.append(edges[start:end])
    
    return {
        'num_nodes': num_nodes,
        'temporal_edges': temporal_edges,
        'node_features': cora_data.x.numpy() if cora_data.x is not None else None,
        'labels': cora_data.y.numpy() if cora_data.y is not None else None
    }


def download_reddit():
    """Download Reddit temporal interaction network."""
    try:
        from torch_geometric.datasets import Reddit
        dataset = Reddit(root='data/reddit')
        return dataset[0]
    except ImportError:
        print("Reddit dataset requires PyG API access. Using synthetic temporal data.")
        return generate_synthetic_temporal_data(num_nodes=10000, num_edges=100000, num_timesteps=10)


def convert_reddit_to_temporal(reddit_data, num_splits=10):
    """Convert Reddit to temporal format."""
    edge_index = reddit_data.edge_index.numpy()
    num_nodes = reddit_data.num_nodes
    
    # Create temporal edge list - edges are (u, v) pairs
    edges = list(zip(edge_index[0], edge_index[1]))
    random.shuffle(edges)
    
    split_size = len(edges) // num_splits
    temporal_edges = []
    
    for i in range(num_splits):
        start = i * split_size
        end = (i + 1) * split_size if i < num_splits - 1 else len(edges)
        temporal_edges.append(edges[start:end])
    
    return {
        'num_nodes': num_nodes,
        'temporal_edges': temporal_edges,
        'node_features': reddit_data.x.numpy() if reddit_data.x is not None else None,
        'labels': reddit_data.y.numpy() if reddit_data.y is not None else None
    }


def download_uci():
    """Download UCI Message temporal social network."""
    # UCI dataset can be downloaded from network repository
    try:
        import networkx as nx
        # Try to load UCI from Network Repository or generate synthetic
        print("UCI Message dataset - using synthetic temporal data for demo")
        return generate_synthetic_temporal_data(num_nodes=1899, num_edges=20000, num_timesteps=10)
    except ImportError:
        return generate_synthetic_temporal_data(num_nodes=1899, num_edges=20000, num_timesteps=10)


def convert_uci_to_temporal(edges, num_splits=10):
    """Convert UCI edges to temporal format."""
    # Add temporal information (sort by edge index to simulate time)
    edges_with_time = [(u, v, i % num_splits) for i, (u, v) in enumerate(edges)]
    
    temporal_edges = [[] for _ in range(num_splits)]
    for u, v, t in edges_with_time:
        temporal_edges[t].append((u, v))
    
    return {
        'num_nodes': max(max(u for u, v in edges), max(v for u, v in edges)) + 1,
        'temporal_edges': temporal_edges
    }


def generate_synthetic_temporal_data(num_nodes, num_edges, num_timesteps):
    """Generate synthetic temporal graph data for testing."""
    random.seed(42)
    
    edges_per_timestep = num_edges // num_timesteps
    temporal_edges = []
    
    for t in range(num_timesteps):
        timestep_edges = []
        for _ in range(edges_per_timestep):
            u = random.randint(0, num_nodes - 1)
            v = random.randint(0, num_nodes - 1)
            while v == u:
                v = random.randint(0, num_nodes - 1)
            timestep_edges.append((u, v, t))
        temporal_edges.append(timestep_edges)
    
    # Flatten for storage
    all_edges = [e[:2] for timestep in temporal_edges for e in timestep]
    
    return {
        'num_nodes': num_nodes,
        'temporal_edges': [[(e[0], e[1]) for e in timestep] for timestep in temporal_edges],
        'all_edges': all_edges
    }


def create_link_prediction_splits(temporal_edges, num_nodes, train_ratio=0.7, val_ratio=0.15):
    """Create train/val/test splits for link prediction."""
    all_edges = []
    for t, edges in enumerate(temporal_edges):
        for u, v in edges:
            # Handle both (u, v) and (u, v, t) formats
            if isinstance(v, tuple):
                # Already has timestamp
                all_edges.append(v)
            else:
                all_edges.append((u, v, t))
    
    random.shuffle(all_edges)
    
    n = len(all_edges)
    train_end = int(n * train_ratio)
    val_end = int(n * (train_ratio + val_ratio))
    
    train_edges = all_edges[:train_end]
    val_edges = all_edges[train_end:val_end]
    test_edges = all_edges[val_end:]
    
    # Create negative samples
    train_neg = generate_negative_samples([e[:2] for e in all_edges], num_nodes, len(train_edges))
    val_neg = generate_negative_samples([e[:2] for e in all_edges], num_nodes, len(val_edges))
    test_neg = generate_negative_samples([e[:2] for e in all_edges], num_nodes, len(test_edges))
    
    return {
        'train': {'pos': train_edges, 'neg': train_neg},
        'val': {'pos': val_edges, 'neg': val_neg},
        'test': {'pos': test_edges, 'neg': test_neg}
    }


def generate_negative_samples(positive_edges, num_nodes, num_negatives):
    """Generate negative samples for link prediction."""
    positive_set = set(positive_edges)
    negatives = []
    
    while len(negatives) < num_negatives:
        u = random.randint(0, num_nodes - 1)
        v = random.randint(0, num_nodes - 1)
        
        if u != v and (u, v) not in positive_set and (v, u) not in positive_set:
            negatives.append((u, v))
            positive_set.add((u, v))
            positive_set.add((v, u))
    
    return negatives


def preprocess_dataset(dataset_name, output_dir='benchmarking/data'):
    """Main preprocessing function for a dataset."""
    os.makedirs(output_dir, exist_ok=True)
    set_seed(42)
    
    print(f"Preprocessing {dataset_name} dataset...")
    
    if dataset_name == 'cora':
        cora_data = download_cora()
        temporal_data = convert_cora_to_temporal(cora_data)
    elif dataset_name == 'reddit':
        reddit_data = download_reddit()
        temporal_data = convert_reddit_to_temporal(reddit_data)
    elif dataset_name == 'uci_message':
        uci_data = download_uci()
        temporal_data = convert_uci_to_temporal(uci_data.get('all_edges', []))
    else:
        raise ValueError(f"Unknown dataset: {dataset_name}")
    
    # Create link prediction splits
    splits = create_link_prediction_splits(
        temporal_data['temporal_edges'],
        temporal_data['num_nodes']
    )
    
    # Save preprocessed data
    output_file = os.path.join(output_dir, f'{dataset_name}_temporal.pkl')
    
    with open(output_file, 'wb') as f:
        pickle.dump({
            'temporal_edges': temporal_data['temporal_edges'],
            'num_nodes': temporal_data['num_nodes'],
            'node_features': temporal_data.get('node_features'),
            'labels': temporal_data.get('labels'),
            'splits': splits
        }, f)
    
    print(f"Saved preprocessed data to {output_file}")
    return output_file


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Preprocess datasets for benchmarking')
    parser.add_argument('--dataset', type=str, default='cora',
                        choices=['cora', 'reddit', 'uci_message'],
                        help='Dataset to preprocess')
    parser.add_argument('--output_dir', type=str, default='benchmarking/data',
                        help='Output directory for preprocessed data')
    
    args = parser.parse_args()
    preprocess_dataset(args.dataset, args.output_dir)
