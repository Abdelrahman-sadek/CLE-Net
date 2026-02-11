#!/usr/bin/env python3
"""
DynamicTriad Training Script
"""

import sys
import os
import argparse
import pickle
import json
import numpy as np
import torch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dynamic_triad import DynamicTriad, DynamicTriadTrainer


def set_seed(seed):
    np.random.seed(seed)
    torch.manual_seed(seed)


def main():
    parser = argparse.ArgumentParser(description='Train DynamicTriad model')
    parser.add_argument('--dataset', type=str, default='cora',
                        choices=['cora', 'reddit', 'uci_message'],
                        help='Dataset name')
    parser.add_argument('--output', type=str, default='results/dynamic_triad/embeddings.json',
                        help='Output file for embeddings')
    parser.add_argument('--epochs', type=int, default=100,
                        help='Number of training epochs')
    parser.add_argument('--embedding-dim', type=int, default=64,
                        help='Embedding dimension')
    parser.add_argument('--lr', type=float, default=0.01,
                        help='Learning rate')
    parser.add_argument('--batch-size', type=int, default=256,
                        help='Batch size')
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
    
    # Convert temporal edges to list format for training
    all_edges = []
    for t, edges in enumerate(temporal_edges):
        for u, v in edges:
            all_edges.append((u, v, t))
    
    # Train DynamicTriad
    print(f"Training DynamicTriad on {args.dataset}...")
    print(f"  Nodes: {num_nodes}, Edges: {len(all_edges)}")
    
    model = DynamicTriad(
        num_nodes=num_nodes,
        embedding_dim=args.embedding_dim,
        time_window=5
    )
    
    trainer = DynamicTriadTrainer(model, lr=args.lr)
    trainer.fit(temporal_edges, num_epochs=args.epochs, batch_size=args.batch_size)
    
    # Get embeddings
    embeddings = model.get_embeddings()
    
    # Save results
    results = {
        'dataset': args.dataset,
        'num_nodes': num_nodes,
        'embedding_dim': args.embedding_dim,
        'embeddings': embeddings.tolist(),
        'epochs': args.epochs
    }
    
    with open(args.output, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Embeddings saved to {args.output}")
    print(f"Embedding shape: {embeddings.shape}")


if __name__ == '__main__':
    main()
