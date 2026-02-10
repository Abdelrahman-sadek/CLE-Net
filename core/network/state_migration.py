"""
State Migration Protocols

Enables survivability across machines by allowing agents to migrate
their state from one host to another.
"""

import asyncio
import json
import hashlib
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import base64


class MigrationState(Enum):
    """States in the migration process."""
    IDLE = "idle"
    PREPARING = "preparing"
    EXPORTING = "exporting"
    TRANSFERRING = "transferring"
    IMPORTING = "importing"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class MigrationConfig:
    """Configuration for state migration."""
    chunk_size: int = 1024 * 1024  # 1MB chunks
    max_retries: int = 3
    timeout: int = 300  # 5 minutes
    encryption_enabled: bool = True
    compression_enabled: bool = True


@dataclass
class MigrationStatus:
    """Status of a migration operation."""
    migration_id: str
    state: MigrationState
    progress: float  # 0.0 to 1.0
    source_host: str
    target_host: str
    bytes_transferred: int = 0
    total_bytes: int = 0
    error: Optional[str] = None
    started_at: float = 0.0
    completed_at: Optional[float] = None


class StateMigration:
    """
    Manages state migration between hosts.
    
    Responsibilities:
    - Export agent state to portable format
    - Transfer state to new host
    - Import and verify state on new host
    - Handle migration failures and retries
    """
    
    def __init__(self, config: MigrationConfig = None):
        """
        Initialize state migration manager.
        
        Args:
            config: Migration configuration
        """
        self.config = config or MigrationConfig()
        self.active_migrations: Dict[str, MigrationStatus] = {}
        self.migration_history: List[MigrationStatus] = []
    
    async def prepare_migration(self, agent_id: str, state: Dict) -> str:
        """
        Prepare a migration by creating a migration ID and validating state.
        
        Args:
            agent_id: ID of the agent being migrated
            state: Current agent state
            
        Returns:
            Migration ID
        """
        migration_id = self._generate_migration_id(agent_id)
        
        # Create migration status
        status = MigrationStatus(
            migration_id=migration_id,
            state=MigrationState.PREPARING,
            progress=0.0,
            source_host=self._get_current_host(),
            target_host="",
            started_at=time.time()
        )
        
        self.active_migrations[migration_id] = status
        
        # Validate state
        if not self._validate_state(state):
            status.state = MigrationState.FAILED
            status.error = "Invalid state"
            status.completed_at = time.time()
            return migration_id
        
        status.state = MigrationState.EXPORTING
        status.progress = 0.1
        
        return migration_id
    
    async def export_state(self, migration_id: str, state: Dict) -> bytes:
        """
        Export agent state to portable format.
        
        Args:
            migration_id: Migration ID
            state: Agent state to export
            
        Returns:
            Exported state as bytes
        """
        status = self.active_migrations.get(migration_id)
        if not status:
            raise ValueError(f"Migration {migration_id} not found")
        
        # Serialize state
        state_json = json.dumps(state, indent=2)
        state_bytes = state_json.encode('utf-8')
        
        # Calculate hash
        state_hash = hashlib.sha256(state_bytes).hexdigest()
        
        # Create migration package
        package = {
            "migration_id": migration_id,
            "agent_id": state.get("agent_id", ""),
            "timestamp": time.time(),
            "state_hash": state_hash,
            "state_data": base64.b64encode(state_bytes).decode('utf-8'),
            "metadata": {
                "version": "1.0",
                "source_host": status.source_host
            }
        }
        
        # Serialize package
        package_json = json.dumps(package, separators=(',', ':'))
        package_bytes = package_json.encode('utf-8')
        
        status.total_bytes = len(package_bytes)
        status.progress = 0.3
        
        return package_bytes
    
    async def transfer_state(self, migration_id: str, state_bytes: bytes, 
                           target_host: str) -> bool:
        """
        Transfer state to target host.
        
        Args:
            migration_id: Migration ID
            state_bytes: State data to transfer
            target_host: Target host address
            
        Returns:
            True if transfer successful
        """
        status = self.active_migrations.get(migration_id)
        if not status:
            raise ValueError(f"Migration {migration_id} not found")
        
        status.state = MigrationState.TRANSERRING
        status.target_host = target_host
        status.progress = 0.4
        
        # Simulate transfer (in production, use actual network transfer)
        chunk_size = self.config.chunk_size
        total_chunks = (len(state_bytes) + chunk_size - 1) // chunk_size
        
        for i in range(total_chunks):
            start = i * chunk_size
            end = min(start + chunk_size, len(state_bytes))
            chunk = state_bytes[start:end]
            
            # Simulate network transfer
            await asyncio.sleep(0.1)
            
            status.bytes_transferred = end
            status.progress = 0.4 + (0.3 * (i + 1) / total_chunks)
        
        return True
    
    async def import_state(self, migration_id: str, state_bytes: bytes) -> Dict:
        """
        Import state on target host.
        
        Args:
            migration_id: Migration ID
            state_bytes: State data to import
            
        Returns:
            Imported state dictionary
        """
        status = self.active_migrations.get(migration_id)
        if not status:
            raise ValueError(f"Migration {migration_id} not found")
        
        status.state = MigrationState.IMPORTING
        status.progress = 0.8
        
        # Deserialize package
        package_json = state_bytes.decode('utf-8')
        package = json.loads(package_json)
        
        # Verify migration ID
        if package["migration_id"] != migration_id:
            raise ValueError("Migration ID mismatch")
        
        # Decode state data
        state_data = base64.b64decode(package["state_data"])
        state = json.loads(state_data.decode('utf-8'))
        
        # Verify hash
        state_hash = hashlib.sha256(state_data).hexdigest()
        if state_hash != package["state_hash"]:
            raise ValueError("State hash mismatch - data corrupted")
        
        status.progress = 0.9
        
        return state
    
    async def verify_migration(self, migration_id: str, imported_state: Dict) -> bool:
        """
        Verify that imported state is valid and consistent.
        
        Args:
            migration_id: Migration ID
            imported_state: Imported state to verify
            
        Returns:
            True if verification successful
        """
        status = self.active_migrations.get(migration_id)
        if not status:
            raise ValueError(f"Migration {migration_id} not found")
        
        status.state = MigrationState.VERIFYING
        status.progress = 0.95
        
        # Validate imported state
        if not self._validate_state(imported_state):
            status.state = MigrationState.FAILED
            status.error = "Imported state validation failed"
            status.completed_at = time.time()
            return False
        
        # Check for required fields
        required_fields = ["agent_id", "node_identity", "current_rules"]
        for field in required_fields:
            if field not in imported_state:
                status.state = MigrationState.FAILED
                status.error = f"Missing required field: {field}"
                status.completed_at = time.time()
                return False
        
        status.state = MigrationState.COMPLETED
        status.progress = 1.0
        status.completed_at = time.time()
        
        # Move to history
        self.migration_history.append(status)
        del self.active_migrations[migration_id]
        
        return True
    
    async def complete_migration(self, migration_id: str) -> bool:
        """
        Complete a migration and reattach to consensus.
        
        Args:
            migration_id: Migration ID
            
        Returns:
            True if completion successful
        """
        status = self.active_migrations.get(migration_id)
        if not status:
            # Check history
            for hist in self.migration_history:
                if hist.migration_id == migration_id:
                    return hist.state == MigrationState.COMPLETED
            return False
        
        if status.state != MigrationState.COMPLETED:
            return False
        
        # Reattach to consensus (placeholder)
        # In production, this would involve:
        # 1. Connecting to P2P network
        # 2. Syncing latest state
        # 3. Resuming operation
        
        return True
    
    def _generate_migration_id(self, agent_id: str) -> str:
        """Generate a unique migration ID."""
        timestamp = int(time.time())
        content = f"{agent_id}_{timestamp}"
        hash_val = hashlib.sha256(content.encode()).hexdigest()[:16]
        return f"migration_{hash_val}"
    
    def _get_current_host(self) -> str:
        """Get current host identifier."""
        # Placeholder - in production, get actual host info
        return "localhost"
    
    def _validate_state(self, state: Dict) -> bool:
        """
        Validate that state is well-formed.
        
        Args:
            state: State to validate
            
        Returns:
            True if valid
        """
        # Basic validation
        if not isinstance(state, dict):
            return False
        
        if "agent_id" not in state:
            return False
        
        return True
    
    def get_migration_status(self, migration_id: str) -> Optional[MigrationStatus]:
        """
        Get status of a migration.
        
        Args:
            migration_id: Migration ID
            
        Returns:
            Migration status or None
        """
        return self.active_migrations.get(migration_id)
    
    def get_all_migrations(self) -> List[MigrationStatus]:
        """
        Get all active and recent migrations.
        
        Returns:
            List of migration statuses
        """
        return list(self.active_migrations.values()) + self.migration_history[-10:]


class MigrationCoordinator:
    """
    Coordinates migration across multiple agents.
    
    Ensures that migrations don't cause consensus issues
    and that the network remains stable during migrations.
    """
    
    def __init__(self):
        """Initialize migration coordinator."""
        self.pending_migrations: Dict[str, List[str]] = {}  # agent_id -> migration_ids
        self.locked_agents: set = set()
    
    async def request_migration(self, agent_id: str) -> bool:
        """
        Request permission to migrate an agent.
        
        Args:
            agent_id: ID of agent to migrate
            
        Returns:
            True if migration approved
        """
        # Check if agent is locked
        if agent_id in self.locked_agents:
            return False
        
        # Check if there are pending migrations
        if agent_id in self.pending_migrations and self.pending_migrations[agent_id]:
            return False
        
        # Lock agent for migration
        self.locked_agents.add(agent_id)
        
        return True
    
    async def complete_migration(self, agent_id: str, migration_id: str):
        """
        Mark a migration as complete and unlock agent.
        
        Args:
            agent_id: ID of migrated agent
            migration_id: Migration ID
        """
        # Remove from locked agents
        if agent_id in self.locked_agents:
            self.locked_agents.remove(agent_id)
        
        # Clean up pending migrations
        if agent_id in self.pending_migrations:
            if migration_id in self.pending_migrations[agent_id]:
                self.pending_migrations[agent_id].remove(migration_id)
    
    def get_locked_agents(self) -> List[str]:
        """Get list of locked agents."""
        return list(self.locked_agents)
