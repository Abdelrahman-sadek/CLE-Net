# Dynamic Triad Implementation
# Based on "Dynamic Triad Closure Model for Predicting Temporal Networks" (Zhou et al., 2018)

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
import numpy as np


class TriadDataset(Dataset):
    """Dataset for DynamicTriad training."""
    
    def __init__(self, temporal_edges, num_nodes, time_window=5, neg_samples=5):
        self.samples = []
        self.num_nodes = num_nodes
        self.time_window = time_window
        self.neg_samples = neg_samples
        
        # Build edge dictionary with timestamps
        self.edge_dict = {}
        for t, edges in enumerate(temporal_edges):
            for u, v in edges:
                if u > v:
                    u, v = v, u
                key = (u, v)
                if key not in self.edge_dict:
                    self.edge_dict[key] = []
                self.edge_dict[key].append(t)
        
        # Generate samples
        self._generate_samples()
    
    def _generate_samples(self):
        """Generate training samples."""
        for (u, v), timestamps in self.edge_dict.items():
            for t in timestamps:
                if t < self.time_window - 1:
                    continue
                
                # Get window of past edges
                window_start = max(0, t - self.time_window + 1)
                
                # Positive sample: edge exists
                self.samples.append({
                    'u': u,
                    'v': v,
                    'w': -1,  # Use -1 to indicate no third node
                    'window_start': window_start,
                    't': t,
                    'label': 1
                })
                
                # Negative samples: non-existent edges
                for _ in range(self.neg_samples):
                    w = np.random.randint(0, self.num_nodes)
                    while w == u or w == v:
                        w = np.random.randint(0, self.num_nodes)
                    
                    self.samples.append({
                        'u': u,
                        'v': v,
                        'w': w,
                        'window_start': window_start,
                        't': t,
                        'label': 0
                    })
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        return self.samples[idx]


def custom_collate_fn(batch):
    """Custom collate function that handles varying sample formats."""
    u = [item['u'] for item in batch]
    v = [item['v'] for item in batch]
    w = [item['w'] for item in batch]
    labels = [item['label'] for item in batch]
    window_start = [item['window_start'] for item in batch]
    
    return {
        'u': u,
        'v': v,
        'w': w,
        'labels': labels,
        'window_start': window_start
    }


class DynamicTriad(nn.Module):
    """
    Dynamic Triad Closure Model for temporal network embedding.
    
    This model learns embeddings that capture the tendency of open triads
    to close over time in evolving networks.
    """
    
    def __init__(self, num_nodes, embedding_dim=64, time_window=5, 
                 hidden_dim=32, num_layers=2, dropout=0.5):
        super(DynamicTriad, self).__init__()
        
        self.num_nodes = num_nodes
        self.embedding_dim = embedding_dim
        self.time_window = time_window
        
        # Node embeddings
        self.node_embedding = nn.Embedding(num_nodes, embedding_dim)
        
        # Triad closure encoder (3 nodes)
        self.triad_encoder = nn.Sequential(
            nn.Linear(embedding_dim * 3, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1)
        )
        
        # Link prediction encoder (2 nodes)
        self.link_encoder = nn.Sequential(
            nn.Linear(embedding_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1)
        )
        
        # Initialize weights
        self._init_weights()
    
    def _init_weights(self):
        """Initialize weights using Xavier initialization."""
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                if module.bias is not None:
                    nn.init.zeros_(module.bias)
    
    def forward(self, u, v, w=None, window_edges=None):
        """
        Forward pass.
        
        Args:
            u: Source nodes [batch_size]
            v: Target nodes [batch_size]
            w: Third node for triad (optional, -1 for link prediction) [batch_size]
            window_edges: Number of edges in time window [batch_size]
            
        Returns:
            Logits for link/triad closure prediction
        """
        # Get node embeddings
        emb_u = self.node_embedding(u)
        emb_v = self.node_embedding(v)
        
        # Check if this is triad prediction or link prediction
        # w tensor contains -1 for link prediction samples
        is_triad = w is not None and (w >= 0).all()
        
        if is_triad:
            # Triad closure prediction with third node
            emb_w = self.node_embedding(w)
            combined = torch.cat([emb_u, emb_v, emb_w], dim=-1)
            logits = self.triad_encoder(combined)
        else:
            # Link prediction
            combined = torch.cat([emb_u, emb_v], dim=-1)
            logits = self.link_encoder(combined)
        
        return logits.squeeze(-1)
    
    def get_embeddings(self, nodes=None):
        """Get embeddings for specified nodes or all nodes."""
        if nodes is None:
            nodes = torch.arange(self.num_nodes)
        
        with torch.no_grad():
            embeddings = self.node_embedding(nodes)
        
        return embeddings.cpu().numpy()


class DynamicTriadTrainer:
    """Trainer for DynamicTriad model."""
    
    def __init__(self, model, lr=0.01, weight_decay=1e-5):
        self.model = model
        self.optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)
        self.criterion = nn.BCEWithLogitsLoss()
    
    def train_epoch(self, dataloader):
        """Train for one epoch."""
        self.model.train()
        total_loss = 0
        
        for batch in dataloader:
            u = torch.tensor(batch['u']).long()
            v = torch.tensor(batch['v']).long()
            labels = torch.tensor(batch['labels']).float()
            w = torch.tensor(batch['w']).long()
            
            self.optimizer.zero_grad()
            
            logits = self.model(u, v, w)
            loss = self.criterion(logits, labels)
            loss.backward()
            self.optimizer.step()
            
            total_loss += loss.item()
        
        return total_loss / len(dataloader)
    
    def evaluate(self, dataloader):
        """Evaluate the model."""
        self.model.eval()
        all_preds = []
        all_labels = []
        
        with torch.no_grad():
            for batch in dataloader:
                u = torch.tensor(batch['u']).long()
                v = torch.tensor(batch['v']).long()
                labels = torch.tensor(batch['labels']).float()
                w = torch.tensor(batch['w']).long()
                
                logits = self.model(u, v, w)
                preds = torch.sigmoid(logits) > 0.5
                
                all_preds.extend(preds.cpu().numpy())
                all_labels.extend(labels.cpu().numpy())
        
        accuracy = np.mean(np.array(all_preds) == np.array(all_labels))
        return accuracy
    
    def fit(self, temporal_edges, num_epochs=100, batch_size=256):
        """Train the model."""
        dataset = TriadDataset(temporal_edges, self.model.num_nodes)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True, collate_fn=custom_collate_fn)
        
        best_acc = 0
        for epoch in range(num_epochs):
            loss = self.train_epoch(dataloader)
            acc = self.evaluate(dataloader)
            
            if acc > best_acc:
                best_acc = acc
                best_state = {k: v.clone() for k, v in self.model.state_dict().items()}
            
            if (epoch + 1) % 10 == 0:
                print(f"Epoch {epoch + 1}/{num_epochs}, Loss: {loss:.4f}, Acc: {acc:.4f}")
        
        self.model.load_state_dict(best_state)
        return best_acc


def train_dynamic_triad(temporal_edges, num_nodes, embedding_dim=64, 
                       num_epochs=100, lr=0.01):
    """Train DynamicTriad model and return embeddings."""
    model = DynamicTriad(num_nodes, embedding_dim=embedding_dim)
    trainer = DynamicTriadTrainer(model, lr=lr)
    
    trainer.fit(temporal_edges, num_epochs=num_epochs)
    
    return model.get_embeddings()


if __name__ == '__main__':
    # Example usage
    from preprocess import generate_synthetic_temporal_data
    
    # Generate synthetic data
    temporal_data = generate_synthetic_temporal_data(num_nodes=100, num_edges=500, num_timesteps=5)
    
    # Train model
    embeddings = train_dynamic_triad(
        temporal_data['temporal_edges'],
        num_nodes=temporal_data['num_nodes'],
        num_epochs=50
    )
    
    print(f"Generated embeddings with shape: {embeddings.shape}")
