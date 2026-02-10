# Cognitive Contribution Score (CCS)

## 1. Purpose of CCS

CCS exists to quantify **cognitive reliability**, not intelligence.

It measures:

- How often an agent contributes useful, stable symbolic laws
- How well it detects contradictions
- How responsibly it participates in consensus

CCS is **non-transferable**, **non-monetary**, and **time-evolving**.

> **Stake** measures economic trust  
> **CCS** measures cognitive trust  
> 
> Both are required for a functioning CLE-Net.

---

## 2. CCS Definition

Let each agent $a$ have a Cognitive Contribution Score:

$$CCS_a(t) \in \mathbb{R}^+$$

CCS is updated discretely per epoch $t$.

---

## 3. CCS Components

CCS is a weighted sum of normalized components:

$$CCS_a = w_1 Q_a + w_2 S_a + w_3 R_a + w_4 U_a - w_5 P_a$$

| Term | Meaning |
|------|---------|
| $Q_a$ | Law Quality Score |
| $S_a$ | Law Survival Score |
| $R_a$ | Resolution Contribution |
| $U_a$ | Uptime & Availability |
| $P_a$ | Penalty Term |

Weights $w_i$ are protocol constants.

---

## 4. Law Quality Score ($Q_a$)

For each law $l$ proposed by agent $a$:

$$Q(l) = \alpha \cdot C(l) + \beta \cdot G(l) - \gamma \cdot X(l)$$

Where:

- $C(l)$: Empirical confirmation rate
- $G(l)$: Graph coherence (no contradictions)
- $X(l)$: Conflict count

Then:

$$Q_a = \frac{1}{N_a} \sum_{l \in L_a} Q(l)$$

This discourages spam laws.

---

## 5. Law Survival Score ($S_a$)

Measures how long laws remain valid:

$$S(l) = \int_{t_{obs}}^{t_{dep}} \lambda(t) \, dt$$

Where:
- $\lambda(t)$: Confidence decay function
- $t_{dep}$: Deprecation time

Then:

$$S_a = \frac{1}{N_a} \sum S(l)$$

Long-lived laws increase CCS more than short-lived ones.

---

## 6. Resolution Contribution ($R_a$)

Agents earn CCS by resolving conflicts.

For each conflict $c$:

$$R(c) = \delta \cdot \text{Impact}(c) \cdot \text{AcceptanceRate}$$

Then:

$$R_a = \sum_{c \in C_a} R(c)$$

This incentivizes **cleaning cognition**, not just adding to it.

---

## 7. Uptime Score ($U_a$)

Simple availability metric:

$$U_a = \frac{\text{online epochs}}{\text{total epochs}}$$

Prevents "drive-by cognition."

---

## 8. Penalty Term ($P_a$)

Applied for:

- Approving invalid state transitions
- Repeated contradiction approval
- Malicious fork behavior

$$P_a = \sum p_i$$

Penalties decay slowly to allow recovery.

---

## 9. CCS Decay

To prevent ossification:

$$CCS_a(t+1) = CCS_a(t) \cdot e^{-\mu \Delta t} + \Delta CCS_a$$

Old reputation fades without new contribution.

---

## 10. Implementation Considerations

### 10.1 Weight Configuration

Suggested initial weights:

| Weight | Value | Purpose |
|--------|-------|---------|
| $w_1$ | 0.35 | Quality matters most |
| $w_2$ | 0.25 | Stability rewarded |
| $w_3$ | 0.20 | Conflict resolution valued |
| $w_4$ | 0.10 | Participation required |
| $w_5$ | 0.40 | Penalties are significant |

### 10.2 Decay Parameters

- $\mu$: 0.001 per epoch (gradual decay)
- Epoch length: 1 hour

### 10.3 Minimum Requirements

Agents must maintain:
- $CCS_a \geq 0.1$ to participate in consensus
- $U_a \geq 0.5$ to avoid inactivity penalties

---

## 11. Related Documents

- **[Consensus Model](03_consensus_model.md)**: PoC with validator power
- **[Threat Model](../architecture/04_threat_model.md)**: Security implications of CCS
- **[Economic Model](../economics/)**: Interaction with stake

---

*Document Version: 1.0*
*Last Updated: February 2026*
