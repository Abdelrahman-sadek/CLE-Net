#!/usr/bin/env python3
"""
Model Comparison Visualization Script
Generates comparison tables and graphs for benchmark results.
"""

import argparse
import json
import os
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

from sklearn.metrics import roc_curve, auc, precision_recall_curve, average_precision_score


def load_results(filepath):
    """Load results from JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)


def load_data(filepath):
    """Load preprocessed data."""
    with open(filepath, 'rb') as f:
        return pickle.load(f)


def compute_roc_pr_curves(embeddings, pos_edges, neg_edges):
    """Compute ROC and PR curve data."""
    def extract_edge(edge):
        if len(edge) == 2:
            return edge[0], edge[1]
        return edge[0], edge[1]
    
    # Compute scores
    pos_scores = []
    for edge in pos_edges:
        u, v = extract_edge(edge)
        emb_u = embeddings[u]
        emb_v = embeddings[v]
        score = np.dot(emb_u, emb_v) / (np.linalg.norm(emb_u) * np.linalg.norm(emb_v) + 1e-8)
        pos_scores.append(score)
    
    neg_scores = []
    for edge in neg_edges:
        u, v = extract_edge(edge)
        emb_u = embeddings[u]
        emb_v = embeddings[v]
        score = np.dot(emb_u, emb_v) / (np.linalg.norm(emb_u) * np.linalg.norm(emb_v) + 1e-8)
        neg_scores.append(score)
    
    all_scores = pos_scores + neg_scores
    all_labels = [1] * len(pos_scores) + [0] * len(neg_scores)
    
    # ROC curve
    fpr, tpr, _ = roc_curve(all_labels, all_scores)
    roc_auc = auc(fpr, tpr)
    
    # PR curve
    precision, recall, _ = precision_recall_curve(all_labels, all_scores)
    ap = average_precision_score(all_labels, all_scores)
    
    return {
        'fpr': fpr.tolist(),
        'tpr': tpr.tolist(),
        'roc_auc': roc_auc,
        'precision': precision.tolist(),
        'recall': recall.tolist(),
        'ap': ap
    }


def generate_comparison_table(results_dict, data_file, output_path):
    """Generate comparison table."""
    # Load data for computing metrics
    data = load_data(data_file)
    splits = data['splits']
    
    table_data = []
    
    for model_name, results in results_dict.items():
        row = {
            'Dataset': results.get('dataset', 'Unknown'),
            'Model': model_name
        }
        
        # Link prediction metrics
        if 'embeddings' in results:
            try:
                embeddings = np.array(results['embeddings'])
                pos_edges = splits['test']['pos']
                neg_edges = splits['test']['neg']
                curves = compute_roc_pr_curves(embeddings, pos_edges, neg_edges)
                row['AUC'] = curves['roc_auc']
                row['Avg Precision'] = curves['ap']
            except:
                row['AUC'] = 'N/A'
                row['Avg Precision'] = 'N/A'
        else:
            row['AUC'] = results.get('link_prediction', {}).get('auc', 'N/A')
            row['Avg Precision'] = results.get('link_prediction', {}).get('average_precision', 'N/A')
        
        # CLE-Net specific metrics
        rule_metrics = results.get('rule_discovery', {})
        row['Rule Precision'] = rule_metrics.get('rule_precision', 'N/A')
        row['Rule Recall'] = rule_metrics.get('rule_recall', 'N/A')
        row['Num Rules'] = rule_metrics.get('num_rules', 'N/A')
        
        # Stability (higher is better)
        stability_cv = rule_metrics.get('rule_stability_cv', 1)
        if isinstance(stability_cv, (int, float)) and stability_cv > 0:
            row['Stability'] = 1 / (1 + stability_cv)  # Convert CV to stability score
        else:
            row['Stability'] = 'N/A'
        
        table_data.append(row)
    
    # Create DataFrame and save
    df = pd.DataFrame(table_data)
    df.to_csv(output_path.replace('.png', '_table.csv'), index=False)
    
    # Print table
    print("\n" + "="*80)
    print("MODEL COMPARISON TABLE")
    print("="*80)
    print(df.to_string(index=False))
    print("="*80 + "\n")
    
    return df


def plot_roc_curves(results_dict, data_file, output_path):
    """Plot ROC curves for all models."""
    data = load_data(data_file)
    splits = data['splits']
    pos_edges = splits['test']['pos']
    neg_edges = splits['test']['neg']
    
    plt.figure(figsize=(10, 8))
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    color_idx = 0
    
    for model_name, results in results_dict.items():
        if 'embeddings' not in results:
            continue
        
        try:
            embeddings = np.array(results['embeddings'])
            curves = compute_roc_pr_curves(embeddings, pos_edges, neg_edges)
            
            fpr = curves['fpr']
            tpr = curves['tpr']
            roc_auc = curves['roc_auc']
            
            plt.plot(fpr, tpr, color=colors[color_idx % len(colors)], 
                    lw=2, label=f'{model_name} (AUC = {roc_auc:.4f})')
            color_idx += 1
        except Exception as e:
            print(f"Warning: Could not plot ROC for {model_name}: {e}")
    
    plt.plot([0, 1], [0, 1], 'k--', lw=1, label='Random')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate', fontsize=12)
    plt.ylabel('True Positive Rate', fontsize=12)
    plt.title('ROC Curves - Link Prediction Comparison', fontsize=14)
    plt.legend(loc='lower right', fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    plt.savefig(output_path.replace('.png', '_roc.png'), dpi=150)
    plt.close()
    
    print(f"ROC curves saved to {output_path.replace('.png', '_roc.png')}")


def plot_precision_recall_curves(results_dict, data_file, output_path):
    """Plot Precision-Recall curves for all models."""
    data = load_data(data_file)
    splits = data['splits']
    pos_edges = splits['test']['pos']
    neg_edges = splits['test']['neg']
    
    plt.figure(figsize=(10, 8))
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    color_idx = 0
    
    for model_name, results in results_dict.items():
        if 'embeddings' not in results:
            continue
        
        try:
            embeddings = np.array(results['embeddings'])
            curves = compute_roc_pr_curves(embeddings, pos_edges, neg_edges)
            
            precision = curves['precision']
            recall = curves['recall']
            ap = curves['ap']
            
            plt.plot(recall, precision, color=colors[color_idx % len(colors)], 
                    lw=2, label=f'{model_name} (AP = {ap:.4f})')
            color_idx += 1
        except Exception as e:
            print(f"Warning: Could not plot PR curve for {model_name}: {e}")
    
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('Recall', fontsize=12)
    plt.ylabel('Precision', fontsize=12)
    plt.title('Precision-Recall Curves - Link Prediction Comparison', fontsize=14)
    plt.legend(loc='lower left', fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    plt.savefig(output_path.replace('.png', '_pr.png'), dpi=150)
    plt.close()
    
    print(f"PR curves saved to {output_path.replace('.png', '_pr.png')}")


def plot_metric_bar_chart(results_dict, output_path):
    """Plot bar chart comparing metrics."""
    metrics = ['AUC', 'Avg Precision']
    models = list(results_dict.keys())
    
    # Extract metrics
    auc_values = []
    ap_values = []
    
    for model_name, results in results_dict.items():
        auc_val = results.get('link_prediction', {}).get('auc', 0)
        ap_val = results.get('link_prediction', {}).get('average_precision', 0)
        auc_values.append(auc_val if auc_val else 0)
        ap_values.append(ap_val if ap_val else 0)
    
    # Create bar chart
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # AUC bar chart
    ax1 = axes[0]
    bars1 = ax1.bar(models, auc_values, color=['#1f77b4', '#ff7f0e', '#2ca02c'])
    ax1.set_ylabel('AUC Score', fontsize=12)
    ax1.set_title('Link Prediction AUC Comparison', fontsize=14)
    ax1.set_ylim([0, 1])
    ax1.axhline(y=0.5, color='red', linestyle='--', label='Random baseline')
    ax1.legend()
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for bar, val in zip(bars1, auc_values):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f'{val:.4f}', ha='center', va='bottom', fontsize=10)
    
    # Average Precision bar chart
    ax2 = axes[1]
    bars2 = ax2.bar(models, ap_values, color=['#1f77b4', '#ff7f0e', '#2ca02c'])
    ax2.set_ylabel('Average Precision', fontsize=12)
    ax2.set_title('Average Precision Comparison', fontsize=14)
    ax2.set_ylim([0, 1])
    ax2.axhline(y=len(pos_edges)/(len(pos_edges)+len(neg_edges)) if 'pos_edges' in dir() else 0.5, 
               color='red', linestyle='--', label='Baseline')
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for bar, val in zip(bars2, ap_values):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f'{val:.4f}', ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(output_path.replace('.png', '_bars.png'), dpi=150)
    plt.close()
    
    print(f"Bar charts saved to {output_path.replace('.png', '_bars.png')}")


def plot_rule_comparison(results_dict, output_path):
    """Plot rule-related metrics for CLE-Net."""
    cle_results = results_dict.get('CLE-Net', {})
    rule_metrics = cle_results.get('rule_discovery', {})
    
    if rule_metrics.get('num_rules', 0) == 0:
        print("No rule metrics to plot for CLE-Net")
        return
    
    metrics = ['Rule Precision', 'Rule Recall']
    values = [
        rule_metrics.get('rule_precision', 0),
        rule_metrics.get('rule_recall', 0)
    ]
    
    plt.figure(figsize=(8, 6))
    
    bars = plt.bar(metrics, values, color=['#9467bd', '#8c564b'])
    
    plt.ylabel('Score', fontsize=12)
    plt.title('CLE-Net Rule Discovery Metrics', fontsize=14)
    plt.ylim([0, 1])
    plt.grid(True, alpha=0.3, axis='y')
    
    # Add value labels
    for bar, val in zip(bars, values):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f'{val:.4f}', ha='center', va='bottom', fontsize=12)
    
    plt.tight_layout()
    plt.savefig(output_path.replace('.png', '_rules.png'), dpi=150)
    plt.close()
    
    print(f"Rule metrics saved to {output_path.replace('.png', '_rules.png')}")


def plot_temporal_drift(results_dict, output_path):
    """Plot temporal embedding drift if available."""
    cle_results = results_dict.get('CLE-Net', {})
    stability = cle_results.get('temporal_stability', [])
    
    if not stability:
        print("No temporal stability data to plot")
        return
    
    plt.figure(figsize=(10, 5))
    
    plt.plot(range(1, len(stability)+1), stability, 'o-', color='#17becf', lw=2, markersize=8)
    
    plt.xlabel('Time Window', fontsize=12)
    plt.ylabel('Number of Discovered Rules', fontsize=12)
    plt.title('CLE-Net Rule Discovery Stability Over Time', fontsize=14)
    plt.grid(True, alpha=0.3)
    
    # Add trend line
    z = np.polyfit(range(1, len(stability)+1), stability, 1)
    p = np.poly1d(z)
    plt.plot(range(1, len(stability)+1), p(range(1, len(stability)+1)), 
             '--', color='red', alpha=0.7, label='Trend')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig(output_path.replace('.png', '_drift.png'), dpi=150)
    plt.close()
    
    print(f"Temporal drift plot saved to {output_path.replace('.png', '_drift.png')}")


def main():
    parser = argparse.ArgumentParser(description='Generate comparison visualizations')
    parser.add_argument('--cle-net', type=str, help='Path to CLE-Net results JSON')
    parser.add_argument('--triad', type=str, help='Path to DynamicTriad results JSON')
    parser.add_argument('--vgrnn', type=str, help='Path to VGRNN results JSON')
    parser.add_argument('--dataset', type=str, default='cora', help='Dataset name')
    parser.add_argument('--data', type=str, help='Path to preprocessed data')
    parser.add_argument('--output', type=str, default='results/comparison',
                        help='Output prefix for files')
    
    args = parser.parse_args()
    
    # Build results dictionary
    results_dict = {}
    
    if args.cle_net and os.path.exists(args.cle_net):
        results_dict['CLE-Net'] = load_results(args.cle_net)
    
    if args.triad and os.path.exists(args.triad):
        results_dict['DynamicTriad'] = load_results(args.triad)
    
    if args.vgrnn and os.path.exists(args.vgrnn):
        results_dict['VGRNN'] = load_results(args.vgrnn)
    
    if not results_dict:
        print("Error: No result files provided or found.")
        return
    
    # Set data file path
    data_file = args.data or f'benchmarking/data/{args.dataset}_temporal.pkl'
    
    # Create output directory
    output_dir = os.path.dirname(args.output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # Generate visualizations
    print("\n" + "="*60)
    print("GENERATING COMPARISON VISUALIZATIONS")
    print("="*60 + "\n")
    
    # Comparison table
    df = generate_comparison_table(results_dict, data_file, args.output)
    
    # ROC curves
    plot_roc_curves(results_dict, data_file, args.output)
    
    # PR curves
    plot_precision_recall_curves(results_dict, data_file, args.output)
    
    # Bar charts
    plot_metric_bar_chart(results_dict, args.output)
    
    # Rule comparison (CLE-Net only)
    plot_rule_comparison(results_dict, args.output)
    
    # Temporal drift
    plot_temporal_drift(results_dict, args.output)
    
    print("\n" + "="*60)
    print("VISUALIZATION COMPLETE")
    print("="*60)
    print(f"\nOutput files:")
    print(f"  - {args.output}_table.csv (Comparison table)")
    print(f"  - {args.output}_roc.png (ROC curves)")
    print(f"  - {args.output}_pr.png (Precision-Recall curves)")
    print(f"  - {args.output}_bars.png (Metric bar charts)")
    print(f"  - {args.output}_rules.png (Rule metrics)")
    print(f"  - {args.output}_drift.png (Temporal drift)")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
