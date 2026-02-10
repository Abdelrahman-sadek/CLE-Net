# CLE-Net P2P Network Layer Design

This document specifies the peer-to-peer network layer for CLE-Net.

---

## 1. Overview

The CLE-Net P2P layer enables:

- **Node Discovery**: Finding other CLE-Net participants
- **Message Routing**: Delivering messages to peers
- **Gossip Protocol**: Efficient information dissemination
- **State Synchronization**: Keeping nodes in sync

---

## 2. Network Topology

### 2.1 Hybrid Topology

CLE-Net uses a hybrid peer-to-peer topology:

```
┌─────────────────────────────────────────────────┐
│                  Bootstrap Nodes                  │
│           (Well-known, always-on)               │
└─────────────────────┬───────────────────────────┘
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
    ┌──────────┐           ┌──────────┐
    │  Peer A  │◄─────────►│  Peer B  │
    └────┬─────┘           └────┬─────┘
         │                       │
    ┌────┴─────┐           ┌────┴─────┐
    ▼           ▼           ▼           ▼
 ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐
 │Peer C│  │Peer D│  │Peer E│  │Peer F│
 └──────┘  └──────┘  └──────┘  └──────┘
```

**Characteristics:**

- **Bootstrap nodes**: Fixed entry points (DNS or well-known IPs)
- **Full mesh among active peers**: Each node maintains connections to ~10 peers
- **Partial mesh overall**: Network remains connected through multiple paths
- **No supernodes**: All peers have equal status

### 2.2 Connection Types

| Type | Purpose | Persistence |
|------|---------|-------------|
| Bootstrap | Initial discovery | Ephemeral |
| Persistent | Regular communication | Long-lived |
| Gossip | Information spread | Short-lived |
| Sync | State transfer | On-demand |

---

## 3. Node Discovery

### 3.1 Bootstrap List

Nodes maintain a list of bootstrap addresses:

```yaml
bootstrap_nodes:
  - host: "bootstrap-1.cle-net.example"
    port: 8888
    public_key: "base64-key-1"
  - host: "bootstrap-2.cle-net.example"
    port: 8888
    public_key: "base64-key-2"
  - host: "bootstrap-3.cle-net.example"
    port: 8888
    public_key: "base64-key-3"
```

### 3.2 Discovery Protocol

```python
class NodeDiscovery:
    async def discover(self) -> List[Peer]:
        """Discover peers from bootstrap nodes."""
        peers = []
        
        # Query bootstrap nodes
        for bootstrap in self.bootstrap_nodes:
            response = await self.query_bootstrap(bootstrap)
            peers.extend(response.known_peers)
        
        # Filter and deduplicate
        peers = self.filter_peers(peers)
        return peers
    
    async def query_bootstrap(self, node: Node) -> DiscoveryResponse:
        """Query a bootstrap node for peers."""
        message = {
            "type": "peer_request",
            "node_id": self.node_id,
            "capabilities": ["consensus", "gossip", "sync"]
        }
        return await self.send_and_wait(node, message)
```

### 3.3 Peer Exchange

When nodes connect, they exchange peer lists:

```json
{
  "message_type": "peer_exchange",
  "payload": {
    "peers": [
      {"node_id": "node_xxx", "address": "1.2.3.4:8888"},
      {"node_id": "node_yyy", "address": "5.6.7.8:8888"}
    ]
  }
}
```

---

## 4. Message Routing

### 4.1 Direct Routing

For known recipients:

```python
async def send_direct(self, peer: Peer, message: Message) -> Response:
    """Send message directly to a known peer."""
    connection = await self.get_connection(peer)
    return await connection.send(message)
```

### 4.2 Gossip Routing

For broadcast messages:

```python
async def gossip(self, message: Message, topic: str, ttl: int = 3):
    """Gossip a message through the network."""
    peers = self.get_random_peers(k=3)  # Fanout factor
    
    for peer in peers:
        asyncio.create_task(self.send_gossip(peer, message, topic, ttl))
```

**Gossip Parameters:**

| Parameter | Value | Description |
|-----------|-------|-------------|
| Fanout (k) | 3 | Peers per gossip step |
| TTL | 3 | Maximum hops |
| Cache TTL | 60s | Duplicate detection window |

### 4.3 Routing Table

Nodes maintain a routing table:

```python
class RoutingTable:
    def __init__(self):
        self.peers: Dict[NodeId, PeerInfo] = {}
        self.buckets: List[PeerBucket] = []
    
    def update(self, peer: PeerInfo):
        """Update routing table with new peer."""
        bucket = self.get_bucket(peer.node_id)
        if peer in bucket:
            bucket.move_to_head(peer)
        elif len(bucket) < bucket_size:
            bucket.add(peer)
        else:
            if self.should_replace(bucket.lru):
                bucket.remove(bucket.lru)
                bucket.add(peer)
```

---

## 5. Gossip Protocol

### 5.1 Message Types

| Type | Purpose |
|------|---------|
| `announce` | New rule commit available |
| `request` | Request information about topic |
| `response` | Respond to gossip request |
| `heartbeat` | Keep-alive signal |

### 5.2 Gossip Message Format

```json
{
  "message_type": "gossip",
  "payload": {
    "gossip_id": "uuid-v4",
    "topic": "new_commit",
    "topics": ["new_commit", "challenge"],
    "item_hashes": ["rule_abc123"],
    "ttl": 2,
    "origin": "node_xxx"
  }
}
```

### 5.3 Gossip Algorithm

```python
async def gossip_message(self, message: GossipMessage):
    """Spread message through gossip protocol."""
    topic = message.topic
    message_id = message.gossip_id
    
    # Check cache for duplicates
    if self.cache.has(message_id):
        return
    
    self.cache.add(message_id, ttl=60)
    
    # Process message
    await self.handle_gossip_message(message)
    
    # Forward to random peers (if TTL > 0)
    if message.ttl > 0:
        peers = self.get_random_peers(k=3)
        for peer in peers:
            await self.forward_gossip(peer, message)
```

### 5.4 Anti-Entropy

Nodes periodically synchronize:

```python
async def anti_entropy(self):
    """Perform anti-entropy synchronization."""
    peer = self.get_random_peer()
    
    # Exchange digests
    local_digest = self.compute_state_digest()
    request = {
        "type": "sync_digest",
        "digest": local_digest
    }
    response = await self.send_and_wait(peer, request)
    
    # Find differences
    differences = self.find_differences(local_digest, response.digest)
    
    # Sync missing items
    for item_hash in differences.missing:
        await self.request_item(peer, item_hash)
```

---

## 6. State Synchronization

### 6.1 Sync Protocol

```python
class StateSync:
    async def sync_state(self, peer: Peer, checkpoint_hash: str = None):
        """Synchronize state with a peer."""
        
        # Get checkpoint
        if checkpoint_hash:
            checkpoint = await self.get_checkpoint(peer, checkpoint_hash)
        else:
            checkpoint = await self.get_latest_checkpoint(peer)
        
        # Apply checkpoint
        await self.apply_checkpoint(checkpoint)
        
        # Sync missing items
        missing = self.find_missing(checkpoint.state_hash)
        for item_hash in missing:
            item = await self.get_item(peer, item_hash)
            await self.apply_item(item)
```

### 6.2 Checkpoint Format

```json
{
  "checkpoint": {
    "height": 1500,
    "hash": "sha256-of-checkpoint",
    "previous_hash": "sha256-of-previous",
    "timestamp": 1700000000.000,
    "state_root": "merkle-root",
    "accepted_rules": ["rule_abc", "rule_def"],
    "statistics": {
      "total_commits": 500,
      "total_agents": 50,
      "avg_confidence": 0.72
    },
    "signature": "aggregate-signature"
  }
}
```

---

## 7. Connection Management

### 7.1 Connection Lifecycle

```
DISCONNECTED → CONNECTING → HANDSHAKE → CONNECTED → CLOSING → DISCONNECTED
```

### 7.2 Handshake Protocol

```python
async def handshake(self, connection: Connection) -> bool:
    """Perform connection handshake."""
    
    # Step 1: Exchange hello
    hello = {
        "type": "hello",
        "version": PROTOCOL_VERSION,
        "node_id": self.node_id,
        "capabilities": ["v1", "consensus"]
    }
    await connection.send(hello)
    
    # Step 2: Receive hello
    response = await connection.receive()
    if not self.validate_hello(response):
        return False
    
    # Step 3: Exchange state summary
    state_summary = self.get_state_summary()
    await connection.send(state_summary)
    
    return True
```

### 7.3 Heartbeat

```python
async def heartbeat(self):
    """Send periodic heartbeat to peers."""
    while self.running:
        await asyncio.sleep(30)  # 30 second interval
        
        for peer in self.connected_peers:
            try:
                await self.send_heartbeat(peer)
            except ConnectionError:
                await self.handle_disconnect(peer)
```

---

## 8. Security

### 8.1 Node Authentication

All connections use TLS 1.3 with mutual authentication:

```yaml
tls_config:
  min_version: "1.3"
  cipher_suites:
    - "TLS_AES_256_GCM_SHA384"
  certificate_requirements:
    - selfsigned_allowed: false
    - requires_agent_id: true
```

### 8.2 Message Signing

All messages are signed:

```python
def sign_message(self, message: dict, private_key: bytes) -> str:
    serialized = json.dumps(message, sort_keys=True).encode()
    signature = ed25519_sign(serialized, private_key)
    return base64.b64encode(signature).decode()
```

### 8.3 Flood Prevention

Rate limiting per peer:

```python
RATE_LIMITS = {
    "commits_per_minute": 10,
    "queries_per_minute": 30,
    "bytes_per_second": 1048576  # 1 MB/s
}
```

---

## 9. Performance

### 9.1 Target Metrics

| Metric | Target |
|--------|--------|
| Discovery latency | < 2 seconds |
| Gossip convergence | < 10 seconds |
| Sync latency | < 30 seconds |
| Message latency (p95) | < 500 ms |

### 9.2 Scalability

| Parameter | Value |
|-----------|-------|
| Max peers per node | 50 |
| Gossip fanout | 3 |
| Gossip TTL | 3 |
| Expected convergence | O(log n) |

---

## 10. Implementation

### 10.1 Core Components

```python
class P2PNetwork:
    def __init__(self, config: P2PConfig):
        self.config = config
        self.discovery = NodeDiscovery(config)
        self.gossip = GossipProtocol(config)
        self.sync = StateSync(config)
        self.connections: Dict[PeerId, Connection] = {}
    
    async def start(self):
        """Start the P2P network layer."""
        await self.discovery.start()
        await self.connect_to_peers()
        await self.start_gossip()
    
    async def broadcast(self, message: Message, topic: str):
        """Broadcast message to network."""
        await self.gossip.broadcast(message, topic)
```

---

## 11. Related Documents

- **[Message Formats](01_message_formats.md)**: Wire protocol
- **[Consensus Model](../../architecture/03_consensus_model.md)**: PoC consensus
- **[Threat Model](../../architecture/04_threat_model.md)**: Security analysis

---

*Document Version: 1.1*
*Last Updated: February 2026*
*Changes: Updated to reflect Phase 3 completion (Enhanced Symbolic Regression, Multi-Modal Input)*
