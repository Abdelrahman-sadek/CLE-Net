# Proof of Cognition (PoC) Consensus Model

This document details the Proof of Cognition consensus mechanism, the heart of CLE-Net's decentralized coordination.

## 1. Motivation

Traditional blockchain consensus mechanisms solve different problems:

| Mechanism | Problem Solved | Resource |
|-----------|---------------|----------|
| Proof of Work | Sybil resistance + ordering | Energy |
| Proof of Stake | Sybil resistance + stake | Capital |
| BFT Protocols | Agreement under faults | Communication |

CLE-Net needs something different:

> **We need consensus on knowledge, not transactions.**

Traditional consensus asks: "Did this transaction happen?"

CLE-Net asks: "Is this rule likely true?"

This requires a fundamentally different primitive.

---

## 2. Core Idea: Proof of Cognition

### 2.1 Intuition

If multiple independent agents, operating on different data, reach the same conclusion → that conclusion is more likely true.

This mirrors the scientific method:

1. Multiple researchers observe independently
2. They converge on similar findings
3. Consensus emerges from replication

### 2.2 Formal Definition

A rule R achieves Proof of Cognition consensus when:

```
PoC(R) = True IF AND ONLY IF

∃ Agents A₁, A₂, ..., Aₙ such that:
  ∀ i ≠ j: Independent(Aᵢ, Aⱼ)
  ∀ i: Discover(Aᵢ, R) locally
  ∀ i: Confidence(Aᵢ, R) ≥ θ
  Contradiction_Penalty(R) < φ
```

**Where**:

- `Independent(Aᵢ, Aⱼ)`: Agents did not share data or coordinate
- `Discover(Aᵢ, R)`: Agent independently derived rule R
- `θ`: Minimum confidence threshold
- `φ`: Maximum allowed contradiction

---

## 3. Key Concepts

### 3.1 Cognitive Agent (Node)

A CLE-Net node that:

1. Observes local data
2. Discovers candidate rules
3. Broadcasts commitments (not raw data)
4. Validates network consensus

**Independence Requirements**:

An agent is considered independent if:

- No shared training data with other agents
- No shared local memory state
- No communication before discovery
- Different data sources (at least probabilistically)

### 3.2 Rule Candidate

A symbolic rule discovered by an agent:

```python
class RuleCandidate:
    rule_id: str                    # SHA256 hash of canonical form
    logic_form: str                 # IF...THEN... canonical form
    context_signature: str           # Domain/context hash
    agent_id: str                   # Discovering agent
    timestamp: float               # Discovery time
    confidence: float              # Agent's confidence (0-1)
    evidence_count: int             # Supporting events
```

### 3.3 Rule Commitment

When an agent discovers a rule with sufficient confidence, it commits to the network:

```python
class RuleCommit:
    rule_hash: str                  # SHA256(logic_form)
    logic_signature: str             # Normalized logic hash
    context_signature: str           # Context hash
    agent_id: str
    timestamp: float
    confidence: float
    # NOTE: Raw rule text is NOT committed
    # Only hashes + metadata
```

**Critical**: The actual rule text never leaves the agent. Only hashes are broadcast.

### 3.4 Rule Matching

The network groups commits that represent the same rule:

```python
class RuleCluster:
    rule_hash: str                  # Cluster identifier
    commits: List[RuleCommit]       # All commits for this rule
    unique_agents: Set[str]         # Distinct agents
    first_commit: float
    last_commit: float
    avg_confidence: float
```

Two commits match if:

- `logic_signature` is semantically equivalent
- `context_signature` is compatible

---

## 4. Consensus Conditions

### 4.1 Mandatory Conditions

A rule achieves consensus when:

| Condition | Description | Required |
|-----------|-------------|----------|
| Independence | ≥ N agents, no coordination | Yes |
| Diversity | Distinct data sources | Yes |
| Confidence | Each agent confidence ≥ θ | Yes |
| Temporal | Not synchronized discovery | Yes |
| Stability | Survives for time τ | Yes |

### 4.2 Independence Score

Agents are not perfectly independent. We compute an independence score:

```
Independence_Score = f(
  data_source_overlap,
  communication_events,
  temporal_correlation,
  reasoning_trace_similarity
)
```

Higher overlap → Lower independence

### 4.3 Confidence Calculation

Final rule confidence is a function of:

```
C_final = α × C_avg           # Average agent confidence
        + β × D               # Diversity score
        - γ × Contradictions  # Contradiction penalty
        + δ × T_survival      # Time stability bonus
```

Where α, β, γ, δ are configurable weights.

---

## 5. Contradiction Handling

### 5.1 Contradictions Are Signals

In traditional systems, contradictions are errors.

In CLE-Net, contradictions are **first-class signals**:

- They indicate complexity in the domain
- They suggest context-dependent rules
- They invite more evidence

### 5.2 Handling Process

When an agent submits a contradiction:

1. **Both rules persist** in the knowledge graph
2. **Confidence decays** for both
3. **Context analysis** determines applicability
4. **Network waits** for more evidence

### 5.3 Context Separation

Contradicting rules can coexist if:

```
Rule_A IS_CONTRADICTED_BY Rule_B ONLY_IF
  Context(Rule_A) ≠ Context(Rule_B)
```

Example:

- Rule: "VIP clients ignore delays"
- Context: "Standard policy"

- Rule: "VIP clients must acknowledge delays"
- Context: "Security policy"

These are not contradictory — they apply in different contexts.

### 5.4 Confidence Decay

Rules decay over time if:

- Not confirmed by new evidence
- Contradicted by other agents
- Context becomes obsolete

Decay function:

```
C(t) = C₀ × e^(-λ × t) + C_min
```

Where λ is decay rate, C_min is minimum confidence floor.

---

## 6. Incentive Mechanism

### 6.1 Mining = Thinking

Traditional mining: Solve arbitrary puzzles

CLE-Net mining: **Discover useful rules**

### 6.2 Reward Function

Agents earn rewards when:

1. Their rule enters consensus
2. Their rule survives over time
3. Their rule has high coverage

```python
Reward = Coverage × Stability × Simplicity
```

- **Coverage**: Fraction of events explained
- **Stability**: Time since consensus
- **Simplicity**: Inverse of rule complexity

### 6.3 Sybil Resistance

PoC naturally resists Sybil attacks because:

- Fake agents need independent cognition
- Similar data → reduced independence score
- Temporal sync → penalized
- Reasoning traces → analyzed

Creating 1,000 fake nodes ≠ 1,000 discoveries.

---

## 7. Formal Specification

### 7.1 Consensus Algorithm

```python
def achieve_consensus(rule_cluster: RuleCluster) -> ConsensusResult:
    # Check mandatory conditions
    if len(rule_cluster.unique_agents) < N_MIN:
        return ConsensusResult.REJECTED("insufficient_agents")
    
    if rule_cluster.avg_confidence < THETA:
        return ConsensusResult.REJECTED("low_confidence")
    
    # Check independence
    independence = calculate_independence(rule_cluster.commits)
    if independence < INDEPENDENCE_THRESHOLD:
        return ConsensusResult.REJECTED("dependent_agents")
    
    # Check stability
    if not is_stable(rule_cluster, TAU):
        return ConsensusResult.PENDING("awaiting_stability")
    
    # Calculate final confidence
    confidence = calculate_final_confidence(rule_cluster)
    
    # Check contradictions
    contradictions = get_contradictions(rule_cluster.rule_hash)
    if contradictions.stronger_than(confidence):
        return ConsensusResult.WEAKENED("contradicted")
    
    # Consensus achieved
    return ConsensusResult.ACCEPTED(
        rule_hash=rule_cluster.rule_hash,
        confidence=confidence,
        supporting_agents=list(rule_cluster.unique_agents)
    )
```

### 7.2 Acceptance Criteria

A rule is **ACCEPTED** if:

```
∃ R_cluster:
  |unique_agents(R_cluster)| ≥ 3
  ∧ independence(R_cluster) ≥ 0.8
  ∧ avg_confidence(R_cluster) ≥ 0.7
  ∧ stability_time(R_cluster) ≥ 86400
  ∧ contradiction_strength(R_cluster) < 0.3
```

A rule is **WEAKENED** if:

```
Contradiction exists
∧ contradiction_strength > 0.3
∧ contradiction_strength < confidence
```

A rule is **REJECTED** if:

```
Insufficient independent agents
OR
confidence < 0.7
OR
independence < 0.8
```

---

## 8. Why PoC Is Different

| Aspect | PoW | PoS | PoC |
|--------|-----|-----|-----|
| Resource | Energy | Capital | Cognition |
| Output | Blocks | Blocks | Rules |
| Waste | High | Medium | Low |
| Explainability | None | None | Full |
| Adversarial | 51% | 51% | Independent discovery |
| Truth basis | Longest chain | Most stake | Replication |

---

## 9. Limitations

### 9.1 Known Weaknesses

- **Coordinated false consensus**: Well-funded attackers could coordinate
- **Data homogeneity**: If all agents see similar data, independence is reduced
- **Temporal gaming**: Agents could fake discovery times

### 9.2 Mitigation Strategies

- Require diverse data sources
- Penalize temporal clustering
- Analyze reasoning traces
- Allow contradictions to persist

### 9.3 Honest Acknowledgment

PoC does NOT guarantee:

- Absolute truth
- Immediate consensus
- Resistance to global collusion

It guarantees:

- Emergence of shared rules under realistic conditions
- Transparency about uncertainty
- Resistance to simple manipulation

---

## 10. Implementation Notes

### 10.1 Message Types

| Message | Purpose |
|---------|---------|
| `RuleCommit` | Agent broadcasts rule hash |
| `RuleChallenge` | Agent challenges a rule |
| `RuleConfirm` | Agent confirms a rule |
| `StateSync` | Full state synchronization |
| `Block` | Consensus checkpoint |

### 10.2 Performance Considerations

- PoC is not designed for high throughput
- Consensus takes time (τ = 24 hours minimum)
- Scalability limited by independence requirements

### 10.3 Monitoring Metrics

- Consensus rate
- Independence scores
- Contradiction frequency
- Rule stability
- Reward distribution

---

## 11. Related Documents

- **[System Overview](01_system_overview.md)**: Context for consensus
- **[Agent Architecture](02_agent_architecture.md)**: How agents implement PoC
- **[Threat Model](04_threat_model.md)**: Security analysis of PoC
- **[Economic Model](../economics/)**: Token and incentive design

---

*Document Version: 1.0*
*Last Updated: 2024*
