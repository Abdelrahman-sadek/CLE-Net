# Law Conflict Resolution Algorithm

This is the core intellectual engine of CLE-Net.

---

## 1. What is a Conflict?

A conflict exists when two laws cannot both hold in the same context.

Formally, laws $l_1$ and $l_2$ conflict if:

$$\exists c \in \text{Contexts}: l_1(c) = \text{true} \land l_2(c) = \text{false}$$

---

## 2. Law Representation

Each law is represented as:

$$l = (P, C, A, \theta)$$

| Symbol | Meaning |
|--------|---------|
| $P$ | Predicates |
| $C$ | Conditions |
| $A$ | Action or implication |
| $\theta$ | Confidence distribution |

---

## 3. Conflict Resolution Pipeline

### Step 1: Detection

Conflicts are detected via:

- Graph inconsistencies
- Contradictory outcomes
- Validator challenges

### Step 2: Context Expansion

CLE-Net attempts to separate contexts:

$$C_1 \neq C_2 \Rightarrow \text{No conflict}$$

> Many conflicts dissolve here.

### Step 3: Dominance Evaluation

If conflict remains, compute dominance score:

$$D(l) = \omega_1 \cdot \theta + \omega_2 \cdot S(l) + \omega_3 \cdot CCS_{author} + \omega_4 \cdot \text{Recency}$$

| Weight | Purpose |
|--------|---------|
| $\omega_1$ | Confidence matters |
| $\omega_2$ | Stability rewarded |
| $\omega_3$ | Author reliability |
| $\omega_4$ | Recent laws prioritized |

### Step 4: Resolution Decision

| Case | Outcome |
|------|---------|
| $D(l_1) \gg D(l_2)$ | Deprecate $l_2$ |
| Similar dominance | Split contexts |
| Unclear | Mark both as provisional |

**No forced deletion unless confidence is high.**

### Step 5: Learning from Conflict

The conflict itself generates a meta-law:

> *"In context X, rule Y overrides rule Z"*

This improves future reasoning.

---

## 4. Formal Algorithm

```python
def resolve_conflict(l1: Law, l2: Law) -> ResolutionResult:
    """
    Resolve a conflict between two laws.
    
    Returns:
        ResolutionResult with decision and reasoning
    """
    
    # Step 1: Check if contexts can be separated
    if can_separate_contexts(l1.context, l2.context):
        return ResolutionResult(
            decision="separate",
            reason="Contexts can be distinguished",
            meta_law=generate_meta_law(l1, l2)
        )
    
    # Step 2: Calculate dominance scores
    d1 = calculate_dominance(l1)
    d2 = calculate_dominance(l2)
    
    # Step 3: Make resolution decision
    threshold = 0.3  # Significant dominance threshold
    
    if d1 - d2 > threshold:
        return ResolutionResult(
            decision="deprecate_l2",
            reason=f"l1 dominance ({d1:.2f}) >> l2 ({d2:.2f})",
            surviving_law=l1,
            deprecated_law=l2
        )
    elif d2 - d1 > threshold:
        return ResolutionResult(
            decision="deprecate_l1",
            reason=f"l2 dominance ({d2:.2f}) >> l1 ({d1:.2f})",
            surviving_law=l2,
            deprecated_law=l1
        )
    else:
        return ResolutionResult(
            decision="provisional",
            reason="Dominance unclear, marking both provisional",
            requires_evidence=True
        )


def can_separate_contexts(c1: Context, c2: Context) -> bool:
    """
    Check if two contexts can be distinguished.
    
    Returns True if contexts are separable,
    meaning the conflict is only apparent.
    """
    # Check for explicit context differences
    if c1.domain != c2.domain:
        return True
    
    # Check temporal separation
    if c1.time_range and c2.time_range:
        if not ranges_overlap(c1.time_range, c2.time_range):
            return True
    
    # Check actor differences
    if c1.actors != c2.actors:
        return True
    
    return False


def calculate_dominance(law: Law) -> float:
    """
    Calculate dominance score for a law.
    """
    weights = {
        'confidence': 0.3,
        'survival': 0.25,
        'author_ccs': 0.25,
        'recency': 0.2
    }
    
    score = (
        weights['confidence'] * law.confidence +
        weights['survival'] * law.survival_score +
        weights['author_ccs'] * law.author_ccs +
        weights['recency'] * law.recency_score
    )
    
    return score
```

---

## 5. Meta-Law Generation

When conflicts are resolved, meta-laws are generated:

```python
def generate_meta_law(l1: Law, l2: Law) -> MetaLaw:
    """
    Generate a meta-law from conflict resolution.
    """
    return MetaLaw(
        rule=f"In {l1.context}, prefer {l1.predicate} over {l2.predicate}",
        precedence=l1.dominance_score - l2.dominance_score,
        conditions=l1.context,
        confidence=abs(l1.dominance_score - l2.dominance_score)
    )
```

---

## 6. Example Resolution

### Conflict Example

**Law 1**: "VIP clients ignore delays"
**Law 2**: "VIP clients must acknowledge all delays"

### Resolution Process

1. **Detection**: Contradictory outcomes detected
2. **Context Expansion**: 
   - Law 1: "standard VIP policy"
   - Law 2: "security context"
3. **Separation**: Contexts can be distinguished
4. **Result**: Meta-law generated

### Generated Meta-Law

> "In security contexts, acknowledgment is required. In standard VIP policy, delays may be ignored."

---

## 7. Properties

### 7.1 Convergence

The conflict resolution algorithm is designed to converge:

- Each resolution reduces ambiguity
- Meta-laws encode decisions
- Future conflicts reference meta-laws

### 7.2 No Deletion

Important property: **Laws are never deleted.**

They may be:
- Deprecated (confidence → 0)
- Marked provisional (requires evidence)
- Contextually limited (applies only in specific contexts)

But the historical record is preserved.

### 7.3 Transparency

Every resolution is:
- Recorded in the ledger
- Accompanied by reasoning
- Subject to challenge

---

## 8. Implementation Notes

### Confidence Thresholds

| Threshold | Action |
|-----------|--------|
| > 0.8 | Strong confidence |
| 0.5 - 0.8 | Moderate confidence |
| < 0.5 | Weak (requires evidence) |

### Dominance Thresholds

| Difference | Decision |
|------------|----------|
| > 0.3 | Clear dominance |
| 0.1 - 0.3 | Similar (provisional) |
| < 0.1 | Unclear (needs review) |

---

## 9. Related Documents

- **[Cognitive Contribution Score](03_cognitive_contribution_score.md)**: CCS affects dominance
- **[Consensus Model](03_consensus_model.md)**: Validation of resolutions
- **[Threat Model](../architecture/04_threat_model.md)**: Attack vectors on conflict resolution

---

*Document Version: 1.0*
*Last Updated: February 2026*
