"""
P2P Node Implementation

Core networking node for CLE-Net P2P communication.
"""

import asyncio
import json
import uuid
import hashlib
import base64
import time
from typing import Dict, List, Optional, Set, Callable
from dataclasses import dataclass, field
from enum import Enum


class MessageType(Enum):
    """Types of P2P messages."""
    HELLO = "hello"
    HELLO_ACK = "hello_ack"
    PING = "ping"
    PONG = "pong"
    PEER_EXCHANGE = "peer_exchange"
    GOSSIP = "gossip"
    STATE_SYNC = "state_sync"
    COMMIT = "commit"
    QUERY = "query"
    RESPONSE = "response"
    ERROR = "error"


@dataclass
class Peer:
    """Represents a network peer."""
    node_id: str
    address: str
    port: int
    public_key: str
    last_seen: float
    capabilities: List[str] = field(default_factory=list)
    is_connected: bool = False


@dataclass
class Message:
    """Network message envelope."""
    version: str = "1.0"
    message_type: str = ""
    message_id: str = ""
    timestamp: float = 0.0
    sender: Dict = field(default_factory=dict)
    payload: Dict = field(default_factory=dict)
    signature: str = ""

    @classmethod
    def create(cls, message_type: str, payload: Dict, sender: Dict) -> 'Message':
        """Create a new message."""
        return cls(
            message_type=message_type,
            message_id=str(uuid.uuid4()),
            timestamp=time.time(),
            sender=sender,
            payload=payload
        )

    def to_bytes(self) -> bytes:
        """Serialize message to bytes."""
        data = {
            "version": self.version,
            "message_type": self.message_type,
            "message_id": self.message_id,
            "timestamp": self.timestamp,
            "sender": self.sender,
            "payload": self.payload
        }
        return json.dumps(data, separators=(',', ':')).encode('utf-8')

    @classmethod
    def from_bytes(cls, data: bytes) -> 'Message':
        """Deserialize message from bytes."""
        parsed = json.loads(data.decode('utf-8'))
        return cls(**parsed)


@dataclass
class P2PConfig:
    """Configuration for P2P node."""
    node_id: str
    host: str = "0.0.0.0"
    port: int = 8888
    bootstrap_nodes: List[Dict] = field(default_factory=list)
    max_peers: int = 50
    ping_interval: float = 30.0
    gossip_fanout: int = 3
    gossip_ttl: int = 3
    private_key: bytes = None


class P2PNode:
    """
    CLE-Net P2P Network Node.
    
    Responsibilities:
    - Manage peer connections
    - Handle message routing
    - Implement gossip protocol
    - Maintain routing table
    """

    def __init__(self, config: P2PConfig):
        """
        Initialize P2P node.
        
        Args:
            config: Node configuration
        """
        self.config = config
        self.node_id = config.node_id
        self.peers: Dict[str, Peer] = {}
        self.connections: Dict[str, asyncio.StreamWriter] = {}
        self.handlers: Dict[str, Callable] = {}
        self.running = False
        self.server = None
        
        # Message cache for gossip deduplication
        self.message_cache: Set[str] = set()
        self.cache_ttl = 60  # seconds

    async def start(self):
        """Start the P2P node."""
        self.running = True
        
        # Start TCP server
        self.server = await asyncio.start_server(
            self.handle_connection,
            self.config.host,
            self.config.port
        )
        
        print(f"P2P node {self.node_id} listening on {self.config.host}:{self.config.port}")
        
        # Discover initial peers
        await self.discover_peers()
        
        # Start gossip loop
        asyncio.create_task(self.gossip_loop())
        
        # Start heartbeat
        asyncio.create_task(self.heartbeat_loop())

    async def stop(self):
        """Stop the P2P node."""
        self.running = False
        
        # Close all connections
        for writer in self.connections.values():
            writer.close()
        
        if self.server:
            self.server.close()
            await self.server.wait_closed()

    async def handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Handle incoming connection."""
        addr = writer.get_extra_info('peername')
        peer_id = None
        
        try:
            while self.running:
                data = await reader.read(65536)
                if not data:
                    break
                
                message = Message.from_bytes(data)
                
                # Handle message
                response = await self.process_message(message, writer)
                
                # Send response if any
                if response:
                    signed = self.sign_message(response)
                    writer.write(signed)
                    await writer.drain()
                
                peer_id = message.sender.get('node_id')
                
        except Exception as e:
            print(f"Error handling connection from {addr}: {e}")
        finally:
            if peer_id:
                self.disconnect_peer(peer_id)
            writer.close()
            await writer.wait_closed()

    async def process_message(self, message: Message, writer: asyncio.StreamWriter) -> Optional[Message]:
        """
        Process incoming message.
        
        Args:
            message: Incoming message
            writer: Response writer
            
        Returns:
            Response message or None
        """
        msg_type = message.message_type
        
        # Route to handler
        handler = self.handlers.get(msg_type)
        if handler:
            return await handler(message)
        
        # Default routing for unknown types
        print(f"Unknown message type: {msg_type}")
        return Message.create(
            message_type="error",
            payload={"error": f"Unknown message type: {msg_type}"},
            sender=self.get_sender_info()
        )

    def register_handler(self, message_type: str, handler: Callable):
        """Register message handler."""
        self.handlers[message_type] = handler

    async def connect_to_peer(self, peer: Peer) -> bool:
        """
        Connect to a remote peer.
        
        Args:
            peer: Peer to connect to
            
        Returns:
            True if connection successful
        """
        try:
            reader, writer = await asyncio.open_connection(
                peer.address,
                peer.port
            )
            
            # Perform handshake
            response = await self.handshake(reader, writer, peer)
            
            if response:
                self.connections[peer.node_id] = writer
                self.peers[peer.node_id] = peer
                peer.is_connected = True
                print(f"Connected to peer {peer.node_id}")
                return True
            
            writer.close()
            await writer.wait_closed()
            
        except Exception as e:
            print(f"Failed to connect to {peer.node_id}: {e}")
        
        return False

    async def handshake(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter, 
                        peer: Peer) -> Optional[Message]:
        """
        Perform connection handshake.
        
        Args:
            reader: Input stream
            writer: Output stream
            peer: Peer info
            
        Returns:
            Response message or None
        """
        # Send hello
        hello = Message.create(
            message_type="hello",
            payload={
                "node_id": self.node_id,
                "version": "1.0",
                "capabilities": ["consensus", "gossip", "sync"]
            },
            sender=self.get_sender_info()
        )
        
        signed = self.sign_message(hello)
        writer.write(signed)
        await writer.drain()
        
        # Receive response
        data = await asyncio.wait_for(reader.read(65536), timeout=10.0)
        if not data:
            return None
        
        response = Message.from_bytes(data)
        
        if response.message_type == "hello_ack":
            return response
        
        return None

    def disconnect_peer(self, peer_id: str):
        """Disconnect from a peer."""
        if peer_id in self.connections:
            writer = self.connections[peer_id]
            writer.close()
            del self.connections[peer_id]
        
        if peer_id in self.peers:
            self.peers[peer_id].is_connected = False

    async def discover_peers(self):
        """Discover initial peers from bootstrap nodes."""
        for bootstrap in self.config.bootstrap_nodes:
            try:
                reader, writer = await asyncio.open_connection(
                    bootstrap['host'],
                    bootstrap['port']
                )
                
                # Request peers
                request = Message.create(
                    message_type="peer_request",
                    payload={"node_id": self.node_id},
                    sender=self.get_sender_info()
                )
                
                signed = self.sign_message(request)
                writer.write(signed)
                await writer.drain()
                
                # Receive response
                data = await asyncio.wait_for(reader.read(65536), timeout=10.0)
                response = Message.from_bytes(data)
                
                if response.message_type == "peer_exchange":
                    for peer_data in response.payload.get('peers', []):
                        if peer_data['node_id'] != self.node_id:
                            peer = Peer(
                                node_id=peer_data['node_id'],
                                address=peer_data['address'],
                                port=peer_data.get('port', 8888),
                                public_key=peer_data.get('public_key', ''),
                                last_seen=time.time()
                            )
                            if peer.node_id not in self.peers:
                                self.peers[peer.node_id] = peer
                                asyncio.create_task(self.connect_to_peer(peer))
                
                writer.close()
                await writer.wait_closed()
                
            except Exception as e:
                print(f"Bootstrap node {bootstrap['host']} unreachable: {e}")

    async def broadcast(self, message: Message, topic: str):
        """
        Broadcast message via gossip protocol.
        
        Args:
            message: Message to broadcast
            topic: Gossip topic
        """
        gossip = Message.create(
            message_type="gossip",
            payload={
                "gossip_id": str(uuid.uuid4()),
                "topic": topic,
                "item_hashes": [message.message_id],
                "ttl": self.config.gossip_ttl,
                "origin": self.node_id
            },
            sender=self.get_sender_info()
        )
        
        await self.gossip_message(gossip)

    async def gossip_message(self, message: Message):
        """
        Spread message through gossip protocol.
        
        Args:
            message: Gossip message
        """
        message_id = message.payload.get('gossip_id', '')
        
        # Check cache
        if message_id in self.message_cache:
            return
        
        self.message_cache.add(message_id)
        
        # Clean old cache entries periodically
        if len(self.message_cache) > 10000:
            self.message_cache.clear()
        
        # Forward to random peers
        peers = self.get_random_peers(self.config.gossip_fanout)
        ttl = message.payload.get('ttl', 3)
        
        if ttl > 0:
            for peer_id in peers:
                if peer_id in self.connections:
                    writer = self.connections[peer_id]
                    try:
                        signed = self.sign_message(message)
                        writer.write(signed)
                        await writer.drain()
                    except Exception:
                        self.disconnect_peer(peer_id)

    def get_random_peers(self, k: int) -> List[str]:
        """
        Get k random peer IDs.
        
        Args:
            k: Number of peers to return
            
        Returns:
            List of peer IDs
        """
        connected = [pid for pid, peer in self.peers.items() 
                     if peer.is_connected and pid in self.connections]
        
        if len(connected) <= k:
            return connected
        
        import random
        return random.sample(connected, k)

    async def gossip_loop(self):
        """Background gossip processing loop."""
        while self.running:
            await asyncio.sleep(1)
            # Gossip maintenance happens in message processing

    async def heartbeat_loop(self):
        """Background heartbeat loop."""
        while self.running:
            await asyncio.sleep(self.config.ping_interval)
            
            for peer_id, writer in list(self.connections.items()):
                try:
                    ping = Message.create(
                        message_type="ping",
                        payload={"timestamp": time.time()},
                        sender=self.get_sender_info()
                    )
                    signed = self.sign_message(ping)
                    writer.write(signed)
                    await writer.drain()
                except Exception:
                    self.disconnect_peer(peer_id)

    def get_sender_info(self) -> Dict:
        """Get sender information for messages."""
        return {
            "node_id": self.node_id,
            "host": self.config.host,
            "port": self.config.port
        }

    def sign_message(self, message: Message) -> bytes:
        """
        Sign a message.
        
        Args:
            message: Message to sign
            
        Returns:
            Signed message bytes
        """
        if self.config.private_key:
            # In real implementation, use actual crypto
            message.signature = "signature_placeholder"
        return message.to_bytes()

    def get_status(self) -> Dict:
        """Get node status."""
        return {
            "node_id": self.node_id,
            "connected_peers": len(self.connections),
            "known_peers": len(self.peers),
            "running": self.running
        }
