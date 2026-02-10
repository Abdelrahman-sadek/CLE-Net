"""
CLE-Net Cosmos SDK Types

This module defines the core types for CLE-Net's Cosmos SDK integration.
These types represent the on-chain state for cognitive laws, CCS, and consensus.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from enum import Enum
from datetime import datetime
import hashlib


class LawStatus(Enum):
    """Status of a cognitive law in the lifecycle."""
    PROPOSED = "proposed"
    VALIDATING = "validating"
    ACTIVE = "active"
    CONFLICTED = "conflicted"
    DEPRECATED = "deprecated"
    REVOKED = "revoked"


class LawType(Enum):
    """Type of cognitive law."""
    SYMBOLIC_RULE = "symbolic_rule"
    CONTEXT_BOUNDARY = "context_boundary"
    DECISION_PATTERN = "decision_pattern"
    CAUSAL_RELATION = "causal_relation"


class ValidatorRole(Enum):
    """Role of a validator in CLE-Net consensus."""
    COGNITIVE_MINER = "cognitive_miner"  # Mines cognitive laws
    STATE_VALIDATOR = "state_validator"  # Validates state transitions
    CONFLICT_RESOLVER = "conflict_resolver"  # Resolves law conflicts
    WATCHDOG = "watchdog"  # Monitors network health


@dataclass
class CognitiveContributionScore:
    """
    Cognitive Contribution Score (CCS) for a participant.
    
    CCS measures the quality and impact of cognitive contributions.
    """
    participant_id: str
    score: float = 0.0
    contributions_count: int = 0
    laws_discovered: int = 0
    conflicts_resolved: int = 0
    last_updated: datetime = field(default_factory=datetime.utcnow)
    
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
    
    @classmethod
    def from_dict(cls, data: Dict) -> "CognitiveContributionScore":
        """Create from dictionary."""
        return cls(
            participant_id=data["participant_id"],
            score=data["score"],
            contributions_count=data["contributions_count"],
            laws_discovered=data["laws_discovered"],
            conflicts_resolved=data["conflicts_resolved"],
            last_updated=datetime.fromisoformat(data["last_updated"])
        )


@dataclass
class CognitiveLaw:
    """
    A cognitive law discovered by CLE-Net.
    
    Laws are symbolic representations of decision patterns discovered
    from human interaction.
    """
    law_id: str
    law_type: LawType
    symbolic_expression: str
    context: str
    status: LawStatus = LawStatus.PROPOSED
    proposer_id: str = ""
    confidence: float = 0.0
    support_count: int = 0
    contradiction_count: int = 0
    evidence: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    decay_factor: float = 1.0  # Decay factor for law relevance
    
    def compute_hash(self) -> str:
        """Compute hash of the law for integrity verification."""
        data = f"{self.law_id}:{self.symbolic_expression}:{self.context}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "law_id": self.law_id,
            "law_type": self.law_type.value,
            "symbolic_expression": self.symbolic_expression,
            "context": self.context,
            "status": self.status.value,
            "proposer_id": self.proposer_id,
            "confidence": self.confidence,
            "support_count": self.support_count,
            "contradiction_count": self.contradiction_count,
            "evidence": self.evidence,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "decay_factor": self.decay_factor,
            "hash": self.compute_hash()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "CognitiveLaw":
        """Create from dictionary."""
        return cls(
            law_id=data["law_id"],
            law_type=LawType(data["law_type"]),
            symbolic_expression=data["symbolic_expression"],
            context=data["context"],
            status=LawStatus(data["status"]),
            proposer_id=data["proposer_id"],
            confidence=data["confidence"],
            support_count=data["support_count"],
            contradiction_count=data["contradiction_count"],
            evidence=data["evidence"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            decay_factor=data["decay_factor"]
        )


@dataclass
class CognitiveStateBlock:
    """
    Cognitive State Block (CSB) - the fundamental unit of CLE-Net.
    
    A CSB contains the cognitive state transition for a block,
    including new laws, CCS updates, and conflict resolutions.
    """
    block_height: int
    block_hash: str
    proposer_id: str
    timestamp: datetime
    new_laws: List[CognitiveLaw] = field(default_factory=list)
    updated_laws: List[CognitiveLaw] = field(default_factory=list)
    ccs_updates: List[CognitiveContributionScore] = field(default_factory=list)
    conflict_resolutions: List[Dict] = field(default_factory=list)
    prev_block_hash: str = ""
    
    def compute_hash(self) -> str:
        """Compute hash of the CSB."""
        data = f"{self.block_height}:{self.prev_block_hash}:{self.proposer_id}:{self.timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "block_height": self.block_height,
            "block_hash": self.block_hash,
            "proposer_id": self.proposer_id,
            "timestamp": self.timestamp.isoformat(),
            "new_laws": [law.to_dict() for law in self.new_laws],
            "updated_laws": [law.to_dict() for law in self.updated_laws],
            "ccs_updates": [ccs.to_dict() for ccs in self.ccs_updates],
            "conflict_resolutions": self.conflict_resolutions,
            "prev_block_hash": self.prev_block_hash
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "CognitiveStateBlock":
        """Create from dictionary."""
        return cls(
            block_height=data["block_height"],
            block_hash=data["block_hash"],
            proposer_id=data["proposer_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            new_laws=[CognitiveLaw.from_dict(law) for law in data["new_laws"]],
            updated_laws=[CognitiveLaw.from_dict(law) for law in data["updated_laws"]],
            ccs_updates=[CognitiveContributionScore.from_dict(ccs) for ccs in data["ccs_updates"]],
            conflict_resolutions=data["conflict_resolutions"],
            prev_block_hash=data["prev_block_hash"]
        )


@dataclass
class ValidatorInfo:
    """
    Information about a CLE-Net validator.
    
    Validators participate in consensus and have specific roles
    in the cognitive network.
    """
    validator_address: str
    role: ValidatorRole
    stake: float = 0.0
    uptime: float = 100.0
    laws_validated: int = 0
    conflicts_resolved: int = 0
    last_active: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "validator_address": self.validator_address,
            "role": self.role.value,
            "stake": self.stake,
            "uptime": self.uptime,
            "laws_validated": self.laws_validated,
            "conflicts_resolved": self.conflicts_resolved,
            "last_active": self.last_active.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "ValidatorInfo":
        """Create from dictionary."""
        return cls(
            validator_address=data["validator_address"],
            role=ValidatorRole(data["role"]),
            stake=data["stake"],
            uptime=data["uptime"],
            laws_validated=data["laws_validated"],
            conflicts_resolved=data["conflicts_resolved"],
            last_active=datetime.fromisoformat(data["last_active"])
        )


@dataclass
class ConflictResolution:
    """
    A conflict resolution between two or more laws.
    
    Conflicts arise when laws contradict each other.
    Resolutions determine which law(s) are valid.
    """
    resolution_id: str
    conflicting_law_ids: List[str]
    resolution_type: str  # "merge", "prioritize", "deprecate", "context_split"
    resolved_law_id: Optional[str] = None
    context_boundaries: List[str] = field(default_factory=list)
    resolver_id: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "resolution_id": self.resolution_id,
            "conflicting_law_ids": self.conflicting_law_ids,
            "resolution_type": self.resolution_type,
            "resolved_law_id": self.resolved_law_id,
            "context_boundaries": self.context_boundaries,
            "resolver_id": self.resolver_id,
            "timestamp": self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "ConflictResolution":
        """Create from dictionary."""
        return cls(
            resolution_id=data["resolution_id"],
            conflicting_law_ids=data["conflicting_law_ids"],
            resolution_type=data["resolution_type"],
            resolved_law_id=data["resolved_law_id"],
            context_boundaries=data["context_boundaries"],
            resolver_id=data["resolver_id"],
            timestamp=datetime.fromisoformat(data["timestamp"])
        )


# Module message types for Cosmos SDK
class MessageType(Enum):
    """Message types for CLE-Net Cosmos SDK module."""
    PROPOSE_LAW = "cognitive/ProposeLaw"
    VALIDATE_LAW = "cognitive/ValidateLaw"
    REPORT_CONFLICT = "cognitive/ReportConflict"
    RESOLVE_CONFLICT = "cognitive/ResolveConflict"
    UPDATE_CCS = "cognitive/UpdateCCS"
    REGISTER_VALIDATOR = "consensus/RegisterValidator"
    UPDATE_VALIDATOR = "consensus/UpdateValidator"
