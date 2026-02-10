"""
CLE-Net Consensus Module

This module manages validators, consensus, and Proof of Cognition (PoC).
It maps CLE-Net's consensus to Tendermint's BFT consensus.
"""

from typing import Dict, List, Optional, Set
from datetime import datetime
import hashlib

from ..types import (
    ValidatorInfo,
    ValidatorRole,
    CognitiveStateBlock,
    MessageType
)


class ConsensusKeeper:
    """
    Keeper for the consensus module.
    
    Manages validators, their roles, and consensus state.
    """
    
    def __init__(self):
        """Initialize the consensus keeper."""
        self.validators: Dict[str, ValidatorInfo] = {}
        self.active_validators: Set[str] = set()
        self.proposer_queue: List[str] = []
        self.current_proposer_index: int = 0
        self.block_height: int = 0
        self.last_block_hash: str = ""
    
    def get_validator(self, validator_address: str) -> Optional[ValidatorInfo]:
        """Get a validator by address."""
        return self.validators.get(validator_address)
    
    def set_validator(self, validator: ValidatorInfo) -> None:
        """Set a validator in state."""
        self.validators[validator.validator_address] = validator
    
    def get_all_validators(self) -> List[ValidatorInfo]:
        """Get all validators."""
        return list(self.validators.values())
    
    def get_validators_by_role(self, role: ValidatorRole) -> List[ValidatorInfo]:
        """Get validators by role."""
        return [v for v in self.validators.values() if v.role == role]
    
    def get_active_validators(self) -> List[ValidatorInfo]:
        """Get all active validators."""
        return [v for v in self.validators.values() if v.validator_address in self.active_validators]
    
    def add_active_validator(self, validator_address: str) -> None:
        """Add a validator to the active set."""
        self.active_validators.add(validator_address)
    
    def remove_active_validator(self, validator_address: str) -> None:
        """Remove a validator from the active set."""
        self.active_validators.discard(validator_address)
    
    def get_current_proposer(self) -> Optional[ValidatorInfo]:
        """Get the current proposer."""
        if not self.proposer_queue or self.current_proposer_index >= len(self.proposer_queue):
            return None
        proposer_address = self.proposer_queue[self.current_proposer_index]
        return self.get_validator(proposer_address)
    
    def rotate_proposer(self) -> Optional[ValidatorInfo]:
        """Rotate to the next proposer."""
        self.current_proposer_index = (self.current_proposer_index + 1) % len(self.proposer_queue)
        return self.get_current_proposer()
    
    def get_block_height(self) -> int:
        """Get the current block height."""
        return self.block_height
    
    def increment_block_height(self) -> int:
        """Increment the block height."""
        self.block_height += 1
        return self.block_height
    
    def set_last_block_hash(self, block_hash: str) -> None:
        """Set the last block hash."""
        self.last_block_hash = block_hash
    
    def get_last_block_hash(self) -> str:
        """Get the last block hash."""
        return self.last_block_hash


class RegisterValidatorMessage:
    """Message to register a new validator."""
    
    def __init__(
        self,
        validator_address: str,
        role: ValidatorRole,
        stake: float = 0.0
    ):
        self.type = MessageType.REGISTER_VALIDATOR
        self.validator_address = validator_address
        self.role = role
        self.stake = stake
        self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "type": self.type.value,
            "validator_address": self.validator_address,
            "role": self.role.value,
            "stake": self.stake,
            "timestamp": self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "RegisterValidatorMessage":
        """Create from dictionary."""
        return cls(
            validator_address=data["validator_address"],
            role=ValidatorRole(data["role"]),
            stake=data["stake"]
        )


class UpdateValidatorMessage:
    """Message to update validator information."""
    
    def __init__(
        self,
        validator_address: str,
        stake_delta: float = 0.0,
        uptime_delta: float = 0.0,
        laws_validated_delta: int = 0,
        conflicts_resolved_delta: int = 0
    ):
        self.type = MessageType.UPDATE_VALIDATOR
        self.validator_address = validator_address
        self.stake_delta = stake_delta
        self.uptime_delta = uptime_delta
        self.laws_validated_delta = laws_validated_delta
        self.conflicts_resolved_delta = conflicts_resolved_delta
        self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "type": self.type.value,
            "validator_address": self.validator_address,
            "stake_delta": self.stake_delta,
            "uptime_delta": self.uptime_delta,
            "laws_validated_delta": self.laws_validated_delta,
            "conflicts_resolved_delta": self.conflicts_resolved_delta,
            "timestamp": self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "UpdateValidatorMessage":
        """Create from dictionary."""
        return cls(
            validator_address=data["validator_address"],
            stake_delta=data["stake_delta"],
            uptime_delta=data["uptime_delta"],
            laws_validated_delta=data["laws_validated_delta"],
            conflicts_resolved_delta=data["conflicts_resolved_delta"]
        )


class ConsensusModule:
    """
    The consensus module for CLE-Net.
    
    This module handles:
    - Validator registration and management
    - Proposer selection
    - Proof of Cognition (PoC) consensus
    - Block proposal and validation
    """
    
    def __init__(self):
        """Initialize the consensus module."""
        self.keeper = ConsensusKeeper()
        self.min_stake = 1000.0  # Minimum stake to become a validator
        self.proposer_rotation_interval = 1  # Rotate proposer every block
        self.slashing_threshold = 0.5  # Slash validators with uptime below 50%
    
    def handle_register_validator(self, msg: RegisterValidatorMessage) -> bool:
        """
        Handle a register validator message.
        
        Registers a new validator if they meet the minimum stake requirement.
        """
        # Check minimum stake
        if msg.stake < self.min_stake:
            return False
        
        # Check if validator already exists
        if self.keeper.get_validator(msg.validator_address):
            return False
        
        # Create validator
        validator = ValidatorInfo(
            validator_address=msg.validator_address,
            role=msg.role,
            stake=msg.stake,
            uptime=100.0,
            laws_validated=0,
            conflicts_resolved=0,
            last_active=datetime.utcnow()
        )
        
        # Store validator
        self.keeper.set_validator(validator)
        
        # Add to active validators
        self.keeper.add_active_validator(msg.validator_address)
        
        # Add to proposer queue
        self.keeper.proposer_queue.append(msg.validator_address)
        
        return True
    
    def handle_update_validator(self, msg: UpdateValidatorMessage) -> bool:
        """
        Handle an update validator message.
        
        Updates validator information.
        """
        validator = self.keeper.get_validator(msg.validator_address)
        if not validator:
            return False
        
        # Update validator
        validator.stake += msg.stake_delta
        validator.uptime += msg.uptime_delta
        validator.laws_validated += msg.laws_validated_delta
        validator.conflicts_resolved += msg.conflicts_resolved_delta
        validator.last_active = datetime.utcnow()
        
        # Check for slashing
        if validator.uptime < self.slashing_threshold * 100:
            self._slash_validator(validator)
        
        # Store updated validator
        self.keeper.set_validator(validator)
        
        return True
    
    def propose_block(self, proposer_id: str, new_laws: List, updated_laws: List, 
                     ccs_updates: List, conflict_resolutions: List) -> CognitiveStateBlock:
        """
        Propose a new block.
        
        Creates a Cognitive State Block (CSB) with the proposed changes.
        """
        # Increment block height
        block_height = self.keeper.increment_block_height()
        
        # Get previous block hash
        prev_block_hash = self.keeper.get_last_block_hash()
        
        # Create block
        block = CognitiveStateBlock(
            block_height=block_height,
            block_hash="",  # Will be computed
            proposer_id=proposer_id,
            timestamp=datetime.utcnow(),
            new_laws=new_laws,
            updated_laws=updated_laws,
            ccs_updates=ccs_updates,
            conflict_resolutions=conflict_resolutions,
            prev_block_hash=prev_block_hash
        )
        
        # Compute block hash
        block.block_hash = block.compute_hash()
        
        return block
    
    def validate_block(self, block: CognitiveStateBlock) -> bool:
        """
        Validate a proposed block.
        
        Checks that the block is valid according to PoC consensus.
        """
        # Check block height
        if block.block_height != self.keeper.get_block_height():
            return False
        
        # Check previous block hash
        if block.prev_block_hash != self.keeper.get_last_block_hash():
            return False
        
        # Check block hash
        if block.block_hash != block.compute_hash():
            return False
        
        # Check proposer is active
        proposer = self.keeper.get_validator(block.proposer_id)
        if not proposer or block.proposer_id not in self.keeper.active_validators:
            return False
        
        # Validate laws
        for law in block.new_laws:
            if not self._validate_law(law):
                return False
        
        for law in block.updated_laws:
            if not self._validate_law(law):
                return False
        
        return True
    
    def commit_block(self, block: CognitiveStateBlock) -> None:
        """
        Commit a validated block.
        
        Updates the consensus state after a block is committed.
        """
        # Set last block hash
        self.keeper.set_last_block_hash(block.block_hash)
        
        # Rotate proposer
        self.keeper.rotate_proposer()
        
        # Update proposer's stats
        proposer = self.keeper.get_validator(block.proposer_id)
        if proposer:
            proposer.laws_validated += len(block.new_laws) + len(block.updated_laws)
            self.keeper.set_validator(proposer)
    
    def get_proposer_sequence(self, count: int = 10) -> List[str]:
        """
        Get the next N proposers in sequence.
        
        Useful for planning and validation.
        """
        proposers = []
        for i in range(count):
            index = (self.keeper.current_proposer_index + i) % len(self.keeper.proposer_queue)
            proposers.append(self.keeper.proposer_queue[index])
        return proposers
    
    def get_validator_set(self) -> List[ValidatorInfo]:
        """
        Get the current validator set.
        
        Returns all active validators sorted by stake.
        """
        validators = self.keeper.get_active_validators()
        return sorted(validators, key=lambda v: v.stake, reverse=True)
    
    def _validate_law(self, law) -> bool:
        """
        Validate a law.
        
        Checks that the law is well-formed.
        """
        # Check law has required fields
        if not law.law_id or not law.symbolic_expression or not law.context:
            return False
        
        # Check law hash
        if law.compute_hash() != law.to_dict()["hash"]:
            return False
        
        return True
    
    def _slash_validator(self, validator: ValidatorInfo) -> None:
        """
        Slash a validator for misbehavior.
        
        Reduces stake and may deactivate the validator.
        """
        # Slash 50% of stake
        validator.stake *= 0.5
        
        # Remove from active validators if stake is too low
        if validator.stake < self.min_stake:
            self.keeper.remove_active_validator(validator.validator_address)
            # Remove from proposer queue
            if validator.validator_address in self.keeper.proposer_queue:
                self.keeper.proposer_queue.remove(validator.validator_address)
        
        self.keeper.set_validator(validator)


class ProofOfCognition:
    """
    Proof of Cognition (PoC) consensus mechanism.
    
    PoC is CLE-Net's consensus mechanism that rewards independent
    discovery of cognitive laws.
    """
    
    def __init__(self, consensus_module: ConsensusModule):
        """Initialize PoC."""
        self.consensus = consensus_module
        self.discovery_window = 100  # Blocks to consider for discovery
        self.min_independent_discoverers = 2  # Minimum independent discoverers
    
    def validate_discovery(self, law_id: str, discoverers: List[str]) -> bool:
        """
        Validate that a law was independently discovered.
        
        Checks that the law was discovered by multiple independent parties.
        """
        # Check minimum number of discoverers
        if len(discoverers) < self.min_independent_discoverers:
            return False
        
        # Check that discoverers are independent (not the same validator)
        unique_discoverers = set(discoverers)
        if len(unique_discoverers) < self.min_independent_discoverers:
            return False
        
        # Check that discoverers are active validators
        for discoverer in discoverers:
            validator = self.consensus.keeper.get_validator(discoverer)
            if not validator or discoverer not in self.consensus.keeper.active_validators:
                return False
        
        return True
    
    def calculate_cognitive_reward(self, law_id: str, discoverers: List[str]) -> Dict[str, float]:
        """
        Calculate cognitive rewards for discoverers.
        
        Rewards are distributed based on contribution and independence.
        """
        # Base reward
        base_reward = 100.0
        
        # Calculate reward per discoverer
        reward_per_discoverer = base_reward / len(discoverers)
        
        # Distribute rewards
        rewards = {}
        for discoverer in discoverers:
            rewards[discoverer] = reward_per_discoverer
        
        return rewards
    
    def validate_consensus(self, block: CognitiveStateBlock, votes: Dict[str, bool]) -> bool:
        """
        Validate consensus on a block.
        
        Checks that 2/3 of validators voted for the block.
        """
        # Get active validators
        validators = self.consensus.get_validator_set()
        
        # Count votes
        total_votes = len(votes)
        approve_votes = sum(1 for vote in votes.values() if vote)
        
        # Check 2/3 supermajority
        if total_votes < len(validators) * 2 / 3:
            return False
        
        if approve_votes < total_votes * 2 / 3:
            return False
        
        return True
