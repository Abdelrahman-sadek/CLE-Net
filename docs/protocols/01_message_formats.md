# CLE-Net Protocol Specification: Message Formats

This document defines the wire-level message formats for CLE-Net communication.

---

## 1. Overview

CLE-Net uses a simple JSON-based protocol for all network communication. Messages are:

- **Atomic**: One request/response per message
- **Ordered**: Messages within a session are ordered
- **Authenticated**: All messages include sender signature

---

## 2. Message Envelope

All messages wrap the payload in a standard envelope:

```json
{
  "version": "1.0",
  "message_type": "commit | query | response | error",
  "message_id": "uuid-v4",
  "timestamp": 1700000000.000,
  "sender": {
    "agent_id": "agent_xxxxxxxx",
    "node_id": "node_xxxxxxxx",
    "public_key": "base64-encoded-public-key"
  },
  "payload": { ... },
  "signature": "base64-encoded-signature"
}
```

### Envelope Fields

| Field | Type | Description |
|-------|------|-------------|
| version | string | Protocol version (e.g., "1.0") |
| message_type | enum | Type of message |
| message_id | string | Unique message identifier |
| timestamp | float | Unix timestamp of creation |
| sender | object | Sender identification |
| payload | object | Message-specific content |
| signature | string | Ed25519 signature of payload |

---

## 3. Message Types

### 3.1 Rule Commit Message

Broadcast a discovered rule to the network.

```json
{
  "message_type": "commit",
  "payload": {
    "rule_hash": "rule_xxxxxxxxxxxxxxxx",
    "logic_signature": "a1b2c3d4e5f6",
    "context_signature": "f6e5d4c3b2a1",
    "confidence": 0.75,
    "evidence_count": 5,
    "metadata": {
      "source_domain": "customer_support",
      "language": "en"
    }
  }
}
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| rule_hash | string | SHA256 hash of canonical rule |
| logic_signature | string | Hash of normalized logic form |
| context_signature | string | Hash of context string |
| confidence | float | Agent confidence (0-1) |
| evidence_count | int | Number of supporting events |
| metadata | object | Additional context |

### 3.2 Challenge Message

Challenge a previously committed rule.

```json
{
  "message_type": "challenge",
  "payload": {
    "target_rule_hash": "rule_xxxxxxxxxxxxxxxx",
    "contradicting_rule": {
      "logic_form": "IF Client.VIP = false ...",
      "context": "security_policy"
    },
    "reason": "Contradicts security requirements",
    "evidence": ["event_1", "event_2"]
  }
}
```

### 3.3 Confirm Message

Confirm support for a rule.

```json
{
  "message_type": "confirm",
  "payload": {
    "rule_hash": "rule_xxxxxxxxxxxxxxxx",
    "confidence_delta": 0.05,
    "additional_evidence": 3
  }
}
```

### 3.4 Query Message

Query the network for rules or state.

```json
{
  "message_type": "query",
  "payload": {
    "query_type": "by_hash | by_context | by_agent",
    "filters": {
      "rule_hash": "rule_xxxxxxxxxxxxxxxx",
      "context_pattern": "*vip*",
      "agent_id": "agent_xxxxxxxx",
      "min_confidence": 0.5,
      "limit": 100
    }
  }
}
```

### 3.5 Response Message

Response to a query.

```json
{
  "message_type": "response",
  "payload": {
    "request_id": "uuid-of-original-query",
    "results": [
      {
        "rule_hash": "rule_xxxxxxxxxxxxxxxx",
        "logic_signature": "a1b2c3d4e5f6",
        "confidence": 0.75,
        "supporting_agents": ["agent_a", "agent_b", "agent_c"],
        "created_at": 1700000000.000
      }
    ],
    "total_count": 1
  }
}
```

### 3.6 Error Message

Report an error.

```json
{
  "message_type": "error",
  "payload": {
    "error_code": "INVALID_SIGNATURE | UNKNOWN_HASH | RATE_LIMIT",
    "error_message": "Human-readable description",
    "details": { ... }
  }
}
```

### 3.7 State Sync Message

Request or send full state synchronization.

```json
{
  "message_type": "state_sync",
  "payload": {
    "sync_type": "request | response | push",
    "checkpoint_hash": "checkpoint_xxxxxxxx",
    "last_known_height": 1500,
    "state": { ... }  // Full state for response/push
  }
}
```

### 3.8 Gossip Message

Gossip protocol message for discovery.

```json
{
  "message_type": "gossip",
  "payload": {
    "gossip_type": "announce | request | response",
    "topics": ["new_commit", "challenge", "checkpoint"],
    "item_hashes": ["rule_xxx", "rule_yyy"],
    "ttl": 3  // Hop limit
  }
}
```

---

## 4. Phase 3 Message Types ✅ NEW

### 4.1 Multi-Modal Input Message

Process multi-modal input (voice, video, documents, images).

```json
{
  "message_type": "multimodal_input",
  "payload": {
    "modality": "voice | video | document | image",
    "input_data": "base64-encoded-content",
    "metadata": {
      "format": "wav | mp4 | pdf | png",
      "duration": 120.5,
      "sample_rate": 16000,
      "language": "en"
    }
  }
}
```

### 4.2 Enhanced Symbolic Regression Message

Exchange symbolic regression results and patterns.

```json
{
  "message_type": "symbolic_regression",
  "payload": {
    "regression_type": "gp_evolution | temporal_pattern | uncertainty_quantification",
    "expression": {
      "operator": "+",
      "left": {"value": "VIP"},
      "right": {"operator": "*", "left": {"value": "delay"}, "right": {"value": "0.5"}}
    },
    "fitness": 0.85,
    "complexity": 5,
    "generation": 42
  }
}
```

### 4.3 Full-Duplex Control Message

Control full-duplex interaction (simultaneous I/O).

```json
{
  "message_type": "full_duplex_control",
  "payload": {
    "action": "start_session | stop_session | interrupt | resume",
    "session_id": "uuid-v4",
    "timestamp": 1700000000.000
  }
}
```

---

## 5. State Models

### 4.1 Agent State

```typescript
interface AgentState {
  agent_id: string;
  node_id: string;
  public_key: string;
  
  // Local knowledge
  local_rules: Map<RuleHash, LocalRule>;
  event_buffer: Event[];
  
  // Consensus state
  pending_commits: Map<RuleHash, Commit>;
  accepted_rules: Set<RuleHash>;
  
  // Performance
  ccs_score: number;
  uptime_epochs: number;
  
  // Checkpoint
  last_checkpoint: number;
  state_hash: string;
}
```

### 4.2 Rule State

```typescript
interface RuleState {
  rule_hash: string;
  logic_form: string;
  context: string;
  
  // Discovery
  first_discovered: number;
  discovered_by: string[];
  
  // Consensus
  confidence: number;
  supporting_agents: number;
  contradicting_agents: number;
  
  // Lifecycle
  status: "pending" | "accepted" | "weakened" | "deprecated";
  last_updated: number;
  deprecated_at?: number;
}
```

### 4.3 Ledger State

```typescript
interface LedgerState {
  height: number;
  checkpoint_hash: string;
  
  // Rule commitments
  commits: Map<RuleHash, CommitRecord>;
  
  // Consensus results
  accepted_rules: Set<RuleHash>;
  
  // Challenges
  challenges: Map<RuleHash, ChallengeRecord>;
}
```

---

## 5. Protocol Constants

| Constant | Value | Description |
|----------|-------|-------------|
| PROTOCOL_VERSION | "1.0" | Current protocol version |
| MAX_MESSAGE_SIZE | 65536 | 64KB max message size |
| MAX_PAYLOAD_SIZE | 60000 | Max payload within message |
| DEFAULT_TIMEOUT | 5000 | Default response timeout (ms) |
| MAX_RETRIES | 3 | Max retry attempts |
| GOSSIP_TTL | 3 | Gossip time-to-live hops |
| SYNC_BATCH_SIZE | 100 | State sync batch size |

---

## 6. Serialization

Messages are serialized as JSON with:

- UTF-8 encoding
- No whitespace except for formatting
- Sorted keys for deterministic output
- NaN/Infinity replaced with null

### Example Serialization

```python
def serialize_message(envelope: dict) -> bytes:
    # Remove signature for signing
    payload = envelope.copy()
    del payload["signature"]
    
    # Sort keys for determinism
    payload["payload"] = sort_dict_recursive(payload["payload"])
    
    # Serialize
    json_str = json.dumps(payload, separators=(',', ':'), ensure_ascii=False)
    return json_str.encode('utf-8')
```

---

## 7. Security

### 7.1 Signing

All messages are signed using Ed25519:

```python
def sign_message(envelope: dict, private_key: bytes) -> str:
    serialized = serialize_message(envelope)
    signature = ed25519_sign(serialized, private_key)
    return base64.b64encode(signature).decode('ascii')
```

### 7.2 Verification

```python
def verify_message(envelope: dict) -> bool:
    signature = base64.b64decode(envelope["signature"])
    serialized = serialize_message(envelope)
    return ed25519_verify(serialized, signature, envelope["sender"]["public_key"])
```

### 7.3 Encryption

For sensitive payloads, use NaCl box encryption:

```json
{
  "encrypted_payload": "base64-encoded-nacl-box",
  "nonce": "base64-encoded-nonce"
}
```

---

## 8. Related Documents

- **[Consensus Model](../../architecture/03_consensus_model.md)**: PoC specification
- **[Agent Architecture](../../architecture/02_agent_architecture.md)**: Agent state management
- **[Threat Model](../../architecture/04_threat_model.md)**: Security considerations

---

*Document Version: 1.1*
*Last Updated: February 2026*
*Changes: Added Phase 3 message types (Multi-Modal Input, Enhanced Symbolic Regression, Full-Duplex Control)*
