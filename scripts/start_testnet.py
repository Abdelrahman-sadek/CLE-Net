#!/usr/bin/env python3
"""
CLE-Net Testnet Start Script

This script starts a CLE-Net testnet node.
"""

import os
import sys
import json
import argparse
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.cosmos.app.app import CLENetApp, AppConfig
from core.cosmos.tendermint import TendermintBFT
from core.cosmos.state_machine import CognitiveStateMachine


class TestnetNode:
    """Testnet node manager."""
    
    def __init__(self, config_path: str = "config/testnet.toml"):
        """
        Initialize the testnet node.
        
        Args:
            config_path: Path to the testnet configuration file
        """
        self.config_path = config_path
        self.config = self._load_config()
        self.app: Optional[CLENetApp] = None
        self.tendermint: Optional[TendermintBFT] = None
        self.state_machine: Optional[CognitiveStateMachine] = None
        self.running = False
    
    def _load_config(self) -> dict:
        """
        Load the testnet configuration.
        
        Returns:
            Configuration dictionary
        """
        config_file = Path(self.config_path)
        
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
        
        with open(config_file, 'r') as f:
            return json.load(f)
    
    def load_genesis(self) -> dict:
        """
        Load the genesis file.
        
        Returns:
            Genesis state dictionary
        """
        genesis_path = Path("data/testnet/genesis.json")
        
        if not genesis_path.exists():
            raise FileNotFoundError(f"Genesis file not found: {genesis_path}")
        
        with open(genesis_path, 'r') as f:
            return json.load(f)
    
    def initialize(self) -> None:
        """Initialize the testnet node."""
        print("Initializing testnet node...")
        
        # Load genesis
        genesis = self.load_genesis()
        
        # Create app config
        app_config = AppConfig(
            chain_id=self.config["chain_id"],
            min_gas_prices="0.025ucle",
            block_time=self.config.get("block_time", 5.0)
        )
        
        # Create app
        self.app = CLENetApp(app_config)
        
        # Initialize chain
        genesis_state = {
            "accounts": genesis.get("accounts", []),
            "validators": genesis.get("validators", []),
            "app_state": genesis.get("app_state", {})
        }
        
        self.app.init_chain(genesis_state)
        
        # Create Tendermint BFT
        self.tendermint = TendermintBFT(total_validators=len(genesis.get("validators", [])))
        
        # Add validators
        for validator in genesis.get("validators", []):
            self.tendermint.add_validator(validator["address"])
        
        # Start Tendermint
        self.tendermint.start()
        
        # Create state machine
        self.state_machine = CognitiveStateMachine()
        
        # Import state from genesis
        app_state = genesis.get("app_state", {})
        
        # Import validators
        for validator_address, validator_data in app_state.get("validators", {}).items():
            from core.cosmos.state_machine import ValidatorState
            validator_state = ValidatorState(
                validator_address=validator_address,
                role=validator_data.get("role", "cognitive_miner"),
                stake=validator_data.get("stake", 0),
                uptime=100.0,
                laws_validated=0,
                conflicts_resolved=0,
                last_active=datetime.utcnow(),
                jailed=False
            )
            self.state_machine.validators[validator_address] = validator_state
        
        print("✓ Testnet node initialized")
    
    async def run(self) -> None:
        """Run the testnet node."""
        print("\nStarting testnet node...")
        self.running = True
        
        try:
            # Run consensus loop
            block_time = self.config.get("block_time", 5.0)
            await self.tendermint.run_consensus_loop(block_time=block_time)
        except KeyboardInterrupt:
            print("\nShutting down testnet node...")
        finally:
            self.stop()
    
    def stop(self) -> None:
        """Stop the testnet node."""
        self.running = False
        
        if self.tendermint:
            self.tendermint.stop()
        
        print("✓ Testnet node stopped")
    
    def get_status(self) -> dict:
        """
        Get the status of the testnet node.
        
        Returns:
            Status dictionary
        """
        status = {
            "running": self.running,
            "chain_id": self.config["chain_id"],
            "block_height": self.tendermint.current_block_height if self.tendermint else 0,
            "last_block_hash": self.tendermint.last_block_hash if self.tendermint else "",
            "validators": len(self.tendermint.validators) if self.tendermint else 0,
            "consensus_state": self.tendermint.get_consensus_state() if self.tendermint else {}
        }
        
        return status


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Start CLE-Net testnet node")
    parser.add_argument(
        "--config",
        default="config/testnet.toml",
        help="Path to testnet configuration file"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show node status and exit"
    )
    
    args = parser.parse_args()
    
    # Create node
    node = TestnetNode(config_path=args.config)
    
    try:
        # Initialize node
        node.initialize()
        
        # Show status if requested
        if args.status:
            status = node.get_status()
            print("\n" + "=" * 60)
            print("Testnet Node Status")
            print("=" * 60)
            print(f"Running: {status['running']}")
            print(f"Chain ID: {status['chain_id']}")
            print(f"Block Height: {status['block_height']}")
            print(f"Last Block Hash: {status['last_block_hash']}")
            print(f"Validators: {status['validators']}")
            print("=" * 60)
            return
        
        # Run node
        asyncio.run(node.run())
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
