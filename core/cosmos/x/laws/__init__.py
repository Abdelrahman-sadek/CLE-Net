"""
CLE-Net Laws Module

This module manages the lifecycle, storage, and retrieval of cognitive laws.
It provides efficient querying and indexing of laws.
"""

from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime
import json

from ...types import (
    CognitiveLaw,
    LawStatus,
    LawType,
    CognitiveContributionScore
)


class LawsKeeper:
    """
    Keeper for the laws module.
    
    Manages law storage, indexing, and retrieval.
    """
    
    def __init__(self):
        """Initialize the laws keeper."""
        self.laws: Dict[str, CognitiveLaw] = {}
        self.laws_by_status: Dict[LawStatus, Set[str]] = {
            LawStatus.PROPOSED: set(),
            LawStatus.VALIDATING: set(),
            LawStatus.ACTIVE: set(),
            LawStatus.CONFLICTED: set(),
            LawStatus.DEPRECATED: set(),
            LawStatus.REVOKED: set()
        }
        self.laws_by_type: Dict[LawType, Set[str]] = {
            LawType.SYMBOLIC_RULE: set(),
            LawType.CONTEXT_BOUNDARY: set(),
            LawType.DECISION_PATTERN: set(),
            LawType.CAUSAL_RELATION: set()
        }
        self.laws_by_context: Dict[str, Set[str]] = {}
        self.laws_by_proposer: Dict[str, Set[str]] = {}
        self.law_index: int = 0
    
    def get_law(self, law_id: str) -> Optional[CognitiveLaw]:
        """Get a law by ID."""
        return self.laws.get(law_id)
    
    def set_law(self, law: CognitiveLaw) -> None:
        """Set a law in state."""
        # Update main storage
        self.laws[law.law_id] = law
        
        # Update status index
        for status_set in self.laws_by_status.values():
            status_set.discard(law.law_id)
        self.laws_by_status[law.status].add(law.law_id)
        
        # Update type index
        for type_set in self.laws_by_type.values():
            type_set.discard(law.law_id)
        self.laws_by_type[law.law_type].add(law.law_id)
        
        # Update context index
        if law.context not in self.laws_by_context:
            self.laws_by_context[law.context] = set()
        self.laws_by_context[law.context].add(law.law_id)
        
        # Update proposer index
        if law.proposer_id not in self.laws_by_proposer:
            self.laws_by_proposer[law.proposer_id] = set()
        self.laws_by_proposer[law.proposer_id].add(law.law_id)
    
    def delete_law(self, law_id: str) -> bool:
        """Delete a law from state."""
        law = self.laws.get(law_id)
        if not law:
            return False
        
        # Remove from main storage
        del self.laws[law_id]
        
        # Remove from indexes
        self.laws_by_status[law.status].discard(law_id)
        self.laws_by_type[law.law_type].discard(law_id)
        self.laws_by_context.get(law.context, set()).discard(law_id)
        self.laws_by_proposer.get(law.proposer_id, set()).discard(law_id)
        
        return True
    
    def get_all_laws(self) -> List[CognitiveLaw]:
        """Get all laws."""
        return list(self.laws.values())
    
    def get_laws_by_status(self, status: LawStatus) -> List[CognitiveLaw]:
        """Get laws by status."""
        law_ids = self.laws_by_status.get(status, set())
        return [self.laws[law_id] for law_id in law_ids if law_id in self.laws]
    
    def get_laws_by_type(self, law_type: LawType) -> List[CognitiveLaw]:
        """Get laws by type."""
        law_ids = self.laws_by_type.get(law_type, set())
        return [self.laws[law_id] for law_id in law_ids if law_id in self.laws]
    
    def get_laws_by_context(self, context: str) -> List[CognitiveLaw]:
        """Get laws by context."""
        law_ids = self.laws_by_context.get(context, set())
        return [self.laws[law_id] for law_id in law_ids if law_id in self.laws]
    
    def get_laws_by_proposer(self, proposer_id: str) -> List[CognitiveLaw]:
        """Get laws by proposer."""
        law_ids = self.laws_by_proposer.get(proposer_id, set())
        return [self.laws[law_id] for law_id in law_ids if law_id in self.laws]
    
    def search_laws(self, query: str) -> List[CognitiveLaw]:
        """Search laws by symbolic expression."""
        results = []
        query_lower = query.lower()
        for law in self.laws.values():
            if query_lower in law.symbolic_expression.lower():
                results.append(law)
        return results
    
    def get_law_count(self) -> int:
        """Get total law count."""
        return len(self.laws)
    
    def get_law_count_by_status(self, status: LawStatus) -> int:
        """Get law count by status."""
        return len(self.laws_by_status.get(status, set()))
    
    def get_law_count_by_type(self, law_type: LawType) -> int:
        """Get law count by type."""
        return len(self.laws_by_type.get(law_type, set()))


class LawsModule:
    """
    The laws module for CLE-Net.
    
    This module handles:
    - Law lifecycle management
    - Law storage and indexing
    - Law querying and search
    - Law evolution and decay
    """
    
    def __init__(self):
        """Initialize the laws module."""
        self.keeper = LawsKeeper()
        self.decay_rate = 0.01  # 1% decay per block
        self.min_confidence = 0.5  # Minimum confidence for activation
        self.max_laws_per_context = 100  # Maximum laws per context
    
    def create_law(
        self,
        law_type: LawType,
        symbolic_expression: str,
        context: str,
        proposer_id: str,
        evidence: List[str],
        confidence: float = 0.0
    ) -> CognitiveLaw:
        """
        Create a new law.
        
        Generates a unique law ID and creates the law.
        """
        # Generate law ID
        law_id = f"law_{self.keeper.law_index}"
        self.keeper.law_index += 1
        
        # Create law
        law = CognitiveLaw(
            law_id=law_id,
            law_type=law_type,
            symbolic_expression=symbolic_expression,
            context=context,
            status=LawStatus.PROPOSED,
            proposer_id=proposer_id,
            confidence=confidence,
            evidence=evidence
        )
        
        # Store law
        self.keeper.set_law(law)
        
        return law
    
    def update_law_status(self, law_id: str, new_status: LawStatus) -> bool:
        """
        Update the status of a law.
        
        Transitions a law to a new status in its lifecycle.
        """
        law = self.keeper.get_law(law_id)
        if not law:
            return False
        
        # Validate status transition
        if not self._is_valid_status_transition(law.status, new_status):
            return False
        
        # Update status
        law.status = new_status
        law.updated_at = datetime.utcnow()
        
        # Store updated law
        self.keeper.set_law(law)
        
        return True
    
    def evolve_law(self, law_id: str, new_evidence: List[str]) -> bool:
        """
        Evolve a law with new evidence.
        
        Updates a law's confidence and evidence based on new information.
        """
        law = self.keeper.get_law(law_id)
        if not law:
            return False
        
        # Add new evidence
        law.evidence.extend(new_evidence)
        law.support_count += len(new_evidence)
        
        # Recalculate confidence
        law.confidence = self._calculate_confidence(law)
        
        # Update timestamp
        law.updated_at = datetime.utcnow()
        
        # Store updated law
        self.keeper.set_law(law)
        
        return True
    
    def decay_law(self, law_id: str) -> bool:
        """
        Apply decay to a law.
        
        Reduces a law's relevance over time if not confirmed.
        """
        law = self.keeper.get_law(law_id)
        if not law:
            return False
        
        # Apply decay
        law.decay_factor *= (1 - self.decay_rate)
        
        # Check if law should be deprecated
        if law.decay_factor < 0.1:
            law.status = LawStatus.DEPRECATED
        
        # Update timestamp
        law.updated_at = datetime.utcnow()
        
        # Store updated law
        self.keeper.set_law(law)
        
        return True
    
    def get_similar_laws(self, law_id: str, threshold: float = 0.8) -> List[CognitiveLaw]:
        """
        Get laws similar to a given law.
        
        Finds laws with similar symbolic expressions.
        """
        law = self.keeper.get_law(law_id)
        if not law:
            return []
        
        similar_laws = []
        for other_law in self.keeper.get_all_laws():
            if other_law.law_id == law_id:
                continue
            
            similarity = self._calculate_similarity(law, other_law)
            if similarity >= threshold:
                similar_laws.append(other_law)
        
        return similar_laws
    
    def get_conflicting_laws(self, law_id: str) -> List[CognitiveLaw]:
        """
        Get laws that conflict with a given law.
        
        Finds laws in the same context with contradictory expressions.
        """
        law = self.keeper.get_law(law_id)
        if not law:
            return []
        
        conflicting_laws = []
        for other_law in self.keeper.get_laws_by_context(law.context):
            if other_law.law_id == law_id:
                continue
            
            if self._is_contradiction(law, other_law):
                conflicting_laws.append(other_law)
        
        return conflicting_laws
    
    def get_top_laws(self, count: int = 10) -> List[CognitiveLaw]:
        """
        Get the top laws by confidence.
        
        Returns the most confident laws.
        """
        laws = self.keeper.get_laws_by_status(LawStatus.ACTIVE)
        return sorted(laws, key=lambda l: l.confidence, reverse=True)[:count]
    
    def get_recent_laws(self, count: int = 10) -> List[CognitiveLaw]:
        """
        Get the most recent laws.
        
        Returns the most recently created laws.
        """
        laws = self.keeper.get_all_laws()
        return sorted(laws, key=lambda l: l.created_at, reverse=True)[:count]
    
    def get_law_statistics(self) -> Dict:
        """
        Get statistics about laws.
        
        Returns counts and metrics about the law database.
        """
        return {
            "total_laws": self.keeper.get_law_count(),
            "by_status": {
                status.value: self.keeper.get_law_count_by_status(status)
                for status in LawStatus
            },
            "by_type": {
                law_type.value: self.keeper.get_law_count_by_type(law_type)
                for law_type in LawType
            },
            "active_laws": self.keeper.get_law_count_by_status(LawStatus.ACTIVE),
            "conflicted_laws": self.keeper.get_law_count_by_status(LawStatus.CONFLICTED)
        }
    
    def _is_valid_status_transition(self, current_status: LawStatus, new_status: LawStatus) -> bool:
        """
        Validate a status transition.
        
        Checks if a transition from current_status to new_status is valid.
        """
        valid_transitions = {
            LawStatus.PROPOSED: [LawStatus.VALIDATING, LawStatus.DEPRECATED],
            LawStatus.VALIDATING: [LawStatus.ACTIVE, LawStatus.CONFLICTED, LawStatus.DEPRECATED],
            LawStatus.ACTIVE: [LawStatus.CONFLICTED, LawStatus.DEPRECATED, LawStatus.REVOKED],
            LawStatus.CONFLICTED: [LawStatus.ACTIVE, LawStatus.DEPRECATED],
            LawStatus.DEPRECATED: [],
            LawStatus.REVOKED: []
        }
        
        return new_status in valid_transitions.get(current_status, [])
    
    def _calculate_confidence(self, law: CognitiveLaw) -> float:
        """
        Calculate the confidence of a law.
        
        Confidence is based on support count, evidence, and decay factor.
        """
        # Base confidence from support count
        support_confidence = min(law.support_count / 10.0, 1.0)
        
        # Evidence confidence
        evidence_confidence = min(len(law.evidence) / 5.0, 1.0)
        
        # Combine confidences
        combined_confidence = (support_confidence + evidence_confidence) / 2.0
        
        # Apply decay factor
        final_confidence = combined_confidence * law.decay_factor
        
        return final_confidence
    
    def _calculate_similarity(self, law1: CognitiveLaw, law2: CognitiveLaw) -> float:
        """
        Calculate similarity between two laws.
        
        Uses simple string similarity on symbolic expressions.
        """
        expr1 = law1.symbolic_expression.lower()
        expr2 = law2.symbolic_expression.lower()
        
        # Simple Jaccard similarity
        words1 = set(expr1.split())
        words2 = set(expr2.split())
        
        intersection = words1 & words2
        union = words1 | words2
        
        if not union:
            return 0.0
        
        return len(intersection) / len(union)
    
    def _is_contradiction(self, law1: CognitiveLaw, law2: CognitiveLaw) -> bool:
        """
        Check if two laws contradict each other.
        
        Simple heuristic: laws with opposite expressions in the same context.
        """
        # Check if laws are in the same context
        if law1.context != law2.context:
            return False
        
        # Check for contradictory keywords
        expr1 = law1.symbolic_expression.lower()
        expr2 = law2.symbolic_expression.lower()
        
        contradictory_pairs = [
            ("always", "never"),
            ("must", "must not"),
            ("should", "should not"),
            ("required", "forbidden"),
            ("enable", "disable"),
            ("allow", "deny")
        ]
        
        for word1, word2 in contradictory_pairs:
            if word1 in expr1 and word2 in expr2:
                return True
            if word2 in expr1 and word1 in expr2:
                return True
        
        return False
