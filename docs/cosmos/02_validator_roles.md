# CLE-Net Validator Roles

**Version**: 1.0  
**Last Updated**: 2026-02-10  
**Status**: Design Document

## Overview

CLE-Net validators have specialized roles that reflect the cognitive nature of the network. Unlike traditional blockchain validators who only validate transactions, CLE-Net validators participate in cognitive processes including law discovery, validation, conflict resolution, and network health monitoring.

## Validator Roles

### 1. Cognitive Miner

**Purpose**: Discovers new cognitive laws from interaction data.

**Responsibilities**:
- Analyze human interaction data (text, voice, documents, video)
- Extract symbolic patterns and decision rules
- Propose new cognitive laws for validation
- Earn CCS for successful discoveries

**Requirements**:
- Minimum stake: 1000 tokens
- Access to interaction data sources
- Symbol extraction capabilities
- LLM inference capabilities

**Rewards**:
- Base reward: 100 CCS per discovered law
- Bonus for high-confidence laws: +50 CCS
- Bonus for novel discoveries: +100 CCS

**Example Workflow**:

```python
# 1. Analyze interaction data
interaction_data = analyze_interaction(conversation)

# 2. Extract symbolic pattern
pattern = extract_symbolic_pattern(interaction_data)

# 3. Propose new law
propose_msg = ProposeLawMessage(
    proposer_id="miner1",
    law_type=LawType.SYMBOLIC_RULE,
    symbolic_expression=pattern,
    context="customer_service",
    evidence=["ticket_123", "ticket_456"],
    confidence=0.8
)
law = cognitive_module.handle_propose_law(propose_msg)
```

### 2. State Validator

**Purpose**: Validates proposed laws and ensures law integrity.

**Responsibilities**:
- Review proposed cognitive laws
- Vote on law activation (approve/reject)
- Verify law integrity and correctness
- Ensure laws follow CLE-Net protocols

**Requirements**:
- Minimum stake: 1000 tokens
- Understanding of CLE-Net protocols
- Ability to evaluate law quality
- High uptime (>95%)

**Rewards**:
- Base reward: 10 CCS per vote
- Bonus for correct votes: +20 CCS
- Penalty for incorrect votes: -10 CCS

**Validation Criteria**:

1. **Well-formedness**: Law has all required fields
2. **Integrity**: Law hash matches computed hash
3. **Evidence**: Law has sufficient supporting evidence
4. **Context**: Law is appropriate for its context
5. **Novelty**: Law is not a duplicate of existing laws

**Example Workflow**:

```python
# 1. Review proposed law
law = cognitive_module.keeper.get_law("law_abc123")

# 2. Evaluate law quality
is_valid = evaluate_law(law)

# 3. Cast vote
validate_msg = ValidateLawMessage(
    validator_id="validator1",
    law_id=law.law_id,
    vote=is_valid,
    reason="Law is well-formed and supported by evidence"
)
cognitive_module.handle_validate_law(validate_msg)
```

### 3. Conflict Resolver

**Purpose**: Detects and resolves conflicts between laws.

**Responsibilities**:
- Monitor for conflicting laws
- Report conflicts to the network
- Propose conflict resolutions
- Manage context boundaries

**Requirements**:
- Minimum stake: 1500 tokens (higher due to complexity)
- Deep understanding of CLE-Net semantics
- Conflict resolution expertise
- High uptime (>95%)

**Rewards**:
- Base reward: 50 CCS per conflict reported
- Bonus for successful resolution: +200 CCS
- Bonus for context boundary creation: +100 CCS

**Conflict Types**:

1. **Direct Contradiction**: Laws with opposite expressions
   - Example: "Users must always authenticate" vs "Users never authenticate"

2. **Context Overlap**: Laws that conflict in overlapping contexts
   - Example: Same rule applies to different but overlapping contexts

3. **Semantic Conflict**: Laws that are semantically incompatible
   - Example: "Enable feature X" vs "Disable feature X" (same feature)

**Resolution Strategies**:

1. **Merge**: Combine conflicting laws into a single, more nuanced law
2. **Prioritize**: Select one law as primary based on evidence
3. **Deprecate**: Mark conflicting laws as deprecated
4. **Context Split**: Create separate context boundaries for each law

**Example Workflow**:

```python
# 1. Detect conflict
conflicting_laws = detect_conflicts(law1, law2)

if conflicting_laws:
    # 2. Report conflict
    report_msg = ReportConflictMessage(
        reporter_id="resolver1",
        conflicting_law_ids=[law1.law_id, law2.law_id],
        conflict_description="Direct contradiction in customer service context"
    )
    resolution_id = cognitive_module.handle_report_conflict(report_msg)
    
    # 3. Propose resolution
    resolve_msg = ResolveConflictMessage(
        resolver_id="resolver1",
        resolution_id=resolution_id,
        conflicting_law_ids=[law1.law_id, law2.law_id],
        resolution_type="context_split",
        context_boundaries=["customer_service_premium", "customer_service_standard"]
    )
    cognitive_module.handle_resolve_conflict(resolve_msg)
```

### 4. Watchdog

**Purpose**: Monitors network health and detects anomalies.

**Responsibilities**:
- Monitor block production
- Detect stalled blocks
- Monitor validator participation
- Detect CCS decay anomalies
- Report network health issues

**Requirements**:
- Minimum stake: 500 tokens (lower due to passive role)
- Network monitoring capabilities
- Alert system
- High uptime (>99%)

**Rewards**:
- Base reward: 5 CCS per block monitored
- Bonus for anomaly detection: +50 CCS
- Bonus for early warning: +100 CCS

**Anomaly Types**:

1. **Stalled Blocks**: No blocks produced for extended period
2. **Low Participation**: Few validators participating in consensus
3. **CCS Decay Anomalies**: Unusual CCS decay patterns
4. **Validator Misbehavior**: Validators acting maliciously
5. **Network Partition**: Network split into disconnected segments

**Alert Levels**:

1. **INFO**: Normal operation, informational only
2. **WARNING**: Potential issue, requires attention
3. **ERROR**: Confirmed issue, requires action
4. **CRITICAL**: Severe issue, immediate action required

**Example Workflow**:

```python
# 1. Monitor block production
time_since_last_block = time.time() - last_block_time

if time_since_last_block > block_timeout:
    # 2. Create alert
    alert = Alert(
        severity=AlertSeverity.ERROR,
        alert_type=AlertType.STALLED_BLOCK,
        message=f"No blocks produced for {time_since_last_block} seconds",
        metadata={"last_block_height": last_block_height}
    )
    
    # 3. Report to network
    watchdog_module.report_alert(alert)
```

## Validator Registration

### Registration Process

1. **Stake Deposit**: Deposit minimum stake (varies by role)
2. **Role Selection**: Choose validator role
3. **Key Generation**: Generate validator keys
4. **Registration Message**: Submit registration to consensus module
5. **Activation**: Wait for activation by existing validators

### Registration Example

```python
# Register as Cognitive Miner
register_msg = RegisterValidatorMessage(
    validator_address="miner1",
    role=ValidatorRole.COGNITIVE_MINER,
    stake=1000.0
)
success = consensus_module.handle_register_validator(register_msg)
```

### Role Changes

Validators can change roles by:

1. Submitting a role change request
2. Meeting new role's stake requirements
3. Waiting for approval from existing validators
4. Updating validator information

```python
# Change from Cognitive Miner to Conflict Resolver
update_msg = UpdateValidatorMessage(
    validator_address="miner1",
    stake_delta=500.0  # Increase stake to 1500
)
consensus_module.handle_update_validator(update_msg)

# Then submit role change request
role_change_msg = RoleChangeMessage(
    validator_address="miner1",
    new_role=ValidatorRole.CONFLICT_RESOLVER
)
consensus_module.handle_role_change(role_change_msg)
```

## Validator Rewards

### CCS Distribution

CCS is distributed based on:

1. **Role**: Different roles have different reward structures
2. **Contribution**: Quality and impact of contributions
3. **Participation**: Active participation in network activities
4. **Uptime**: High uptime earns bonus rewards

### Reward Calculation

```python
def calculate_reward(validator: ValidatorInfo, contribution: Contribution) -> float:
    base_reward = get_base_reward(validator.role)
    quality_bonus = contribution.quality * 50
    participation_bonus = contribution.participation * 20
    uptime_bonus = validator.uptime * 10
    
    total_reward = base_reward + quality_bonus + participation_bonus + uptime_bonus
    return total_reward
```

### Reward Distribution

Rewards are distributed:

1. **Per Block**: For block proposal and validation
2. **Per Law**: For law discovery and validation
3. **Per Conflict**: For conflict detection and resolution
4. **Per Epoch**: For overall participation and uptime

## Validator Slashing

### Slashing Conditions

Validators are slashed for:

1. **Low Uptime**: Uptime below 50%
2. **Double Signing**: Signing conflicting blocks
3. **Invalid Votes**: Voting on invalid laws
4. **Misbehavior**: Malicious behavior detected by watchdogs

### Slashing Penalties

1. **First Offense**: 10% stake slashed
2. **Second Offense**: 25% stake slashed
3. **Third Offense**: 50% stake slashed and deactivation

### Slashing Example

```python
# Validator with low uptime
if validator.uptime < 50:
    # Slash 50% of stake
    validator.stake *= 0.5
    
    # Remove from active validators
    consensus_module.keeper.remove_active_validator(validator.validator_address)
    
    # Remove from proposer queue
    consensus_module.keeper.proposer_queue.remove(validator.validator_address)
```

## Validator Governance

### Voting Rights

All validators have voting rights on:

1. **Protocol Upgrades**: Changes to CLE-Net protocols
2. **Parameter Changes**: Changes to network parameters
3. **Role Changes**: Changes to validator roles
4. **Emergency Actions**: Emergency network actions

### Voting Process

1. **Proposal**: Submit a governance proposal
2. **Discussion**: Discuss proposal in governance forum
3. **Voting**: Validators vote on proposal
4. **Execution**: Proposal is executed if approved

### Voting Example

```python
# Submit governance proposal
proposal = GovernanceProposal(
    proposal_id="prop_001",
    proposer_id="validator1",
    proposal_type=ProposalType.PARAMETER_CHANGE,
    description="Increase minimum stake to 1500 tokens",
    changes={"min_stake": 1500}
)

# Validators vote
vote = GovernanceVote(
    proposal_id="prop_001",
    validator_id="validator1",
    vote=True  # Approve
)
```

## Validator Requirements Summary

| Role | Min Stake | Uptime | Skills | Rewards |
|------|-----------|--------|--------|---------|
| Cognitive Miner | 1000 | >90% | Symbol extraction, LLM | 100-250 CCS/law |
| State Validator | 1000 | >95% | Law evaluation | 10-30 CCS/vote |
| Conflict Resolver | 1500 | >95% | Conflict resolution | 50-350 CCS/conflict |
| Watchdog | 500 | >99% | Network monitoring | 5-155 CCS/block |

## Next Steps

1. Implement validator registration system
2. Implement role-based reward distribution
3. Implement slashing mechanism
4. Implement governance voting
5. Test validator roles on testnet
6. Deploy to mainnet

## References

- [Cosmos SDK Validator Documentation](https://docs.cosmos.network/v0.44/minting/validator.html)
- [Tendermint Validator Documentation](https://docs.tendermint.com/master/spec/consensus/validator.html)
- [CLE-Net Consensus Module](../core/cosmos/x/consensus/__init__.py)
