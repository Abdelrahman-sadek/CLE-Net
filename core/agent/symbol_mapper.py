"""
Symbol Mapper Module

Converts semantic atoms into formal logical representations.
"""

import hashlib
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class SymbolicAtom:
    """
    A symbolic representation of meaning.
    
    Attributes:
        predicate: The logical predicate
        subject: The subject of the predicate
        attributes: Key-value attributes
        negation: Whether this is negated
        confidence: Confidence score
    """
    predicate: str
    subject: str
    attributes: Dict[str, Any]
    negation: bool = False
    confidence: float = 1.0


class SymbolMapper:
    """
    Converts semantic atoms to formal symbolic representations.
    
    This module bridges the gap between natural language meaning
    and formal logical predicates suitable for reasoning.
    """
    
    # Mapping from atom types to predicate templates
    PREDICATE_TEMPLATES = {
        'entity': lambda a: f'{a.value}',
        'action': lambda a: f'action({a.value})',
        'condition': lambda a: f'condition({a.value})',
        'probability': lambda a: f'probably({a.value})',
        'negation': lambda a: f'not_{a.value}',
        'temporal': lambda a: f'always({a.value})',
    }
    
    # Standard attribute mappings
    ATTRIBUTE_NORMALIZATION = {
        'vip': 'importance=high',
        'important': 'importance=high',
        'standard': 'importance=standard',
        'new': 'status=new',
        'old': 'status=old',
    }
    
    def __init__(self):
        """Initialize the symbol mapper."""
        self._predicate_registry = {}
    
    def map(self, atoms: List[Dict]) -> List[SymbolicAtom]:
        """
        Convert semantic atoms to symbolic representations.
        
        Args:
            atoms: List of atom dictionaries from the atomizer
            
        Returns:
            List of symbolic atoms
        """
        symbols = []
        
        for atom in atoms:
            symbol = self._atom_to_symbol(atom)
            if symbol:
                symbols.append(symbol)
        
        return symbols
    
    def _atom_to_symbol(self, atom: Dict) -> SymbolicAtom:
        """
        Convert a single atom to a symbolic representation.
        
        Args:
            atom: Atom dictionary
            
        Returns:
            SymbolicAtom or None if conversion fails
        """
        atom_type = atom.get('atom_type', '')
        value = atom.get('value', '')
        attributes = atom.get('attributes', {})
        confidence = atom.get('confidence', 1.0)
        
        # Handle negation
        negation = False
        if atom_type == 'negation':
            negation = True
            # Negation typically modifies the following atom
            return None
        
        # Build predicate
        predicate = self._build_predicate(atom_type, value, attributes)
        
        # Determine subject
        subject = self._extract_subject(atom_type, value, attributes)
        
        return SymbolicAtom(
            predicate=predicate,
            subject=subject,
            attributes=attributes,
            negation=negation,
            confidence=confidence
        )
    
    def _build_predicate(self, atom_type: str, value: str, attributes: Dict) -> str:
        """
        Build a logical predicate from an atom.
        
        Args:
            atom_type: Type of atom
            value: The atom value
            attributes: Associated attributes
            
        Returns:
            Predicate string
        """
        if atom_type == 'entity':
            # Entities become simple predicates
            normalized_value = self._normalize_value(value)
            return f'{normalized_value}'
        
        elif atom_type == 'action':
            return f'do({value})'
        
        elif atom_type == 'condition':
            return f'condition({value})'
        
        elif atom_type == 'probability':
            return f'probably({value})'
        
        elif atom_type == 'temporal':
            return f'always({value})'
        
        else:
            return f'{atom_type}({value})'
    
    def _extract_subject(self, atom_type: str, value: str, attributes: Dict) -> str:
        """
        Extract the subject from an atom.
        
        Args:
            atom_type: Type of atom
            value: The atom value
            attributes: Associated attributes
            
        Returns:
            Subject string
        """
        if atom_type == 'entity':
            return value.lower()
        elif atom_type == 'action':
            return attributes.get('subtype', 'unknown')
        else:
            return atom_type
    
    def _normalize_value(self, value: str) -> str:
        """Normalize a value for consistent representation."""
        # Convert to lowercase, replace spaces with underscores
        return value.lower().replace(' ', '_')
    
    def symbols_to_logic(self, symbols: List[SymbolicAtom]) -> str:
        """
        Convert a list of symbols to a logical form.
        
        Args:
            symbols: List of symbolic atoms
            
        Returns:
            Canonical logical representation
        """
        if not symbols:
            return ""
        
        # Separate conditions and effects
        conditions = []
        effects = []
        other = []
        
        for symbol in symbols:
            if symbol.predicate.startswith('condition'):
                conditions.append(symbol)
            elif symbol.predicate.startswith('do('):
                effects.append(symbol)
            else:
                other.append(symbol)
        
        # Build IF-THEN form
        parts = []
        
        if conditions:
            cond_strs = [self._symbol_to_str(s) for s in conditions]
            parts.append(f"IF {' AND '.join(cond_strs)}")
        
        if effects:
            eff_strs = [self._symbol_to_str(s) for s in effects]
            parts.append(f"THEN {' AND '.join(eff_strs)}")
        
        if other:
            other_strs = [self._symbol_to_str(s) for s in other]
            parts.append(f"AND {' AND '.join(other_strs)}")
        
        return ' '.join(parts)
    
    def _symbol_to_str(self, symbol: SymbolicAtom) -> str:
        """Convert a symbol to a string representation."""
        parts = [symbol.predicate]
        
        if symbol.attributes:
            attrs = [f'{k}={v}' for k, v in symbol.attributes.items()]
            parts.append(f'[{",".join(attrs)}]')
        
        if symbol.negation:
            parts.insert(0, 'NOT')
        
        return ''.join(parts)
    
    def canonicalize(self, logic_form: str) -> str:
        """
        Create a canonical form of a logical expression.
        
        Args:
            logic_form: Original logical expression
            
        Returns:
            Normalized canonical form
        """
        # Normalize whitespace
        normalized = ' '.join(logic_form.split())
        
        # Convert to lowercase (except for constants)
        normalized = normalized.lower()
        
        # Ensure consistent spacing around operators
        normalized = normalized.replace('then', ' THEN ')
        normalized = normalized.replace('if', ' IF ')
        normalized = normalized.replace('and', ' AND ')
        normalized = normalized.replace('or', ' OR ')
        
        # Normalize whitespace again
        normalized = ' '.join(normalized.split())
        
        return normalized
    
    def compute_hash(self, logic_form: str) -> str:
        """
        Compute a hash for a logical form.
        
        Args:
            logic_form: Logical expression
            
        Returns:
            SHA256 hash (first 16 characters)
        """
        canonical = self.canonicalize(logic_form)
        return hashlib.sha256(canonical.encode()).hexdigest()[:16]
    
    def symbols_to_graph(self, symbols: List[SymbolicAtom]) -> Dict:
        """
        Convert symbols to a graph structure.
        
        Args:
            symbols: List of symbolic atoms
            
        Returns:
            Graph dictionary with nodes and edges
        """
        nodes = []
        edges = []
        
        for symbol in symbols:
            # Add predicate as node
            nodes.append({
                'id': symbol.predicate,
                'type': 'predicate',
                'subject': symbol.subject,
                'attributes': symbol.attributes
            })
            
            # Add edge from subject to predicate
            if symbol.subject:
                edges.append({
                    'from': symbol.subject,
                    'to': symbol.predicate,
                    'type': 'has_property' if not symbol.predicate.startswith('do(') else 'performs'
                })
        
        return {
            'nodes': nodes,
            'edges': edges,
            'node_count': len(nodes),
            'edge_count': len(edges)
        }
