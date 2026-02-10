"""
CLE-Net Genesis File

This module provides the genesis configuration for CLE-Net's Cosmos SDK integration.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import json
from datetime import datetime


@dataclass
class GenesisAccount:
    """Represents a genesis account."""
    address: str
    balance: str
    vesting: Optional[Dict] = None


@dataclass
class GenesisValidator:
    """Represents a genesis validator."""
    address: str
    pub_key: str
    power: int
    name: str


@dataclass
class GenesisAppState:
    """Represents the genesis application state."""
    cognitive: Dict
    laws: Dict
    consensus: Dict


@dataclass
class GenesisFile:
    """
    Represents the complete genesis file for CLE-Net.
    
    This file contains all the initial state and configuration for the blockchain.
    """
    chain_id: str
    genesis_time: str
    initial_height: int
    accounts: List[GenesisAccount]
    validators: List[GenesisValidator]
    app_state: GenesisAppState
    consensus_params: Dict
    staking_params: Dict
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "chain_id": self.chain_id,
            "genesis_time": self.genesis_time,
            "initial_height": self.initial_height,
            "accounts": [asdict(account) for account in self.accounts],
            "validators": [asdict(validator) for validator in self.validators],
            "app_state": asdict(self.app_state),
            "consensus_params": self.consensus_params,
            "staking_params": self.staking_params
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)
    
    def save(self, filepath: str) -> None:
        """Save genesis file to disk."""
        with open(filepath, 'w') as f:
            f.write(self.to_json())
    
    @classmethod
    def from_dict(cls, data: Dict) -> "GenesisFile":
        """Create from dictionary."""
        return cls(
            chain_id=data["chain_id"],
            genesis_time=data["genesis_time"],
            initial_height=data["initial_height"],
            accounts=[GenesisAccount(**account) for account in data["accounts"]],
            validators=[GenesisValidator(**validator) for validator in data["validators"]],
            app_state=GenesisAppState(**data["app_state"]),
            consensus_params=data["consensus_params"],
            staking_params=data["staking_params"]
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> "GenesisFile":
        """Create from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    @classmethod
    def load(cls, filepath: str) -> "GenesisFile":
        """Load genesis file from disk."""
        with open(filepath, 'r') as f:
            return cls.from_json(f.read())


def create_testnet_genesis() -> GenesisFile:
    """
    Create a testnet genesis file.
    
    Returns:
        GenesisFile configured for testnet
    """
    return GenesisFile(
        chain_id="cle-net-testnet-1",
        genesis_time=datetime.utcnow().isoformat() + "Z",
        initial_height=1,
        accounts=[
            GenesisAccount(
                address="cle1xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                balance="1000000000000ucle"
            ),
            GenesisAccount(
                address="cle1yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy",
                balance="1000000000000ucle"
            ),
        ],
        validators=[
            GenesisValidator(
                address="cle1xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                pub_key="clepub1xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                power=100,
                name="validator1"
            ),
            GenesisValidator(
                address="cle1yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy",
                pub_key="clepub1yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy",
                power=100,
                name="validator2"
            ),
        ],
        app_state=GenesisAppState(
            cognitive={
                "params": {
                    "max_laws_per_block": 100,
                    "validation_threshold": 0.67,
                    "decay_rate": 0.01
                },
                "laws": [],
                "ccs_scores": {}
            },
            laws={
                "params": {
                    "max_laws_per_context": 100,
                    "min_confidence": 0.5
                },
                "laws": [],
                "indexes": {}
            },
            consensus={
                "params": {
                    "min_stake": 1000,
                    "slashing_threshold": 0.5,
                    "proposer_rotation_interval": 1
                },
                "validators": [],
                "proposer_queue": []
            }
        ),
        consensus_params={
            "block": {
                "max_bytes": "1048576",
                "max_gas": "1000000",
                "time_iota_ms": "1000"
            },
            "evidence": {
                "max_age_num_blocks": 100000,
                "max_age_duration": "172800000000000"
            },
            "validator": {
                "pub_key_types": ["ed25519"],
                "max_validators": 100
            }
        },
        staking_params={
            "bond_denom": "ucle",
            "min_commission_rate": "0.05",
            "max_validators": 100,
            "unbonding_time": "1814400000000000"
        }
    )


def create_mainnet_genesis() -> GenesisFile:
    """
    Create a mainnet genesis file.
    
    Returns:
        GenesisFile configured for mainnet
    """
    return GenesisFile(
        chain_id="cle-net-1",
        genesis_time=datetime.utcnow().isoformat() + "Z",
        initial_height=1,
        accounts=[
            GenesisAccount(
                address="cle1xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                balance="1000000000000000ucle"
            ),
        ],
        validators=[
            GenesisValidator(
                address="cle1xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                pub_key="clepub1xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                power=1000,
                name="genesis-validator"
            ),
        ],
        app_state=GenesisAppState(
            cognitive={
                "params": {
                    "max_laws_per_block": 100,
                    "validation_threshold": 0.67,
                    "decay_rate": 0.01
                },
                "laws": [],
                "ccs_scores": {}
            },
            laws={
                "params": {
                    "max_laws_per_context": 100,
                    "min_confidence": 0.5
                },
                "laws": [],
                "indexes": {}
            },
            consensus={
                "params": {
                    "min_stake": 10000,
                    "slashing_threshold": 0.5,
                    "proposer_rotation_interval": 1
                },
                "validators": [],
                "proposer_queue": []
            }
        ),
        consensus_params={
            "block": {
                "max_bytes": "1048576",
                "max_gas": "1000000",
                "time_iota_ms": "1000"
            },
            "evidence": {
                "max_age_num_blocks": 100000,
                "max_age_duration": "172800000000000"
            },
            "validator": {
                "pub_key_types": ["ed25519"],
                "max_validators": 100
            }
        },
        staking_params={
            "bond_denom": "ucle",
            "min_commission_rate": "0.05",
            "max_validators": 100,
            "unbonding_time": "1814400000000000"
        }
    )


def generate_genesis_file(network: str = "testnet", output_path: str = "genesis.json") -> None:
    """
    Generate a genesis file for the specified network.
    
    Args:
        network: Network type ("testnet" or "mainnet")
        output_path: Path to save the genesis file
    """
    if network == "testnet":
        genesis = create_testnet_genesis()
    elif network == "mainnet":
        genesis = create_mainnet_genesis()
    else:
        raise ValueError(f"Unknown network: {network}")
    
    genesis.save(output_path)
    print(f"Genesis file generated for {network}: {output_path}")
