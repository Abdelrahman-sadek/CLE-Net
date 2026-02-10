# System Overview

This document provides a high-level overview of the CLE-Net architecture.

## 1. Introduction

CLE-Net (Decentralized Cognitive Agent Network) is an experimental architecture for autonomous cognitive agents that extract, preserve, and evolve symbolic laws from human interaction.

### 1.1 Core Philosophy

The central insight driving CLE-Net is:

> Intelligence is not an answer. Intelligence is continuity of understanding over time.

Traditional AI systems focus on answering questions, executing tasks, or retrieving information. CLE-Net focuses on discovering the implicit rules that govern human behavior and persisting those rules across a decentralized network.

### 1.2 What CLE-Net Is Not

- Not a chatbot or conversational AI
- Not a task execution agent
- Not a RAG (Retrieval-Augmented Generation) system
- Not a traditional blockchain

### 1.3 What CLE-Net Is

- A cognitive architecture for law discovery
- A decentralized network for knowledge persistence
- An exploration of symbolic + neural hybrid AI
- A research platform for understanding cognition

---

## 2. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Human Interaction Layer                   │
│         (Text, Voice, Documents, Multimodal Input)            │
└─────────────────────────────┬───────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────┐
│                    CLE Agent Layer                            │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Event Stream                                        │    │
│  │  → Captures interactions in real-time                │    │
│  └─────────────────────────────┬─────────────────────────┘    │
│                                │                               │
│  ┌─────────────────────────────▼─────────────────────────┐    │
│  │  Semantic Atomizer                                   │    │
│  │  → Extracts entities, actions, conditions            │    │
│  └─────────────────────────────┬─────────────────────────┘    │
│                                │                               │
│  ┌─────────────────────────────▼─────────────────────────┐    │
│  │  Symbol Mapper                                       │    │
│  │  → Converts atoms to logical predicates              │    │
│  └─────────────────────────────┬─────────────────────────┘    │
│                                │                               │
│  ┌─────────────────────────────▼─────────────────────────┐    │
│  │  Symbolic Regression Engine                         │    │
│  │  → Discovers latent rules from symbols               │    │
│  └─────────────────────────────┬─────────────────────────┘    │
└────────────────────────────────┼──────────────────────────────┘
                                 │
┌────────────────────────────────▼──────────────────────────────┐
│                    Cognitive Graph Layer                       │
│  ┌─────────────────────────────────────────────────────┐      │
│  │  Knowledge Graph                                    │      │
│  │  → Persistent, temporal graph of rules              │      │
│  └─────────────────────────────┬─────────────────────────┘      │
└────────────────────────────────┼───────────────────────────────┘
                                 │
┌────────────────────────────────▼──────────────────────────────┐
│                   Blockchain / Consensus Layer                 │
│  ┌─────────────────────────────────────────────────────┐      │
│  │  Rule Ledger                                         │      │
│  │  → Stores rule hashes, signatures, metadata          │      │
│  └─────────────────────────────┬─────────────────────────┘      │
│                                │                               │
│  ┌─────────────────────────────▼─────────────────────────┐      │
│  │  Proof of Cognition (PoC)                           │      │
│  │  → Consensus on discovered rules                     │      │
│  └─────────────────────────────┬─────────────────────────┘      │
│                                │                               │
│  ┌─────────────────────────────▼─────────────────────────┐      │
│  │  Incentive Layer                                    │      │
│  │  → Rewards for rule discovery and validation        │      │
│  └─────────────────────────────┬─────────────────────────┘      │
└────────────────────────────────┼───────────────────────────────┘
                                 │
┌────────────────────────────────▼──────────────────────────────┐
│                    Distributed Node Layer                      │
│  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐        │
│  │   Node A      │ │   Node B      │ │   Node C      │        │
│  │  (Miner)      │ │  (Watchdog)   │ │  (Replica)    │        │
│  └───────────────┘ └───────────────┘ └───────────────┘        │
└───────────────────────────────────────────────────────────────┘
```

---

## 3. Core Layers

### 3.1 Human Interaction Layer

**Purpose**: Capture human input in various modalities

**Supported Inputs**:
- Text (chat, documents, logs) ✅ COMPLETED
- Voice (conversations, meetings) ✅ COMPLETED
  - Speech-to-text transcription
  - Emotion detection
  - Speaker identification
- Documents (PDF, scanned files) ✅ COMPLETED
  - OCR text extraction
  - Layout analysis
  - Table extraction
- Video (with audio extraction) ✅ COMPLETED
  - Frame extraction
  - Scene detection
  - Audio track processing
- Images ✅ COMPLETED
  - Object detection
  - Scene description
  - Text extraction (OCR)
- Full-duplex interaction ✅ COMPLETED
  - Simultaneous input/output
  - Interrupt handling
  - Real-time processing

**Key Insight**: All inputs are converted to an event stream, preserving temporal relationships.

### 3.2 CLE Agent Layer

**Purpose**: Extract cognitive content from raw interaction

**Components**:

1. **Event Stream** ✅ COMPLETED
   - Captures interactions in sequence
   - Preserves temporal ordering
   - Handles interruptions naturally

2. **Semantic Atomizer** ✅ COMPLETED
   - Extracts entities (who, what)
   - Extracts actions (verbs, decisions)
   - Extracts conditions (context, constraints)
   - Extracts negations, probabilities, temporal markers

3. **Symbol Mapper** ✅ COMPLETED
   - Converts atoms to logical predicates
   - Normalizes representations
   - Creates canonical forms

4. **Symbolic Regression Engine** ✅ COMPLETED
   - Discovers patterns in symbols
   - Proposes candidate rules
   - Evaluates rule quality (coverage, simplicity)

5. **Enhanced Symbolic Regression** ✅ PHASE 3 - COMPLETED
   - Genetic Programming (GP) for complex pattern discovery
   - Temporal pattern recognition (trends, periodicity, change points)
   - Uncertainty quantification (bootstrap confidence intervals)
   - Bayesian optimization for parameter tuning

6. **Multi-Modal Input Processing** ✅ PHASE 3 - COMPLETED
   - VoiceHandler: Speech-to-text, emotion detection, speaker identification
   - VideoHandler: Frame extraction, scene detection, audio track processing
   - DocumentHandler: OCR, PDF processing, layout analysis, table extraction
   - ImageHandler: Object detection, scene description, text extraction
   - MultimodalProcessor: Unified interface for all modalities
   - FullDuplexController: Full-duplex interaction support (simultaneous I/O)

### 3.3 Cognitive Graph Layer

**Purpose**: Persist and evolve discovered knowledge

**Properties**:
- Temporal (stores history of changes)
- Probabilistic (edges have confidence weights)
- Contradiction-tolerant (allows conflicting rules)
- Cumulative (no deletion, only decay)

### 3.4 Blockchain / Consensus Layer

**Purpose**: Coordinate multiple agents and persist state

**Components**:

1. **Rule Ledger**
   - Append-only storage of rule metadata
   - Stores hashes, not raw rules
   - Preserves provenance

2. **Proof of Cognition (PoC)**
   - Consensus mechanism for rule validation
   - Requires independent discovery by multiple agents
   - Replaces energy/capital with cognition

3. **Incentive Layer**
   - Rewards rule discovery
   - Encourages stable, simple rules
   - Penalizes contradictions

### 3.5 Distributed Node Layer

**Purpose**: Ensure network survivability

**Node Types**:
- **Miners**: Process events, discover rules, broadcast commits
- **Watchdogs**: Monitor network health, detect anomalies
- **Replicas**: Store state, enable recovery after failures

---

## 4. Data Flow

### 4.1 Forward Flow (Knowledge Discovery)

```
Human Interaction
        ↓
Event Stream (capture)
        ↓
Semantic Atomizer (extract atoms)
        ↓
Symbol Mapper (convert to logic)
        ↓
Symbolic Regression (discover rules)
        ↓
Cognitive Graph (persist)
        ↓
Rule Commit (broadcast hash + metadata)
        ↓
PoC Consensus (validate with other agents)
        ↓
Global Knowledge (accepted rules)
```

### 4.2 Feedback Flow (Learning)

```
Global Knowledge
        ↓
Agent Sync (download new rules)
        ↓
Local Reasoning (apply rules to new interactions)
        ↓
Rule Validation (confirm or contradict)
        ↓
Feedback to Network (report confidence changes)
        ↓
Rule Decay/Strengthen (adaptive learning)
```

---

## 5. Key Innovations

### 5.1 Symbolic + Neural Hybrid

CLE-Net combines:

- **Neural**: LLMs for understanding, pattern recognition
- **Symbolic**: Explicit rules, logical reasoning, knowledge graphs

The best of both worlds: statistical power + explainability

### 5.2 Proof of Cognition

A novel consensus mechanism where:

- Truth emerges from independent discovery
- No single agent controls the narrative
- Energy replaced by reasoning

### 5.3 Contradiction as Signal

In traditional systems, contradictions are errors.

In CLE-Net, contradictions are first-class signals indicating:

- Complex domain knowledge
- Context-dependent rules
- Areas requiring more evidence

### 5.4 Persistence Through Transformation

Agents can die, machines can fail, but knowledge persists:

- State is replicated across nodes
- Consensus ensures agreement
- Transformation (migration) preserves identity

---

## 6. Limitations

### 6.1 Current Limitations

- No absolute truth guarantee
- Economic model is experimental
- Scalability untested
- Symbolic extraction is probabilistic

### 6.2 Fundamental Limitations

- Physical shutdown kills all nodes (physics)
- Global coordination can override consensus
- Ethical use requires human oversight

---

## 7. Next Steps

- **[Agent Architecture](02_agent_architecture.md)**: Deep dive into CLE agent components
- **[Consensus Model](03_consensus_model.md)**: Detailed PoC specification
- **[Threat Model](04_threat_model.md)**: Security analysis
- **[Whitepaper](../whitepaper/)**: Complete research document

---

*Document Version: 1.1*
*Last Updated: February 2026*
*Changes: Added Phase 3 features (Enhanced Symbolic Regression, Multi-Modal Input)*
