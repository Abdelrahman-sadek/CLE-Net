# Agent Architecture

This document details the internal architecture of a CLE-Net agent.

## 1. Overview

A CLE-Net agent is an autonomous cognitive unit that:

1. **Observes** human interaction (text, voice, documents)
2. **Extracts** symbolic representations from raw input
3. **Discovers** latent rules through symbolic regression
4. **Communicates** discoveries to the network
5. **Learns** from global consensus

Agents are designed to be:

- **Independent**: Each agent operates on its own data
- **Resilient**: Can recover from crashes and failures
- **Persistent**: State survives across restarts
- **Evolving**: Rules and knowledge improve over time

---

## 2. Agent Components

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLE Agent                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │  Input       │───▶│  Event       │───▶│  Semantic    │      │
│  │  Handlers    │    │  Stream      │    │  Atomizer    │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│                                                  │              │
│  ┌──────────────┐    ┌──────────────┐           │              │
│  │  Consensus   │◀───│  Rule        │◀──────────┘              │
│  │  Engine      │    │  Manager     │                          │
│  └──────────────┘    └──────────────┘                          │
│         │                   │                                   │
│         │                   ▼                                   │
│         │         ┌──────────────────┐                       │
│         └─────────│  Blockchain       │                       │
│                   │  Interface        │                       │
│                   └──────────────────┘                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.1 Input Handlers

**Purpose**: Convert various input modalities into a unified event stream

**Supported Inputs**:

| Modality | Handler | Output |
|----------|---------|--------|
| Text | TextHandler | TextEvents |
| Voice | VoiceHandler | AudioEvents |
| Documents | DocHandler | DocumentEvents |
| Video | VideoHandler | FrameEvents + AudioEvents |

**Key Design**: All handlers output to the Event Stream, ensuring temporal consistency.

### 2.2 Event Stream

**Purpose**: Maintain chronological order of all interactions

**Properties**:

- **Ordered**: Events have timestamps
- **Interruptible**: Handles overlapping events (for full-duplex)
- **Partial**: Can process incomplete events
- **Persistent**: Events are stored locally

**Event Structure**:

```python
class Event:
    event_id: str              # Unique identifier
    timestamp: float           # When event occurred
    source: str                # Input handler origin
    modality: str              # text, voice, etc.
    speaker: Optional[str]     # Who produced it
    raw_content: Any           # Original content
    confidence: float          # Processing confidence
    metadata: Dict             # Additional info
```

### 2.3 Semantic Atomizer

**Purpose**: Extract meaning units (atoms) from raw events

**Extracts**:

| Atom Type | Description | Example |
|-----------|-------------|---------|
| Entities | Nouns, actors | "client", "manager" |
| Attributes | Properties | VIP=true, delay=short |
| Actions | Verbs, decisions | ignore, approve |
| Conditions | Context | "if client is important" |
| Negations | Inverted meaning | "not applicable" |
| Probabilities | Uncertainty | "usually", "maybe" |
| Temporal | Time markers | "always", "never" |

**Process**:

1. Parse raw content
2. Identify atom types
3. Normalize representations
4. Assign confidence scores

**Example**:

```
Input: "Usually VIP clients don't get penalties for short delays"

Atoms:
- Entity: client (type=VIP)
- Condition: delay (duration=short)
- Action: ignore_penalty
- Probability: usually (confidence=0.8)
```

### 2.4 Symbol Mapper

**Purpose**: Convert atoms to formal logical representations

**Process**:

1. Map atoms to logical predicates
2. Normalize to canonical form
3. Create rule skeleton

**Example**:

```
Atoms:
- client.VIP = true
- delay < T
- ignore_penalty = true

Canonical Rule:
IF Client.VIP = true AND Delay < threshold
THEN IgnorePenalty = true
```

**Canonicalization Rules**:

- Alphabetical ordering of conditions
- Standardized predicate names
- Normalized value representations
- Deterministic formatting

### 2.5 Symbolic Regression Engine

**Purpose**: Discover latent rules from accumulated symbols

**Methods**:

1. **Pattern Detection**: Find repeated co-occurrences
2. **Rule Induction**: Propose candidate rules
3. **Quality Evaluation**: Score rules by:
   - Coverage (how many events explained)
   - Simplicity (Occam's razor)
   - Consistency (low contradictions)

**Output**: RuleCandidate objects

---

### 2.6 Enhanced Symbolic Regression ✅ PHASE 3 - COMPLETED

**Purpose**: Advanced symbolic discovery using Genetic Programming (GP)

**Components**:

#### 2.6.1 SymbolicExpression
- Tree-based representation of symbolic rules
- Supports operators: +, *, >, <, ==, AND, OR
- Tracks fitness, complexity, and canonical form

#### 2.6.2 SymbolicRegressor
- **Genetic Programming (GP)**: Evolves expression trees
  - Population-based evolution (configurable size)
  - Tournament selection for parent selection
  - Crossover and mutation operators
  - Elitism to preserve best solutions
  
- **Fitness Function**: Combines multiple metrics
  - Coverage: Fraction of events explained
  - Correlation: Statistical fit to data
  - Simplicity penalty: Prefers simpler rules
  
- **Configuration**:
  ```yaml
  population_size: 100
  generations: 50
  mutation_rate: 0.1
  crossover_rate: 0.7
  max_depth: 5
  simplicity_weight: 0.3
  ```

#### 2.6.3 TemporalPatternRecognizer
- **Trend Detection**: Identifies increasing/decreasing/stable patterns
- **Periodicity Detection**: Finds repeating patterns using autocorrelation
- **Change Point Detection**: CUSUM-based detection of regime changes
- **Sliding Window**: Configurable window size for analysis

#### 2.6.4 UncertaintyQuantifier
- **Bootstrap Confidence Intervals**: Statistical bounds on predictions
- **Prediction Intervals**: t-distribution based bounds
- **Rule Confidence**: Combines coverage, consistency, and support

---

### 2.7 Multi-Modal Input Processing ✅ PHASE 3 - COMPLETED

**Purpose**: Handle diverse input modalities with unified processing

#### 2.7.1 VoiceHandler
- **Speech-to-Text**: Transcription of audio input
- **Emotion Detection**: Classifies emotional state
- **Speaker Identification**: Distinguishes different speakers
- **Audio Features**: Pitch, speech rate, pause frequency

#### 2.7.2 VideoHandler
- **Frame Extraction**: Key frame sampling from video
- **Scene Detection**: Identifies scene boundaries
- **Audio Track Processing**: Extracts and processes audio
- **Lip Sync**: Enables full-duplex interaction

#### 2.7.3 DocumentHandler
- **OCR**: Text extraction from scanned documents
- **PDF Processing**: Native PDF parsing
- **Layout Analysis**: Identifies structure (headers, tables, lists)
- **Table Extraction**: Extracts tabular data
- **Entity Extraction**: Named entity recognition

#### 2.7.4 ImageHandler
- **Object Detection**: Identifies objects in images
- **Scene Description**: Generates textual descriptions
- **Text Extraction**: OCR for embedded text
- **Feature Extraction**: Visual embeddings

#### 2.7.5 MultimodalProcessor
- **Unified Interface**: Single entry point for all modalities
- **Modality Routing**: Routes to appropriate handler
- **Result Aggregation**: Combines multi-modal outputs

#### 2.7.6 FullDuplexController
- **Simultaneous I/O**: Processes input and output concurrently
- **Interrupt Handling**: Gracefully handles interruptions
- **Real-time Processing**: Low-latency processing
- **State Management**: Tracks listening/speaking states

**RuleCandidate Structure**:

```python
class RuleCandidate:
    rule_id: str
    logic_form: str           # Canonical rule
    context: str              # Domain/context tags
    confidence: float
    coverage: float
    simplicity: float
    support_count: int
    contradiction_count: int
    evidence: List[str]       # Event IDs supporting this rule
```

### 2.6 Rule Manager

**Purpose**: Manage local rules and coordinate with network

**Responsibilities**:

1. Track all discovered rules
2. Maintain local rule state
3. Handle consensus feedback from network
4. Update confidence scores
5. Trigger rule broadcasts

**Rule Lifecycle**:

```
Discovery → Candidate → Broadcast → Consensus → Accepted
                                         ↓
                              Contradiction → Decay
                                         ↓
                              Verification → Strengthen
```

### 2.7 Consensus Engine

**Purpose**: Validate rules against network consensus

**Process**:

1. Receive rule commitments from network
2. Check independence of discoveries
3. Calculate confidence based on:
   - Number of supporting agents
   - Diversity of data sources
   - Time stability
4. Resolve conflicts
5. Update local rule state

### 2.8 Blockchain Interface

**Purpose**: Communicate with the network

**Functions**:

1. **Broadcast**: Send rule commitments
2. **Subscribe**: Receive network events
3. **Query**: Request rule state
4. **Sync**: Download latest consensus

---

## 3. Agent State

### 3.1 Local State Structure

```python
class AgentState:
    agent_id: str
    node_identity: Identity
    current_rules: Dict[str, Rule]
    event_history: List[Event]
    symbol_buffer: List[Atom]
    pending_commits: List[RuleCandidate]
    consensus_state: Dict[str, float]
    last_checkpoint: int
    last_sync: float
```

### 3.2 State Persistence

Agents persist state to:

- **Local disk**: For crash recovery
- **Network**: For migration and replication

**Checkpoint Strategy**:

- Periodic snapshots (configurable interval)
- On significant events (rule accepted, etc.)
- Before network operations

### 3.3 State Migration

If an agent needs to move to a new machine:

1. Export state to encrypted package
2. Broadcast availability
3. New agent imports and verifies
4. Resume operation with full history

---

## 4. Agent Lifecycle

```
┌─────────────┐
│   START     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  INITIALIZE │
│  - Load     │
│  - Sync     │
│  - Verify   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   OBSERVE   │◄──────────────────┐
│  - Capture  │                   │
│  - Extract  │                   │
└──────┬──────┘                   │
       │                          │
       ▼                          │
┌─────────────┐                   │
│  DISCOVER   │                   │
│  - Analyze  │                   │
│  - Propose  │                   │
└──────┬──────┘                   │
       │                          │
       ▼                          │
┌─────────────┐                   │
│  BROADCAST  │                   │
│  - Commit   │                   │
│  - Wait     │                   │
└──────┬──────┘                   │
       │                          │
       ▼                          │
┌─────────────┐                   │
│  CONSENSUS  │                   │
│  - Validate │                   │
│  - Update   │                   │
└──────┬──────┘                   │
       │                          │
       ▼                          │
┌─────────────┐                   │
│   LEARN     │                   │
│  - Adjust   │                   │
│  - Store    │                   │
└──────┬──────┘                   │
       │                          │
       ▼                          │
┌─────────────┐                   │
│   CHECK     │───── CRASH? ─────►│  RECOVER
│  - Healthy? │                   │  - Restore
└──────┬──────┘                   │  - Resume
       │ NO                       └─────────────
       ▼
┌─────────────┐
│   SYNC      │
│  - Network  │
│  - Update   │
└──────┬──────┘
       │
       ▼
    (back to OBSERVE)
```

---

## 5. Configuration

### 5.1 Core Parameters

```yaml
agent:
  id: auto-generated
  mode: full | light
  checkpoint_interval: 300  # seconds
  sync_interval: 60        # seconds

atomizer:
  confidence_threshold: 0.7
  max_tokens: 10000

discovery:
  min_coverage: 0.1
  simplicity_weight: 0.3
  min_support: 3

consensus:
  min_agents: 3
  independence_threshold: 0.8
  stability_window: 86400  # seconds
```

---

## 6. Failure Modes

### 6.1 Crash Recovery

If agent process dies:

1. On restart, load last checkpoint
2. Replay events since checkpoint
3. Verify consistency
4. Resume operation

### 6.2 Network Partition

If disconnected from network:

1. Continue local operation
2. Accumulate local discoveries
3. Broadcast on reconnection
4. Resolve any conflicts

### 6.3 Data Corruption

If local state corrupted:

1. Attempt recovery from replicas
2. If unavailable, reset to genesis state
3. Rebuild from network consensus

---

## 7. Security

### 7.1 Agent Identity

Each agent has a cryptographic identity:

- Public/private key pair
- Certificate from network (if applicable)
- Attestation of node capabilities

### 7.2 Communication Security

All network communication:

- Encrypted (TLS or similar)
- Authenticated (signatures)
- Forward-secret (session keys)

---

## 8. Related Documents

- **[System Overview](01_system_overview.md)**: Context for agent architecture
- **[Consensus Model](03_consensus_model.md)**: PoC specification
- **[Threat Model](04_threat_model.md)**: Security analysis
- **[Protocol Specification](../protocols/)**: Message formats

---

*Document Version: 1.1*
*Last Updated: February 2026*
*Changes: Added Phase 3 features (Enhanced Symbolic Regression, Multi-Modal Input)*
