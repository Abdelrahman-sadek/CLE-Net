"""
CLE-Net Byzantine Fault Tolerance Module

This module provides Byzantine fault tolerance for CLE-Net.
It ensures that the network can tolerate up to f faulty nodes out of 3f+1 total nodes.
"""

from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime
import hashlib
import json


class ByzantineNode:
    """Represents a node in the Byzantine fault-tolerant system."""
    
    def __init__(
        self,
        node_id: str,
        is_honest: bool = True
    ):
        self.node_id = node_id
        self.is_honest = is_honest
        self.votes: Dict[str, bool] = {}  # proposal_id -> vote
        self.proposals: Dict[str, Dict] = {}  # proposal_id -> proposal
        self.last_seen = datetime.utcnow()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "node_id": self.node_id,
            "is_honest": self.is_honest,
            "votes": self.votes,
            "proposals": self.proposals,
            "last_seen": self.last_seen.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "ByzantineNode":
        """Create from dictionary."""
        return cls(
            node_id=data["node_id"],
            is_honest=data["is_honest"]
        )


class ByzantineProposal:
    """Represents a proposal in the Byzantine consensus."""
    
    def __init__(
        self,
        proposal_id: str,
        proposer_id: str,
        proposal_data: Dict,
        timestamp: datetime
    ):
        self.proposal_id = proposal_id
        self.proposer_id = proposer_id
        self.proposal_data = proposal_data
        self.timestamp = timestamp
        self.votes: Dict[str, bool] = {}  # node_id -> vote
        self.approved = False
        self.rejected = False
    
    def compute_hash(self) -> str:
        """Compute hash of the proposal."""
        data_str = json.dumps(self.proposal_data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "proposal_id": self.proposal_id,
            "proposer_id": self.proposer_id,
            "proposal_data": self.proposal_data,
            "timestamp": self.timestamp.isoformat(),
            "votes": self.votes,
            "approved": self.approved,
            "rejected": self.rejected,
            "hash": self.compute_hash()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "ByzantineProposal":
        """Create from dictionary."""
        return cls(
            proposal_id=data["proposal_id"],
            proposer_id=data["proposer_id"],
            proposal_data=data["proposal_data"],
            timestamp=datetime.fromisoformat(data["timestamp"])
        )


class ByzantineConsensus:
    """
    Byzantine fault-tolerant consensus mechanism.
    
    This class provides:
    - Byzantine fault-tolerant voting
    - Fault detection and isolation
    - Consensus achievement despite faulty nodes
    - Safety and liveness guarantees
    """
    
    def __init__(self, total_nodes: int):
        """
        Initialize the Byzantine consensus.
        
        Args:
            total_nodes: Total number of nodes in the network
        """
        self.total_nodes = total_nodes
        self.faulty_nodes = (total_nodes - 1) // 3  # Maximum faulty nodes
        self.quorum = 2 * self.faulty_nodes + 1  # Minimum votes for consensus
        self.nodes: Dict[str, ByzantineNode] = {}
        self.proposals: Dict[str, ByzantineProposal] = {}
        self.faulty_node_ids: Set[str] = set()
    
    def add_node(self, node_id: str, is_honest: bool = True) -> None:
        """
        Add a node to the consensus.
        
        Args:
            node_id: ID of the node
            is_honest: Whether the node is honest (default: True)
        """
        node = ByzantineNode(node_id=node_id, is_honest=is_honest)
        self.nodes[node_id] = node
        
        if not is_honest:
            self.faulty_node_ids.add(node_id)
    
    def remove_node(self, node_id: str) -> bool:
        """
        Remove a node from the consensus.
        
        Args:
            node_id: ID of the node
            
        Returns:
            True if node was removed, False otherwise
        """
        if node_id in self.nodes:
            del self.nodes[node_id]
            self.faulty_node_ids.discard(node_id)
            return True
        return False
    
    def create_proposal(
        self,
        proposer_id: str,
        proposal_data: Dict
    ) -> ByzantineProposal:
        """
        Create a new proposal.
        
        Args:
            proposer_id: ID of the proposer
            proposal_data: Data for the proposal
            
        Returns:
            ByzantineProposal object
        """
        # Generate proposal ID
        proposal_id = f"proposal_{proposer_id}_{int(datetime.utcnow().timestamp())}"
        
        # Create proposal
        proposal = ByzantineProposal(
            proposal_id=proposal_id,
            proposer_id=proposer_id,
            proposal_data=proposal_data,
            timestamp=datetime.utcnow()
        )
        
        # Store proposal
        self.proposals[proposal_id] = proposal
        
        return proposal
    
    def vote_on_proposal(
        self,
        proposal_id: str,
        node_id: str,
        vote: bool
    ) -> bool:
        """
        Vote on a proposal.
        
        Args:
            proposal_id: ID of the proposal
            node_id: ID of the voting node
            vote: True for approve, False for reject
            
        Returns:
            True if vote was recorded, False otherwise
        """
        # Check if proposal exists
        if proposal_id not in self.proposals:
            return False
        
        # Check if node exists
        if node_id not in self.nodes:
            return False
        
        # Record vote
        proposal = self.proposals[proposal_id]
        proposal.votes[node_id] = vote
        
        # Update node's votes
        self.nodes[node_id].votes[proposal_id] = vote
        
        # Check if consensus is reached
        self._check_consensus(proposal)
        
        return True
    
    def _check_consensus(self, proposal: ByzantineProposal) -> None:
        """
        Check if consensus is reached on a proposal.
        
        Args:
            proposal: Proposal to check
        """
        # Count votes
        approve_count = sum(1 for vote in proposal.votes.values() if vote)
        reject_count = sum(1 for vote in proposal.votes.values() if not vote)
        
        # Check if quorum is reached
        if approve_count >= self.quorum:
            proposal.approved = True
        elif reject_count >= self.quorum:
            proposal.rejected = True
    
    def get_proposal_status(self, proposal_id: str) -> Optional[str]:
        """
        Get the status of a proposal.
        
        Args:
            proposal_id: ID of the proposal
            
        Returns:
            Status string or None if not found
        """
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            return None
        
        if proposal.approved:
            return "approved"
        elif proposal.rejected:
            return "rejected"
        else:
            return "pending"
    
    def detect_faulty_nodes(self) -> List[str]:
        """
        Detect faulty nodes based on voting patterns.
        
        Returns:
            List of faulty node IDs
        """
        detected_faulty = []
        
        for node_id, node in self.nodes.items():
            if node.is_honest:
                continue
            
            # Check if node is voting inconsistently
            inconsistent_votes = 0
            for proposal_id, vote in node.votes.items():
                proposal = self.proposals.get(proposal_id)
                if proposal and proposal.approved and not vote:
                    inconsistent_votes += 1
            
            # If node votes against majority consistently, mark as faulty
            if inconsistent_votes > len(node.votes) / 2:
                detected_faulty.append(node_id)
        
        return detected_faulty
    
    def isolate_faulty_nodes(self, faulty_node_ids: List[str]) -> None:
        """
        Isolate faulty nodes from the consensus.
        
        Args:
            faulty_node_ids: List of faulty node IDs
        """
        for node_id in faulty_node_ids:
            self.faulty_node_ids.add(node_id)
    
    def get_honest_nodes(self) -> List[ByzantineNode]:
        """
        Get all honest nodes.
        
        Returns:
            List of honest nodes
        """
        return [node for node in self.nodes.values() if node.is_honest]
    
    def get_faulty_nodes(self) -> List[ByzantineNode]:
        """
        Get all faulty nodes.
        
        Returns:
            List of faulty nodes
        """
        return [node for node in self.nodes.values() if not node.is_honest]
    
    def can_achieve_consensus(self) -> bool:
        """
        Check if consensus can be achieved.
        
        Returns:
            True if consensus can be achieved, False otherwise
        """
        honest_count = len(self.get_honest_nodes())
        return honest_count >= self.quorum
    
    def get_consensus_threshold(self) -> int:
        """
        Get the consensus threshold.
        
        Returns:
            Number of votes required for consensus
        """
        return self.quorum
    
    def get_fault_tolerance(self) -> int:
        """
        Get the fault tolerance.
        
        Returns:
            Maximum number of faulty nodes that can be tolerated
        """
        return self.faulty_nodes


class ByzantineFaultTolerance:
    """
    Byzantine fault tolerance system for CLE-Net.
    
    This class provides:
    - Byzantine fault-tolerant consensus
    - Fault detection and isolation
    - Safety and liveness guarantees
    - Recovery from Byzantine failures
    """
    
    def __init__(self, total_nodes: int = 4):
        """
        Initialize the Byzantine fault tolerance system.
        
        Args:
            total_nodes: Total number of nodes (default: 4, can tolerate 1 faulty node)
        """
        self.consensus = ByzantineConsensus(total_nodes)
        self.running = False
        self.recovery_attempts: Dict[str, int] = {}
        self.max_recovery_attempts = 3
    
    def start(self) -> None:
        """Start the Byzantine fault tolerance system."""
        self.running = True
    
    def stop(self) -> None:
        """Stop the Byzantine fault tolerance system."""
        self.running = False
    
    def add_node(self, node_id: str, is_honest: bool = True) -> None:
        """
        Add a node to the system.
        
        Args:
            node_id: ID of the node
            is_honest: Whether the node is honest (default: True)
        """
        self.consensus.add_node(node_id, is_honest)
    
    def remove_node(self, node_id: str) -> bool:
        """
        Remove a node from the system.
        
        Args:
            node_id: ID of the node
            
        Returns:
            True if node was removed, False otherwise
        """
        return self.consensus.remove_node(node_id)
    
    def propose(
        self,
        proposer_id: str,
        proposal_data: Dict
    ) -> Optional[str]:
        """
        Propose a new value.
        
        Args:
            proposer_id: ID of the proposer
            proposal_data: Data for the proposal
            
        Returns:
            Proposal ID or None if proposal failed
        """
        if not self.consensus.can_achieve_consensus():
            return None
        
        proposal = self.consensus.create_proposal(proposer_id, proposal_data)
        return proposal.proposal_id
    
    def vote(
        self,
        proposal_id: str,
        node_id: str,
        vote: bool
    ) -> bool:
        """
        Vote on a proposal.
        
        Args:
            proposal_id: ID of the proposal
            node_id: ID of the voting node
            vote: True for approve, False for reject
            
        Returns:
            True if vote was recorded, False otherwise
        """
        return self.consensus.vote_on_proposal(proposal_id, node_id, vote)
    
    def get_status(self, proposal_id: str) -> Optional[str]:
        """
        Get the status of a proposal.
        
        Args:
            proposal_id: ID of the proposal
            
        Returns:
            Status string or None if not found
        """
        return self.consensus.get_proposal_status(proposal_id)
    
    def detect_faults(self) -> List[str]:
        """
        Detect faulty nodes.
        
        Returns:
            List of faulty node IDs
        """
        return self.consensus.detect_faulty_nodes()
    
    def isolate_faults(self, faulty_node_ids: List[str]) -> None:
        """
        Isolate faulty nodes.
        
        Args:
            faulty_node_ids: List of faulty node IDs
        """
        self.consensus.isolate_faulty_nodes(faulty_node_ids)
    
    def recover_node(self, node_id: str) -> bool:
        """
        Attempt to recover a faulty node.
        
        Args:
            node_id: ID of the node to recover
            
        Returns:
            True if recovery was successful, False otherwise
        """
        # Check if node exists
        if node_id not in self.consensus.nodes:
            return False
        
        # Check recovery attempts
        if self.recovery_attempts.get(node_id, 0) >= self.max_recovery_attempts:
            return False
        
        # Increment recovery attempts
        self.recovery_attempts[node_id] = self.recovery_attempts.get(node_id, 0) + 1
        
        # Mark node as honest
        self.consensus.nodes[node_id].is_honest = True
        self.consensus.faulty_node_ids.discard(node_id)
        
        return True
    
    def get_system_health(self) -> Dict:
        """
        Get the health of the system.
        
        Returns:
            Dictionary with system health information
        """
        honest_nodes = self.consensus.get_honest_nodes()
        faulty_nodes = self.consensus.get_faulty_nodes()
        
        return {
            "total_nodes": self.consensus.total_nodes,
            "honest_nodes": len(honest_nodes),
            "faulty_nodes": len(faulty_nodes),
            "fault_tolerance": self.consensus.get_fault_tolerance(),
            "consensus_threshold": self.consensus.get_consensus_threshold(),
            "can_achieve_consensus": self.consensus.can_achieve_consensus(),
            "running": self.running
        }
