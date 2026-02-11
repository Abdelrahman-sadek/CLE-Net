#!/usr/bin/env python3
"""
EvolveGCN Implementation for Dynamic Graph Embeddings

EvolveGCN uses RNNs to evolve Graph Convolutional Network parameters over time.
Reference: Pareja et al., "EvolveGCN: Evolving Graph Convolutional Networks for Dynamic Graphs", AAAI 2020.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.nn import Linear
from torch_geometric.nn import GCNConv
from torch_geometric.utils import to_undirected
import numpy as np
import random


class EvolveGCNLayer(nn.Module):
    """
    GCN layer that evolves its weights using an RNN.
    """
    def __init__(self, in_channels, out_channels):
        super(EvolveGCNLayer, self).__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        
        # Initial weights
        self.weight = nn.Parameter(torch.Tensor(in_channels, out_channels))
        self.bias = nn.Parameter(torch.Tensor(out_channels))
        
        nn.init.xavier_uniform_(self.weight)
        nn.init.zeros_(self.bias)
        
        # RNN to evolve weights
        self.rnn = nn.GRUCell(out_channels, out_channels)
        
    def forward(self, x, edge_index, h_prev=None):
        # Compute graph convolution
        x = F.relu(torch.mm(x, self.weight) + self.bias)
        
        # Normalize messages
        edge_index = to_undirected(edge_index)
        row, col = edge_index
        deg = row.new_zeros(row.size(0))
        deg.scatter_add_(0, row, torch.ones_like(row))
        deg_inv_sqrt = deg.pow(-0.5)
        deg_inv_sqrt[deg_inv_sqrt == float('inf')] = 0
        norm = deg_inv_sqrt[row] * deg_inv_sqrt[col]
        
        # Message passing
        out = torch.zeros_like(x)
        out = out.scatter_add(0, row.unsqueeze(1).expand_as(x), x[col] * norm.unsqueeze(1))
        
        # Evolve weights if previous hidden state exists
        if h_prev is not None:
            h_new = self.rnn(out, h_prev)
            return out, h_new
        
        return out, None


class EvolveGCN(nn.Module):
    """
    EvolveGCN Model using GCN layers with RNN-based weight evolution.
    """
    def __init__(self, num_features, hidden_dim, num_layers=2, dropout=0.5):
        super(EvolveGCN, self).__init__()
        
        self.num_features = num_features
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.dropout = dropout
        
        # Input layer
        self.input_fn = Linear(num_features, hidden_dim)
        
        # GCN layers with evolution
        self.layers = nn.ModuleList()
        for i in range(num_layers):
            self.layers.append(EvolveGCNLayer(hidden_dim, hidden_dim))
        
        # Output layer
        self.output_fn = Linear(hidden_dim, hidden_dim)
        
        # Hidden state
        self.h = None
        
    def reset_hidden_state(self):
        """Reset hidden states for new sequence."""
        self.h = [None] * len(self.layers)
        
    def forward(self, x, edge_index):
        """
        Forward pass through the model.
        
        Args:
            x: Node features [num_nodes, num_features]
            edge_index: Edge indices [2, num_edges]
            
        Returns:
            embeddings: Node embeddings [num_nodes, hidden_dim]
        """
        # Input transformation
        x = self.input_fn(x)
        x = F.dropout(x, p=self.dropout, training=self.training)
        
        # GCN layers with weight evolution
        for i, layer in enumerate(self.layers):
            x, self.h[i] = layer(x, edge_index, self.h[i])
            x = F.dropout(x, p=self.dropout, training=self.training)
        
        # Output
        x = self.output_fn(x)
        
        return x
    
    def get_embeddings(self, x, edge_index):
        """Extract embeddings without classification layer."""
        self.eval()
        with torch.no_grad():
            self.reset_hidden_state()
            embeddings = self.forward(x, edge_index)
        return embeddings.numpy()


def evaluate_evolvegcn(embeddings, pos_edges, neg_edges):
    """Evaluate EvolveGCN embeddings for link prediction."""
    from sklearn.metrics import roc_auc_score, average_precision_score
    
    pos_scores = []
    for u, v in pos_edges:
        emb_u = embeddings[u]
        emb_v = embeddings[v]
        score = np.dot(emb_u, emb_v) / (np.linalg.norm(emb_u) * np.linalg.norm(emb_v) + 1e-8)
        pos_scores.append(score)
    
    neg_scores = []
    for u, v in neg_edges:
        emb_u = embeddings[u]
        emb_v = embeddings[v]
        score = np.dot(emb_u, emb_v) / (np.linalg.norm(emb_u) * np.linalg.norm(emb_v) + 1e-8)
        neg_scores.append(score)
    
    all_scores = pos_scores + neg_scores
    all_labels = [1] * len(pos_scores) + [0] * len(neg_scores)
    
    auc = roc_auc_score(all_labels, all_scores)
    ap = average_precision_score(all_labels, all_scores)
    
    return {
        'auc': auc,
        'average_precision': ap
    }


if __name__ == '__main__':
    # Simple test
    print("Testing EvolveGCN implementation...")
    
    num_nodes = 100
    num_features = 64
    hidden_dim = 32
    
    # Create random graph
    edge_index = torch.randint(0, num_nodes, (2, 200))
    x = torch.randn(num_nodes, num_features)
    
    # Initialize model
    model = EvolveGCN(num_features, hidden_dim, num_layers=2)
    
    # Forward pass
    embeddings = model.get_embeddings(x, edge_index)
    
    print(f"Input shape: {x.shape}")
    print(f"Embeddings shape: {embeddings.shape}")
    print("EvolveGCN test passed!")
