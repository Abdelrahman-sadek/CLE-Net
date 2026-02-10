"""
CLE-Net Incentive Mechanisms Module

This module provides incentive mechanisms for node operation in CLE-Net.
It ensures that nodes are properly incentivized to participate in the network.
"""

from typing import Dict, List, Optional
from datetime import datetime
import math


class IncentiveType:
    """Types of incentives."""
    CCS = "cognitive_contribution_score"
    TOKEN = "token"
    REPUTATION = "reputation"


class IncentiveEvent:
    """Represents an incentive event."""
    
    def __init__(
        self,
        event_id: str,
        node_id: str,
        incentive_type: str,
        amount: float,
        reason: str,
        timestamp: datetime
    ):
        self.event_id = event_id
        self.node_id = node_id
        self.incentive_type = incentive_type
        self.amount = amount
        self.reason = reason
        self.timestamp = timestamp
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "event_id": self.event_id,
            "node_id": self.node_id,
            "incentive_type": self.incentive_type,
            "amount": self.amount,
            "reason": self.reason,
            "timestamp": self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "IncentiveEvent":
        """Create from dictionary."""
        return cls(
            event_id=data["event_id"],
            node_id=data["node_id"],
            incentive_type=data["incentive_type"],
            amount=data["amount"],
            reason=data["reason"],
            timestamp=datetime.fromisoformat(data["timestamp"])
        )


class NodeIncentives:
    """Represents the incentives for a node."""
    
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.ccs_score = 0.0
        self.token_balance = 0.0
        self.reputation_score = 0.0
        self.incentive_events: List[IncentiveEvent] = []
        self.last_updated = datetime.utcnow()
    
    def add_incentive(
        self,
        incentive_type: str,
        amount: float,
        reason: str
    ) -> IncentiveEvent:
        """
        Add an incentive to the node.
        
        Args:
            incentive_type: Type of incentive
            amount: Amount of incentive
            reason: Reason for the incentive
            
        Returns:
            IncentiveEvent object
        """
        # Generate event ID
        event_id = f"event_{self.node_id}_{int(datetime.utcnow().timestamp())}"
        
        # Create event
        event = IncentiveEvent(
            event_id=event_id,
            node_id=self.node_id,
            incentive_type=incentive_type,
            amount=amount,
            reason=reason,
            timestamp=datetime.utcnow()
        )
        
        # Update incentives
        if incentive_type == IncentiveType.CCS:
            self.ccs_score += amount
        elif incentive_type == IncentiveType.TOKEN:
            self.token_balance += amount
        elif incentive_type == IncentiveType.REPUTATION:
            self.reputation_score += amount
        
        # Add to events
        self.incentive_events.append(event)
        self.last_updated = datetime.utcnow()
        
        return event
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "node_id": self.node_id,
            "ccs_score": self.ccs_score,
            "token_balance": self.token_balance,
            "reputation_score": self.reputation_score,
            "incentive_events": [event.to_dict() for event in self.incentive_events],
            "last_updated": self.last_updated.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "NodeIncentives":
        """Create from dictionary."""
        incentives = cls(node_id=data["node_id"])
        incentives.ccs_score = data["ccs_score"]
        incentives.token_balance = data["token_balance"]
        incentives.reputation_score = data["reputation_score"]
        incentives.incentive_events = [
            IncentiveEvent.from_dict(event_data)
            for event_data in data["incentive_events"]
        ]
        incentives.last_updated = datetime.fromisoformat(data["last_updated"])
        return incentives


class IncentiveMechanism:
    """
    Incentive mechanism for CLE-Net nodes.
    
    This class provides:
    - CCS-based incentives
    - Token-based incentives
    - Reputation-based incentives
    - Reward distribution
    - Penalty enforcement
    """
    
    def __init__(self):
        """Initialize the incentive mechanism."""
        self.node_incentives: Dict[str, NodeIncentives] = {}
        self.base_ccs_reward = 100.0
        self.base_token_reward = 10.0
        self.base_reputation_reward = 1.0
        self.decay_rate = 0.01  # 1% decay per day
        self.min_reputation = -100.0
        self.max_reputation = 100.0
    
    def register_node(self, node_id: str) -> NodeIncentives:
        """
        Register a node for incentives.
        
        Args:
            node_id: ID of the node
            
        Returns:
            NodeIncentives object
        """
        if node_id not in self.node_incentives:
            self.node_incentives[node_id] = NodeIncentives(node_id)
        return self.node_incentives[node_id]
    
    def reward_law_discovery(
        self,
        node_id: str,
        law_confidence: float,
        is_novel: bool = False
    ) -> IncentiveEvent:
        """
        Reward a node for discovering a law.
        
        Args:
            node_id: ID of the node
            law_confidence: Confidence of the discovered law
            is_novel: Whether the law is novel
            
        Returns:
            IncentiveEvent object
        """
        incentives = self.register_node(node_id)
        
        # Calculate reward
        base_reward = self.base_ccs_reward
        confidence_bonus = law_confidence * 50.0
        novelty_bonus = 100.0 if is_novel else 0.0
        
        total_reward = base_reward + confidence_bonus + novelty_bonus
        
        # Add incentive
        event = incentives.add_incentive(
            incentive_type=IncentiveType.CCS,
            amount=total_reward,
            reason=f"Law discovery (confidence: {law_confidence:.2f}, novel: {is_novel})"
        )
        
        return event
    
    def reward_law_validation(
        self,
        node_id: str,
        is_correct: bool
    ) -> IncentiveEvent:
        """
        Reward a node for validating a law.
        
        Args:
            node_id: ID of the node
            is_correct: Whether the validation was correct
            
        Returns:
            IncentiveEvent object
        """
        incentives = self.register_node(node_id)
        
        # Calculate reward
        if is_correct:
            reward = self.base_ccs_reward * 0.3  # 30 CCS for correct validation
            reason = "Correct law validation"
        else:
            reward = -self.base_ccs_score * 0.1  # -10 CCS for incorrect validation
            reason = "Incorrect law validation"
        
        # Add incentive
        event = incentives.add_incentive(
            incentive_type=IncentiveType.CCS,
            amount=reward,
            reason=reason
        )
        
        return event
    
    def reward_conflict_resolution(
        self,
        node_id: str,
        resolution_type: str
    ) -> IncentiveEvent:
        """
        Reward a node for resolving a conflict.
        
        Args:
            node_id: ID of the node
            resolution_type: Type of resolution (merge, prioritize, deprecate, context_split)
            
        Returns:
            IncentiveEvent object
        """
        incentives = self.register_node(node_id)
        
        # Calculate reward based on resolution type
        resolution_rewards = {
            "merge": 200.0,
            "prioritize": 150.0,
            "deprecate": 100.0,
            "context_split": 250.0
        }
        
        reward = resolution_rewards.get(resolution_type, 100.0)
        
        # Add incentive
        event = incentives.add_incentive(
            incentive_type=IncentiveType.CCS,
            amount=reward,
            reason=f"Conflict resolution ({resolution_type})"
        )
        
        return event
    
    def reward_block_proposal(
        self,
        node_id: str,
        block_size: int
    ) -> IncentiveEvent:
        """
        Reward a node for proposing a block.
        
        Args:
            node_id: ID of the node
            block_size: Size of the block
            
        Returns:
            IncentiveEvent object
        """
        incentives = self.register_node(node_id)
        
        # Calculate reward
        base_reward = self.base_token_reward
        size_bonus = min(block_size * 0.1, 50.0)  # Max 50 bonus for block size
        
        total_reward = base_reward + size_bonus
        
        # Add incentive
        event = incentives.add_incentive(
            incentive_type=IncentiveType.TOKEN,
            amount=total_reward,
            reason=f"Block proposal (size: {block_size})"
        )
        
        return event
    
    def reward_network_participation(
        self,
        node_id: str,
        uptime: float
    ) -> IncentiveEvent:
        """
        Reward a node for network participation.
        
        Args:
            node_id: ID of the node
            uptime: Uptime percentage (0-100)
            
        Returns:
            IncentiveEvent object
        """
        incentives = self.register_node(node_id)
        
        # Calculate reward
        if uptime >= 99.0:
            reward = self.base_token_reward * 2.0  # 2x reward for excellent uptime
            reason = f"Excellent network participation (uptime: {uptime:.2f}%)"
        elif uptime >= 95.0:
            reward = self.base_token_reward * 1.5  # 1.5x reward for good uptime
            reason = f"Good network participation (uptime: {uptime:.2f}%)"
        elif uptime >= 90.0:
            reward = self.base_token_reward  # Base reward for acceptable uptime
            reason = f"Acceptable network participation (uptime: {uptime:.2f}%)"
        else:
            reward = -self.base_token_reward * 0.5  # Penalty for poor uptime
            reason = f"Poor network participation (uptime: {uptime:.2f}%)"
        
        # Add incentive
        event = incentives.add_incentive(
            incentive_type=IncentiveType.TOKEN,
            amount=reward,
            reason=reason
        )
        
        return event
    
    def penalize_misbehavior(
        self,
        node_id: str,
        misbehavior_type: str,
        severity: float = 1.0
    ) -> IncentiveEvent:
        """
        Penalize a node for misbehavior.
        
        Args:
            node_id: ID of the node
            misbehavior_type: Type of misbehavior
            severity: Severity of the misbehavior (0-1)
            
        Returns:
            IncentiveEvent object
        """
        incentives = self.register_node(node_id)
        
        # Calculate penalty
        base_penalty = self.base_ccs_score * 0.5
        severity_multiplier = severity
        
        total_penalty = base_penalty * severity_multiplier
        
        # Add incentive (negative)
        event = incentives.add_incentive(
            incentive_type=IncentiveType.CCS,
            amount=-total_penalty,
            reason=f"Penalty for {misbehavior_type} (severity: {severity:.2f})"
        )
        
        # Also penalize reputation
        reputation_penalty = -self.base_reputation_reward * 10 * severity_multiplier
        incentives.add_incentive(
            incentive_type=IncentiveType.REPUTATION,
            amount=reputation_penalty,
            reason=f"Reputation penalty for {misbehavior_type}"
        )
        
        return event
    
    def apply_decay(self, node_id: str) -> None:
        """
        Apply decay to a node's incentives.
        
        Args:
            node_id: ID of the node
        """
        if node_id not in self.node_incentives:
            return
        
        incentives = self.node_incentives[node_id]
        
        # Apply decay to CCS
        incentives.ccs_score *= (1 - self.decay_rate)
        
        # Clamp reputation
        incentives.reputation_score = max(
            self.min_reputation,
            min(self.max_reputation, incentives.reputation_score)
        )
        
        incentives.last_updated = datetime.utcnow()
    
    def get_node_incentives(self, node_id: str) -> Optional[NodeIncentives]:
        """
        Get the incentives for a node.
        
        Args:
            node_id: ID of the node
            
        Returns:
            NodeIncentives object or None if not found
        """
        return self.node_incentives.get(node_id)
    
    def get_all_incentives(self) -> Dict[str, NodeIncentives]:
        """
        Get all node incentives.
        
        Returns:
            Dictionary of node IDs to NodeIncentives objects
        """
        return self.node_incentives.copy()
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """
        Get the leaderboard of nodes by CCS score.
        
        Args:
            limit: Maximum number of nodes to return
            
        Returns:
            List of dictionaries with node information
        """
        # Sort nodes by CCS score
        sorted_nodes = sorted(
            self.node_incentives.items(),
            key=lambda x: x[1].ccs_score,
            reverse=True
        )
        
        # Create leaderboard
        leaderboard = []
        for rank, (node_id, incentives) in enumerate(sorted_nodes[:limit], 1):
            leaderboard.append({
                "rank": rank,
                "node_id": node_id,
                "ccs_score": incentives.ccs_score,
                "token_balance": incentives.token_balance,
                "reputation_score": incentives.reputation_score,
                "last_updated": incentives.last_updated.isoformat()
            })
        
        return leaderboard
    
    def get_total_incentives(self) -> Dict:
        """
        Get the total incentives distributed.
        
        Returns:
            Dictionary with total incentives
        """
        total_ccs = sum(incentives.ccs_score for incentives in self.node_incentives.values())
        total_tokens = sum(incentives.token_balance for incentives in self.node_incentives.values())
        total_reputation = sum(incentives.reputation_score for incentives in self.node_incentives.values())
        
        return {
            "total_ccs": total_ccs,
            "total_tokens": total_tokens,
            "total_reputation": total_reputation,
            "total_nodes": len(self.node_incentives)
        }
