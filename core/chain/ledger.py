"""
Ledger Module

Append-only storage for rule commitments and consensus outcomes.
"""

import json
import time
import hashlib
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class LedgerEntry:
    """
    A single entry in the CLE-Net ledger.
    
    The ledger stores rule commitments, not raw rules.
    Only hashes and metadata are stored.
    """
    entry_id: str
    entry_type: str  # 'commit', 'challenge', 'confirm', 'checkpoint'
    timestamp: float
    data: Dict[str, Any]
    hash: str
    previous_hash: str = ""
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            'entry_id': self.entry_id,
            'entry_type': self.entry_type,
            'timestamp': self.timestamp,
            'data': self.data,
            'hash': self.hash,
            'previous_hash': self.previous_hash
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'LedgerEntry':
        """Create from dictionary."""
        return cls(
            entry_id=data['entry_id'],
            entry_type=data['entry_type'],
            timestamp=data['timestamp'],
            data=data['data'],
            hash=data['hash'],
            previous_hash=data.get('previous_hash', '')
        )


class Ledger:
    """
    An append-only ledger for CLE-Net.
    
    The ledger stores:
    - Rule commitments (hashes, not raw rules)
    - Consensus checkpoints
    - Network events
    
    Properties:
    - Append-only: Entries cannot be modified or deleted
    - Linked: Each entry references the previous
    - Verifiable: Hash chain ensures integrity
    """
    
    def __init__(self, file_path: str = None):
        """
        Initialize the ledger.
        
        Args:
            file_path: Path to ledger file (for persistence)
        """
        self.file_path = file_path
        self._entries: List[LedgerEntry] = []
        self._index: Dict[str, int] = {}  # entry_id -> index
        
        # Load existing ledger if file exists
        if file_path:
            self._load()
    
    def add_commit(self, 
                   rule_hash: str,
                   logic_signature: str,
                   context_signature: str,
                   agent_id: str,
                   confidence: float,
                   metadata: Dict = None) -> LedgerEntry:
        """
        Add a rule commitment to the ledger.
        
        Args:
            rule_hash: Hash of the rule
            logic_signature: Normalized logic hash
            context_signature: Context hash
            agent_id: Discovering agent
            confidence: Agent's confidence
            metadata: Additional metadata
            
        Returns:
            Created ledger entry
        """
        data = {
            'rule_hash': rule_hash,
            'logic_signature': logic_signature,
            'context_signature': context_signature,
            'agent_id': agent_id,
            'confidence': confidence,
            'metadata': metadata or {}
        }
        
        return self._add_entry('commit', data)
    
    def add_challenge(self,
                      rule_hash: str,
                      contradicting_rule: Dict,
                      agent_id: str) -> LedgerEntry:
        """
        Add a challenge (contradiction) for a rule.
        
        Args:
            rule_hash: Rule being challenged
            contradicting_rule: The contradicting rule data
            agent_id: Challenging agent
            
        Returns:
            Created ledger entry
        """
        data = {
            'rule_hash': rule_hash,
            'contradicting_rule': contradicting_rule,
            'agent_id': agent_id
        }
        
        return self._add_entry('challenge', data)
    
    def add_checkpoint(self,
                       accepted_rules: List[str],
                       statistics: Dict) -> LedgerEntry:
        """
        Add a consensus checkpoint.
        
        Args:
            accepted_rules: List of accepted rule hashes
            statistics: Network statistics
            
        Returns:
            Created ledger entry
        """
        data = {
            'accepted_rules': accepted_rules,
            'statistics': statistics,
            'checkpoint_time': time.time()
        }
        
        return self._add_entry('checkpoint', data)
    
    def _add_entry(self, entry_type: str, data: Dict) -> LedgerEntry:
        """
        Internal method to add an entry.
        
        Args:
            entry_type: Type of entry
            data: Entry data
            
        Returns:
            Created ledger entry
        """
        # Get previous hash
        previous_hash = ''
        if self._entries:
            previous_hash = self._entries[-1].hash
        
        # Create entry
        entry = LedgerEntry(
            entry_id=self._generate_id(),
            entry_type=entry_type,
            timestamp=time.time(),
            data=data,
            previous_hash=previous_hash
        )
        
        # Calculate hash
        entry.hash = self._calculate_hash(entry)
        
        # Add to ledger
        self._entries.append(entry)
        self._index[entry.entry_id] = len(self._entries) - 1
        
        # Persist
        if self.file_path:
            self._save()
        
        return entry
    
    def _generate_id(self) -> str:
        """Generate a unique entry ID."""
        timestamp = str(time.time()).encode()
        random_part = hashlib.sha256(str(id(self)).encode()).hexdigest()[:8]
        return f"entry_{timestamp.decode('utf-8', errors='replace')}_{random_part}"
    
    def _calculate_hash(self, entry: LedgerEntry) -> str:
        """
        Calculate the hash for an entry.
        
        Args:
            entry: Ledger entry
            
        Returns:
            Entry hash
        """
        # Create deterministic string representation
        content = f"{entry.entry_id}{entry.entry_type}{entry.timestamp}"
        content += f"{json.dumps(entry.data, sort_keys=True)}{entry.previous_hash}"
        
        return hashlib.sha256(content.encode()).hexdigest()
    
    def verify_integrity(self) -> Tuple[bool, List[str]]:
        """
        Verify the integrity of the ledger.
        
        Returns:
            Tuple of (is_valid, list of errors)
        """
        errors = []
        
        if not self._entries:
            return True, errors
        
        # Check genesis entry
        first_entry = self._entries[0]
        if first_entry.previous_hash != '':
            errors.append("Genesis entry has non-empty previous_hash")
        
        # Check hash chain
        for i, entry in enumerate(self._entries):
            expected_hash = self._calculate_hash(entry)
            if entry.hash != expected_hash:
                errors.append(f"Entry {entry.entry_id} has invalid hash")
            
            # Check previous hash linkage
            if i > 0:
                if entry.previous_hash != self._entries[i-1].hash:
                    errors.append(f"Entry {entry.entry_id} has broken chain")
        
        return len(errors) == 0, errors
    
    def get_commits_by_rule(self, rule_hash: str) -> List[LedgerEntry]:
        """
        Get all commits for a specific rule.
        
        Args:
            rule_hash: Rule hash to query
            
        Returns:
            List of matching entries
        """
        commits = []
        
        for entry in self._entries:
            if entry.entry_type == 'commit':
                if entry.data.get('rule_hash') == rule_hash:
                    commits.append(entry)
        
        return commits
    
    def get_commits_by_agent(self, agent_id: str) -> List[LedgerEntry]:
        """
        Get all commits by a specific agent.
        
        Args:
            agent_id: Agent to query
            
        Returns:
            List of matching entries
        """
        commits = []
        
        for entry in self._entries:
            if entry.entry_type == 'commit':
                if entry.data.get('agent_id') == agent_id:
                    commits.append(entry)
        
        return commits
    
    def get_latest_checkpoint(self) -> Optional[LedgerEntry]:
        """
        Get the latest checkpoint entry.
        
        Returns:
            Most recent checkpoint or None
        """
        for entry in reversed(self._entries):
            if entry.entry_type == 'checkpoint':
                return entry
        return None
    
    def get_statistics(self) -> Dict:
        """
        Get ledger statistics.
        
        Returns:
            Statistics dictionary
        """
        commits = [e for e in self._entries if e.entry_type == 'commit']
        challenges = [e for e in self._entries if e.entry_type == 'challenge']
        checkpoints = [e for e in self._entries if e.entry_type == 'checkpoint']
        
        agents = set()
        for entry in commits:
            agent_id = entry.data.get('agent_id')
            if agent_id:
                agents.add(agent_id)
        
        return {
            'total_entries': len(self._entries),
            'total_commits': len(commits),
            'total_challenges': len(challenges),
            'total_checkpoints': len(checkpoints),
            'unique_agents': len(agents),
            'first_entry_time': self._entries[0].timestamp if self._entries else None,
            'last_entry_time': self._entries[-1].timestamp if self._entries else None
        }
    
    def export(self) -> List[dict]:
        """
        Export the entire ledger as dictionaries.
        
        Returns:
            List of entry dictionaries
        """
        return [entry.to_dict() for entry in self._entries]
    
    def _save(self) -> None:
        """Save ledger to file."""
        if not self.file_path:
            return
        
        data = self.export()
        
        with open(self.file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _load(self) -> None:
        """Load ledger from file."""
        if not self.file_path:
            return
        
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
            
            for entry_data in data:
                entry = LedgerEntry.from_dict(entry_data)
                self._entries.append(entry)
                self._index[entry.entry_id] = len(self._entries) - 1
                
        except FileNotFoundError:
            pass  # New ledger
        except json.JSONDecodeError:
            pass  # Corrupted ledger
    
    def clear(self) -> None:
        """Clear the ledger (for testing/reset)."""
        self._entries.clear()
        self._index.clear()
        
        if self.file_path:
            self._save()
