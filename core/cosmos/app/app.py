"""
CLE-Net Cosmos SDK Application

This module provides the main application scaffolding for CLE-Net's Cosmos SDK integration.
It serves as the entry point for the CLE-Net blockchain application.
"""

from typing import Dict, List, Optional, Union
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
    min_gas_prices: str = "0.025ucle"
    block_time: float = 5.0


@dataclass
class Message:
    """Message for the CLE-Net application."""
    type: str
    sender: str
    data: Dict
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "type": self.type,
            "sender": self.sender,
            "data": self.data
        }


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
    
    def register_module(self, name: str, module: object) -> None:
        """
        Register a module with the application.
        
        Args:
            name: Module name
            module: Module instance
        """
        self.modules[name] = module
    
    def unregister_module(self, name: str) -> bool:
        """
        Unregister a module from the application.
        
        Args:
            name: Module name
            
        Returns:
            True if module was unregistered, False otherwise
        """
        if name in self.modules:
            del self.modules[name]
            return True
        return False
    
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
    
    def begin_block(self, block_header: Dict) -> Dict:
        """
        Begin processing a new block.
        
        Args:
            block_header: Block header information
            
        Returns:
            Block header information
        """
        self.block_height = block_header.get('height', 0)
        self.last_block_hash = block_header.get('hash', '')
        
        # Call begin_block on each module
        for module_name, module in self.modules.items():
            if hasattr(module, 'begin_block'):
                module.begin_block(block_header)
        
        return block_header
    
    def deliver_tx(self, tx: Union[Dict, Message]) -> Dict:
        """
        Deliver a transaction to the appropriate module.
        
        Args:
            tx: Transaction to deliver (Dict or Message object)
            
        Returns:
            Transaction result
        """
        # Keep track of original tx type
        is_message = isinstance(tx, Message)
        
        # Convert Message to Dict if needed
        if is_message:
            tx_dict = tx.to_dict()
        else:
            tx_dict = tx
        
        # Route transaction to appropriate module
        # Check for module field at top level, then in data
        module_name = tx_dict.get('module')
        if module_name is None:
            module_name = tx_dict.get('data', {}).get('module')
        
        # If no module specified, use the first registered module
        if module_name is None:
            if self.modules:
                module_name = list(self.modules.keys())[0]
            else:
                # No modules registered, return success
                return {'code': 0, 'log': 'Transaction accepted (no modules)', 'success': True}
        
        if module_name in self.modules:
            module = self.modules[module_name]
            # Check for deliver_tx method first, then handle_message
            if hasattr(module, 'deliver_tx'):
                result = module.deliver_tx(tx_dict)
                # Ensure result has success key
                if 'success' not in result:
                    result['success'] = result.get('code', 1) == 0
                return result
            elif hasattr(module, 'handle_message'):
                # Pass original Message object if available, otherwise pass dict
                if is_message:
                    result = module.handle_message(tx)
                else:
                    result = module.handle_message(tx_dict)
                # Ensure result has success key
                if 'success' not in result:
                    result['success'] = result.get('code', 1) == 0
                return result
        
        return {'code': 1, 'log': f'Unknown module: {module_name}', 'success': False}
    
    def end_block(self, block_header: Optional[Dict] = None) -> Dict:
        """
        End processing a block.
        
        Args:
            block_header: Optional block header information
            
        Returns:
            Validator updates with block height
        """
        validator_updates = {}
        
        # Call end_block on each module
        for module_name, module in self.modules.items():
            if hasattr(module, 'end_block'):
                updates = module.end_block(block_header)
                if updates:
                    validator_updates.update(updates)
        
        # Add block height to result
        validator_updates['height'] = self.block_height
        
        # Wrap validator_updates in a dict
        return {
            'validator_updates': validator_updates,
            'height': self.block_height
        }
    
    def commit(self) -> Dict:
        """
        Commit the current state.
        
        Returns:
            Dict with app hash and data
        """
        # Compute app hash from current state
        app_hash = self._compute_app_hash()
        
        return {
            "data": app_hash,
            "height": self.block_height
        }
    
    def query(self, module_name: str, path: str, data: Optional[Dict] = None) -> Dict:
        """
        Handle a query request.
        
        Args:
            module_name: Module to query
            path: Query path
            data: Optional query data
            
        Returns:
            Query response
        """
        if data is None:
            data = {}
        
        if module_name in self.modules:
            module = self.modules[module_name]
            if hasattr(module, 'query'):
                return module.query(path, data)
        
        return {'code': 1, 'log': f'Unknown module: {module_name}'}
    
    def get_state(self) -> Dict:
        """
        Get the current application state.
        
        Returns:
            Current application state
        """
        return self.state
    
    def export_state(self) -> Dict:
        """
        Export the current application state.
        
        Returns:
            Exported state with metadata
        """
        return {
            "chain_id": self.config.chain_id,
            "state": self.state,
            "block_height": self.block_height,
            "last_block_hash": self.last_block_hash,
            "modules": list(self.modules.keys())
        }
    
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
