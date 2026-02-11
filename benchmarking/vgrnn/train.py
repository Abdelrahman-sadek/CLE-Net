#!/usr/bin/env python3
"""
VGRNN Training Script
"""

import argparse
import json
import os
import pickle
import numpy as np
import torch


def set_seed(seed):
    np.random.seed(seed)
    torch.manual_seed(seed)


def main():
    parser = argparse.ArgumentParser(description='Train VGRNN model')
    parser.add_argument('--dataset', type=str, default='cora',
                        choices=['cora', 'reddit', 'uci_message'],
                        help='Dataset name')
    parser.add_argument('--output', type=str, default='results/vgrnn/embeddings.json',
                        help='Output file for embeddings')
    parser.add_argument('--epochs', type=int, default=100,
                        help='Number of training epochs')
    parser.add_argument('--hidden-dim', type=int, default=64,
                        help='Hidden dimension')
    parser.add_argument('--lr', type=float, default=0.01,
                        help='Learning rate')
    parser.add_argument('--seed', type=int, default=42,
                        help='Random seed')
    
    args = parser.parse_args()
    
    set_seed(args.seed)
    
    # Create output directory
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    # Load preprocessed data
    data_path = f'benchmarking/data/{args.dataset}_temporal.pkl'
    if not os.path.exists(data_path):
        from preprocess import preprocess_dataset
        preprocess_dataset(args.dataset)
    
    with open(data_path, 'rb') as f:
        data = pickle.load(f)
    
    temporal_edges = data['temporal_edges']
    num_nodes = data['num_nodes']
    
    print(f"Training VGRNN on {args.dataset}...")
    print(f"  Nodes: {num_nodes}, Timesteps: {len(temporal_edges)}")
    
    # Train VGRNN
    from vgrnn import train_vgrnn
    embeddings = train_vgrnn(
        temporal_edges,
        num_nodes=num_nodes,
        hidden_dim=args.hidden_dim,
        num_epochs=args.epochs,
        lr=args.lr
    )
    
    # Save results
    results = {
        'dataset': args.dataset,
        'num_nodes': num_nodes,
        'hidden_dim': args.hidden_dim,
        'embeddings': embeddings.tolist(),
        'epochs': args.epochs
    }
    
    with open(args.output, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Embeddings saved to {args.output}")
    print(f"Embedding shape: {embeddings.shape}")


if __name__ == '__main__':
    main()
