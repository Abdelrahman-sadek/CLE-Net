"""
Watchdog Mechanisms for Network Health

Monitors network health and detects anomalies in CLE-Net.
"""

import asyncio
import time
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum


class AlertSeverity(Enum):
    """Severity levels for watchdog alerts."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Alert:
    """Watchdog alert."""
    alert_id: str
    severity: AlertSeverity
    component: str
    message: str
    timestamp: float
    metadata: Dict = field(default_factory=dict)


@dataclass
class WatchdogConfig:
    """Configuration for watchdog."""
    block_timeout: int = 300  # 5 minutes
    min_participation: float = 0.5  # 50% of nodes
    ccs_decay_threshold: float = 0.1  # 10% decay rate
    heartbeat_interval: int = 30  # 30 seconds
    alert_cooldown: int = 300  # 5 minutes


class Watchdog:
    """
    Monitors CLE-Net network health and detects anomalies.
    
    Responsibilities:
    - Detect stalled blocks
    - Monitor node participation
    - Detect CCS decay anomalies
    - Generate alerts for network issues
    """
    
    def __init__(self, config: WatchdogConfig = None):
        """
        Initialize watchdog.
        
        Args:
            config: Watchdog configuration
        """
        self.config = config or WatchdogConfig()
        self.alerts: List[Alert] = []
        self.alert_handlers: List[Callable] = []
        self.running = False
        
        # Monitoring state
        self.last_block_height: int = 0
        self.last_block_time: float = 0
        self.active_nodes: set = set()
        self.ccs_history: Dict[str, List[float]] = {}
        
        # Alert cooldowns
        self.alert_cooldowns: Dict[str, float] = {}
    
    async def start(self):
        """Start watchdog monitoring."""
        self.running = True
        self.last_block_time = time.time()
        
        # Start monitoring loops
        asyncio.create_task(self._monitor_blocks())
        asyncio.create_task(self._monitor_participation())
        asyncio.create_task(self._monitor_ccs_decay())
        asyncio.create_task(self._cleanup_alerts())
    
    async def stop(self):
        """Stop watchdog monitoring."""
        self.running = False
    
    def register_alert_handler(self, handler: Callable):
        """Register a handler for alerts."""
        self.alert_handlers.append(handler)
    
    def update_block_height(self, height: int):
        """Update the latest block height."""
        if height > self.last_block_height:
            self.last_block_height = height
            self.last_block_time = time.time()
    
    def update_active_nodes(self, nodes: set):
        """Update the set of active nodes."""
        self.active_nodes = nodes
    
    def update_ccs(self, node_id: str, ccs: float):
        """Update CCS value for a node."""
        if node_id not in self.ccs_history:
            self.ccs_history[node_id] = []
        self.ccs_history[node_id].append(ccs)
        
        # Keep only last 100 values
        if len(self.ccs_history[node_id]) > 100:
            self.ccs_history[node_id] = self.ccs_history[node_id][-100:]
    
    async def _monitor_blocks(self):
        """Monitor for stalled blocks."""
        while self.running:
            await asyncio.sleep(self.config.heartbeat_interval)
            
            # Check if blocks are stalled
            time_since_last_block = time.time() - self.last_block_time
            
            if time_since_last_block > self.config.block_timeout:
                self._create_alert(
                    severity=AlertSeverity.ERROR,
                    component="blockchain",
                    message=f"Blocks stalled for {time_since_last_block:.0f} seconds",
                    metadata={"stall_duration": time_since_last_block}
                )
    
    async def _monitor_participation(self):
        """Monitor node participation levels."""
        while self.running:
            await asyncio.sleep(self.config.heartbeat_interval)
            
            # Check participation level
            if len(self.active_nodes) > 0:
                # This is a simplified check
                # In production, compare against expected node count
                pass
    
    async def _monitor_ccs_decay(self):
        """Monitor CCS decay anomalies."""
        while self.running:
            await asyncio.sleep(self.config.heartbeat_interval)
            
            # Check for abnormal CCS decay
            for node_id, ccs_values in self.ccs_history.items():
                if len(ccs_values) < 10:
                    continue
                
                # Calculate decay rate
                recent = ccs_values[-5:]
                older = ccs_values[-10:-5]
                
                if older:
                    avg_recent = sum(recent) / len(recent)
                    avg_older = sum(older) / len(older)
                    
                    decay_rate = (avg_older - avg_recent) / avg_older if avg_older > 0 else 0
                    
                    if decay_rate > self.config.ccs_decay_threshold:
                        self._create_alert(
                            severity=AlertSeverity.WARNING,
                            component="ccs",
                            message=f"Abnormal CCS decay detected for node {node_id}",
                            metadata={
                                "node_id": node_id,
                                "decay_rate": decay_rate,
                                "recent_ccs": avg_recent,
                                "older_ccs": avg_older
                            }
                        )
    
    async def _cleanup_alerts(self):
        """Clean up old alerts."""
        while self.running:
            await asyncio.sleep(60)  # Every minute
            
            # Remove alerts older than 1 hour
            current_time = time.time()
            self.alerts = [
                alert for alert in self.alerts
                if current_time - alert.timestamp < 3600
            ]
            
            # Clean up cooldowns
            self.alert_cooldowns = {
                key: expiry for key, expiry in self.alert_cooldowns.items()
                if expiry > current_time
            }
    
    def _create_alert(self, severity: AlertSeverity, component: str, 
                     message: str, metadata: Dict = None):
        """Create and process an alert."""
        # Check cooldown
        alert_key = f"{component}:{message}"
        if alert_key in self.alert_cooldowns:
            if time.time() < self.alert_cooldowns[alert_key]:
                return
        
        # Create alert
        alert = Alert(
            alert_id=f"alert_{int(time.time())}",
            severity=severity,
            component=component,
            message=message,
            timestamp=time.time(),
            metadata=metadata or {}
        )
        
        self.alerts.append(alert)
        
        # Set cooldown
        self.alert_cooldowns[alert_key] = time.time() + self.config.alert_cooldown
        
        # Notify handlers
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                print(f"Error in alert handler: {e}")
    
    def get_alerts(self, severity: AlertSeverity = None, 
                   component: str = None) -> List[Alert]:
        """
        Get alerts with optional filtering.
        
        Args:
            severity: Filter by severity
            component: Filter by component
            
        Returns:
            List of matching alerts
        """
        alerts = self.alerts
        
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        
        if component:
            alerts = [a for a in alerts if a.component == component]
        
        return alerts
    
    def get_status(self) -> Dict:
        """
        Get watchdog status.
        
        Returns:
            Status dictionary
        """
        return {
            "running": self.running,
            "last_block_height": self.last_block_height,
            "last_block_time": self.last_block_time,
            "active_nodes": len(self.active_nodes),
            "total_alerts": len(self.alerts),
            "critical_alerts": len([a for a in self.alerts if a.severity == AlertSeverity.CRITICAL]),
            "error_alerts": len([a for a in self.alerts if a.severity == AlertSeverity.ERROR]),
            "warning_alerts": len([a for a in self.alerts if a.severity == AlertSeverity.WARNING])
        }


class HealthChecker:
    """
    Performs health checks on CLE-Net components.
    """
    
    def __init__(self):
        """Initialize health checker."""
        self.checks: Dict[str, Callable] = {}
    
    def register_check(self, name: str, check_func: Callable):
        """Register a health check."""
        self.checks[name] = check_func
    
    async def run_all_checks(self) -> Dict[str, bool]:
        """
        Run all registered health checks.
        
        Returns:
            Dictionary of check names and their results
        """
        results = {}
        
        for name, check_func in self.checks.items():
            try:
                result = await check_func()
                results[name] = result
            except Exception as e:
                print(f"Health check {name} failed: {e}")
                results[name] = False
        
        return results
    
    async def check_blockchain_liveness(self) -> bool:
        """Check if blockchain is producing blocks."""
        # Placeholder implementation
        return True
    
    async def check_network_connectivity(self) -> bool:
        """Check network connectivity."""
        # Placeholder implementation
        return True
    
    async def check_consensus_progress(self) -> bool:
        """Check if consensus is making progress."""
        # Placeholder implementation
        return True
