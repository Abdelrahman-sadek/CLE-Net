# CLE-Net Cosmos SDK Architecture

**Version**: 1.0  
**Last Updated**: 2026-02-10  
**Status**: Design Document

## Overview

CLE-Net is implemented as an application-specific blockchain using the Cosmos SDK. This architecture enables native cognitive state transitions and consensus over symbolic law evolution, without the constraints of generic blockchain platforms.

## Why Cosmos SDK?

CLE-Net evaluated multiple blockchain platforms and selected Cosmos SDK for the following reasons:

### ✅ Advantages

1. **Application-Specific State Machines**: Cosmos treats blockchains as application-specific state machines, which is exactly what CLE-Net needs
2. **Custom State Machine**: Full control over cognitive state transitions, CCS encoding, and law lifecycle
3. **Mature Consensus**: Tendermint BFT provides proven Byzantine fault-tolerant consensus
4. **Modular Design**: Easy to design custom modules for cognitive, laws, and consensus
5. **Research-Friendly**: The ecosystem respects research-grade projects
6. **IBC Interoperability**: Future-proof with Inter-Blockchain Communication protocol
7. **Not EVM-Centric**: No gas metering or financial assumptions

### ❌ Rejected Alternatives

- **Ethereum L2**: EVM is a terrible fit for cognitive state machines; everything is gas-metered
- **Lightweight P2P**: No economic security; weak Sybil resistance
- **Custom Chain**: Years of engineering; massive attack surface; only viable after CLE-Net proves itself
- **Substrate**: Technically excellent but steep learning curve; Rust-heavy limits contributor pool

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     CLE-Net Application                      │
│                   (Cosmos SDK-based Chain)                   │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Cognitive  │  │     Laws     │  │   Consensus  │      │
│  │    Module    │  │    Module    │  │    Module    │      │
│  │              │  │              │  │              │      │
│  │ - Law Prop.  │  │ - Storage    │  │ - Validators │      │
│  │ - Validation │  │ - Indexing   │  │ - PoC        │      │
│  │ - Conflicts  │  │ - Querying   │  │ - Proposers  │      │
│  │ - CCS Track  │  │ - Evolution  │  │ - Slashing   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│           │                 │                 │              │
│           └─────────────────┴─────────────────┘              │
│                             │                                │
│                    ┌────────▼────────┐                       │
│                    │   State Store   │                       │
│                    │  (KV Database)  │                       │
│                    └─────────────────┘                       │
│                             │                                │
│                    ┌────────▼────────┐                       │
│                    │   Tendermint    │                       │
│                    │      BFT        │                       │
│                    └─────────────────┘                       │
│                             │                                │
│                    ┌────────▼────────┐                       │
│                    │   P2P Network   │                       │
│                    │   (libp2p)      │                       │
│                    └─────────────────┘                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Off-Chain Processing                      │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Symbol     │  │  Knowledge   │  │   Multi-     │      │
│  │  Extraction  │  │    Graph     │  │    Modal     │      │
│  │              │  │              │  │              │      │
│  │ - Atomizer   │  │ - Graph RAG  │  │ - Voice      │      │
│  │ - Symbol     │  │ - Temporal   │  │ - Video      │      │
│  │   Mapper     │  │   Storage    │  │ - Documents  │      │
│  │ - Rule       │  │ - Contradict │  │ - Images     │      │
│  │   Engine     │  │   Detection  │  │ - Full-Duplex│      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│           │                 │                 │              │
│           └─────────────────┴─────────────────┘              │
│                             │                                │
│                    ┌────────▼────────┐                       │
│                    │   LLM / AI      │                       │
│                    │   Inference     │                       │
│                    └─────────────────┘                       │
└─────────────────────────────────────────────────────────────┘
```

## Module Structure

### 1. Cognitive Module (`core/cosmos/x/cognitive/`)

**Purpose**: Manages cognitive laws, their lifecycle, and validation.

**Components**:
- `CognitiveKeeper`: Manages state of cognitive laws, CCS, and conflict resolutions
- `CognitiveModule`: Handles law proposal, validation, conflict detection, and resolution
- Message Types:
  - `ProposeLawMessage`: Propose a new cognitive law
  - `ValidateLawMessage`: Validate a proposed law
  - `ReportConflictMessage`: Report a conflict between laws
  - `ResolveConflictMessage`: Resolve a conflict between laws
  - `UpdateCCSMessage`: Update a participant's CCS

**State**:
- `laws`: Map of law ID to `CognitiveLaw`
- `ccs_scores`: Map of participant ID to `CognitiveContributionScore`
- `conflicts`: Map of resolution ID to `ConflictResolution`
- `context_boundaries`: Map of context to list of law IDs

### 2. Laws Module (`core/cosmos/x/laws/`)

**Purpose**: Provides law storage, indexing, and retrieval.

**Components**:
- `LawsKeeper`: Manages law storage, indexing, and retrieval
- `LawsModule`: Handles law lifecycle, evolution, decay, and querying

**Indexes**:
- By status: `PROPOSED`, `VALIDATING`, `ACTIVE`, `CONFLICTED`, `DEPRECATED`, `REVOKED`
- By type: `SYMBOLIC_RULE`, `CONTEXT_BOUNDARY`, `DECISION_PATTERN`, `CAUSAL_RELATION`
- By context: Laws grouped by context
- By proposer: Laws grouped by proposer

**Queries**:
- Get law by ID
- Get laws by status
- Get laws by type
- Get laws by context
- Get laws by proposer
- Search laws by expression
- Get similar laws
- Get conflicting laws
- Get top laws by confidence
- Get recent laws

### 3. Consensus Module (`core/cosmos/x/consensus/`)

**Purpose**: Manages validators and Proof of Cognition (PoC) consensus.

**Components**:
- `ConsensusKeeper`: Manages validators, their roles, and consensus state
- `ConsensusModule`: Handles validator registration, block proposal, and validation
- `ProofOfCognition`: Implements PoC consensus mechanism

**Validator Roles**:
- `COGNITIVE_MINER`: Discovers new cognitive laws
- `STATE_VALIDATOR`: Validates proposed laws
- `CONFLICT_RESOLVER`: Resolves conflicts between laws
- `WATCHDOG`: Monitors network health

**State**:
- `validators`: Map of validator address to `ValidatorInfo`
- `active_validators`: Set of active validator addresses
- `proposer_queue`: Ordered list of proposers
- `block_height`: Current block height
- `last_block_hash`: Hash of the last committed block

## On-Chain State

### Cognitive State Block (CSB)

The fundamental unit of CLE-Net. A CSB contains:

```python
class CognitiveStateBlock:
    block_height: int
    block_hash: str
    proposer_id: str
    timestamp: datetime
    new_laws: List[CognitiveLaw]
    updated_laws: List[CognitiveLaw]
    ccs_updates: List[CognitiveContributionScore]
    conflict_resolutions: List[Dict]
    prev_block_hash: str
```

### Cognitive Law

A symbolic representation of a decision pattern:

```python
class CognitiveLaw:
    law_id: str
    law_type: LawType
    symbolic_expression: str
    context: str
    status: LawStatus
    proposer_id: str
    confidence: float
    support_count: int
    contradiction_count: int
    evidence: List[str]
    created_at: datetime
    updated_at: datetime
    decay_factor: float
```

### Cognitive Contribution Score (CCS)

Measures the quality and impact of cognitive contributions:

```python
class CognitiveContributionScore:
    participant_id: str
    score: float
    contributions_count: int
    laws_discovered: int
    conflicts_resolved: int
    last_updated: datetime
```

### Validator Information

Tracks validators and their roles:

```python
class ValidatorInfo:
    validator_address: str
    role: ValidatorRole
    stake: float
    uptime: float
    laws_validated: int
    conflicts_resolved: int
    last_active: datetime
```

## Consensus Mechanism

### Proof of Cognition (PoC)

PoC is CLE-Net's consensus mechanism that rewards independent discovery of cognitive laws.

**Key Principles**:

1. **Independent Discovery**: Laws must be discovered by multiple independent parties
2. **Cognitive Contribution**: Contributors earn CCS based on quality and impact
3. **Consensus Validation**: 2/3 supermajority required for law activation
4. **Fork Tolerance**: Temporary divergence is acceptable for research

**Validation Process**:

1. Law is proposed by a Cognitive Miner
2. State Validators vote on the law
3. If 2/3 supermajority approves, law becomes ACTIVE
4. If 2/3 supermajority rejects, law becomes DEPRECATED
5. If no supermajority, law remains in VALIDATING state

**Reward Distribution**:

- Base reward: 100 CCS per law
- Distributed among independent discoverers
- Bonus for conflict resolution: +200 CCS

### Tendermint BFT Integration

CLE-Net uses Tendermint BFT for block-level consensus:

1. **Block Proposal**: Current proposer creates a CSB
2. **Pre-vote**: Validators vote on the block
3. **Pre-commit**: Validators commit to the block
4. **Commit**: Block is committed to the chain

**Mapping CLE-Consensus to Tendermint**:

| CLE-Net Concept | Tendermint Concept |
|----------------|-------------------|
| Cognitive State Block | Block |
| Law Proposal | Transaction |
| Law Validation | Transaction Execution |
| CCS Update | State Transition |
| Conflict Resolution | State Transition |
| Validator | Validator |
| Proposer | Proposer |

## Off-Chain Processing

CLE-Net separates on-chain and off-chain processing:

### On-Chain (Consensus)
- Cognitive State Blocks (CSBs)
- Law lifecycle state machine
- CCS tracking
- Validator voting

### Off-Chain (Computation)
- Symbol extraction from human interaction
- Knowledge graph construction
- LLM inference and reasoning
- OCR and multi-modal input processing

This separation ensures:
- No gas abuse for cognitive workloads
- Efficient use of blockchain resources
- Flexibility in AI model choice
- Privacy for sensitive data

## Migration Path

### Phase 1: Cosmos SDK v1 (Current)

- Application-specific blockchain
- Native cognitive state machine
- Tendermint BFT consensus
- Basic PoC mechanism

### Phase 2: Custom Chain (Future)

- Optimized consensus for cognitive workloads
- Custom state transition logic
- Enhanced PoC mechanism
- Improved performance

### Phase 3: IBC Integration (Future)

- Interoperability with other Cosmos chains
- Cross-chain cognitive state sharing
- Distributed cognition across networks

## Security Considerations

### Validator Security

- Minimum stake requirement: 1000 tokens
- Slashing for uptime below 50%
- Role-based access control
- Regular validator rotation

### Law Security

- Hash-based integrity verification
- Status transition validation
- Conflict detection and resolution
- Decay mechanism for stale laws

### Network Security

- Tendermint BFT provides Byzantine fault tolerance
- 2/3 supermajority required for consensus
- Fork tolerance for research flexibility
- Watchdog mechanisms for anomaly detection

## Performance Considerations

### Throughput

- Low throughput, high semantic density
- Target: 1-10 blocks per second
- Block size: Limited by cognitive state complexity

### Latency

- Block time: 1-10 seconds
- Finality: ~2 block times (Tendermint)
- Law activation: ~3-5 blocks

### Storage

- Law storage: Indexed by multiple attributes
- State pruning: Deprecated laws can be pruned
- Snapshot support: For state recovery

## References

- [Cosmos SDK Documentation](https://docs.cosmos.network/)
- [Tendermint Documentation](https://docs.tendermint.com/)
- [IBC Protocol](https://ibc.cosmos.network/)
- [Cosmos Module Tutorial](https://docs.cosmos.network/v0.44/building-modules/intro.html)

## Next Steps

1. Implement Cosmos SDK module scaffolding
2. Define state machine and message handlers
3. Implement PoC consensus mechanism
4. Integrate with existing CLE-Net codebase
5. Test on local testnet
6. Deploy to public testnet
7. Security audit
8. Mainnet launch
