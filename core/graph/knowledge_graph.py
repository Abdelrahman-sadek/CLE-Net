"""
Knowledge Graph Module

Optimized knowledge graph for CLE-Net cognitive representation.

Graph RAG inspired by: github.com/rahulnyk/knowledge_graph
"""

import hashlib
import json
import time
from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import networkx as nx


class NodeType(Enum):
    """Types of graph nodes."""
    ENTITY = "entity"
    PREDICATE = "predicate"
    RULE = "rule"
    CONTEXT = "context"
    EVENT = "event"
    AGENT = "agent"


class EdgeType(Enum):
    """Types of graph edges."""
    HAS_PROPERTY = "has_property"
    IMPLIES = "implies"
    CONTRADICTS = "contradicts"
    SUPPORTS = "supports"
    DEPENDS_ON = "depends_on"
    OCCURRED_IN = "occurred_in"
    DISCOVERED_BY = "discovered_by"


@dataclass
class Node:
    """Graph node."""
    node_id: str
    node_type: NodeType
    properties: Dict = field(default_factory=dict)
    created_at: float = 0.0
    updated_at: float = 0.0
    confidence: float = 1.0
    active: bool = True
    
    def to_dict(self) -> dict:
        return self.__dict__
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Node':
        data['node_type'] = NodeType(data['node_type'])
        return cls(**data)


@dataclass
class Edge:
    """Graph edge."""
    edge_id: str
    source_id: str
    target_id: str
    edge_type: EdgeType
    weight: float = 1.0
    created_at: float = 0.0
    active: bool = True
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return self.__dict__
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Edge':
        data['edge_type'] = EdgeType(data['edge_type'])
        return cls(**data)


@dataclass
class KnowledgeGraphConfig:
    """Configuration for knowledge graph."""
    max_nodes: int = 100000
    max_edges: int = 500000
    cache_size: int = 10000
    decay_rate: float = 0.01
    consolidation_interval: int = 3600  # 1 hour


class KnowledgeGraph:
    """
    Knowledge graph for CLE-Net.
    
    Features:
    - Temporal graph (stores history)
    - Contradiction handling
    - Rule evolution
    - Graph RAG integration
    """
    
    def __init__(self, config: KnowledgeGraphConfig = None):
        """
        Initialize knowledge graph.
        
        Args:
            config: Graph configuration
        """
        self.config = config or KnowledgeGraphConfig()
        
        # NetworkX graph
        self.graph = nx.DiGraph()
        
        # Indices for fast lookup
        self.node_index: Dict[str, Node] = {}
        self.type_index: Dict[NodeType, Set[str]] = defaultdict(set)
        self.property_index: Dict[str, Set[str]] = defaultdict(set)
        
        # Temporal storage
        self.node_history: List[Dict] = []
        self.edge_history: List[Dict] = []
        
        # Statistics
        self.stats = {
            "nodes_added": 0,
            "edges_added": 0,
            "contradictions_found": 0,
            "rules_stored": 0
        }
    
    def add_node(self, node_type: NodeType, properties: Dict, 
                confidence: float = 1.0) -> str:
        """
        Add a node to the graph.
        
        Args:
            node_type: Type of node
            properties: Node properties
            confidence: Confidence score
            
        Returns:
            Node ID
        """
        # Generate node ID
        node_id = self._generate_node_id(node_type, properties)
        
        # Check limit
        if len(self.node_index) >= self.config.max_nodes:
            self._consolidate()
        
        # Create node
        node = Node(
            node_id=node_id,
            node_type=node_type,
            properties=properties,
            created_at=time.time(),
            updated_at=time.time(),
            confidence=confidence
        )
        
        # Add to graph
        self.graph.add_node(node_id, **node.to_dict())
        self.node_index[node_id] = node
        self.type_index[node_type].add(node_id)
        
        # Index properties
        for key, value in properties.items():
            if isinstance(value, (str, int, float)):
                self.property_index[f"{key}:{value}"].add(node_id)
        
        # Record history
        self.node_history.append({
            "action": "add",
            "node_id": node_id,
            "timestamp": time.time()
        })
        
        self.stats["nodes_added"] += 1
        
        return node_id
    
    def add_edge(self, source_id: str, target_id: str, 
                edge_type: EdgeType, weight: float = 1.0,
                metadata: Dict = None) -> str:
        """
        Add an edge to the graph.
        
        Args:
            source_id: Source node ID
            target_id: Target node ID
            edge_type: Type of edge
            weight: Edge weight
            metadata: Additional metadata
            
        Returns:
            Edge ID
        """
        # Validate nodes exist
        if source_id not in self.node_index or target_id not in self.node_index:
            raise ValueError("Source or target node not found")
        
        # Generate edge ID
        edge_id = self._generate_edge_id(source_id, target_id, edge_type)
        
        # Create edge
        edge = Edge(
            edge_id=edge_id,
            source_id=source_id,
            target_id=target_id,
            edge_type=edge_type,
            weight=weight,
            created_at=time.time(),
            metadata=metadata or {}
        )
        
        # Add to graph
        self.graph.add_edge(source_id, target_id, **edge.to_dict())
        
        # Record history
        self.edge_history.append({
            "action": "add",
            "edge_id": edge_id,
            "timestamp": time.time()
        })
        
        self.stats["edges_added"] += 1
        
        return edge_id
    
    def find_pattern(self, pattern: Dict) -> List[str]:
        """
        Find nodes matching a pattern.
        
        Args:
            pattern: Search pattern (e.g., {"type": "entity", "properties": {...}})
            
        Returns:
            List of matching node IDs
        """
        results = []
        
        for node_id, node in self.node_index.items():
            if node.node_type == NodeType(pattern.get("type", "")):
                match = True
                for key, value in pattern.get("properties", {}).items():
                    if node.properties.get(key) != value:
                        match = False
                        break
                if match:
                    results.append(node_id)
        
        return results
    
    def get_subgraph(self, node_ids: List[str], depth: int = 1) -> nx.DiGraph:
        """
        Get subgraph around specified nodes.
        
        Args:
            node_ids: Starting node IDs
            depth: Traversal depth
            
        Returns:
            Subgraph
        """
        subgraph = self.graph.subgraph(node_ids).copy()
        
        for _ in range(depth):
            # Expand
            new_nodes = set()
            for node_id in list(subgraph.nodes()):
                # Predecessors
                preds = list(self.graph.predecessors(node_id))
                new_nodes.update(preds)
                # Successors
                succs = list(self.graph.successors(node_id))
                new_nodes.update(succs)
            
            # Add to subgraph
            for nid in new_nodes:
                if nid not in subgraph:
                    subgraph.add_node(nid, **self.node_index[nid].to_dict())
            
            # Add edges
            for nid in new_nodes:
                for pred in self.graph.predecessors(nid):
                    if pred in subgraph:
                        subgraph.add_edge(pred, nid, **self.graph.edges[pred, nid])
                for succ in self.graph.successors(nid):
                    if succ in subgraph:
                        subgraph.add_edge(nid, succ, **self.graph.edges[nid, succ])
        
        return subgraph
    
    def detect_contradictions(self) -> List[Tuple[str, str]]:
        """
        Detect contradictory rules in the graph.
        
        Returns:
            List of (contradicting_node_1, contradicting_node_2)
        """
        contradictions = []
        
        # Find all rule nodes
        rule_nodes = [nid for nid, n in self.node_index.items() 
                     if n.node_type == NodeType.RULE]
        
        for i, rule1 in enumerate(rule_nodes):
            for rule2 in rule_nodes[i+1:]:
                # Check if they contradict
                if self._check_contradiction(rule1, rule2):
                    contradictions.append((rule1, rule2))
                    self.stats["contradictions_found"] += 1
        
        return contradictions
    
    def _check_contradiction(self, node1_id: str, node2_id: str) -> bool:
        """Check if two nodes contradict."""
        node1 = self.node_index.get(node1_id)
        node2 = self.node_index.get(node2_id)
        
        if not node1 or not node2:
            return False
        
        # Check for explicit contradiction edge
        for succ in self.graph.successors(node1_id):
            edge_data = self.graph.edges[node1_id, succ]
            if edge_data.get("edge_type") == EdgeType.CONTRADICTS.value:
                if succ == node2_id:
                    return True
        
        # Check logical contradiction
        # (Simplified - production would use proper logic)
        props1 = node1.properties
        props2 = node2.properties
        
        # Check for mutually exclusive properties
        if "condition" in props1 and "condition" in props2:
            if props1["condition"] != props2["condition"]:
                # Same predicate, different conditions
                pred1 = props1.get("predicate", "")
                pred2 = props2.get("predicate", "")
                if pred1 == pred2:
                    return True
        
        return False
    
    def apply_decay(self):
        """Apply confidence decay to nodes."""
        current_time = time.time()
        
        for node_id, node in self.node_index.items():
            # Calculate decay
            age = current_time - node.updated_at
            decay_factor = self.config.decay_rate * (age / 3600)  # Per hour
            
            # Apply decay
            node.confidence = max(0.1, node.confidence * (1 - decay_factor))
            node.updated_at = current_time
            
            # Deactivate very old low-confidence nodes
            if node.confidence < 0.1 and age > 7 * 24 * 3600:  # 7 days
                node.active = False
    
    def consolidate(self):
        """Consolidate graph - remove inactive nodes/edges."""
        inactive_nodes = [nid for nid, n in self.node_index.items() if not n.active]
        
        for node_id in inactive_nodes:
            # Remove from graph
            self.graph.remove_node(node_id)
            
            # Remove from indices
            self.type_index[n].discard(node_id)
            del self.node_index[node_id]
            
            # Clean property index
            for key in list(self.property_index.keys()):
                self.property_index[key].discard(node_id)
                if not self.property_index[key]:
                    del self.property_index[key]
    
    def _consolidate(self):
        """Internal consolidation with decay."""
        self.apply_decay()
        self.consolidate()
    
    def _generate_node_id(self, node_type: NodeType, properties: Dict) -> str:
        """Generate unique node ID."""
        content = f"{node_type.value}:{json.dumps(properties, sort_keys=True)}"
        return f"node_{hashlib.sha256(content.encode()).hexdigest()[:16]}"
    
    def _generate_edge_id(self, source: str, target: str, edge_type: EdgeType) -> str:
        """Generate unique edge ID."""
        content = f"{source}:{target}:{edge_type.value}"
        return f"edge_{hashlib.sha256(content.encode()).hexdigest()[:16]}"
    
    def export(self) -> Dict:
        """Export graph as dictionary."""
        return {
            "nodes": [n.to_dict() for n in self.node_index.values()],
            "edges": [
                {
                    "source": e.source_id,
                    "target": e.target_id,
                    **e.to_dict()
                }
                for e in self._get_all_edges()
            ],
            "stats": self.stats,
            "timestamp": time.time()
        }
    
    def _get_all_edges(self) -> List[Edge]:
        """Get all edges from graph."""
        edges = []
        for u, v, data in self.graph.edges(data=True):
            edge = Edge(
                edge_id=data.get("edge_id", ""),
                source_id=u,
                target_id=v,
                edge_type=EdgeType(data.get("edge_type", "has_property")),
                weight=data.get("weight", 1.0),
                created_at=data.get("created_at", 0.0)
            )
            edges.append(edge)
        return edges
    
    def get_statistics(self) -> Dict:
        """Get graph statistics."""
        return {
            "total_nodes": len(self.node_index),
            "total_edges": self.graph.number_of_edges(),
            "nodes_by_type": {
                nt.value: len(ids) for nt, ids in self.type_index.items()
            },
            "stats": self.stats
        }


class GraphRAGIntegrator:
    """
    Integrates knowledge graph with RAG (Retrieval-Augmented Generation).
    
    Inspired by: github.com/rahulnyk/knowledge_graph
    """
    
    def __init__(self, knowledge_graph: KnowledgeGraph):
        """
        Initialize integrator.
        
        Args:
            knowledge_graph: Connected knowledge graph
        """
        self.graph = knowledge_graph
    
    def query(self, query_text: str, top_k: int = 5) -> List[Dict]:
        """
        Query the knowledge graph using RAG.
        
        Args:
            query_text: Query text
            top_k: Number of results
            
        Returns:
            List of relevant nodes with context
        """
        # Extract entities from query (simplified)
        query_entities = self._extract_entities(query_text)
        
        # Find matching nodes
        results = []
        for entity in query_entities:
            node_ids = self.graph.property_index.get(f"entity:{entity}", set())
            for nid in list(node_ids)[:top_k]:
                node = self.graph.node_index.get(nid)
                if node:
                    results.append({
                        "node_id": nid,
                        "type": node.node_type.value,
                        "properties": node.properties,
                        "confidence": node.confidence,
                        "context": self._get_context(nid)
                    })
        
        # Sort by confidence
        results.sort(key=lambda x: x["confidence"], reverse=True)
        
        return results[:top_k]
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract entities from text (simplified)."""
        # In production, use NER
        return text.lower().split()
    
    def _get_context(self, node_id: str) -> Dict:
        """Get context for a node."""
        return {
            "predecessors": list(self.graph.graph.predecessors(node_id)),
            "successors": list(self.graph.graph.successors(node_id))
        }
    
    def add_rule_context(self, rule_id: str, supporting_evidence: List[str],
                        contradicting_evidence: List[str] = None):
        """
        Add RAG context to a rule.
        
        Args:
            rule_id: Rule node ID
            supporting_evidence: Supporting evidence IDs
            contradicting_evidence: Contradicting evidence IDs
        """
        # Add supporting edges
        for evidence_id in supporting_evidence:
            self.graph.add_edge(
                rule_id, evidence_id,
                EdgeType.SUPPORTS
            )
        
        # Add contradicting edges
        if contradicting_evidence:
            for evidence_id in contradicting_evidence:
                self.graph.add_edge(
                    rule_id, evidence_id,
                    EdgeType.CONTRADICTS
                )
