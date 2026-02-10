"""
CLE-Net Cognitive Module

This module manages cognitive laws, their lifecycle, and validation.
It is the core module of CLE-Net's Cosmos SDK integration.
"""

from typing import Dict, List, Optional
from datetime import datetime
import json

from ...types import (
    CognitiveLaw,
    CognitiveContributionScore,
    LawStatus,
    LawType,
    ConflictResolution,
    MessageType
)


class CognitiveKeeper:
    """
    Keeper for the cognitive module.
    
    Manages the state of cognitive laws, CCS, and conflict resolutions.
    """
    
    def __init__(self):
        """Initialize the cognitive keeper."""
        self.laws: Dict[str, CognitiveLaw] = {}
        self.ccs_scores: Dict[str, CognitiveContributionScore] = {}
        self.conflicts: Dict[str, ConflictResolution] = {}
        self.context_boundaries: Dict[str, List[str]] = {}
    
    def get_law(self, law_id: str) -> Optional[CognitiveLaw]:
        """Get a law by ID."""
        return self.laws.get(law_id)
    
    def set_law(self, law: CognitiveLaw) -> None:
        """Set a law in state."""
        self.laws[law.law_id] = law
    
    def get_all_laws(self) -> List[CognitiveLaw]:
        """Get all laws."""
        return list(self.laws.values())
    
    def get_laws_by_status(self, status: LawStatus) -> List[CognitiveLaw]:
        """Get laws by status."""
        return [law for law in self.laws.values() if law.status == status]
    
    def get_laws_by_context(self, context: str) -> List[CognitiveLaw]:
        """Get laws by context."""
        return [law for law in self.laws.values() if law.context == context]
    
    def get_ccs(self, participant_id: str) -> Optional[CognitiveContributionScore]:
        """Get CCS for a participant."""
        return self.ccs_scores.get(participant_id)
    
    def set_ccs(self, ccs: CognitiveContributionScore) -> None:
        """Set CCS for a participant."""
        self.ccs_scores[ccs.participant_id] = ccs
    
    def get_all_ccs(self) -> List[CognitiveContributionScore]:
        """Get all CCS scores."""
        return list(self.ccs_scores.values())
    
    def get_conflict(self, resolution_id: str) -> Optional[ConflictResolution]:
        """Get a conflict resolution by ID."""
        return self.conflicts.get(resolution_id)
    
    def set_conflict(self, conflict: ConflictResolution) -> None:
        """Set a conflict resolution in state."""
        self.conflicts[conflict.resolution_id] = conflict
    
    def get_all_conflicts(self) -> List[ConflictResolution]:
        """Get all conflict resolutions."""
        return list(self.conflicts.values())
    
    def add_context_boundary(self, context: str, law_ids: List[str]) -> None:
        """Add a context boundary with associated laws."""
        self.context_boundaries[context] = law_ids
    
    def get_context_boundary(self, context: str) -> List[str]:
        """Get laws in a context boundary."""
        return self.context_boundaries.get(context, [])


class ProposeLawMessage:
    """Message to propose a new cognitive law."""
    
    def __init__(
        self,
        proposer_id: str,
        law_type: LawType,
        symbolic_expression: str,
        context: str,
        evidence: List[str],
        confidence: float = 0.0
    ):
        self.type = MessageType.PROPOSE_LAW
        self.proposer_id = proposer_id
        self.law_type = law_type
        self.symbolic_expression = symbolic_expression
        self.context = context
        self.evidence = evidence
        self.confidence = confidence
        self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "type": self.type.value,
            "proposer_id": self.proposer_id,
            "law_type": self.law_type.value,
            "symbolic_expression": self.symbolic_expression,
            "context": self.context,
            "evidence": self.evidence,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "ProposeLawMessage":
        """Create from dictionary."""
        return cls(
            proposer_id=data["proposer_id"],
            law_type=LawType(data["law_type"]),
            symbolic_expression=data["symbolic_expression"],
            context=data["context"],
            evidence=data["evidence"],
            confidence=data["confidence"]
        )


class ValidateLawMessage:
    """Message to validate a proposed law."""
    
    def __init__(
        self,
        validator_id: str,
        law_id: str,
        vote: bool,  # True = approve, False = reject
        reason: str = ""
    ):
        self.type = MessageType.VALIDATE_LAW
        self.validator_id = validator_id
        self.law_id = law_id
        self.vote = vote
        self.reason = reason
        self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "type": self.type.value,
            "validator_id": self.validator_id,
            "law_id": self.law_id,
            "vote": self.vote,
            "reason": self.reason,
            "timestamp": self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "ValidateLawMessage":
        """Create from dictionary."""
        return cls(
            validator_id=data["validator_id"],
            law_id=data["law_id"],
            vote=data["vote"],
            reason=data["reason"]
        )


class ReportConflictMessage:
    """Message to report a conflict between laws."""
    
    def __init__(
        self,
        reporter_id: str,
        conflicting_law_ids: List[str],
        conflict_description: str
    ):
        self.type = MessageType.REPORT_CONFLICT
        self.reporter_id = reporter_id
        self.conflicting_law_ids = conflicting_law_ids
        self.conflict_description = conflict_description
        self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "type": self.type.value,
            "reporter_id": self.reporter_id,
            "conflicting_law_ids": self.conflicting_law_ids,
            "conflict_description": self.conflict_description,
            "timestamp": self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "ReportConflictMessage":
        """Create from dictionary."""
        return cls(
            reporter_id=data["reporter_id"],
            conflicting_law_ids=data["conflicting_law_ids"],
            conflict_description=data["conflict_description"]
        )


class ResolveConflictMessage:
    """Message to resolve a conflict between laws."""
    
    def __init__(
        self,
        resolver_id: str,
        resolution_id: str,
        conflicting_law_ids: List[str],
        resolution_type: str,
        resolved_law_id: Optional[str] = None,
        context_boundaries: List[str] = None
    ):
        self.type = MessageType.RESOLVE_CONFLICT
        self.resolver_id = resolver_id
        self.resolution_id = resolution_id
        self.conflicting_law_ids = conflicting_law_ids
        self.resolution_type = resolution_type
        self.resolved_law_id = resolved_law_id
        self.context_boundaries = context_boundaries or []
        self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "type": self.type.value,
            "resolver_id": self.resolver_id,
            "resolution_id": self.resolution_id,
            "conflicting_law_ids": self.conflicting_law_ids,
            "resolution_type": self.resolution_type,
            "resolved_law_id": self.resolved_law_id,
            "context_boundaries": self.context_boundaries,
            "timestamp": self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "ResolveConflictMessage":
        """Create from dictionary."""
        return cls(
            resolver_id=data["resolver_id"],
            resolution_id=data["resolution_id"],
            conflicting_law_ids=data["conflicting_law_ids"],
            resolution_type=data["resolution_type"],
            resolved_law_id=data["resolved_law_id"],
            context_boundaries=data["context_boundaries"]
        )


class UpdateCCSMessage:
    """Message to update a participant's CCS."""
    
    def __init__(
        self,
        participant_id: str,
        score_delta: float,
        laws_discovered_delta: int = 0,
        conflicts_resolved_delta: int = 0
    ):
        self.type = MessageType.UPDATE_CCS
        self.participant_id = participant_id
        self.score_delta = score_delta
        self.laws_discovered_delta = laws_discovered_delta
        self.conflicts_resolved_delta = conflicts_resolved_delta
        self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "type": self.type.value,
            "participant_id": self.participant_id,
            "score_delta": self.score_delta,
            "laws_discovered_delta": self.laws_discovered_delta,
            "conflicts_resolved_delta": self.conflicts_resolved_delta,
            "timestamp": self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "UpdateCCSMessage":
        """Create from dictionary."""
        return cls(
            participant_id=data["participant_id"],
            score_delta=data["score_delta"],
            laws_discovered_delta=data["laws_discovered_delta"],
            conflicts_resolved_delta=data["conflicts_resolved_delta"]
        )


class CognitiveModule:
    """
    The cognitive module for CLE-Net.
    
    This module handles:
    - Law proposal and validation
    - Conflict detection and resolution
    - CCS tracking and updates
    """
    
    def __init__(self):
        """Initialize the cognitive module."""
        self.keeper = CognitiveKeeper()
        self.validation_threshold = 0.67  # 2/3 supermajority
        self.decay_rate = 0.01  # 1% decay per block
    
    def handle_propose_law(self, msg: ProposeLawMessage) -> CognitiveLaw:
        """
        Handle a propose law message.
        
        Creates a new law and adds it to the proposed state.
        """
        # Generate law ID
        law_id = f"law_{hashlib.sha256(msg.symbolic_expression.encode()).hexdigest()[:16]}"
        
        # Create the law
        law = CognitiveLaw(
            law_id=law_id,
            law_type=msg.law_type,
            symbolic_expression=msg.symbolic_expression,
            context=msg.context,
            status=LawStatus.PROPOSED,
            proposer_id=msg.proposer_id,
            confidence=msg.confidence,
            evidence=msg.evidence
        )
        
        # Store the law
        self.keeper.set_law(law)
        
        # Update proposer's CCS
        self._update_proposer_ccs(msg.proposer_id, 1.0, 1, 0)
        
        return law
    
    def handle_validate_law(self, msg: ValidateLawMessage) -> bool:
        """
        Handle a validate law message.
        
        Records a validator's vote for a law.
        """
        law = self.keeper.get_law(msg.law_id)
        if not law:
            return False
        
        # Update law support/contradiction count
        if msg.vote:
            law.support_count += 1
        else:
            law.contradiction_count += 1
        
        # Check if law has reached validation threshold
        total_votes = law.support_count + law.contradiction_count
        if total_votes >= 3:  # Minimum votes required
            approval_ratio = law.support_count / total_votes
            if approval_ratio >= self.validation_threshold:
                law.status = LawStatus.ACTIVE
            elif approval_ratio < (1 - self.validation_threshold):
                law.status = LawStatus.DEPRECATED
        
        # Update validator's CCS
        self._update_validator_ccs(msg.validator_id, 0.1, 0, 0)
        
        self.keeper.set_law(law)
        return True
    
    def handle_report_conflict(self, msg: ReportConflictMessage) -> str:
        """
        Handle a report conflict message.
        
        Marks laws as conflicted and creates a conflict record.
        """
        # Mark all conflicting laws as conflicted
        for law_id in msg.conflicting_law_ids:
            law = self.keeper.get_law(law_id)
            if law:
                law.status = LawStatus.CONFLICTED
                self.keeper.set_law(law)
        
        # Create conflict resolution record
        resolution_id = f"conflict_{hashlib.sha256(json.dumps(msg.conflicting_law_ids).encode()).hexdigest()[:16]}"
        conflict = ConflictResolution(
            resolution_id=resolution_id,
            conflicting_law_ids=msg.conflicting_law_ids,
            resolution_type="pending",
            resolver_id=msg.reporter_id
        )
        
        self.keeper.set_conflict(conflict)
        
        # Update reporter's CCS
        self._update_proposer_ccs(msg.reporter_id, 0.5, 0, 1)
        
        return resolution_id
    
    def handle_resolve_conflict(self, msg: ResolveConflictMessage) -> bool:
        """
        Handle a resolve conflict message.
        
        Resolves a conflict between laws.
        """
        conflict = self.keeper.get_conflict(msg.resolution_id)
        if not conflict:
            return False
        
        # Update conflict resolution
        conflict.resolution_type = msg.resolution_type
        conflict.resolved_law_id = msg.resolved_law_id
        conflict.context_boundaries = msg.context_boundaries
        conflict.resolver_id = msg.resolver_id
        
        # Update law statuses based on resolution
        for law_id in msg.conflicting_law_ids:
            law = self.keeper.get_law(law_id)
            if law:
                if msg.resolution_type == "deprecate":
                    law.status = LawStatus.DEPRECATED
                elif msg.resolution_type == "prioritize" and law_id == msg.resolved_law_id:
                    law.status = LawStatus.ACTIVE
                elif msg.resolution_type == "merge" and law_id == msg.resolved_law_id:
                    law.status = LawStatus.ACTIVE
                elif msg.resolution_type == "context_split":
                    law.status = LawStatus.ACTIVE
                self.keeper.set_law(law)
        
        # Store context boundaries if provided
        if msg.context_boundaries:
            for context in msg.context_boundaries:
                self.keeper.add_context_boundary(context, msg.conflicting_law_ids)
        
        self.keeper.set_conflict(conflict)
        
        # Update resolver's CCS
        self._update_proposer_ccs(msg.resolver_id, 2.0, 0, 1)
        
        return True
    
    def handle_update_ccs(self, msg: UpdateCCSMessage) -> bool:
        """
        Handle an update CCS message.
        
        Updates a participant's CCS.
        """
        ccs = self.keeper.get_ccs(msg.participant_id)
        if not ccs:
            ccs = CognitiveContributionScore(participant_id=msg.participant_id)
        
        ccs.score += msg.score_delta
        ccs.laws_discovered += msg.laws_discovered_delta
        ccs.conflicts_resolved += msg.conflicts_resolved_delta
        ccs.contributions_count += 1
        ccs.last_updated = datetime.utcnow()
        
        self.keeper.set_ccs(ccs)
        return True
    
    def apply_law_decay(self) -> None:
        """
        Apply decay to all active laws.
        
        Laws that are not confirmed over time decay in relevance.
        """
        for law in self.keeper.get_laws_by_status(LawStatus.ACTIVE):
            law.decay_factor *= (1 - self.decay_rate)
            if law.decay_factor < 0.1:
                law.status = LawStatus.DEPRECATED
            self.keeper.set_law(law)
    
    def _update_proposer_ccs(self, proposer_id: str, score_delta: float, 
                            laws_delta: int, conflicts_delta: int) -> None:
        """Update CCS for a proposer."""
        ccs = self.keeper.get_ccs(proposer_id)
        if not ccs:
            ccs = CognitiveContributionScore(participant_id=proposer_id)
        
        ccs.score += score_delta
        ccs.laws_discovered += laws_delta
        ccs.conflicts_resolved += conflicts_delta
        ccs.contributions_count += 1
        ccs.last_updated = datetime.utcnow()
        
        self.keeper.set_ccs(ccs)
    
    def _update_validator_ccs(self, validator_id: str, score_delta: float) -> None:
        """Update CCS for a validator."""
        ccs = self.keeper.get_ccs(validator_id)
        if not ccs:
            ccs = CognitiveContributionScore(participant_id=validator_id)
        
        ccs.score += score_delta
        ccs.contributions_count += 1
        ccs.last_updated = datetime.utcnow()
        
        self.keeper.set_ccs(ccs)


# Import hashlib for law ID generation
import hashlib
