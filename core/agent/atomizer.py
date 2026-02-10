"""
Semantic Atomizer Module

Extracts meaning units (atoms) from raw text content.
"""

import re
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class SemanticAtom:
    """
    A unit of meaning extracted from text.
    
    Attributes:
        atom_type: Type of atom (entity, action, condition, etc.)
        value: The actual content
        attributes: Associated properties
        confidence: Extraction confidence score
        position: Position in original text
    """
    atom_type: str
    value: str
    attributes: Dict[str, Any] = None
    confidence: float = 1.0
    position: tuple = None


class SemanticAtomizer:
    """
    Extracts semantic atoms from raw text.
    
    This module breaks down text into meaning units:
    - Entities (who, what)
    - Actions (verbs, decisions)
    - Conditions (context, constraints)
    - Negations (inverted meaning)
    - Probabilities (uncertainty markers)
    - Temporal (time markers)
    """
    
    # Patterns for extracting different atom types
    ENTITY_PATTERNS = [
        (r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', 'entity'),  # Proper nouns
        (r'\b(it|they|he|she|this|that|these|those)\b', 'pronoun'),
    ]
    
    ACTION_PATTERNS = [
        (r'\b(should|must|will|can|does|don\'t|doesn\'t|won\'t)\b', 'modal'),
        (r'\b(approve|deny|accept|reject|ignore|grant|deny)\b', 'action'),
        (r'\b(allowed|not allowed|permitted|forbidden)\b', 'action'),
    ]
    
    CONDITION_PATTERNS = [
        (r'\bif|when|unless|provided that', 'condition_marker'),
        (r'\b(vip|important|standard|new|old|regular)\b', 'attribute'),
    ]
    
    PROBABILITY_MARKERS = [
        'usually', 'always', 'never', 'sometimes', 'often',
        'rarely', 'maybe', 'perhaps', 'probably', 'likely'
    ]
    
    NEGATION_MARKERS = [
        'not', "n't", 'never', 'without', 'none', 'neither'
    ]
    
    TEMPORAL_MARKERS = [
        'always', 'never', 'sometimes', 'usually', 'rarely',
        'every', 'each', 'once', 'twice'
    ]
    
    def __init__(self, confidence_threshold: float = 0.5):
        """
        Initialize the semantic atomizer.
        
        Args:
            confidence_threshold: Minimum confidence to include an atom
        """
        self.confidence_threshold = confidence_threshold
    
    def extract(self, text: str) -> List[SemanticAtom]:
        """
        Extract semantic atoms from text.
        
        Args:
            text: Raw text content
            
        Returns:
            List of extracted semantic atoms
        """
        atoms = []
        text_lower = text.lower()
        
        # Extract entities
        atoms.extend(self._extract_entities(text, text_lower))
        
        # Extract actions
        atoms.extend(self._extract_actions(text, text_lower))
        
        # Extract conditions
        atoms.extend(self._extract_conditions(text, text_lower))
        
        # Extract probability markers
        atoms.extend(self._extract_probabilities(text, text_lower))
        
        # Extract negations
        atoms.extend(self._extract_negations(text, text_lower))
        
        # Extract temporal markers
        atoms.extend(self._extract_temporal(text, text_lower))
        
        return atoms
    
    def _extract_entities(self, text: str, text_lower: str) -> List[SemanticAtom]:
        """Extract entity atoms from text."""
        atoms = []
        
        for pattern, subtype in self.ENTITY_PATTERNS:
            for match in re.finditer(pattern, text):
                atom = SemanticAtom(
                    atom_type='entity',
                    value=match.group(1),
                    attributes={'subtype': subtype},
                    confidence=0.9,
                    position=(match.start(), match.end())
                )
                atoms.append(atom)
        
        return atoms
    
    def _extract_actions(self, text: str, text_lower: str) -> List[SemanticAtom]:
        """Extract action atoms from text."""
        atoms = []
        
        for pattern, subtype in self.ACTION_PATTERNS:
            for match in re.finditer(pattern, text_lower):
                atom = SemanticAtom(
                    atom_type='action',
                    value=match.group(1),
                    attributes={'subtype': subtype},
                    confidence=0.85,
                    position=(match.start(), match.end())
                )
                atoms.append(atom)
        
        return atoms
    
    def _extract_conditions(self, text: str, text_lower: str) -> List[SemanticAtom]:
        """Extract condition atoms from text."""
        atoms = []
        
        for pattern, subtype in self.CONDITION_PATTERNS:
            for match in re.finditer(pattern, text_lower):
                atom = SemanticAtom(
                    atom_type='condition',
                    value=match.group(),
                    attributes={'subtype': subtype},
                    confidence=0.8,
                    position=(match.start(), match.end())
                )
                atoms.append(atom)
        
        return atoms
    
    def _extract_probabilities(self, text: str, text_lower: str) -> List[SemanticAtom]:
        """Extract probability/uncertainty markers."""
        atoms = []
        
        for marker in self.PROBABILITY_MARKERS:
            if marker in text_lower:
                # Find position
                pos = text_lower.find(marker)
                atom = SemanticAtom(
                    atom_type='probability',
                    value=marker,
                    confidence=self._get_probability_confidence(marker),
                    position=(pos, pos + len(marker))
                )
                atoms.append(atom)
        
        return atoms
    
    def _extract_negations(self, text: str, text_lower: str) -> List[SemanticAtom]:
        """Extract negation markers."""
        atoms = []
        
        for marker in self.NEGATION_MARKERS:
            if marker in text_lower:
                pos = text_lower.find(marker)
                atom = SemanticAtom(
                    atom_type='negation',
                    value=marker,
                    confidence=0.95,
                    position=(pos, pos + len(marker))
                )
                atoms.append(atom)
        
        return atoms
    
    def _extract_temporal(self, text: str, text_lower: str) -> List[SemanticAtom]:
        """Extract temporal markers."""
        atoms = []
        
        for marker in self.TEMPORAL_MARKERS:
            if marker in text_lower:
                pos = text_lower.find(marker)
                atom = SemanticAtom(
                    atom_type='temporal',
                    value=marker,
                    confidence=0.8,
                    position=(pos, pos + len(marker))
                )
                atoms.append(atom)
        
        return atoms
    
    def _get_probability_confidence(self, marker: str) -> float:
        """Get confidence score for probability marker."""
        high_confidence = {'always', 'never', 'certainly'}
        medium_confidence = {'usually', 'often', 'rarely'}
        low_confidence = {'sometimes', 'maybe', 'perhaps', 'probably', 'likely'}
        
        if marker in high_confidence:
            return 0.95
        elif marker in medium_confidence:
            return 0.8
        elif marker in low_confidence:
            return 0.6
        else:
            return 0.7
    
    def atoms_to_dict(self, atoms: List[SemanticAtom]) -> List[dict]:
        """Convert atoms to dictionary format for serialization."""
        return [
            {
                'atom_type': a.atom_type,
                'value': a.value,
                'attributes': a.attributes or {},
                'confidence': a.confidence,
                'position': a.position
            }
            for a in atoms
        ]
    
    def dict_to_atoms(self, data: List[dict]) -> List[SemanticAtom]:
        """Convert dictionaries back to SemanticAtom objects."""
        atoms = []
        for item in data:
            atom = SemanticAtom(
                atom_type=item['atom_type'],
                value=item['value'],
                attributes=item.get('attributes'),
                confidence=item.get('confidence', 1.0),
                position=item.get('position')
            )
            atoms.append(atom)
        return atoms
