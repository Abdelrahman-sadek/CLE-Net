"""
CLE-Net Network Partition Handling Module

This module provides network partition handling for CLE-Net.
It ensures that the network can handle network partitions and recover from them.
"""

from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime
import time


class Partition:
    """Represents a network partition."""
    
    def __init__(
        self,
        partition_id: str,
        nodes: Set[str],
        start_time: datetime
    ):
        self.partition_id = partition_id
        self.nodes = nodes
        self.start_time = start_time
        self.end_time: Optional[datetime] = None
        self.is_active = True
        self.recovered = False
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "partition_id": self.partition_id,
            "nodes": list(self.nodes),
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "is_active": self.is_active,
            "recovered": self.recovered
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Partition":
        """Create from dictionary."""
        partition = cls(
            partition_id=data["partition_id"],
            nodes=set(data["nodes"]),
            start_time=datetime.fromisoformat(data["start_time"])
        )
        partition.end_time = datetime.fromisoformat(data["end_time"]) if data["end_time"] else None
        partition.is_active = data["is_active"]
        partition.recovered = data["recovered"]
        return partition
    
    def get_duration(self) -> float:
        """Get the duration of the partition in seconds."""
        end_time = self.end_time if self.end_time else datetime.utcnow()
        return (end_time - self.start_time).total_seconds()


class PartitionDetector:
    """
    Detects network partitions.
    
    This class provides:
    - Partition detection based on connectivity
    - Partition identification
    - Partition monitoring
    """
    
    def __init__(self, partition_timeout: int = 60):
        """
        Initialize the partition detector.
        
        Args:
            partition_timeout: Timeout in seconds before considering a node partitioned
        """
        self.partition_timeout = partition_timeout
        self.node_connectivity: Dict[str, Dict[str, float]] = {}  # node_id -> {peer_id -> last_seen}
        self.last_check = datetime.utcnow()
    
    def update_connectivity(self, node_id: str, peer_id: str) -> None:
        """
        Update connectivity between nodes.
        
        Args:
            node_id: ID of the node
            peer_id: ID of the peer node
        """
        if node_id not in self.node_connectivity:
            self.node_connectivity[node_id] = {}
        
        self.node_connectivity[node_id][peer_id] = time.time()
    
    def detect_partitions(self, all_nodes: Set[str]) -> List[Set[str]]:
        """
        Detect network partitions.
        
        Args:
            all_nodes: Set of all node IDs
            
        Returns:
            List of partitions (each partition is a set of node IDs)
        """
        current_time = time.time()
        partitions = []
        visited = set()
        
        for node_id in all_nodes:
            if node_id in visited:
                continue
            
            # Find connected component
            component = self._find_connected_component(node_id, all_nodes, current_time)
            partitions.append(component)
            visited.update(component)
        
        # Filter out single-node partitions (not really partitions)
        partitions = [p for p in partitions if len(p) > 1]
        
        return partitions
    
    def _find_connected_component(
        self,
        start_node: str,
        all_nodes: Set[str],
        current_time: float
    ) -> Set[str]:
        """
        Find the connected component containing a node.
        
        Args:
            start_node: Starting node ID
            all_nodes: Set of all node IDs
            current_time: Current timestamp
            
        Returns:
            Set of node IDs in the connected component
        """
        component = set()
        queue = [start_node]
        
        while queue:
            node_id = queue.pop(0)
            if node_id in component:
                continue
            
            component.add(node_id)
            
            # Get connected peers
            if node_id in self.node_connectivity:
                for peer_id, last_seen in self.node_connectivity[node_id].items():
                    # Check if peer is still connected
                    if current_time - last_seen < self.partition_timeout:
                        if peer_id not in component:
                            queue.append(peer_id)
        
        return component
    
    def get_partitioned_nodes(self, all_nodes: Set[str]) -> Set[str]:
        """
        Get nodes that are partitioned from the majority.
        
        Args:
            all_nodes: Set of all node IDs
            
        Returns:
            Set of partitioned node IDs
        """
        partitions = self.detect_partitions(all_nodes)
        
        if not partitions:
            return set()
        
        # Find the largest partition (the majority)
        largest_partition = max(partitions, key=len)
        
        # All nodes not in the largest partition are partitioned
        partitioned_nodes = all_nodes - largest_partition
        
        return partitioned_nodes


class PartitionRecovery:
    """
    Handles recovery from network partitions.
    
    This class provides:
    - Partition recovery strategies
    - State synchronization after recovery
    - Conflict resolution after partition
    """
    
    def __init__(self):
        """Initialize the partition recovery."""
        self.recovery_strategies = {
            "merge": self._merge_strategy,
            "majority": self._majority_strategy,
            "latest": self._latest_strategy
        }
    
    def recover_partition(
        self,
        partition: Partition,
        strategy: str = "merge"
    ) -> bool:
        """
        Recover from a network partition.
        
        Args:
            partition: Partition to recover
            strategy: Recovery strategy (merge, majority, latest)
            
        Returns:
            True if recovery was successful, False otherwise
        """
        if strategy not in self.recovery_strategies:
            return False
        
        # Execute recovery strategy
        success = self.recovery_strategies[strategy](partition)
        
        if success:
            partition.recovered = True
            partition.end_time = datetime.utcnow()
            partition.is_active = False
        
        return success
    
    def _merge_strategy(self, partition: Partition) -> bool:
        """
        Merge strategy: merge states from all partitions.
        
        Args:
            partition: Partition to recover
            
        Returns:
            True if recovery was successful
        """
        # In a real implementation, this would merge states from all partitions
        # For now, we just mark the partition as recovered
        return True
    
    def _majority_strategy(self, partition: Partition) -> bool:
        """
        Majority strategy: use state from majority partition.
        
        Args:
            partition: Partition to recover
            
        Returns:
            True if recovery was successful
        """
        # In a real implementation, this would use state from majority partition
        # For now, we just mark the partition as recovered
        return True
    
    def _latest_strategy(self, partition: Partition) -> bool:
        """
        Latest strategy: use state from latest partition.
        
        Args:
            partition: Partition to recover
            
        Returns:
            True if recovery was successful
        """
        # In a real implementation, this would use state from latest partition
        # For now, we just mark the partition as recovered
        return True


class PartitionHandler:
    """
    Handles network partitions for CLE-Net.
    
    This class provides:
    - Partition detection
    - Partition monitoring
    - Partition recovery
    - State synchronization after recovery
    """
    
    def __init__(self, partition_timeout: int = 60):
        """
        Initialize the partition handler.
        
        Args:
            partition_timeout: Timeout in seconds before considering a node partitioned
        """
        self.detector = PartitionDetector(partition_timeout)
        self.recovery = PartitionRecovery()
        self.partitions: Dict[str, Partition] = {}
        self.active_partitions: Set[str] = set()
        self.recovered_partitions: Set[str] = set()
        self.running = False
    
    def start(self) -> None:
        """Start the partition handler."""
        self.running = True
    
    def stop(self) -> None:
        """Stop the partition handler."""
        self.running = False
    
    def update_connectivity(self, node_id: str, peer_id: str) -> None:
        """
        Update connectivity between nodes.
        
        Args:
            node_id: ID of the node
            peer_id: ID of the peer node
        """
        self.detector.update_connectivity(node_id, peer_id)
    
    def check_partitions(self, all_nodes: Set[str]) -> List[Partition]:
        """
        Check for network partitions.
        
        Args:
            all_nodes: Set of all node IDs
            
        Returns:
            List of active partitions
        """
        if not self.running:
            return []
        
        # Detect partitions
        partition_sets = self.detector.detect_partitions(all_nodes)
        
        # Create partition objects
        active_partitions = []
        for i, nodes in enumerate(partition_sets):
            partition_id = f"partition_{int(time.time())}_{i}"
            
            # Check if partition already exists
            if partition_id not in self.partitions:
                partition = Partition(
                    partition_id=partition_id,
                    nodes=nodes,
                    start_time=datetime.utcnow()
                )
                self.partitions[partition_id] = partition
                self.active_partitions.add(partition_id)
            
            active_partitions.append(self.partitions[partition_id])
        
        return active_partitions
    
    def recover_partition(
        self,
        partition_id: str,
        strategy: str = "merge"
    ) -> bool:
        """
        Recover from a network partition.
        
        Args:
            partition_id: ID of the partition to recover
            strategy: Recovery strategy (merge, majority, latest)
            
        Returns:
            True if recovery was successful, False otherwise
        """
        if partition_id not in self.partitions:
            return False
        
        partition = self.partitions[partition_id]
        
        # Recover partition
        success = self.recovery.recover_partition(partition, strategy)
        
        if success:
            self.active_partitions.discard(partition_id)
            self.recovered_partitions.add(partition_id)
        
        return success
    
    def recover_all_partitions(self, strategy: str = "merge") -> Dict[str, bool]:
        """
        Recover all active partitions.
        
        Args:
            strategy: Recovery strategy (merge, majority, latest)
            
        Returns:
            Dictionary of partition IDs to recovery success status
        """
        recovery_results = {}
        
        for partition_id in list(self.active_partitions):
            success = self.recover_partition(partition_id, strategy)
            recovery_results[partition_id] = success
        
        return recovery_results
    
    def get_active_partitions(self) -> List[Partition]:
        """
        Get all active partitions.
        
        Returns:
            List of active partitions
        """
        return [
            self.partitions[partition_id]
            for partition_id in self.active_partitions
        ]
    
    def get_recovered_partitions(self) -> List[Partition]:
        """
        Get all recovered partitions.
        
        Returns:
            List of recovered partitions
        """
        return [
            self.partitions[partition_id]
            for partition_id in self.recovered_partitions
        ]
    
    def get_partition_statistics(self) -> Dict:
        """
        Get partition statistics.
        
        Returns:
            Dictionary with partition statistics
        """
        active_partitions = self.get_active_partitions()
        recovered_partitions = self.get_recovered_partitions()
        
        total_duration = sum(
            partition.get_duration()
            for partition in recovered_partitions
        )
        
        avg_duration = (
            total_duration / len(recovered_partitions)
            if recovered_partitions
            else 0
        )
        
        return {
            "active_partitions": len(active_partitions),
            "recovered_partitions": len(recovered_partitions),
            "total_partitions": len(self.partitions),
            "total_duration": total_duration,
            "average_duration": avg_duration,
            "running": self.running
        }
    
    def cleanup_old_partitions(self, max_age_seconds: int = 86400) -> int:
        """
        Clean up old recovered partitions.
        
        Args:
            max_age_seconds: Maximum age of partitions to keep (default: 24 hours)
            
        Returns:
            Number of partitions removed
        """
        current_time = datetime.utcnow()
        removed_count = 0
        
        for partition_id in list(self.recovered_partitions):
            partition = self.partitions[partition_id]
            
            if partition.end_time:
                age = (current_time - partition.end_time).total_seconds()
                if age > max_age_seconds:
                    # Remove from memory
                    del self.partitions[partition_id]
                    self.recovered_partitions.discard(partition_id)
                    removed_count += 1
        
        return removed_count
