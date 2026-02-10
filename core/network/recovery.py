"""
CLE-Net Automatic Recovery Module

This module provides automatic recovery after crashes and failures.
It ensures that CLE-Net agents can recover from crashes and resume operation.
"""

from typing import Dict, List, Optional, Callable
from datetime import datetime
import json
import os
import hashlib
import time


class RecoveryState:
    """Represents the recovery state of an agent."""
    
    def __init__(
        self,
        agent_id: str,
        last_checkpoint: datetime,
        state_hash: str,
        recovery_status: str = "pending"
    ):
        self.agent_id = agent_id
        self.last_checkpoint = last_checkpoint
        self.state_hash = state_hash
        self.recovery_status = recovery_status
        self.recovery_attempts = 0
        self.last_recovery_attempt = None
        self.recovery_log: List[str] = []
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "agent_id": self.agent_id,
            "last_checkpoint": self.last_checkpoint.isoformat(),
            "state_hash": self.state_hash,
            "recovery_status": self.recovery_status,
            "recovery_attempts": self.recovery_attempts,
            "last_recovery_attempt": self.last_recovery_attempt.isoformat() if self.last_recovery_attempt else None,
            "recovery_log": self.recovery_log
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "RecoveryState":
        """Create from dictionary."""
        return cls(
            agent_id=data["agent_id"],
            last_checkpoint=datetime.fromisoformat(data["last_checkpoint"]),
            state_hash=data["state_hash"],
            recovery_status=data["recovery_status"]
        )


class Checkpoint:
    """Represents a checkpoint of agent state."""
    
    def __init__(
        self,
        checkpoint_id: str,
        agent_id: str,
        timestamp: datetime,
        state_data: Dict,
        state_hash: str
    ):
        self.checkpoint_id = checkpoint_id
        self.agent_id = agent_id
        self.timestamp = timestamp
        self.state_data = state_data
        self.state_hash = state_hash
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "checkpoint_id": self.checkpoint_id,
            "agent_id": self.agent_id,
            "timestamp": self.timestamp.isoformat(),
            "state_data": self.state_data,
            "state_hash": self.state_hash
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Checkpoint":
        """Create from dictionary."""
        return cls(
            checkpoint_id=data["checkpoint_id"],
            agent_id=data["agent_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            state_data=data["state_data"],
            state_hash=data["state_hash"]
        )
    
    def compute_hash(self) -> str:
        """Compute hash of the checkpoint."""
        data_str = json.dumps(self.state_data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()


class RecoveryManager:
    """
    Manages automatic recovery after crashes.
    
    This class provides:
    - Checkpoint creation and management
    - Automatic recovery after crashes
    - State validation and restoration
    - Recovery logging and monitoring
    """
    
    def __init__(self, checkpoint_dir: str = "./checkpoints"):
        """Initialize the recovery manager."""
        self.checkpoint_dir = checkpoint_dir
        self.checkpoints: Dict[str, Checkpoint] = {}
        self.recovery_states: Dict[str, RecoveryState] = {}
        self.recovery_callbacks: Dict[str, Callable] = {}
        self.max_recovery_attempts = 3
        self.recovery_timeout = 300  # 5 minutes
        self.checkpoint_interval = 60  # 1 minute
        
        # Create checkpoint directory if it doesn't exist
        os.makedirs(checkpoint_dir, exist_ok=True)
        
        # Load existing checkpoints
        self._load_checkpoints()
    
    def create_checkpoint(
        self,
        agent_id: str,
        state_data: Dict
    ) -> Checkpoint:
        """
        Create a checkpoint of agent state.
        
        Args:
            agent_id: ID of the agent
            state_data: Current state data of the agent
            
        Returns:
            Checkpoint object
        """
        # Generate checkpoint ID
        checkpoint_id = f"checkpoint_{agent_id}_{int(time.time())}"
        
        # Compute state hash
        data_str = json.dumps(state_data, sort_keys=True)
        state_hash = hashlib.sha256(data_str.encode()).hexdigest()
        
        # Create checkpoint
        checkpoint = Checkpoint(
            checkpoint_id=checkpoint_id,
            agent_id=agent_id,
            timestamp=datetime.utcnow(),
            state_data=state_data,
            state_hash=state_hash
        )
        
        # Store checkpoint
        self.checkpoints[checkpoint_id] = checkpoint
        
        # Save checkpoint to disk
        self._save_checkpoint(checkpoint)
        
        # Update recovery state
        if agent_id not in self.recovery_states:
            self.recovery_states[agent_id] = RecoveryState(
                agent_id=agent_id,
                last_checkpoint=checkpoint.timestamp,
                state_hash=state_hash,
                recovery_status="healthy"
            )
        else:
            self.recovery_states[agent_id].last_checkpoint = checkpoint.timestamp
            self.recovery_states[agent_id].state_hash = state_hash
            self.recovery_states[agent_id].recovery_status = "healthy"
        
        return checkpoint
    
    def recover_agent(
        self,
        agent_id: str,
        recovery_callback: Optional[Callable] = None
    ) -> bool:
        """
        Recover an agent after a crash.
        
        Args:
            agent_id: ID of the agent to recover
            recovery_callback: Optional callback function for recovery
            
        Returns:
            True if recovery was successful, False otherwise
        """
        # Get recovery state
        recovery_state = self.recovery_states.get(agent_id)
        if not recovery_state:
            return False
        
        # Check if recovery is needed
        if recovery_state.recovery_status == "healthy":
            return True
        
        # Check recovery attempts
        if recovery_state.recovery_attempts >= self.max_recovery_attempts:
            recovery_state.recovery_status = "failed"
            recovery_state.recovery_log.append("Max recovery attempts reached")
            return False
        
        # Increment recovery attempts
        recovery_state.recovery_attempts += 1
        recovery_state.last_recovery_attempt = datetime.utcnow()
        
        # Get latest checkpoint
        latest_checkpoint = self._get_latest_checkpoint(agent_id)
        if not latest_checkpoint:
            recovery_state.recovery_log.append("No checkpoint found")
            return False
        
        # Validate checkpoint
        if not self._validate_checkpoint(latest_checkpoint):
            recovery_state.recovery_log.append("Checkpoint validation failed")
            return False
        
        # Restore state
        try:
            if recovery_callback:
                recovery_callback(latest_checkpoint.state_data)
            
            recovery_state.recovery_status = "recovered"
            recovery_state.recovery_log.append("Recovery successful")
            return True
        except Exception as e:
            recovery_state.recovery_log.append(f"Recovery failed: {str(e)}")
            return False
    
    def register_recovery_callback(
        self,
        agent_id: str,
        callback: Callable
    ) -> None:
        """
        Register a recovery callback for an agent.
        
        Args:
            agent_id: ID of the agent
            callback: Callback function for recovery
        """
        self.recovery_callbacks[agent_id] = callback
    
    def get_recovery_status(self, agent_id: str) -> Optional[RecoveryState]:
        """
        Get the recovery status of an agent.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            RecoveryState object or None if not found
        """
        return self.recovery_states.get(agent_id)
    
    def get_all_recovery_statuses(self) -> Dict[str, RecoveryState]:
        """
        Get all recovery statuses.
        
        Returns:
            Dictionary of agent IDs to RecoveryState objects
        """
        return self.recovery_states.copy()
    
    def mark_agent_crashed(self, agent_id: str) -> None:
        """
        Mark an agent as crashed.
        
        Args:
            agent_id: ID of the agent
        """
        if agent_id in self.recovery_states:
            self.recovery_states[agent_id].recovery_status = "crashed"
            self.recovery_states[agent_id].recovery_log.append("Agent marked as crashed")
    
    def cleanup_old_checkpoints(self, max_age_seconds: int = 86400) -> int:
        """
        Clean up old checkpoints.
        
        Args:
            max_age_seconds: Maximum age of checkpoints to keep (default: 24 hours)
            
        Returns:
            Number of checkpoints removed
        """
        current_time = datetime.utcnow()
        removed_count = 0
        
        for checkpoint_id, checkpoint in list(self.checkpoints.items()):
            age = (current_time - checkpoint.timestamp).total_seconds()
            if age > max_age_seconds:
                # Remove from memory
                del self.checkpoints[checkpoint_id]
                
                # Remove from disk
                checkpoint_file = os.path.join(self.checkpoint_dir, f"{checkpoint_id}.json")
                if os.path.exists(checkpoint_file):
                    os.remove(checkpoint_file)
                
                removed_count += 1
        
        return removed_count
    
    def _get_latest_checkpoint(self, agent_id: str) -> Optional[Checkpoint]:
        """Get the latest checkpoint for an agent."""
        agent_checkpoints = [
            cp for cp in self.checkpoints.values()
            if cp.agent_id == agent_id
        ]
        
        if not agent_checkpoints:
            return None
        
        return max(agent_checkpoints, key=lambda cp: cp.timestamp)
    
    def _validate_checkpoint(self, checkpoint: Checkpoint) -> bool:
        """Validate a checkpoint."""
        # Compute hash of state data
        computed_hash = checkpoint.compute_hash()
        
        # Compare with stored hash
        return computed_hash == checkpoint.state_hash
    
    def _save_checkpoint(self, checkpoint: Checkpoint) -> None:
        """Save checkpoint to disk."""
        checkpoint_file = os.path.join(self.checkpoint_dir, f"{checkpoint.checkpoint_id}.json")
        with open(checkpoint_file, 'w') as f:
            json.dump(checkpoint.to_dict(), f, indent=2)
    
    def _load_checkpoints(self) -> None:
        """Load checkpoints from disk."""
        if not os.path.exists(self.checkpoint_dir):
            return
        
        for filename in os.listdir(self.checkpoint_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.checkpoint_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                    checkpoint = Checkpoint.from_dict(data)
                    self.checkpoints[checkpoint.checkpoint_id] = checkpoint
                except Exception as e:
                    print(f"Failed to load checkpoint {filename}: {e}")


class AutoRecovery:
    """
    Automatic recovery system for CLE-Net agents.
    
    This class provides automatic recovery after crashes with:
    - Periodic checkpointing
    - Crash detection
    - Automatic recovery
    - Recovery monitoring
    """
    
    def __init__(self, recovery_manager: RecoveryManager):
        """Initialize the auto recovery system."""
        self.recovery_manager = recovery_manager
        self.running = False
        self.agent_heartbeats: Dict[str, float] = {}
        self.heartbeat_timeout = 120  # 2 minutes
    
    def start(self) -> None:
        """Start the auto recovery system."""
        self.running = True
    
    def stop(self) -> None:
        """Stop the auto recovery system."""
        self.running = False
    
    def update_heartbeat(self, agent_id: str) -> None:
        """
        Update heartbeat for an agent.
        
        Args:
            agent_id: ID of the agent
        """
        self.agent_heartbeats[agent_id] = time.time()
    
    def check_crashes(self) -> List[str]:
        """
        Check for crashed agents.
        
        Returns:
            List of crashed agent IDs
        """
        crashed_agents = []
        current_time = time.time()
        
        for agent_id, last_heartbeat in self.agent_heartbeats.items():
            if current_time - last_heartbeat > self.heartbeat_timeout:
                crashed_agents.append(agent_id)
                self.recovery_manager.mark_agent_crashed(agent_id)
        
        return crashed_agents
    
    def recover_crashed_agents(self) -> Dict[str, bool]:
        """
        Recover all crashed agents.
        
        Returns:
            Dictionary of agent IDs to recovery success status
        """
        crashed_agents = self.check_crashes()
        recovery_results = {}
        
        for agent_id in crashed_agents:
            callback = self.recovery_manager.recovery_callbacks.get(agent_id)
            success = self.recovery_manager.recover_agent(agent_id, callback)
            recovery_results[agent_id] = success
        
        return recovery_results
