#!/usr/bin/env python3
"""
Evaluation and Comparison Script
Compares CLE-Net, DynamicTriad, and VGRNN benchmark results.
"""

import argparse
import json
import os
import pickle
import pandas as pd
import numpy as np
from sklearn.metrics import roc_auc_score, average_precision_score, precision_recall_curve


def load_json_results(filepath):
    """Load results from JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)


def compute_baseline_metrics(embeddings, pos_edges, neg_edges):
    """Compute link prediction metrics for baseline models."""
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


def compute_precision_at_k(pos_edges, neg_edges, embeddings, k_values=[10, 50, 100]):
    """Compute Precision@K metrics."""
    # Score all edges
    edge_scores = []
    for u, v in pos_edges:
        emb_u = embeddings[u]
        emb_v = embeddings[v]
        score = np.dot(emb_u, emb_v)
        edge_scores.append((u, v, score, 1))
    
    for u, v in neg_edges:
        emb_u = embeddings[u]
        emb_v = embeddings[v]
        score = np.dot(emb_u, emb_v)
        edge_scores.append((u, v, score, 0))
    
    # Sort by score
    edge_scores.sort(key=lambda x: x[2], reverse=True)
    
    results = {}
    for k in k_values:
        top_k = edge_scores[:k]
        relevant = sum(1 for _, _, _, label in top_k if label == 1)
        results[f'precision@{k}'] = relevant / k
    
    return results


def compute_recall_at_k(pos_edges, neg_edges, embeddings, k_values=[10, 50, 100]):
    """Compute Recall@K metrics."""
    total_positives = len(pos_edges)
    
    edge_scores = []
    for u, v in pos_edges:
        emb_u = embeddings[u]
        emb_v = embeddings[v]
        score = np.dot(emb_u, emb_v)
        edge_scores.append((u, v, score, 1))
    
    for u, v in neg_edges:
        emb_u = embeddings[u]
        emb_v = embeddings[v]
        score = np.dot(emb_u, emb_v)
        edge_scores.append((u, v, score, 0))
    
    edge_scores.sort(key=lambda x: x[2], reverse=True)
    
    results = {}
    for k in k_values:
        top_k = edge_scores[:k]
        retrieved = sum(1 for _, _, _, label in top_k if label == 1)
        results[f'recall@{k}'] = retrieved / total_positives if total_positives > 0 else 0
    
    return results


def compute_temporal_drift(embeddings_sequence):
    """Compute embedding stability/drift over time."""
    drifts = []
    for i in range(1, len(embeddings_sequence)):
        emb_prev = embeddings_sequence[i-1]
        emb_curr = embeddings_sequence[i]
        
        # Compute Frobenius norm of difference
        diff = emb_curr - emb_prev
        drift = np.linalg.norm(diff, 'fro') / np.linalg.norm(emb_prev, 'fro')
        drifts.append(drift)
    
    return {
        'mean_drift': np.mean(drifts),
        'std_drift': np.std(drifts),
        'max_drift': np.max(drifts),
        'drift_sequence': drifts
    }


def evaluate_dynamic_triad_results(results_file, data_file):
    """Evaluate DynamicTriad results."""
    results = load_json_results(results_file)
    
    with open(data_file, 'rb') as f:
        data = pickle.load(f)
    
    embeddings = np.array(results['embeddings'])
    pos_edges = [(e[0], e[1]) for e in data['splits']['test']['pos']]
    neg_edges = [(e[0], e[1]) for e in data['splits']['test']['neg']]
    
    link_metrics = compute_baseline_metrics(embeddings, pos_edges, neg_edges)
    precision_k = compute_precision_at_k(pos_edges, neg_edges, embeddings)
    recall_k = compute_recall_at_k(pos_edges, neg_edges, embeddings)
    
    # Temporal stability
    if 'temporal_embeddings' in results:
        temporal_drift = compute_temporal_drift(results['temporal_embeddings'])
    else:
        temporal_drift = {'mean_drift': 0, 'std_drift': 0}
    
    return {
        'model': 'DynamicTriad',
        'link_prediction': link_metrics,
        'precision_at_k': precision_k,
        'recall_at_k': recall_k,
        'temporal_stability': temporal_drift
    }


def evaluate_vgrnn_results(results_file, data_file):
    """Evaluate VGRNN results."""
    results = load_json_results(results_file)
    
    with open(data_file, 'rb') as f:
        data = pickle.load(f)
    
    embeddings = np.array(results['embeddings'])
    pos_edges = [(e[0], e[1]) for e in data['splits']['test']['pos']]
    neg_edges = [(e[0], e[1]) for e in data['splits']['test']['neg']]
    
    link_metrics = compute_baseline_metrics(embeddings, pos_edges, neg_edges)
    precision_k = compute_precision_at_k(pos_edges, neg_edges, embeddings)
    recall_k = compute_recall_at_k(pos_edges, neg_edges, embeddings)
    
    return {
        'model': 'VGRNN',
        'link_prediction': link_metrics,
        'precision_at_k': precision_k,
        'recall_at_k': recall_k,
        'variational_metrics': results.get('variational_metrics', {})
    }


def evaluate_cle_net_results(results_file, data_file):
    """Evaluate CLE-Net results."""
    results = load_json_results(results_file)
    
    with open(data_file, 'rb') as f:
        data = pickle.load(f)
    
    # CLE-Net specific metrics
    rule_metrics = results.get('rule_discovery', {})
    
    return {
        'model': 'CLE-Net',
        'link_prediction': results.get('link_prediction', {}),
        'rule_discovery': {
            'num_rules': rule_metrics.get('num_rules', 0),
            'avg_support': rule_metrics.get('avg_support', 0),
            'avg_confidence': rule_metrics.get('avg_confidence', 0),
            'rule_precision': rule_metrics.get('rule_precision', 0),
            'rule_recall': rule_metrics.get('rule_recall', 0),
            'rule_stability_cv': rule_metrics.get('rule_stability_cv', 0)
        }
    }


def generate_comparison_table(dataset, cle_results, triad_results, vgrnn_results):
    """Generate comparison table."""
    table_data = []
    
    # CLE-Net row
    cle_row = {
        'Dataset': dataset,
        'Model': 'CLE-Net',
        'Link Pred AUC': cle_results.get('link_prediction', {}).get('auc', 'N/A'),
        'Avg Precision': cle_results.get('link_prediction', {}).get('average_precision', 'N/A'),
        'Rule Precision': cle_results.get('rule_discovery', {}).get('rule_precision', 'N/A'),
        'Rule Recall': cle_results.get('rule_discovery', {}).get('rule_recall', 'N/A'),
        'Rule Stability': 1 - cle_results.get('rule_discovery', {}).get('rule_stability_cv', 1)
    }
    table_data.append(cle_row)
    
    # DynamicTriad row
    triad_row = {
        'Dataset': dataset,
        'Model': 'DynamicTriad',
        'Link Pred AUC': triad_results.get('link_prediction', {}).get('auc', 'N/A'),
        'Avg Precision': triad_results.get('link_prediction', {}).get('average_precision', 'N/A'),
        'Rule Precision': 'N/A',
        'Rule Recall': 'N/A',
        'Rule Stability': 1 - triad_results.get('temporal_stability', {}).get('mean_drift', 0)
    }
    table_data.append(triad_row)
    
    # VGRNN row
    vgrnn_row = {
        'Dataset': dataset,
        'Model': 'VGRNN',
        'Link Pred AUC': vgrnn_results.get('link_prediction', {}).get('auc', 'N/A'),
        'Avg Precision': vgrnn_results.get('link_prediction', {}).get('average_precision', 'N/A'),
        'Rule Precision': 'N/A',
        'Rule Recall': 'N/A',
        'Rule Stability': 'N/A'
    }
    table_data.append(vgrnn_row)
    
    return pd.DataFrame(table_data)


def main():
    parser = argparse.ArgumentParser(description='Evaluate and compare benchmark results')
    parser.add_argument('--cle-net', type=str, help='Path to CLE-Net results JSON')
    parser.add_argument('--triad', type=str, help='Path to DynamicTriad results JSON')
    parser.add_argument('--vgrnn', type=str, help='Path to VGRNN results JSON')
    parser.add_argument('--dataset', type=str, default='cora', help='Dataset name')
    parser.add_argument('--data', type=str, help='Path to preprocessed data')
    parser.add_argument('--output', type=str, default='results/final_comparison.csv',
                        help='Output path for comparison CSV')
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    data_file = args.data or f'benchmarking/data/{args.dataset}_temporal.pkl'
    
    # Evaluate each model
    results = {}
    
    if args.cle_net and os.path.exists(args.cle_net):
        results['CLE-Net'] = evaluate_cle_net_results(args.cle_net, data_file)
    
    if args.triad and os.path.exists(args.triad):
        results['DynamicTriad'] = evaluate_dynamic_triad_results(args.triad, data_file)
    
    if args.vgrnn and os.path.exists(args.vgrnn):
        results['VGRNN'] = evaluate_vgrnn_results(args.vgrnn, data_file)
    
    # Generate comparison table
    if len(results) > 0:
        df = generate_comparison_table(args.dataset, 
                                       results.get('CLE-Net', {}),
                                       results.get('DynamicTriad', {}),
                                       results.get('VGRNN', {}))
        
        # Save to CSV
        df.to_csv(args.output, index=False)
        print(f"Comparison results saved to {args.output}")
        print("\nComparison Table:")
        print(df.to_string(index=False))
        
        # Save detailed results
        detailed_output = args.output.replace('.csv', '_detailed.json')
        with open(detailed_output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nDetailed results saved to {detailed_output}")
    else:
        print("No results to compare. Please provide at least one result file.")


if __name__ == '__main__':
    main()
