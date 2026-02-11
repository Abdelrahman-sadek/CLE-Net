#!/usr/bin/env python3
"""
Synthetic Dataset Generator with Ground-Truth Rules

Generates temporal graphs with known community structures and explicit rules
for evaluating CLE-Net's rule discovery capabilities.
"""

import numpy as np
import pickle
import random
from collections import defaultdict


def generate_synthetic_dataset(
    num_nodes=500,
    num_timesteps=10,
    num_communities=5,
    num_rules=10,
    edge_prob_base=0.01,
    edge_prob_rule=0.3,
    seed=42
):
    """
    Generate a synthetic temporal graph with ground-truth rules.
    
    Args:
        num_nodes: Number of nodes
        num_timesteps: Number of temporal snapshots
        num_communities: Number of communities
        num_rules: Number of ground-truth rules to embed
        edge_prob_base: Base edge probability
        edge_prob_rule: Edge probability for rule-following pairs
        seed: Random seed
        
    Returns:
        Dictionary containing temporal edges and ground-truth rules
    """
    np.random.seed(seed)
    random.seed(seed)
    
    # Assign nodes to communities
    community_assignments = np.random.randint(0, num_communities, num_nodes)
    
    # Create ground-truth rules based on community structure
    rules = []
    rule_pairs = []
    
    # Generate rules: community X nodes tend to connect to community Y nodes
    community_rules = defaultdict(list)
    for i in range(num_rules):
        source_comm = np.random.randint(0, num_communities)
        target_comm = np.random.randint(0, num_communities)
        while target_comm == source_comm:
            target_comm = np.random.randint(0, num_communities)
        
        source_nodes = np.where(community_assignments == source_comm)[0]
        target_nodes = np.where(community_assignments == target_comm)[0]
        
        if len(source_nodes) > 0 and len(target_nodes) > 0:
            rule = {
                'antecedent': f'community({source_comm})',
                'consequent': f'community({target_comm})',
                'source_community': int(source_comm),
                'target_community': int(target_comm),
                'source_nodes': source_nodes.tolist(),
                'target_nodes': target_nodes.tolist()
            }
            community_rules[(source_comm, target_comm)].append(rule)
            rules.append(rule)
    
    # Generate temporal edges
    temporal_edges = []
    all_edges = []
    
    for t in range(num_timesteps):
        edges = []
        
        # Base edges: random connections
        for i in range(num_nodes):
            for j in range(i + 1, num_nodes):
                if np.random.random() < edge_prob_base:
                    edges.append((i, j))
                    all_edges.append((i, j))
        
        # Rule-based edges: community-driven connections
        for rule in rules:
            source_nodes = rule['source_nodes']
            target_nodes = rule['target_nodes']
            
            # Add edges between communities following the rule
            for src in source_nodes[:min(20, len(source_nodes))]:
                for tgt in target_nodes[:min(20, len(target_nodes))]:
                    if src < tgt:  # Avoid duplicates
                        if np.random.random() < edge_prob_rule:
                            edges.append((src, tgt))
                            all_edges.append((src, tgt))
        
        temporal_edges.append(edges)
    
    # Create train/test splits
    num_train_timesteps = int(num_timesteps * 0.8)
    
    train_edges = [e for t_edges in temporal_edges[:num_train_timesteps] for e in t_edges]
    test_edges = [e for t_edges in temporal_edges[num_train_timesteps:] for e in t_edges]
    
    # Generate negative edges for evaluation
    all_pos_edges = set([tuple(sorted(e)) for e in all_edges])
    
    neg_edges = []
    while len(neg_edges) < len(test_edges):
        u, v = random.sample(range(num_nodes), 2)
        pair = tuple(sorted([u, v]))
        if pair not in all_pos_edges:
            neg_edges.append(pair)
    
    # Shuffle edges
    random.shuffle(train_edges)
    random.shuffle(test_edges)
    random.shuffle(neg_edges)
    
    # Limit test edges
    test_edges = test_edges[:len(neg_edges)]
    
    return {
        'num_nodes': num_nodes,
        'num_timesteps': num_timesteps,
        'num_communities': num_communities,
        'num_rules': len(rules),
        'temporal_edges': temporal_edges,
        'ground_truth_rules': rules,
        'community_assignments': community_assignments.tolist(),
        'splits': {
            'train': {
                'pos': train_edges,
                'neg': []
            },
            'test': {
                'pos': test_edges,
                'neg': neg_edges
            }
        }
    }


def generate_reddit_like_dataset(
    num_users=1000,
    num_posts=500,
    num_timesteps=10,
    seed=42
):
    """
    Generate a Reddit-like synthetic dataset with user-post interactions.
    
    Simulates users posting and commenting in communities over time.
    """
    np.random.seed(seed)
    random.seed(seed)
    
    # Define communities
    num_communities = 10
    users_per_community = num_users // num_communities
    
    # User-community assignments
    user_communities = {}
    for c in range(num_communities):
        start = c * users_per_community
        end = min((c + 1) * users_per_community, num_users)
        for u in range(start, end):
            user_communities[u] = c
    
    # Generate temporal interactions
    temporal_edges = []
    
    for t in range(num_timesteps):
        edges = []
        
        # User-user interactions (within communities)
        for c in range(num_communities):
            community_users = [u for u, uc in user_communities.items() if uc == c]
            
            # Dense intra-community interactions
            for i, u in enumerate(community_users[:50]):  # Active users
                for v in community_users[i+1:i+10]:  # Connect to 9 others
                    if np.random.random() < 0.3:
                        edges.append((u, v))
        
        # Cross-community interactions (rare)
        for _ in range(100):
            c1, c2 = random.sample(range(num_communities), 2)
            u = random.choice([u for u, uc in user_communities.items() if uc == c1])
            v = random.choice([u for u, uc in user_communities.items() if uc == c2])
            if np.random.random() < 0.05:  # Rare cross-community edges
                edges.append((u, v))
        
        temporal_edges.append(edges)
    
    # Create splits
    num_train = int(num_timesteps * 0.8)
    train_edges = [e for t_edges in temporal_edges[:num_train] for e in t_edges]
    test_edges = [e for t_edges in temporal_edges[num_train:] for e in t_edges]
    
    # Negative edges
    all_pos = set([tuple(sorted(e)) for e in train_edges + test_edges])
    neg_edges = []
    while len(neg_edges) < len(test_edges):
        u, v = random.sample(range(num_users), 2)
        pair = tuple(sorted([u, v]))
        if pair not in all_pos:
            neg_edges.append(pair)
    
    random.shuffle(test_edges)
    random.shuffle(neg_edges)
    test_edges = test_edges[:len(neg_edges)]
    
    return {
        'num_nodes': num_users,
        'num_timesteps': num_timesteps,
        'num_communities': num_communities,
        'temporal_edges': temporal_edges,
        'community_assignments': [user_communities.get(i, 0) for i in range(num_users)],
        'splits': {
            'train': {'pos': train_edges, 'neg': []},
            'test': {'pos': test_edges, 'neg': neg_edges}
        }
    }


if __name__ == '__main__':
    print("Generating synthetic datasets...")
    
    # Generate synthetic dataset with ground-truth rules
    print("\n1. Generating synthetic dataset with ground-truth rules...")
    synthetic = generate_synthetic_dataset(
        num_nodes=500,
        num_timesteps=10,
        num_communities=5,
        num_rules=10
    )
    
    print(f"   Nodes: {synthetic['num_nodes']}")
    print(f"   Timesteps: {synthetic['num_timesteps']}")
    print(f"   Communities: {synthetic['num_communities']}")
    print(f"   Ground-truth rules: {synthetic['num_rules']}")
    print(f"   Total edges: {sum(len(e) for e in synthetic['temporal_edges'])}")
    
    # Save synthetic dataset
    with open('benchmarking/data/synthetic_temporal.pkl', 'wb') as f:
        pickle.dump(synthetic, f)
    print("   Saved to: benchmarking/data/synthetic_temporal.pkl")
    
    # Generate Reddit-like dataset
    print("\n2. Generating Reddit-like dataset...")
    reddit = generate_reddit_like_dataset(
        num_users=1000,
        num_timesteps=10
    )
    
    print(f"   Users: {reddit['num_nodes']}")
    print(f"   Timesteps: {reddit['num_timesteps']}")
    print(f"   Communities: {reddit['num_communities']}")
    print(f"   Total edges: {sum(len(e) for e in reddit['temporal_edges'])}")
    
    # Save Reddit-like dataset
    with open('benchmarking/data/reddit_temporal.pkl', 'wb') as f:
        pickle.dump(reddit, f)
    print("   Saved to: benchmarking/data/reddit_temporal.pkl")
    
    print("\nSynthetic datasets generated successfully!")
