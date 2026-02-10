"""
CLE-Net Autonomous Cognitive Agent

This module implements the core CLE agent that observes, extracts,
discovers rules, and participates in network consensus.
"""

import uuid
import time
import hashlib
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

from .event_stream import EventStream, Event
from .atomizer import SemanticAtomizer
from .symbol_mapper import SymbolMapper
from .rule_engine import RuleEngine, RuleCandidate


@dataclass
class AgentConfig:
    """Configuration for a CLE agent."""
    agent_id: Optional[str] = None
    mode: str = "full"  # full or light
    checkpoint_interval: int = 300  # seconds
    sync_interval: int = 60  # seconds
    confidence_threshold: float = 0.7
    min_coverage: float = 0.1


@dataclass
class AgentState:
    """State of a CLE agent."""
    agent_id: str
    node_identity: str
    current_rules: Dict[str, Dict] = field(default_factory=dict)
    event_history: List[Event] = field(default_factory=list)
    symbol_buffer: List[Dict] = field(default_factory=list)
    pending_commits: List[Dict] = field(default_factory=list)
    consensus_state: Dict[str, float] = field(default_factory=dict)
    last_checkpoint: int = 0
    last_sync: int = 0


class CLEAgent:
    """
    A CLE-Net autonomous cognitive agent.
    
    Responsibilities:
    - Observe human interaction (text, voice, documents)
    - Extract symbolic representations from raw input
    - Discover latent rules through symbolic regression
    - Communicate discoveries to the network
    - Learn from global consensus
    """
    
    def __init__(self, config: AgentConfig, data_path: str):
        """
        Initialize a CLE agent.
        
        Args:
            config: Agent configuration
            data_path: Path to local data directory
        """
        self.config = config
        self.data_path = data_path
        
        # Generate or use provided agent ID
        self.agent_id = config.agent_id or f"agent_{uuid.uuid4().hex[:8]}"
        
        # Initialize components
        self.event_stream = EventStream()
        self.atomizer = SemanticAtomizer()
        self.symbol_mapper = SymbolMapper()
        self.rule_engine = RuleEngine()
        
        # Initialize state
        self.state = AgentState(
            agent_id=self.agent_id,
            node_identity=self._generate_identity()
        )
        
        # Load local data
        self.local_data = self._load_local_data()
    
    def _generate_identity(self) -> str:
        """Generate a unique node identity."""
        seed = f"{self.agent_id}_{time.time()}"
        return hashlib.sha256(seed.encode()).hexdigest()[:16]
    
    def _load_local_data(self) -> List[str]:
        """
        Load local data from the data path.
        
        For MVP, this reads text files.
        In production, this would handle multiple modalities.
        """
        # Placeholder for data loading
        # In MVP: read text files from data_path
        return []
    
    def observe(self, content: str, modality: str = "text") -> Event:
        """
        Observe new human interaction.
        
        Args:
            content: Raw interaction content
            modality: Type of input (text, voice, document)
            
        Returns:
            Captured event
        """
        event = Event(
            event_id=uuid.uuid4().hex,
            timestamp=time.time(),
            source=self.agent_id,
            modality=modality,
            raw_content=content,
            confidence=1.0,
            metadata={}
        )
        
        self.event_stream.add_event(event)
        self.state.event_history.append(event)
        
        return event
    
    def extract(self, event: Event) -> List[Dict]:
        """
        Extract symbolic atoms from an event.
        
        Args:
            event: Input event
            
        Returns:
            List of extracted atoms
        """
        atoms = self.atomizer.extract(event.raw_content)
        self.state.symbol_buffer.extend(atoms)
        return atoms
    
    def symbolize(self, atoms: List[Dict]) -> List[Dict]:
        """
        Convert atoms to symbolic representations.
        
        Args:
            atoms: List of semantic atoms
            
        Returns:
            List of symbolic predicates
        """
        symbols = self.symbol_mapper.map(atoms)
        return symbols
    
    def discover(self) -> List[RuleCandidate]:
        """
        Discover rules from accumulated symbols.
        
        Returns:
            List of discovered rule candidates
        """
        candidates = self.rule_engine.discover(self.state.symbol_buffer)
        return candidates
    
    def commit(self, candidate: RuleCandidate) -> Dict:
        """
        Create a rule commitment for broadcast.
        
        Args:
            candidate: Rule candidate to commit
            
        Returns:
            Rule commitment message
        """
        if candidate.confidence < self.config.confidence_threshold:
            return None
        
        commit = {
            "rule_hash": candidate.rule_id,
            "logic_signature": self._compute_logic_signature(candidate),
            "context_signature": self._compute_context_signature(candidate),
            "agent_id": self.agent_id,
            "timestamp": time.time(),
            "confidence": candidate.confidence
        }
        
        self.state.pending_commits.append(commit)
        return commit
    
    def _compute_logic_signature(self, candidate: RuleCandidate) -> str:
        """Compute a normalized signature for the rule logic."""
        # Normalize and hash the logic form
        normalized = candidate.logic_form.strip().lower()
        normalized = ' '.join(normalized.split())  # Normalize whitespace
        return hashlib.sha256(normalized.encode()).hexdigest()[:32]
    
    def _compute_context_signature(self, candidate: RuleCandidate) -> str:
        """Compute a signature for the rule context."""
        context = candidate.context or ""
        return hashlib.sha256(context.encode()).hexdigest()[:16]
    
    def process_interaction(self, content: str) -> List[Dict]:
        """
        Process a single human interaction end-to-end.
        
        Args:
            content: Raw interaction content
            
        Returns:
            List of generated rule commits
        """
        # Step 1: Observe
        event = self.observe(content)
        
        # Step 2: Extract atoms
        atoms = self.extract(event)
        
        # Step 3: Convert to symbols
        symbols = self.symbolize(atoms)
        
        # Step 4: Discover rules
        candidates = self.discover()
        
        # Step 5: Create commitments
        commits = []
        for candidate in candidates:
            commit = self.commit(candidate)
            if commit:
                commits.append(commit)
        
        return commits
    
    def get_status(self) -> Dict:
        """
        Get the current status of the agent.
        
        Returns:
            Status dictionary
        """
        return {
            "agent_id": self.agent_id,
            "node_identity": self.state.node_identity,
            "events_processed": len(self.state.event_history),
            "symbols_buffered": len(self.state.symbol_buffer),
            "pending_commits": len(self.state.pending_commits),
            "accepted_rules": len(self.state.current_rules),
            "uptime_seconds": time.time() - self.state.last_checkpoint
        }
    
    def save_state(self, path: str) -> None:
        """Save agent state to disk."""
        state_data = {
            "agent_id": self.state.agent_id,
            "node_identity": self.state.node_identity,
            "event_history": [e.__dict__ for e in self.state.event_history],
            "current_rules": self.state.current_rules,
            "consensus_state": self.state.consensus_state,
            "timestamp": time.time()
        }
        
        with open(path, 'w') as f:
            json.dump(state_data, f, indent=2)
    
    def load_state(self, path: str) -> None:
        """Load agent state from disk."""
        with open(path, 'r') as f:
            state_data = json.load(f)
        
        self.state.agent_id = state_data["agent_id"]
        self.state.node_identity = state_data["node_identity"]
        self.state.current_rules = state_data.get("current_rules", {})
        self.state.consensus_state = state_data.get("consensus_state", {})
        # Rebuild event history from serialized data
        self.state.event_history = [
            Event(**e) for e in state_data.get("event_history", [])
        ]
