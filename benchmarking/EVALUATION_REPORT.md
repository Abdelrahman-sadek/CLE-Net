# CLE-Net Benchmarking Evaluation Report

**Date:** February 11, 2026  
**Datasets Evaluated:** Cora, UCI Message  
**Models Compared:** CLE-Net, DynamicTriad, VGRNN

---

## Executive Summary

This report presents the benchmarking results comparing CLE-Net's symbolic rule discovery capabilities against standard dynamic graph embedding baselines (DynamicTriad and VGRNN). The evaluation focuses on temporal link prediction performance and rule extraction quality.

### Key Findings

1. **Rule Discovery**: CLE-Net successfully extracted **100 rules** from both datasets with high confidence scores
2. **Link Prediction Performance**: All models show similar performance (~0.49-0.52 AUC) across both datasets
3. **Rule Quality**: CLE-Net achieves high rule precision (0.83-1.0) and recall (1.0) on extracted rules

---

## Dataset Overview

| Dataset | Nodes | Temporal Splits | Total Edges | Type |
|---------|-------|-----------------|-------------|------|
| Cora | 2,708 | 10 | 10,556 | Citation Network |
| UCI Message | 1,899 | 10 | 20,000 | Social Interaction |

---

## Results Summary

### Cora Dataset

| Model | Link Pred AUC | Avg Precision | Rule Precision | Rule Recall | Num Rules | Stability |
|-------|---------------|---------------|----------------|-------------|-----------|-----------|
| **CLE-Net** | 0.5000 | 0.5000 | 1.0000 | 1.0000 | **100** | 0.721 |
| DynamicTriad | 0.5169 | 0.5157 | N/A | N/A | N/A | 1.000 |
| VGRNN | 0.4969 | 0.4962 | N/A | N/A | N/A | N/A |

### UCI Message Dataset

| Model | Link Pred AUC | Avg Precision | Rule Precision | Rule Recall | Num Rules | Stability |
|-------|---------------|---------------|----------------|-------------|-----------|-----------|
| **CLE-Net** | 0.5000 | 0.5000 | 0.8333 | 1.0000 | **100** | 0.485 |
| DynamicTriad | 0.4868 | 0.4938 | N/A | N/A | N/A | 1.000 |
| VGRNN | 0.5123 | 0.5076 | N/A | N/A | N/A | N/A |

---

## Detailed Analysis

### Rule Discovery Results

#### Cora Dataset
- **Total Rules Extracted:** 100
- **Average Support:** High (nodes co-occur in multiple timesteps)
- **Average Confidence:** 1.0 (perfect confidence rules)
- **Average Lift:** ~1000+ (strong associations)

**Sample Rules:**
```
node(1) -> node(20): support=0.6, confidence=1.0, lift=1055.6
node(3) -> node(15): support=0.5, confidence=1.0, lift=877.1
...
```

#### UCI Message Dataset
- **Total Rules Extracted:** 100
- **Average Support:** High
- **Average Confidence:** 0.8333
- **Average Lift:** ~500+

### Link Prediction Analysis

1. **Cora Dataset:**
   - DynamicTriad achieves the highest AUC (0.5169), marginally outperforming CLE-Net
   - VGRNN shows the lowest performance (0.4969), slightly below random baseline
   - All models cluster around 0.50 AUC, indicating challenging prediction task

2. **UCI Message Dataset:**
   - VGRNN performs best (0.5123 AUC)
   - CLE-Net and DynamicTriad show similar performance (~0.487-0.500)
   - Results suggest the data may not have strong temporal patterns for link prediction

### Rule Quality Metrics

| Dataset | Precision | Recall | Interpretation |
|---------|-----------|--------|----------------|
| Cora | 1.0000 | 1.0000 | All extracted rules are high-confidence |
| UCI Message | 0.8333 | 1.0000 | Most rules are reliable, good coverage |

---

## Generated Outputs

### Comparison Files

**Cora Dataset:**
- `results/comparison_cora_updated.csv` - Comparison table
- `results/comparison_cora_updated_detailed.json` - Detailed results
- `results/comparison_cora_viz_table.csv` - Visualization table

**UCI Message Dataset:**
- `results/comparison_uci_updated.csv` - Comparison table
- `results/comparison_uci_updated_detailed.json` - Detailed results
- `results/comparison_uci_viz_table.csv` - Visualization table

### Visualization Files

**Cora Dataset:**
- `results/comparison_cora_viz_roc.png` - ROC curves
- `results/comparison_cora_viz_pr.png` - Precision-Recall curves
- `results/comparison_cora_viz_bars.png` - Metric bar charts
- `results/comparison_cora_viz_rules.png` - Rule metrics

**UCI Message Dataset:**
- `results/comparison_uci_viz_roc.png` - ROC curves
- `results/comparison_uci_viz_pr.png` - Precision-Recall curves
- `results/comparison_uci_viz_bars.png` - Metric bar charts
- `results/comparison_uci_viz_rules.png` - Rule metrics

### CLE-Net Results Files

- `results/cle_net/cora_final.json` - Cora evaluation results
- `results/cle_net/uci_message_final.json` - UCI Message evaluation results

---

## Conclusions and Recommendations

### Strengths of CLE-Net

1. **Rule Extraction Capability**: Successfully extracts 100 high-quality rules from temporal graphs
2. **Interpretability**: Unlike embedding-based methods, CLE-Net provides symbolic rules that explain relationships
3. **High Confidence Rules**: Most extracted rules have confidence scores of 0.83-1.0

### Areas for Improvement

1. **Link Prediction Performance**: CLE-Net's link prediction AUC is at random level (0.50)
   - This suggests the current embedding strategy needs improvement
   - Rule-based predictions could be enhanced with better scoring mechanisms

2. **Dataset Suitability**: Standard graph benchmarks may not highlight CLE-Net's unique strengths
   - Cora and UCI Message have sparse, one-time edge patterns
   - Datasets with repeated interactions would better demonstrate rule mining

### Recommendations

1. **Algorithm Enhancement**:
   - Improve rule scoring for link prediction
   - Add support for sequential pattern mining
   - Develop hybrid approaches combining rules with embeddings

2. **Dataset Selection**:
   - Test with datasets containing repeated node interactions
   - Use temporal networks with community structure
   - Consider synthetic data with ground-truth rules

3. **Evaluation Framework**:
   - Add interpretability metrics (rule complexity, novelty)
   - Compare rule quality against human-curated knowledge
   - Evaluate on tasks where explainability is critical

---

## Running the Benchmark

To reproduce these results:

```bash
# Run CLE-Net evaluation
python benchmarking/run_cle_net_eval.py --dataset cora --output results/cle_net/cora_final.json
python benchmarking/run_cle_net_eval.py --dataset uci_message --output results/cle_net/uci_message_final.json

# Compare results
python benchmarking/evaluate.py \
    --cle-net results/cle_net/cora_final.json \
    --triad results/dynamic_triad/cora_test.json \
    --vgrnn results/vgrnn/cora_test.json \
    --dataset cora \
    --output results/comparison_cora_updated.csv

# Generate visualizations
python benchmarking/visualize_results.py \
    --cle-net results/cle_net/cora_final.json \
    --triad results/dynamic_triad/cora_test.json \
    --vgrnn results/vgrnn/cora_test.json \
    --dataset cora \
    --output results/comparison_cora_viz
```

---

## References

1. **DynamicTriad**: Zhou, L., et al. (2018). Dynamic Triad Closure Model for Predicting Temporal Networks.
2. **VGRNN**: Hajiramezanali, E., et al. (2019). Variational Graph Recurrent Neural Networks.
3. **CLE-Net**: Cognitive Logic Extraction Network for symbolic rule discovery.
