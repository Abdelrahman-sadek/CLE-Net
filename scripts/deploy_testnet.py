#!/usr/bin/env python3
"""
CLE-Net Testnet Deployment Script

This script deploys a CLE-Net testnet with the following components:
- Cosmos SDK application
- Tendermint BFT consensus
- Initial validator set
- Genesis configuration
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.cosmos.app.app import CLENetApp, AppConfig
from core.cosmos.app.genesis import GenesisFile, GenesisAccount, GenesisValidator, GenesisAppState
from core.cosmos.tendermint import TendermintBFT
from core.cosmos.state_machine import CognitiveStateMachine, LawState, CCSState, ValidatorState


class TestnetDeployment:
    """Testnet deployment manager."""
    
    def __init__(self, config_path: str = "config/testnet.toml"):
        """
        Initialize the testnet deployment.
        
        Args:
            config_path: Path to the testnet configuration file
        """
        self.config_path = config_path
        self.config = self._load_config()
        self.app: Optional[CLENetApp] = None
        self.tendermint: Optional[TendermintBFT] = None
        self.state_machine: Optional[CognitiveStateMachine] = None
    
    def _load_config(self) -> Dict:
        """
        Load the testnet configuration.
        
        Returns:
            Configuration dictionary
        """
        config_file = Path(self.config_path)
        
        if not config_file.exists():
            # Create default configuration
            default_config = {
                "chain_id": "clenet-testnet-1",
                "genesis_time": datetime.utcnow().isoformat(),
                "initial_height": 1,
                "block_time": 5.0,
                "validators": [
                    {
                        "address": "validator1",
                        "stake": 1000000,
                        "role": "cognitive_miner"
                    },
                    {
                        "address": "validator2",
                        "stake": 1000000,
                        "role": "state_validator"
                    },
                    {
                        "address": "validator3",
                        "stake": 1000000,
                        "role": "conflict_resolver"
                    },
                    {
                        "address": "validator4",
                        "stake": 1000000,
                        "role": "watchdog"
                    }
                ],
                "accounts": [
                    {
                        "address": "user1",
                        "balance": 1000000
                    },
                    {
                        "address": "user2",
                        "balance": 1000000
                    }
                ],
                "consensus_params": {
                    "block": {
                        "max_bytes": 22020096,
                        "max_gas": -1,
                        "time_iota_ms": 1000
                    },
                    "evidence": {
                        "max_age_num_blocks": 100000,
                        "max_age_duration": "172800000000000"
                    },
                    "validator": {
                        "pub_key_types": ["ed25519"]
                    }
                },
                "staking_params": {
                    "unbonding_time": "1814400000000000",
                    "max_validators": 100,
                    "max_entries": 7,
                    "historical_entries": 10000,
                    "bond_denom": "ucle"
                }
            }
            
            # Create config directory if it doesn't exist
            config_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Write default configuration
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            
            return default_config
        
        with open(config_file, 'r') as f:
            return json.load(f)
    
    def create_genesis_file(self) -> GenesisFile:
        """
        Create the genesis file for the testnet.
        
        Returns:
            Genesis file
        """
        # Create genesis accounts
        accounts = []
        for account_data in self.config.get("accounts", []):
            account = GenesisAccount(
                address=account_data["address"],
                balance=account_data["balance"]
            )
            accounts.append(account)
        
        # Create genesis validators
        validators = []
        for validator_data in self.config.get("validators", []):
            validator = GenesisValidator(
                address=validator_data["address"],
                stake=validator_data["stake"],
                role=validator_data["role"]
            )
            validators.append(validator)
        
        # Create app state
        app_state = GenesisAppState(
            laws={},
            ccs_scores={},
            validators={v.address: {"role": v.role, "stake": v.stake} for v in validators},
            conflicts={}
        )
        
        # Create genesis file
        genesis_file = GenesisFile(
            chain_id=self.config["chain_id"],
            genesis_time=self.config["genesis_time"],
            initial_height=self.config["initial_height"],
            accounts=accounts,
            validators=validators,
            app_state=app_state,
            consensus_params=self.config["consensus_params"],
            staking_params=self.config["staking_params"]
        )
        
        return genesis_file
    
    def initialize_app(self) -> CLENetApp:
        """
        Initialize the CLE-Net application.
        
        Returns:
            Initialized application
        """
        # Create app config
        app_config = AppConfig(
            chain_id=self.config["chain_id"],
            min_gas_prices="0.025ucle",
            block_time=self.config.get("block_time", 5.0)
        )
        
        # Create app
        self.app = CLENetApp(app_config)
        
        # Create genesis file
        genesis_file = self.create_genesis_file()
        
        # Initialize chain
        genesis_state = {
            "accounts": [acc.to_dict() for acc in genesis_file.accounts],
            "validators": [val.to_dict() for val in genesis_file.validators],
            "app_state": genesis_file.to_dict()["app_state"]
        }
        
        self.app.init_chain(genesis_state)
        
        return self.app
    
    def initialize_tendermint(self) -> TendermintBFT:
        """
        Initialize Tendermint BFT.
        
        Returns:
            Initialized Tendermint BFT instance
        """
        # Create Tendermint BFT
        self.tendermint = TendermintBFT(total_validators=len(self.config.get("validators", [])))
        
        # Add validators
        for validator_data in self.config.get("validators", []):
            self.tendermint.add_validator(validator_data["address"])
        
        # Start Tendermint
        self.tendermint.start()
        
        return self.tendermint
    
    def initialize_state_machine(self) -> CognitiveStateMachine:
        """
        Initialize the cognitive state machine.
        
        Returns:
            Initialized state machine
        """
        # Create state machine
        self.state_machine = CognitiveStateMachine()
        
        # Add validators to state machine
        for validator_data in self.config.get("validators", []):
            validator_state = ValidatorState(
                validator_address=validator_data["address"],
                role=validator_data["role"],
                stake=validator_data["stake"],
                uptime=100.0,
                laws_validated=0,
                conflicts_resolved=0,
                last_active=datetime.utcnow(),
                jailed=False
            )
            self.state_machine.validators[validator_data["address"]] = validator_state
        
        # Add accounts to state machine
        for account_data in self.config.get("accounts", []):
            ccs_state = CCSState(
                participant_id=account_data["address"],
                score=0.0,
                contributions_count=0,
                laws_discovered=0,
                conflicts_resolved=0,
                last_updated=datetime.utcnow()
            )
            self.state_machine.ccs_scores[account_data["address"]] = ccs_state
        
        return self.state_machine
    
    def deploy(self) -> bool:
        """
        Deploy the testnet.
        
        Returns:
            True if deployment was successful, False otherwise
        """
        print("=" * 60)
        print("CLE-Net Testnet Deployment")
        print("=" * 60)
        
        try:
            # Initialize application
            print("\n[1/4] Initializing CLE-Net application...")
            self.initialize_app()
            print("✓ Application initialized")
            
            # Initialize Tendermint
            print("\n[2/4] Initializing Tendermint BFT...")
            self.initialize_tendermint()
            print("✓ Tendermint BFT initialized")
            
            # Initialize state machine
            print("\n[3/4] Initializing cognitive state machine...")
            self.initialize_state_machine()
            print("✓ State machine initialized")
            
            # Save genesis file
            print("\n[4/4] Saving genesis file...")
            genesis_file = self.create_genesis_file()
            genesis_path = Path("data/testnet/genesis.json")
            genesis_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(genesis_path, 'w') as f:
                json.dump(genesis_file.to_dict(), f, indent=2)
            
            print(f"✓ Genesis file saved to {genesis_path}")
            
            # Print deployment summary
            print("\n" + "=" * 60)
            print("Deployment Summary")
            print("=" * 60)
            print(f"Chain ID: {self.config['chain_id']}")
            print(f"Initial Height: {self.config['initial_height']}")
            print(f"Block Time: {self.config.get('block_time', 5.0)}s")
            print(f"Validators: {len(self.config.get('validators', []))}")
            print(f"Accounts: {len(self.config.get('accounts', []))}")
            print(f"Genesis File: {genesis_path}")
            print("=" * 60)
            
            print("\n✓ Testnet deployed successfully!")
            print("\nTo start the testnet, run:")
            print("  python scripts/start_testnet.py")
            
            return True
            
        except Exception as e:
            print(f"\n✗ Deployment failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def cleanup(self) -> None:
        """Clean up resources."""
        if self.tendermint:
            self.tendermint.stop()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Deploy CLE-Net testnet")
    parser.add_argument(
        "--config",
        default="config/testnet.toml",
        help="Path to testnet configuration file"
    )
    
    args = parser.parse_args()
    
    # Create deployment
    deployment = TestnetDeployment(config_path=args.config)
    
    # Deploy testnet
    success = deployment.deploy()
    
    # Cleanup
    deployment.cleanup()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
