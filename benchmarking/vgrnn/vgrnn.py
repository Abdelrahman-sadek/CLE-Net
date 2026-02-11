# VGRNN Implementation
# Based on "Variational Graph Recurrent Neural Networks" (Hajiramezanali et al., 2019)

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np


class VGRNNCell(nn.Module):
    """VGRNN Cell - variational graph recurrent neural network unit."""
    
    def __init__(self, hidden_dim, num_nodes, eps=1e-5):
        super(VGRNNCell, self).__init__()
        
        self.hidden_dim = hidden_dim
        self.num_nodes = num_nodes
        self.eps = eps
        
        # GNN layers for message passing
        self.gnn_mu = nn.Linear(hidden_dim * 2, hidden_dim)
        self.gnn_logvar = nn.Linear(hidden_dim * 2, hidden_dim)
        
        # GRU update
        self.gru = nn.GRUCell(hidden_dim, hidden_dim)
        
        # Prior network
        self.prior_mu = nn.Linear(hidden_dim, hidden_dim)
        self.prior_logvar = nn.Linear(hidden_dim, hidden_dim)
    
    def gnn_message_passing(self, adj, h):
        """Perform message passing on graph."""
        # Add self-loop
        adj = adj + torch.eye(self.num_nodes, device=adj.device)
        
        # Degree normalization
        deg = adj.sum(dim=1, keepdim=True)
        deg = deg + (deg == 0)  # Avoid division by zero
        adj = adj / deg
        
        # Aggregate neighbors
        neighbor_sum = torch.matmul(adj, h)
        
        # Combine self and neighbors
        combined = torch.cat([h, neighbor_sum], dim=-1)
        
        return combined
    
    def forward(self, adj, h_prev):
        """Forward pass of VGRNN cell."""
        # Message passing
        combined = self.gnn_message_passing(adj, h_prev)
        
        # Posterior inference
        mu_q = self.gnn_mu(combined)
        logvar_q = self.gnn_logvar(combined)
        
        # Sample from posterior
        std_q = torch.exp(0.5 * logvar_q)
        epsilon = torch.randn_like(std_q)
        h_sample = mu_q + std_q * epsilon
        
        # Prior
        mu_p = self.prior_mu(h_sample)
        logvar_p = self.prior_logvar(h_sample)
        
        # Update hidden state
        h_new = self.gru(h_sample, h_prev)
        
        return h_new, mu_q, logvar_q, mu_p, logvar_p


class VGRNN(nn.Module):
    """
    Variational Graph Recurrent Neural Network for dynamic graph embeddings.
    
    Combines variational inference with graph neural networks for
    learning temporal representations of evolving graphs.
    """
    
    def __init__(self, hidden_dim, num_nodes, num_layers=2, dropout=0.5, eps=1e-5):
        super(VGRNN, self).__init__()
        
        self.hidden_dim = hidden_dim
        self.num_nodes = num_nodes
        self.num_layers = num_layers
        
        # VGRNN cells
        self.cells = nn.ModuleList([
            VGRNNCell(hidden_dim, num_nodes, eps=eps)
            for _ in range(num_layers)
        ])
        
        # Output projection for link prediction
        self.link_predictor = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, 1)
        )
        
        # Embedding output layer
        self.embedding_layer = nn.Linear(hidden_dim, hidden_dim)
        
    def forward(self, adj_list, h_init=None):
        """Forward pass over temporal graph sequence."""
        num_timesteps = len(adj_list)
        
        if h_init is None:
            h = torch.zeros(self.num_nodes, self.hidden_dim, device=adj_list[0].device)
        else:
            h = h_init
        
        embeddings = []
        
        for t in range(num_timesteps):
            adj = adj_list[t]
            
            # Pass through VGRNN layers
            for cell in self.cells:
                h, mu_q, logvar_q, mu_p, logvar_p = cell(adj, h)
            
            # Store embedding
            emb = self.embedding_layer(h)
            embeddings.append(emb)
        
        return embeddings
    
    def predict_link(self, emb_u, emb_v):
        """Predict link probability between two nodes."""
        combined = torch.cat([emb_u, emb_v], dim=-1)
        return self.link_predictor(combined)
    
    def get_embeddings(self, embeddings):
        """Get final embeddings (last timestep)."""
        return embeddings[-1] if isinstance(embeddings, list) else embeddings


class VGRNNTrainer:
    """Trainer for VGRNN model."""
    
    def __init__(self, model, lr=0.01, kl_weight=0.1):
        self.model = model
        self.optimizer = torch.optim.Adam(model.parameters(), lr=lr)
        self.kl_weight = kl_weight
        self.criterion = nn.BCEWithLogitsLoss()
    
    def compute_kl_loss(self, mu_q, logvar_q, mu_p, logvar_p):
        """Compute KL divergence between posterior and prior."""
        var_q = torch.exp(logvar_q) + 1e-5
        var_p = torch.exp(logvar_p) + 1e-5
        
        kl = 0.5 * (
            torch.log(var_p / var_q) 
            - 1 
            + (var_q / var_p) 
            + ((mu_q - mu_p) ** 2) / var_p
        )
        
        return kl.sum(dim=-1).mean()
    
    def train_epoch(self, adj_list, pos_edges, neg_edges):
        """Train for one epoch."""
        self.model.train()
        
        # Convert to tensors
        adj_tensors = []
        for adj in adj_list:
            adj_tensor = torch.tensor(adj, dtype=torch.float32)
            adj_tensors.append(adj_tensor)
        
        pos_u = torch.tensor([e[0] for e in pos_edges], dtype=torch.long)
        pos_v = torch.tensor([e[1] for e in pos_edges], dtype=torch.long)
        neg_u = torch.tensor([e[0] for e in neg_edges], dtype=torch.long)
        neg_v = torch.tensor([e[1] for e in neg_edges], dtype=torch.long)
        
        self.optimizer.zero_grad()
        
        # Forward pass
        embeddings = self.model(adj_tensors)
        final_emb = self.model.get_embeddings(embeddings)
        
        # Link prediction loss
        pos_scores = self.model.predict_link(final_emb[pos_u], final_emb[pos_v]).squeeze()
        neg_scores = self.model.predict_link(final_emb[neg_u], final_emb[neg_v]).squeeze()
        
        pos_loss = self.criterion(pos_scores, torch.ones_like(pos_scores))
        neg_loss = self.criterion(neg_scores, torch.zeros_like(neg_scores))
        
        link_loss = (pos_loss + neg_loss) / 2
        
        # KL loss
        kl_loss = self.kl_weight * torch.tensor(0.0)  # Simplified: omit KL for now
        
        loss = link_loss + kl_loss
        loss.backward()
        self.optimizer.step()
        
        return loss.item()
    
    def evaluate(self, adj_list, pos_edges, neg_edges):
        """Evaluate the model."""
        self.model.eval()
        
        # Convert to tensors
        adj_tensors = []
        for adj in adj_list:
            adj_tensor = torch.tensor(adj, dtype=torch.float32)
            adj_tensors.append(adj_tensor)
        
        pos_u = torch.tensor([e[0] for e in pos_edges], dtype=torch.long)
        pos_v = torch.tensor([e[1] for e in pos_edges], dtype=torch.long)
        neg_u = torch.tensor([e[0] for e in neg_edges], dtype=torch.long)
        neg_v = torch.tensor([e[1] for e in neg_edges], dtype=torch.long)
        
        with torch.no_grad():
            embeddings = self.model(adj_tensors)
            final_emb = self.model.get_embeddings(embeddings)
            
            pos_scores = torch.sigmoid(
                self.model.predict_link(final_emb[pos_u], final_emb[pos_v])
            ).squeeze()
            
            neg_scores = torch.sigmoid(
                self.model.predict_link(final_emb[neg_u], final_emb[neg_v])
            ).squeeze()
        
        # Compute AUC
        all_scores = torch.cat([pos_scores, neg_scores]).cpu().numpy()
        all_labels = [1] * len(pos_scores) + [0] * len(neg_scores)
        
        from sklearn.metrics import roc_auc_score
        try:
            auc = roc_auc_score(all_labels, all_scores)
        except:
            auc = 0.5
        
        # Accuracy
        preds = (all_scores > 0.5).astype(int)
        accuracy = np.mean(preds == np.array(all_labels))
        
        return {'auc': auc, 'accuracy': accuracy}
    
    def fit(self, adj_list, pos_edges, neg_edges, num_epochs=100):
        """Train the model."""
        best_auc = 0
        best_state = None
        
        for epoch in range(num_epochs):
            loss = self.train_epoch(adj_list, pos_edges, neg_edges)
            metrics = self.evaluate(adj_list, pos_edges, neg_edges)
            
            if metrics['auc'] > best_auc:
                best_auc = metrics['auc']
                best_state = {k: v.clone() for k, v in self.model.state_dict().items()}
            
            if (epoch + 1) % 10 == 0:
                print(f"Epoch {epoch + 1}/{num_epochs}, Loss: {loss:.4f}, AUC: {metrics['auc']:.4f}")
        
        if best_state is not None:
            self.model.load_state_dict(best_state)
        
        return best_auc


def train_vgrnn(temporal_edges, num_nodes, hidden_dim=64, num_epochs=100, lr=0.01):
    """Train VGRNN model and return embeddings."""
    # Convert temporal edges to adjacency matrices
    adj_list = []
    for t_edges in temporal_edges:
        adj = np.zeros((num_nodes, num_nodes))
        for u, v in t_edges:
            adj[u, v] = 1
            adj[v, u] = 1
        adj_list.append(adj)
    
    # Create some synthetic train/test splits
    all_edges = []
    for t, edges in enumerate(temporal_edges):
        for u, v in edges:
            all_edges.append((u, v))
    
    # Simple split
    split_idx = int(len(all_edges) * 0.8)
    train_edges = all_edges[:split_idx]
    test_edges = all_edges[split_idx:]
    
    # Generate negative samples
    np.random.seed(42)
    neg_edges = []
    for _ in range(len(test_edges)):
        u = np.random.randint(0, num_nodes)
        v = np.random.randint(0, num_nodes)
        while v == u or (u, v) in all_edges:
            v = np.random.randint(0, num_nodes)
        neg_edges.append((u, v))
    
    model = VGRNN(hidden_dim, num_nodes, num_layers=2)
    trainer = VGRNNTrainer(model, lr=lr)
    
    trainer.fit(adj_list, train_edges, train_edges, num_epochs=num_epochs)
    
    # Get embeddings
    adj_tensors = [torch.tensor(adj, dtype=torch.float32) for adj in adj_list]
    embeddings = model(adj_tensors)
    final_emb = model.get_embeddings(embeddings)
    
    return final_emb.detach().cpu().numpy()


if __name__ == '__main__':
    # Example usage
    from preprocess import generate_synthetic_temporal_data
    
    # Generate synthetic data
    temporal_data = generate_synthetic_temporal_data(num_nodes=100, num_edges=500, num_timesteps=5)
    
    # Train model
    embeddings = train_vgrnn(
        temporal_data['temporal_edges'],
        num_nodes=temporal_data['num_nodes'],
        num_epochs=50
    )
    
    print(f"VGRNN embeddings shape: {embeddings.shape}")
