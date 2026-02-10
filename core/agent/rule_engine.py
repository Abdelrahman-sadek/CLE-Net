"""
Rule Engine Module

Discovers latent rules from accumulated symbols using symbolic regression.
"""

import hashlib
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class RuleCandidate:
    """
    A candidate rule discovered from symbolic analysis.
    
    Attributes:
        rule_id: Unique identifier (hash of logic form)
        logic_form: Canonical logical representation
        context: Domain/context information
        confidence: Discovery confidence (0-1)
        coverage: Fraction of events explained
        simplicity: Inverse complexity (0-1, higher is simpler)
        support_count: Number of supporting observations
        contradiction_count: Number of contradicting observations
        evidence: List of supporting evidence IDs
    """
    rule_id: str
    logic_form: str
    context: str = ""
    confidence: float = 0.5
    coverage: float = 0.0
    simplicity: float = 0.5
    support_count: int = 0
    contradiction_count: int = 0
    evidence: List[str] = field(default_factory=list)


class RuleEngine:
    """
    Discovers latent rules from accumulated symbols.
    
    This module implements symbolic regression to find patterns
    in the symbols extracted from human interaction.
    """
    
    def __init__(self, 
                 min_coverage: float = 0.1,
                 simplicity_weight: float = 0.3,
                 min_support: int = 3):
        """
        Initialize the rule engine.
        
        Args:
            min_coverage: Minimum coverage to consider a rule
            simplicity_weight: Weight for simplicity in scoring
            min_support: Minimum support count for a rule
        """
        self.min_coverage = min_coverage
        self.simplicity_weight = simplicity_weight
        self.min_support = min_support
        
        # Accumulated symbols buffer
        self._symbol_buffer = []
        
        # Discovered patterns
        self._patterns = {}
    
    def discover(self, symbols: List[Dict]) -> List[RuleCandidate]:
        """
        Discover rules from accumulated symbols.
        
        Args:
            symbols: List of symbolic atoms
            
        Returns:
            List of discovered rule candidates
        """
        # Add to buffer
        self._symbol_buffer.extend(symbols)
        
        # Find patterns
        patterns = self._find_patterns(symbols)
        
        # Convert to candidates
        candidates = []
        for pattern in patterns:
            candidate = self._pattern_to_candidate(pattern)
            if candidate:
                candidates.append(candidate)
        
        return candidates
    
    def _find_patterns(self, symbols: List[Dict]) -> List[Dict]:
        """
        Find recurring patterns in symbols.
        
        Args:
            symbols: List of symbolic atoms
            
        Returns:
            List of discovered patterns
        """
        patterns = []
        
        # Count co-occurrences
        cooccurrence = {}
        
        for symbol in symbols:
            pred = symbol.get('predicate', '')
            if pred:
                if pred not in cooccurrence:
                    cooccurrence[pred] = {'count': 0, 'contexts': set()}
                cooccurrence[pred]['count'] += 1
        
        # Find patterns with sufficient support
        for pred, data in cooccurrence.items():
            if data['count'] >= self.min_support:
                patterns.append({
                    'predicates': [pred],
                    'count': data['count'],
                    'coverage': data['count'] / len(self._symbol_buffer) if self._symbol_buffer else 0
                })
        
        # Find multi-predicate patterns
        patterns.extend(self._find_combination_patterns(symbols))
        
        return patterns
    
    def _find_combination_patterns(self, symbols: List[Dict]) -> List[Dict]:
        """
        Find patterns involving multiple predicates.
        
        Args:
            symbols: List of symbolic atoms
            
        Returns:
            List of combination patterns
        """
        patterns = []
        
        # Look for IF-THEN patterns
        conditions = [s for s in symbols if 'condition' in s.get('predicate', '')]
        actions = [s for s in symbols if 'do(' in s.get('predicate', '')]
        
        if conditions and actions:
            for cond in conditions[:5]:  # Limit combinations
                for action in actions[:5]:
                    pattern = {
                        'predicates': [cond.get('predicate'), action.get('predicate')],
                        'count': 1,
                        'coverage': 0.01,
                        'is_conditional': True
                    }
                    patterns.append(pattern)
        
        return patterns
    
    def _pattern_to_candidate(self, pattern: Dict) -> Optional[RuleCandidate]:
        """
        Convert a pattern to a rule candidate.
        
        Args:
            pattern: Discovered pattern
            
        Returns:
            RuleCandidate or None if invalid
        """
        count = pattern.get('count', 0)
        coverage = pattern.get('coverage', 0)
        
        # Skip if coverage too low
        if coverage < self.min_coverage:
            return None
        
        # Skip if support too low
        if count < self.min_support:
            return None
        
        # Build logic form
        logic_form = self._build_logic_form(pattern)
        
        if not logic_form:
            return None
        
        # Calculate simplicity (inverse of complexity)
        simplicity = self._calculate_simplicity(logic_form)
        
        # Calculate confidence
        confidence = self._calculate_confidence(coverage, simplicity, count)
        
        # Generate rule ID
        rule_id = self._generate_rule_id(logic_form)
        
        return RuleCandidate(
            rule_id=rule_id,
            logic_form=logic_form,
            context="",
            confidence=confidence,
            coverage=coverage,
            simplicity=simplicity,
            support_count=count,
            contradiction_count=0,
            evidence=[]
        )
    
    def _build_logic_form(self, pattern: Dict) -> str:
        """
        Build a canonical logic form from a pattern.
        
        Args:
            pattern: Discovered pattern
            
        Returns:
            Logic form string
        """
        predicates = pattern.get('predicates', [])
        
        if not predicates:
            return ""
        
        if len(predicates) == 1:
            return predicates[0]
        
        # Check for IF-THEN pattern
        if pattern.get('is_conditional', False):
            cond = [p for p in predicates if 'condition' in p]
            action = [p for p in predicates if 'do(' in p]
            
            if cond and action:
                return f"IF {cond[0]} THEN {action[0]}"
        
        # Default: AND combination
        return ' AND '.join(predicates)
    
    def _calculate_simplicity(self, logic_form: str) -> float:
        """
        Calculate simplicity score for a logic form.
        
        Simpler rules (shorter, fewer conditions) score higher.
        
        Args:
            logic_form: Logic expression
            
        Returns:
            Simplicity score (0-1)
        """
        # Count elements
        elements = logic_form.split()
        
        # Base simplicity on length (shorter = simpler)
        length = len(elements)
        
        if length <= 2:
            return 1.0
        elif length <= 4:
            return 0.8
        elif length <= 6:
            return 0.6
        elif length <= 10:
            return 0.4
        else:
            return 0.2
    
    def _calculate_confidence(self, coverage: float, simplicity: float, 
                              support: int) -> float:
        """
        Calculate confidence score for a rule.
        
        Args:
            coverage: Fraction of events explained
            simplicity: Simplicity score
            support: Number of supporting observations
            
        Returns:
            Confidence score (0-1)
        """
        # Weighted combination
        coverage_weight = 1 - self.simplicity_weight
        confidence = (coverage_weight * coverage + 
                     self.simplicity_weight * simplicity)
        
        # Boost for higher support
        if support >= 10:
            confidence = min(1.0, confidence * 1.2)
        elif support >= 5:
            confidence = min(1.0, confidence * 1.1)
        
        return confidence
    
    def _generate_rule_id(self, logic_form: str) -> str:
        """
        Generate a unique ID for a rule.
        
        Args:
            logic_form: Logic expression
            
        Returns:
            Rule ID (hash prefix)
        """
        # Canonicalize first
        canonical = ' '.join(logic_form.lower().split())
        
        # Hash
        hash_val = hashlib.sha256(canonical.encode()).hexdigest()
        
        return f"rule_{hash_val[:16]}"
    
    def deduplicate_candidates(self, candidates: List[RuleCandidate]) -> List[RuleCandidate]:
        """
        Remove duplicate candidates (same logic, different instances).
        
        Args:
            candidates: List of candidates
            
        Returns:
            Deduplicated list
        """
        seen = {}
        result = []
        
        for candidate in candidates:
            key = candidate.logic_form.lower()
            if key not in seen:
                seen[key] = candidate
                result.append(candidate)
            else:
                # Merge evidence and update counts
                existing = seen[key]
                existing.support_count += candidate.support_count
                existing.evidence.extend(candidate.evidence)
                # Recalculate confidence
                existing.confidence = self._calculate_confidence(
                    existing.coverage,
                    existing.simplicity,
                    existing.support_count
                )
        
        return result
    
    def get_statistics(self) -> Dict:
        """
        Get rule engine statistics.
        
        Returns:
            Statistics dictionary
        """
        return {
            'symbol_buffer_size': len(self._symbol_buffer),
            'patterns_found': len(self._patterns),
            'min_coverage_threshold': self.min_coverage,
            'min_support_threshold': self.min_support
        }
    
    def clear_buffer(self) -> None:
        """Clear the accumulated symbol buffer."""
        self._symbol_buffer.clear()
        self._patterns.clear()
    
    # --- Phase 3: Rule Evolution and Decay Mechanisms ---
    
    def evolve_rule(self, rule: RuleCandidate, new_evidence: List[str]) -> RuleCandidate:
        """
        Evolve a rule with new evidence.
        
        Args:
            rule: Existing rule to evolve
            new_evidence: New supporting evidence
            
        Returns:
            Updated rule candidate
        """
        # Increase support count
        rule.support_count += len(new_evidence)
        rule.evidence.extend(new_evidence)
        
        # Recalculate confidence
        rule.confidence = self._calculate_confidence(
            rule.coverage,
            rule.simplicity,
            rule.support_count
        )
        
        return rule
    
    def decay_rule(self, rule: RuleCandidate, decay_factor: float = 0.01) -> RuleCandidate:
        """
        Apply decay to a rule based on lack of recent confirmation.
        
        Args:
            rule: Rule to decay
            decay_factor: Decay rate (default 0.01)
            
        Returns:
            Decayed rule candidate
        """
        # Reduce confidence
        rule.confidence = max(0.1, rule.confidence * (1 - decay_factor))
        
        # Mark as weakened if confidence drops significantly
        if rule.confidence < 0.3:
            rule.context = rule.context + " [WEAKENED]"
        
        return rule
    
    def resolve_contradiction(self, rule1: RuleCandidate, rule2: RuleCandidate, 
                         context: str) -> Optional[RuleCandidate]:
        """
        Resolve a contradiction between two rules.
        
        Args:
            rule1: First conflicting rule
            rule2: Second conflicting rule
            context: Context for resolution
            
        Returns:
            Resolved rule or None
        """
        # Check if rules truly contradict
        if not self._rules_contradict(rule1, rule2):
            return None
        
        # Create merged rule with context
        merged_logic = f"({rule1.logic_form}) OR ({rule2.logic_form})"
        merged_rule = RuleCandidate(
            rule_id=self._generate_rule_id(merged_logic),
            logic_form=merged_logic,
            context=f"Resolved contradiction in {context}",
            confidence=min(rule1.confidence, rule2.confidence) * 0.8,
            coverage=max(rule1.coverage, rule2.coverage),
            simplicity=min(rule1.simplicity, rule2.simplicity),
            support_count=rule1.support_count + rule2.support_count,
            contradiction_count=0,
            evidence=rule1.evidence + rule2.evidence
        )
        
        return merged_rule
    
    def _rules_contradict(self, rule1: RuleCandidate, rule2: RuleCandidate) -> bool:
        """
        Check if two rules logically contradict.
        
        Args:
            rule1: First rule
            rule2: Second rule
            
        Returns:
            True if rules contradict
        """
        # Simplified contradiction detection
        # In production, use proper logical reasoning
        logic1 = rule1.logic_form.lower()
        logic2 = rule2.logic_form.lower()
        
        # Check for direct negation
        if f"not {logic1}" == logic2 or f"not {logic2}" == logic1:
            return True
        
        # Check for opposite predicates
        # This is a simplified check - production would use full logical analysis
        return False
    
    def validate_context(self, rule: RuleCandidate, context: Dict) -> bool:
        """
        Validate if a rule applies in a given context.
        
        Args:
            rule: Rule to validate
            context: Context information
            
        Returns:
            True if rule applies in context
        """
        # Check if rule context matches provided context
        if not context:
            return True
        
        # Check for context-specific conditions
        rule_context = rule.context.lower() if rule.context else ""
        
        # Simple context matching (production would be more sophisticated)
        for key, value in context.items():
            if key.lower() in rule_context:
                return True
        
        return False
