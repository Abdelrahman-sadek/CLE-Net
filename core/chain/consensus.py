"""
Proof of Cognition (PoC) Consensus Module

Implements the PoC consensus mechanism for rule validation.
"""

import time
from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class ConsensusStatus(Enum):
    """Status of a rule in the consensus process."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    WEAKENED = "weakened"


@dataclass
class ConsensusResult:
    """Result of a consensus evaluation."""
    status: ConsensusStatus
    rule_hash: str
    confidence: float
    supporting_agents: List[str]
    reason: str = ""
    contradiction_strength: float = 0.0
    
    def to_dict(self) -> dict:
        return {
            'status': self.status.value,
            'rule_hash': self.rule_hash,
            'confidence': self.confidence,
            'supporting_agents': self.supporting_agents,
            'reason': self.reason,
            'contradiction_strength': self.contradiction_strength
        }


@dataclass
class RuleCluster:
    """A group of rule commits representing the same rule."""
    rule_hash: str
    commits: List[Dict] = field(default_factory=list)
    unique_agents: Set[str] = field(default_factory=set)
    first_commit: float = 0.0
    last_commit: float = 0.0
    avg_confidence: float = 0.0
    
    def add_commit(self, commit: Dict) -> None:
        """Add a commit to the cluster."""
        self.commits.append(commit)
        self.unique_agents.add(commit.get('agent_id', ''))
        
        timestamp = commit.get('timestamp', 0)
        if self.first_commit == 0 or timestamp < self.first_commit:
            self.first_commit = timestamp
        if timestamp > self.last_commit:
            self.last_commit = timestamp


class ProofOfCognition:
    """
    Proof of Cognition consensus mechanism.
    
    PoC achieves consensus when multiple independent agents,
    operating on different data, converge on the same symbolic rule.
    """
    
    # Consensus thresholds
    MIN_AGENTS = 3
    MIN_INDEPENDENCE = 0.8
    MIN_CONFIDENCE = 0.7
    MIN_STABILITY_HOURS = 24  # 24 hours
    MAX_CONTRADICTION = 0.3
    
    # Weights for confidence calculation
    COVERAGE_WEIGHT = 0.5
    SIMPLICITY_WEIGHT = 0.3
    DIVERSITY_WEIGHT = 0.2
    
    def __init__(self,
                 min_agents: int = None,
                 min_independence: float = None,
                 min_confidence: float = None,
                 min_stability_hours: int = None,
                 max_contradiction: float = None):
        """
        Initialize PoC consensus.
        
        Args:
            min_agents: Minimum agents for consensus
            min_independence: Minimum independence score
            min_confidence: Minimum confidence threshold
            min_stability_hours: Minimum stability time
            max_contradiction: Maximum allowed contradiction
        """
        self.min_agents = min_agents or self.MIN_AGENTS
        self.min_independence = min_independence or self.MIN_INDEPENDENCE
        self.min_confidence = min_confidence or self.MIN_CONFIDENCE
        self.min_stability_hours = min_stability_hours or self.MIN_STABILITY_HOURS
        self.max_contradiction = max_contradiction or self.MAX_CONTRADICTION
        
        # Storage for commits and contradictions
        self._commits: List[Dict] = []
        self._contradictions: Dict[str, List[Dict]] = {}
    
    def add_commit(self, commit: Dict) -> None:
        """
        Add a rule commit to the network.
        
        Args:
            commit: Rule commit dictionary
        """
        self._commits.append(commit)
        
        # Check for existing cluster
        rule_hash = commit.get('rule_hash', '')
        
        # Track contradictions if any
        if 'contradiction' in commit:
            if rule_hash not in self._contradictions:
                self._contradictions[rule_hash] = []
            self._contradictions[rule_hash].append(commit['contradiction'])
    
    def add_contradiction(self, rule_hash: str, contradicting_rule: Dict) -> None:
        """
        Add a contradiction for a rule.
        
        Args:
            rule_hash: The rule being contradicted
            contradicting_rule: The contradicting rule data
        """
        if rule_hash not in self._contradictions:
            self._contradictions[rule_hash] = []
        self._contradictions[rule_hash].append(contradicting_rule)
    
    def cluster_commits(self) -> List[RuleCluster]:
        """
        Group commits into clusters by rule hash.
        
        Returns:
            List of rule clusters
        """
        clusters: Dict[str, RuleCluster] = {}
        
        for commit in self._commits:
            rule_hash = commit.get('rule_hash', '')
            
            if rule_hash not in clusters:
                clusters[rule_hash] = RuleCluster(rule_hash=rule_hash)
            
            clusters[rule_hash].add_commit(commit)
        
        # Calculate average confidence for each cluster
        for cluster in clusters.values():
            if cluster.commits:
                confidences = [c.get('confidence', 0) for c in cluster.commits]
                cluster.avg_confidence = sum(confidences) / len(confidences)
        
        return list(clusters.values())
    
    def check_independence(self, cluster: RuleCluster) -> float:
        """
        Calculate independence score for a cluster.
        
        For MVP, we use a simple heuristic.
        In production, this would analyze data sources and reasoning traces.
        
        Args:
            cluster: Rule cluster to check
            
        Returns:
            Independence score (0-1)
        """
        # Simple heuristic: more unique agents = higher independence
        # In production, this would check actual data independence
        
        agent_count = len(cluster.unique_agents)
        
        if agent_count < 2:
            return 0.0
        elif agent_count < 3:
            return 0.5
        elif agent_count < 5:
            return 0.7
        else:
            return min(1.0, 0.8 + (agent_count - 5) * 0.05)
    
    def check_stability(self, cluster: RuleCluster) -> bool:
        """
        Check if a rule has been stable long enough.
        
        Args:
            cluster: Rule cluster to check
            
        Returns:
            True if stable, False otherwise
        """
        if cluster.last_commit == 0:
            return False
        
        stability_seconds = self.min_stability_hours * 3600
        
        # Check time since first commit
        time_span = cluster.last_commit - cluster.first_commit
        
        return time_span >= stability_seconds
    
    def get_contradiction_strength(self, rule_hash: str) -> float:
        """
        Calculate the strength of contradictions for a rule.
        
        Args:
            rule_hash: The rule to check
            
        Returns:
            Contradiction strength (0-1)
        """
        contradictions = self._contradictions.get(rule_hash, [])
        
        if not contradictions:
            return 0.0
        
        # Simple calculation: fraction of commits that are contradictions
        total_commits = len([c for c in self._commits if c.get('rule_hash') == rule_hash])
        
        if total_commits == 0:
            return 0.0
        
        return len(contradictions) / total_commits
    
    def evaluate_consensus(self, cluster: RuleCluster) -> ConsensusResult:
        """
        Evaluate whether a rule cluster has achieved consensus.
        
        Args:
            cluster: Rule cluster to evaluate
            
        Returns:
            Consensus evaluation result
        """
        # Check agent count
        agent_count = len(cluster.unique_agents)
        if agent_count < self.min_agents:
            return ConsensusResult(
                status=ConsensusStatus.PENDING,
                rule_hash=cluster.rule_hash,
                confidence=cluster.avg_confidence,
                supporting_agents=list(cluster.unique_agents),
                reason=f"Insufficient agents: {agent_count}/{self.min_agents}"
            )
        
        # Check confidence threshold
        if cluster.avg_confidence < self.min_confidence:
            return ConsensusResult(
                status=ConsensusStatus.REJECTED,
                rule_hash=cluster.rule_hash,
                confidence=cluster.avg_confidence,
                supporting_agents=list(cluster.unique_agents),
                reason=f"Low confidence: {cluster.avg_confidence:.2f}/{self.min_confidence}"
            )
        
        # Check independence
        independence = self.check_independence(cluster)
        if independence < self.min_independence:
            return ConsensusResult(
                status=ConsensusStatus.PENDING,
                rule_hash=cluster.rule_hash,
                confidence=cluster.avg_confidence,
                supporting_agents=list(cluster.unique_agents),
                reason=f"Low independence: {independence:.2f}/{self.min_independence}"
            )
        
        # Check stability
        if not self.check_stability(cluster):
            return ConsensusResult(
                status=ConsensusStatus.PENDING,
                rule_hash=cluster.rule_hash,
                confidence=cluster.avg_confidence,
                supporting_agents=list(cluster.unique_agents),
                reason="Awaiting stability window"
            )
        
        # Check contradictions
        contradiction_strength = self.get_contradiction_strength(cluster.rule_hash)
        if contradiction_strength > self.max_contradiction:
            return ConsensusResult(
                status=ConsensusStatus.WEAKENED,
                rule_hash=cluster.rule_hash,
                confidence=cluster.avg_confidence,
                supporting_agents=list(cluster.unique_agents),
                reason=f"Strong contradictions: {contradiction_strength:.2f}",
                contradiction_strength=contradiction_strength
            )
        
        # Calculate final confidence
        final_confidence = self._calculate_final_confidence(
            cluster.avg_confidence,
            independence,
            contradiction_strength
        )
        
        return ConsensusResult(
            status=ConsensusStatus.ACCEPTED,
            rule_hash=cluster.rule_hash,
            confidence=final_confidence,
            supporting_agents=list(cluster.unique_agents),
            reason="Consensus achieved"
        )
    
    def _calculate_final_confidence(self,
                                    avg_confidence: float,
                                    independence: float,
                                    contradiction: float) -> float:
        """
        Calculate final confidence after all factors.
        
        Args:
            avg_confidence: Average agent confidence
            independence: Independence score
            contradiction: Contradiction strength
            
        Returns:
            Final confidence score
        """
        # Base confidence
        confidence = avg_confidence
        
        # Boost for independence
        if independence > self.min_independence:
            confidence += (independence - self.min_independence) * 0.1
        
        # Penalty for contradictions
        confidence -= contradiction * 0.3
        
        return max(0.0, min(1.0, confidence))
    
    def run_consensus(self) -> List[ConsensusResult]:
        """
        Run consensus evaluation on all pending rules.
        
        Returns:
            List of consensus results
        """
        clusters = self.cluster_commits()
        results = []
        
        for cluster in clusters:
            result = self.evaluate_consensus(cluster)
            results.append(result)
        
        return results
    
    def get_accepted_rules(self) -> List[ConsensusResult]:
        """
        Get all rules that have achieved consensus.
        
        Returns:
            List of accepted rules
        """
        results = self.run_consensus()
        return [r for r in results if r.status == ConsensusStatus.ACCEPTED]
    
    def reset(self) -> None:
        """Reset the consensus state."""
        self._commits.clear()
        self._contradictions.clear()
    
    def get_statistics(self) -> dict:
        """
        Get consensus statistics.
        
        Returns:
            Statistics dictionary
        """
        clusters = self.cluster_commits()
        results = self.run_consensus()
        
        accepted = len([r for r in results if r.status == ConsensusStatus.ACCEPTED])
        pending = len([r for r in results if r.status == ConsensusStatus.PENDING])
        rejected = len([r for r in results if r.status == ConsensusStatus.REJECTED])
        weakened = len([r for r in results if r.status == ConsensusStatus.WEAKENED])
        
        return {
            'total_commits': len(self._commits),
            'total_clusters': len(clusters),
            'accepted': accepted,
            'pending': pending,
            'rejected': rejected,
            'weakened': weakened,
            'unique_agents': len(set(c.get('agent_id') for c in self._commits))
        }
