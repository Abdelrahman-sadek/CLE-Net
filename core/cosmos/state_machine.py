"""
CLE-Net State Machine

This module implements the cognitive state machine for CLE-Net.
It defines the state transitions for cognitive laws, CCS, and consensus.
"""

from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import hashlib
import json


class StateTransition(Enum):
    """Types of state transitions."""
    LAW_PROPOSED = "law_proposed"
    LAW_VALIDATING = "law_validating"
    LAW_VALIDATED = "law_validated"
    LAW_ACTIVATED = "law_activated"
    LAW_ACTIVE = "law_active"
    LAW_CONFLICTED = "law_conflicted"
    LAW_DEPRECATED = "law_deprecated"
    LAW_REVOKED = "law_revoked"
    CCS_UPDATED = "ccs_updated"
    VALIDATOR_REGISTERED = "validator_registered"
    VALIDATOR_SLASHED = "validator_slashed"
    BLOCK_COMMITTED = "block_committed"


@dataclass
class StateTransitionEvent:
    """Represents a state transition event."""
    transition_type: StateTransition
    entity_id: str
    from_state: Optional[str]
    to_state: str
    timestamp: datetime
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "transition_type": self.transition_type.value,
            "entity_id": self.entity_id,
            "from_state": self.from_state,
            "to_state": self.to_state,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }


@dataclass
class LawState:
    """Represents the state of a cognitive law."""
    law_id: str
    status: str
    confidence: float
    support_count: int
    contradiction_count: int
    decay_factor: float
    context: str
    proposer_id: str
    created_at: datetime
    updated_at: datetime
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "law_id": self.law_id,
            "status": self.status,
            "confidence": self.confidence,
            "support_count": self.support_count,
            "contradiction_count": self.contradiction_count,
            "decay_factor": self.decay_factor,
            "context": self.context,
            "proposer_id": self.proposer_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


@dataclass
class CCSState:
    """Represents the state of a Cognitive Contribution Score."""
    participant_id: str
    score: float
    contributions_count: int
    laws_discovered: int
    conflicts_resolved: int
    last_updated: datetime
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "participant_id": self.participant_id,
            "score": self.score,
            "contributions_count": self.contributions_count,
            "laws_discovered": self.laws_discovered,
            "conflicts_resolved": self.conflicts_resolved,
            "last_updated": self.last_updated.isoformat()
        }


@dataclass
class ValidatorState:
    """Represents the state of a validator."""
    validator_address: str
    role: str
    stake: float
    uptime: float
    laws_validated: int
    conflicts_resolved: int
    last_active: datetime
    jailed: bool = False
    jailed_until: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "validator_address": self.validator_address,
            "role": self.role,
            "stake": self.stake,
            "uptime": self.uptime,
            "laws_validated": self.laws_validated,
            "conflicts_resolved": self.conflicts_resolved,
            "last_active": self.last_active.isoformat(),
            "jailed": self.jailed,
            "jailed_until": self.jailed_until.isoformat() if self.jailed_until else None
        }


class CognitiveStateMachine:
    """
    Cognitive State Machine for CLE-Net.
    
    This class implements the state machine for cognitive laws, CCS,
    and validators. It ensures that all state transitions are valid
    and properly recorded.
    """
    
    # Valid state transitions for laws
    LAW_TRANSITIONS = {
        "proposed": ["validating", "deprecated"],
        "validating": ["active", "conflicted", "deprecated"],
        "active": ["conflicted", "deprecated", "revoked"],
        "conflicted": ["active", "deprecated"],
        "deprecated": [],
        "revoked": []
    }
    
    def __init__(self):
        """Initialize the cognitive state machine."""
        self.laws: Dict[str, LawState] = {}
        self.ccs_scores: Dict[str, CCSState] = {}
        self.validators: Dict[str, ValidatorState] = {}
        self.transition_history: List[StateTransitionEvent] = []
        self.current_block_height: int = 0
        self.current_block_hash: str = ""
    
    def transition_law(
        self,
        law_id: str,
        new_status: str,
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        Transition a law to a new status.
        
        Args:
            law_id: ID of the law
            new_status: New status for the law
            metadata: Optional metadata for the transition
            
        Returns:
            True if transition was successful, False otherwise
        """
        # Get current law state
        if law_id not in self.laws:
            return False
        
        law = self.laws[law_id]
        current_status = law.status
        
        # Validate transition
        if new_status not in self.LAW_TRANSITIONS.get(current_status, []):
            return False
        
        # Create transition event
        event = StateTransitionEvent(
            transition_type=StateTransition(f"law_{new_status}"),
            entity_id=law_id,
            from_state=current_status,
            to_state=new_status,
            timestamp=datetime.utcnow(),
            metadata=metadata or {}
        )
        
        # Update law state
        law.status = new_status
        law.updated_at = datetime.utcnow()
        
        # Record transition
        self.transition_history.append(event)
        
        return True
    
    def transition_ccs(
        self,
        participant_id: str,
        score_delta: float,
        laws_discovered_delta: int = 0,
        conflicts_resolved_delta: int = 0,
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        Update a participant's CCS.
        
        Args:
            participant_id: ID of the participant
            score_delta: Change in score
            laws_discovered_delta: Change in laws discovered
            conflicts_resolved_delta: Change in conflicts resolved
            metadata: Optional metadata for the transition
            
        Returns:
            True if transition was successful, False otherwise
        """
        # Get or create CCS state
        if participant_id not in self.ccs_scores:
            self.ccs_scores[participant_id] = CCSState(
                participant_id=participant_id,
                score=0.0,
                contributions_count=0,
                laws_discovered=0,
                conflicts_resolved=0,
                last_updated=datetime.utcnow()
            )
        
        ccs = self.ccs_scores[participant_id]
        old_score = ccs.score
        
        # Update CCS
        ccs.score += score_delta
        ccs.laws_discovered += laws_discovered_delta
        ccs.conflicts_resolved += conflicts_resolved_delta
        ccs.contributions_count += 1
        ccs.last_updated = datetime.utcnow()
        
        # Create transition event
        event = StateTransitionEvent(
            transition_type=StateTransition.CCS_UPDATED,
            entity_id=participant_id,
            from_state=str(old_score),
            to_state=str(ccs.score),
            timestamp=datetime.utcnow(),
            metadata=metadata or {}
        )
        
        # Record transition
        self.transition_history.append(event)
        
        return True
    
    def transition_validator(
        self,
        validator_address: str,
        new_role: Optional[str] = None,
        stake_delta: float = 0.0,
        uptime_delta: float = 0.0,
        jailed: bool = False,
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        Update a validator's state.
        
        Args:
            validator_address: Address of the validator
            new_role: New role for the validator
            stake_delta: Change in stake
            uptime_delta: Change in uptime
            jailed: Whether the validator is jailed
            metadata: Optional metadata for the transition
            
        Returns:
            True if transition was successful, False otherwise
        """
        # Get or create validator state
        if validator_address not in self.validators:
            return False
        
        validator = self.validators[validator_address]
        old_role = validator.role
        
        # Update validator
        if new_role:
            validator.role = new_role
        validator.stake += stake_delta
        validator.uptime += uptime_delta
        validator.last_active = datetime.utcnow()
        validator.jailed = jailed
        
        # Create transition event
        event = StateTransitionEvent(
            transition_type=StateTransition.VALIDATOR_REGISTERED if new_role else StateTransition.VALIDATOR_SLASHED,
            entity_id=validator_address,
            from_state=old_role,
            to_state=validator.role,
            timestamp=datetime.utcnow(),
            metadata=metadata or {}
        )
        
        # Record transition
        self.transition_history.append(event)
        
        return True
    
    def commit_block(
        self,
        block_height: int,
        block_hash: str,
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        Commit a block.
        
        Args:
            block_height: Height of the block
            block_hash: Hash of the block
            metadata: Optional metadata for the transition
            
        Returns:
            True if commit was successful, False otherwise
        """
        # Create transition event
        event = StateTransitionEvent(
            transition_type=StateTransition.BLOCK_COMMITTED,
            entity_id=f"block_{block_height}",
            from_state=str(self.current_block_height),
            to_state=str(block_height),
            timestamp=datetime.utcnow(),
            metadata=metadata or {}
        )
        
        # Update block state
        self.current_block_height = block_height
        self.current_block_hash = block_hash
        
        # Record transition
        self.transition_history.append(event)
        
        return True
    
    def get_law_state(self, law_id: str) -> Optional[LawState]:
        """Get the state of a law."""
        return self.laws.get(law_id)
    
    def get_ccs_state(self, participant_id: str) -> Optional[CCSState]:
        """Get the state of a CCS."""
        return self.ccs_scores.get(participant_id)
    
    def get_validator_state(self, validator_address: str) -> Optional[ValidatorState]:
        """Get the state of a validator."""
        return self.validators.get(validator_address)
    
    def get_transition_history(
        self,
        entity_id: Optional[str] = None,
        limit: int = 100
    ) -> List[StateTransitionEvent]:
        """
        Get transition history.
        
        Args:
            entity_id: Optional entity ID to filter by
            limit: Maximum number of events to return
            
        Returns:
            List of transition events
        """
        if entity_id:
            events = [e for e in self.transition_history if e.entity_id == entity_id]
        else:
            events = self.transition_history
        
        return events[-limit:]
    
    def validate_state(self) -> Tuple[bool, List[str]]:
        """
        Validate the current state.
        
        Returns:
            Tuple of (is_valid, list of validation errors)
        """
        errors = []
        
        # Validate law states
        for law_id, law in self.laws.items():
            if law.status not in self.LAW_TRANSITIONS:
                errors.append(f"Invalid law status: {law.status} for law {law_id}")
        
        # Validate CCS scores
        for participant_id, ccs in self.ccs_scores.items():
            if ccs.score < 0:
                errors.append(f"Negative CCS score for participant {participant_id}")
        
        # Validate validator states
        for validator_address, validator in self.validators.items():
            if validator.stake < 0:
                errors.append(f"Negative stake for validator {validator_address}")
            if validator.uptime < 0 or validator.uptime > 100:
                errors.append(f"Invalid uptime for validator {validator_address}")
        
        return (len(errors) == 0, errors)
    
    def export_state(self) -> Dict:
        """
        Export the current state.
        
        Returns:
            Dictionary containing the current state
        """
        return {
            "laws": {law_id: law.to_dict() for law_id, law in self.laws.items()},
            "ccs_scores": {participant_id: ccs.to_dict() for participant_id, ccs in self.ccs_scores.items()},
            "validators": {validator_address: validator.to_dict() for validator_address, validator in self.validators.items()},
            "current_block_height": self.current_block_height,
            "current_block_hash": self.current_block_hash,
            "transition_count": len(self.transition_history)
        }
    
    def import_state(self, state: Dict) -> bool:
        """
        Import state from a dictionary.
        
        Args:
            state: State dictionary to import
            
        Returns:
            True if import was successful, False otherwise
        """
        try:
            # Import laws
            self.laws = {
                law_id: LawState(**law_data)
                for law_id, law_data in state.get("laws", {}).items()
            }
            
            # Import CCS scores
            self.ccs_scores = {
                participant_id: CCSState(**ccs_data)
                for participant_id, ccs_data in state.get("ccs_scores", {}).items()
            }
            
            # Import validators
            self.validators = {
                validator_address: ValidatorState(**validator_data)
                for validator_address, validator_data in state.get("validators", {}).items()
            }
            
            # Import block state
            self.current_block_height = state.get("current_block_height", 0)
            self.current_block_hash = state.get("current_block_hash", "")
            
            return True
        except Exception as e:
            print(f"Failed to import state: {e}")
            return False
