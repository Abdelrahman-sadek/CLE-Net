#!/usr/bin/env python3
"""
DyGNN (Dynamic Graph Neural Network) Implementation

DyGNN combines GNN with temporal attention for dynamic graphs.
Uses attention mechanism to capture temporal evolution of node representations.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.nn import MultiheadAttention, Linear
import numpy as np


class TemporalAttentionLayer(nn.Module):
    """
    Temporal attention layer to capture evolution of node states over time.
    """
    def __init__(self, hidden_dim, num_heads=4):
        super(TemporalAttentionLayer, self).__init__()
        self.hidden_dim = hidden_dim
        self.num_heads = num_heads
        self.head_dim = hidden_dim // num_heads
        
        self.attention = MultiheadAttention(
            embed_dim=hidden_dim,
            num_heads=num_heads,
            batch_first=True
        )
        
        self.norm = nn.LayerNorm(hidden_dim)
        self.ffn = nn.Sequential(
            Linear(hidden_dim, hidden_dim * 4),
            nn.ReLU(),
            Linear(hidden_dim * 4, hidden_dim)
        )
        
    def forward(self, temporal_embeddings):
        """
        Args:
            temporal_embeddings: [batch_size, seq_len, hidden_dim]
            
        Returns:
            Enhanced embeddings with temporal context
        """
        # Self-attention over time
        attn_out, _ = self.attention(
            temporal_embeddings, temporal_embeddings, temporal_embeddings
        )
        
        # Residual connection and normalization
        out = self.norm(temporal_embeddings + attn_out)
        
        # Feed-forward
        out = self.norm(out + self.ffn(out))
        
        return out


class DyGNNLayer(nn.Module):
    """
    GNN layer with temporal awareness.
    """
    def __init__(self, in_dim, out_dim):
        super(DyGNNLayer, self).__init__()
        self.linear = nn.Linear(in_dim * 2, out_dim)
        
    def forward(self, x, edge_index):
        """
        Args:
            x: Node features [num_nodes, in_dim]
            edge_index: Edge indices [2, num_edges]
            
        Returns:
            Updated node features [num_nodes, out_dim]
        """
        row, col = edge_index
        
        # Message passing
        msg = torch.cat([x[row], x[col]], dim=-1)
        msg = self.linear(msg)
        msg = F.relu(msg)
        
        # Aggregate messages
        out = torch.zeros_like(x)
        out.scatter_add_(0, row.unsqueeze(1).expand_as(msg), msg)
        
        # Combine with original features
        out = torch.cat([x, out], dim=-1)
        out = self.linear(out)
        out = F.relu(out)
        
        return out


class DyGNN(nn.Module):
    """
    Dynamic Graph Neural Network for temporal link prediction.
    """
    def __init__(self, num_features, hidden_dim, num_layers=2, num_heads=4, dropout=0.5):
        super(DyGNN, self).__init__()
        
        self.num_features = num_features
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.dropout = dropout
        
        # Input projection
        self.input_proj = nn.Linear(num_features, hidden_dim)
        
        # GNN layers
        self.gnn_layers = nn.ModuleList()
        for _ in range(num_layers):
            self.gnn_layers.append(DyGNNLayer(hidden_dim, hidden_dim))
        
        # Temporal attention for sequence of embeddings
        self.temporal_attn = TemporalAttentionLayer(hidden_dim, num_heads)
        
        # Output projection
        self.output_proj = nn.Linear(hidden_dim * 2, hidden_dim)
        
    def forward(self, x_sequence, edge_index_sequence):
        """
        Args:
            x_sequence: [seq_len, num_nodes, num_features]
            edge_index_sequence: List of edge indices for each timestep
            
        Returns:
            predictions: Link prediction scores
        """
        seq_len = len(x_sequence)
        temporal_embeddings = []
        
        # Process each timestep
        for t in range(seq_len):
            x = self.input_proj(x_sequence[t])
            
            # GNN layers
            for gnn_layer in self.gnn_layers:
                x = gnn_layer(x, edge_index_sequence[t])
            
            temporal_embeddings.append(x)
        
        # Stack temporal embeddings [seq_len, num_nodes, hidden_dim]
        temporal_embeddings = torch.stack(temporal_embeddings)
        
        # Apply temporal attention
        enhanced_embeddings = self.temporal_attn(temporal_embeddings)
        
        # Use last timestep with temporal context
        final_embeddings = enhanced_embeddings[-1]
        
        return final_embeddings
    
    def get_embeddings(self, x_sequence, edge_index_sequence):
        """Extract embeddings for link prediction."""
        self.eval()
        with torch.no_grad():
            embeddings = self.forward(x_sequence, edge_index_sequence)
        return embeddings.numpy()


def evaluate_dyngnn(embeddings, pos_edges, neg_edges):
    """Evaluate DyGNN embeddings for link prediction."""
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
    print("Testing DyGNN implementation...")
    
    num_nodes = 100
    num_features = 64
    hidden_dim = 32
    seq_len = 5
    
    # Create random temporal graph
    x_sequence = [torch.randn(num_nodes, num_features) for _ in range(seq_len)]
    edge_index_sequence = [torch.randint(0, num_nodes, (2, 200)) for _ in range(seq_len)]
    
    # Initialize model
    model = DyGNN(num_features, hidden_dim, num_layers=2)
    
    # Forward pass
    embeddings = model.get_embeddings(x_sequence, edge_index_sequence)
    
    print(f"Sequence length: {seq_len}")
    print(f"Input shape per timestep: {x_sequence[0].shape}")
    print(f"Embeddings shape: {embeddings.shape}")
    print("DyGNN test passed!")
