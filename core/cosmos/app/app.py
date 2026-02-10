"""
CLE-Net Cosmos SDK Application

This module provides the main application scaffolding for CLE-Net's Cosmos SDK integration.
It serves as the entry point for the CLE-Net blockchain application.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
import json
import hashlib


@dataclass
class ModuleConfig:
    """Configuration for a Cosmos SDK module."""
    name: str
    version: str
    enabled: bool = True


@dataclass
class AppConfig:
    """Configuration for the CLE-Net Cosmos SDK application."""
    chain_id: str
    app_name: str
    app_version: str
    modules: List[ModuleConfig]
    genesis_time: str
    consensus_params: Dict
    staking_params: Dict


class CLENetApp:
    """
    CLE-Net Cosmos SDK Application.
    
    This class provides the main application scaffolding for CLE-Net's
    Cosmos SDK integration, including module registration, state management,
    and message handling.
    """
    
    def __init__(self, config: AppConfig):
        """
        Initialize the CLE-Net application.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.modules: Dict[str, object] = {}
        self.state: Dict = {}
        self.block_height: int = 0
        self.last_block_hash: str = ""
        
        # Register modules
        self._register_modules()
    
    def _register_modules(self) -> None:
        """Register all configured modules."""
        for module_config in self.config.modules:
            if module_config.enabled:
                self._register_module(module_config)
    
    def _register_module(self, module_config: ModuleConfig) -> None:
        """
        Register a single module.
        
        Args:
            module_config: Module configuration
        """
        # Import module based on name
        if module_config.name == "cognitive":
            from ..x.cognitive import CognitiveModule
            self.modules[module_config.name] = CognitiveModule()
        elif module_config.name == "laws":
            from ..x.laws import LawsModule
            self.modules[module_config.name] = LawsModule()
        elif module_config.name == "consensus":
            from ..x.consensus import ConsensusModule
            self.modules[module_config.name] = ConsensusModule()
        else:
            print(f"Warning: Unknown module {module_config.name}")
    
    def init_chain(self, genesis_state: Dict) -> Dict:
        """
        Initialize the chain with genesis state.
        
        Args:
            genesis_state: Initial genesis state
            
        Returns:
            Initial application state
        """
        # Initialize each module
        for module_name, module in self.modules.items():
            if hasattr(module, 'init_genesis'):
                module_state = module.init_genesis(genesis_state.get(module_name, {}))
                self.state[module_name] = module_state
        
        # Set initial block height
        self.block_height = 0
        self.last_block_hash = self._compute_genesis_hash(genesis_state)
        
        return self.state
    
    def begin_block(self, block_header: Dict) -> None:
        """
        Begin processing a new block.
        
        Args:
            block_header: Block header information
        """
        self.block_height = block_header.get('height', 0)
        self.last_block_hash = block_header.get('last_block_hash', '')
        
        # Call begin_block on each module
        for module_name, module in self.modules.items():
            if hasattr(module, 'begin_block'):
                module.begin_block(block_header)
    
    def deliver_tx(self, tx: Dict) -> Dict:
        """
        Deliver a transaction to the appropriate module.
        
        Args:
            tx: Transaction to deliver
            
        Returns:
            Transaction result
        """
        # Route transaction to appropriate module
        module_name = tx.get('module', 'cognitive')
        
        if module_name in self.modules:
            module = self.modules[module_name]
            if hasattr(module, 'deliver_tx'):
                return module.deliver_tx(tx)
        
        return {'code': 1, 'log': f'Unknown module: {module_name}'}
    
    def end_block(self, block_header: Dict) -> Dict:
        """
        End processing a block.
        
        Args:
            block_header: Block header information
            
        Returns:
            Validator updates
        """
        validator_updates = {}
        
        # Call end_block on each module
        for module_name, module in self.modules.items():
            if hasattr(module, 'end_block'):
                updates = module.end_block(block_header)
                if updates:
                    validator_updates.update(updates)
        
        return validator_updates
    
    def commit(self) -> str:
        """
        Commit the current state.
        
        Returns:
            App hash
        """
        # Compute app hash from current state
        app_hash = self._compute_app_hash()
        
        # Update block height
        self.block_height += 1
        
        return app_hash
    
    def query(self, request: Dict) -> Dict:
        """
        Handle a query request.
        
        Args:
            request: Query request
            
        Returns:
            Query response
        """
        # Route query to appropriate module
        module_name = request.get('module', 'cognitive')
        
        if module_name in self.modules:
            module = self.modules[module_name]
            if hasattr(module, 'query'):
                return module.query(request)
        
        return {'code': 1, 'log': f'Unknown module: {module_name}'}
    
    def _compute_genesis_hash(self, genesis_state: Dict) -> str:
        """Compute hash of genesis state."""
        state_str = json.dumps(genesis_state, sort_keys=True)
        return hashlib.sha256(state_str.encode()).hexdigest()
    
    def _compute_app_hash(self) -> str:
        """Compute app hash from current state."""
        state_str = json.dumps(self.state, sort_keys=True)
        return hashlib.sha256(state_str.encode()).hexdigest()


def create_default_config() -> AppConfig:
    """
    Create default application configuration.
    
    Returns:
        Default AppConfig
    """
    return AppConfig(
        chain_id="cle-net-1",
        app_name="cle-net",
        app_version="0.1.0",
        modules=[
            ModuleConfig(name="cognitive", version="0.1.0"),
            ModuleConfig(name="laws", version="0.1.0"),
            ModuleConfig(name="consensus", version="0.1.0"),
        ],
        genesis_time="2026-02-10T00:00:00Z",
        consensus_params={
            "block_time": "5s",
            "max_bytes": "1048576",
            "max_gas": "1000000",
        },
        staking_params={
            "bond_denom": "ucle",
            "min_commission_rate": "0.05",
            "max_validators": 100,
        }
    )


def create_app(config: Optional[AppConfig] = None) -> CLENetApp:
    """
    Create a new CLE-Net application.
    
    Args:
        config: Application configuration (uses default if not provided)
        
    Returns:
        CLENetApp instance
    """
    if config is None:
        config = create_default_config()
    
    return CLENetApp(config)
