"""
Integration tests for CLE-Net Cosmos SDK components.

This module tests the integration between different Cosmos SDK components.
"""

import unittest
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.cosmos.app.app import CLENetApp, AppConfig, Message
from core.cosmos.tendermint import TendermintBFT
from core.cosmos.state_machine import CognitiveStateMachine, LawState, CCSState, ValidatorState


class TestCosmosIntegration(unittest.TestCase):
    """Test cases for Cosmos SDK integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = AppConfig(
            chain_id="clenet-testnet-1",
            min_gas_prices="0.025ucle",
            block_time=5.0
        )
        self.app = CLENetApp(self.config)
        self.tendermint = TendermintBFT(total_validators=4)
        self.state_machine = CognitiveStateMachine()
    
    def test_app_tendermint_integration(self):
        """Test integration between app and Tendermint."""
        # Add validators to Tendermint
        for i in range(1, 5):
            self.tendermint.add_validator(f"validator{i}")
        
        # Initialize app
        genesis_state = {
            "accounts": [],
            "validators": [],
            "app_state": {}
        }
        self.app.init_chain(genesis_state)
        
        # Start Tendermint
        self.tendermint.start()
        
        # Propose block
        proposer = self.tendermint.get_current_proposer()
        block = self.tendermint.propose_block(proposer, [])
        
        # Begin block in app
        block_header = {
            "height": block.header.height,
            "hash": block.header.hash,
            "proposer": block.header.proposer_address,
            "timestamp": block.header.timestamp.isoformat()
        }
        self.app.begin_block(block_header)
        
        # Verify app state
        self.assertEqual(self.app.block_height, block.header.height)
        self.assertEqual(self.app.last_block_hash, block.header.hash)
        
        self.tendermint.stop()
    
    def test_app_state_machine_integration(self):
        """Test integration between app and state machine."""
        # Initialize app
        genesis_state = {
            "accounts": [],
            "validators": [],
            "app_state": {}
        }
        self.app.init_chain(genesis_state)
        
        # Create a law in state machine
        law = LawState(
            law_id="law_1",
            status="proposed",
            confidence=0.8,
            support_count=0,
            contradiction_count=0,
            decay_factor=0.95,
            context="customer_service",
            proposer_id="validator1",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        self.state_machine.laws["law_1"] = law
        
        # Transition law
        self.state_machine.transition_law("law_1", "validating")
        
        # Verify state
        self.assertEqual(self.state_machine.laws["law_1"].status, "validating")
        
        # Export state from state machine
        state_machine_state = self.state_machine.export_state()
        
        # Verify state can be imported
        new_state_machine = CognitiveStateMachine()
        self.assertTrue(new_state_machine.import_state(state_machine_state))
    
    def test_tendermint_state_machine_integration(self):
        """Test integration between Tendermint and state machine."""
        # Add validators to Tendermint
        for i in range(1, 5):
            self.tendermint.add_validator(f"validator{i}")
        
        # Create validators in state machine
        for i in range(1, 5):
            validator = ValidatorState(
                validator_address=f"validator{i}",
                role="cognitive_miner",
                stake=1000.0,
                uptime=100.0,
                laws_validated=0,
                conflicts_resolved=0,
                last_active=datetime.utcnow(),
                jailed=False
            )
            self.state_machine.validators[f"validator{i}"] = validator
        
        # Start Tendermint
        self.tendermint.start()
        
        # Propose and commit block
        proposer = self.tendermint.get_current_proposer()
        block = self.tendermint.propose_block(proposer, [])
        
        for validator in self.tendermint.validators:
            self.tendermint.vote_on_block(validator, block.header.hash, "prevote")
            self.tendermint.vote_on_block(validator, block.header.hash, "precommit")
        
        self.tendermint.commit_block(block)
        
        # Commit block in state machine
        self.state_machine.commit_block(
            block.header.height,
            block.header.hash
        )
        
        # Verify both are in sync
        self.assertEqual(self.tendermint.current_block_height, self.state_machine.current_block_height)
        self.assertEqual(self.tendermint.last_block_hash, self.state_machine.current_block_hash)
        
        self.tendermint.stop()
    
    def test_full_integration(self):
        """Test full integration between all components."""
        # Add validators to Tendermint
        for i in range(1, 5):
            self.tendermint.add_validator(f"validator{i}")
        
        # Create validators in state machine
        for i in range(1, 5):
            validator = ValidatorState(
                validator_address=f"validator{i}",
                role="cognitive_miner",
                stake=1000.0,
                uptime=100.0,
                laws_validated=0,
                conflicts_resolved=0,
                last_active=datetime.utcnow(),
                jailed=False
            )
            self.state_machine.validators[f"validator{i}"] = validator
        
        # Initialize app
        genesis_state = {
            "accounts": [],
            "validators": [],
            "app_state": {
                "validators": {
                    f"validator{i}": {"role": "cognitive_miner", "stake": 1000.0}
                    for i in range(1, 5)
                }
            }
        }
        self.app.init_chain(genesis_state)
        
        # Start Tendermint
        self.tendermint.start()
        
        # Propose and commit block
        proposer = self.tendermint.get_current_proposer()
        block = self.tendermint.propose_block(proposer, [])
        
        for validator in self.tendermint.validators:
            self.tendermint.vote_on_block(validator, block.header.hash, "prevote")
            self.tendermint.vote_on_block(validator, block.header.hash, "precommit")
        
        self.tendermint.commit_block(block)
        
        # Begin block in app
        block_header = {
            "height": block.header.height,
            "hash": block.header.hash,
            "proposer": block.header.proposer_address,
            "timestamp": block.header.timestamp.isoformat()
        }
        self.app.begin_block(block_header)
        
        # Commit block in state machine
        self.state_machine.commit_block(
            block.header.height,
            block.header.hash
        )
        
        # Verify all components are in sync
        self.assertEqual(self.app.block_height, block.header.height)
        self.assertEqual(self.app.last_block_hash, block.header.hash)
        self.assertEqual(self.tendermint.current_block_height, block.header.height)
        self.assertEqual(self.tendermint.last_block_hash, block.header.hash)
        self.assertEqual(self.state_machine.current_block_height, block.header.height)
        self.assertEqual(self.state_machine.current_block_hash, block.header.hash)
        
        # End and commit block in app
        self.app.end_block()
        self.app.commit()
        
        self.tendermint.stop()
    
    def test_law_proposal_workflow(self):
        """Test complete law proposal workflow."""
        # Add validators to Tendermint
        for i in range(1, 5):
            self.tendermint.add_validator(f"validator{i}")
        
        # Create validators in state machine
        for i in range(1, 5):
            validator = ValidatorState(
                validator_address=f"validator{i}",
                role="cognitive_miner",
                stake=1000.0,
                uptime=100.0,
                laws_validated=0,
                conflicts_resolved=0,
                last_active=datetime.utcnow(),
                jailed=False
            )
            self.state_machine.validators[f"validator{i}"] = validator
        
        # Initialize app
        genesis_state = {
            "accounts": [],
            "validators": [],
            "app_state": {}
        }
        self.app.init_chain(genesis_state)
        
        # Start Tendermint
        self.tendermint.start()
        
        # Propose a law
        law = LawState(
            law_id="law_1",
            status="proposed",
            confidence=0.8,
            support_count=0,
            contradiction_count=0,
            decay_factor=0.95,
            context="customer_service",
            proposer_id="validator1",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        self.state_machine.laws["law_1"] = law
        
        # Create a message for law proposal
        message = Message(
            type="propose_law",
            sender="validator1",
            data={
                "law_id": "law_1",
                "law_type": "symbolic_rule",
                "symbolic_expression": "IF user_requests_help THEN provide_assistance",
                "context": "customer_service",
                "confidence": 0.8
            }
        )
        
        # Deliver transaction
        result = self.app.deliver_tx(message)
        self.assertTrue(result["success"])
        
        # Transition law to validating
        self.state_machine.transition_law("law_1", "validating")
        
        # Update CCS for proposer
        self.state_machine.transition_ccs("validator1", 100, laws_discovered_delta=1)
        
        # Verify state
        self.assertEqual(self.state_machine.laws["law_1"].status, "validating")
        self.assertEqual(self.state_machine.ccs_scores["validator1"].score, 100.0)
        
        self.tendermint.stop()
    
    def test_multiple_blocks_workflow(self):
        """Test workflow with multiple blocks."""
        # Add validators to Tendermint
        for i in range(1, 5):
            self.tendermint.add_validator(f"validator{i}")
        
        # Initialize app
        genesis_state = {
            "accounts": [],
            "validators": [],
            "app_state": {}
        }
        self.app.init_chain(genesis_state)
        
        # Start Tendermint
        self.tendermint.start()
        
        # Commit multiple blocks
        for i in range(1, 4):
            proposer = self.tendermint.get_current_proposer()
            block = self.tendermint.propose_block(proposer, [])
            
            for validator in self.tendermint.validators:
                self.tendermint.vote_on_block(validator, block.header.hash, "prevote")
                self.tendermint.vote_on_block(validator, block.header.hash, "precommit")
            
            self.tendermint.commit_block(block)
            
            # Begin block in app
            block_header = {
                "height": block.header.height,
                "hash": block.header.hash,
                "proposer": block.header.proposer_address,
                "timestamp": block.header.timestamp.isoformat()
            }
            self.app.begin_block(block_header)
            
            # Commit block in state machine
            self.state_machine.commit_block(
                block.header.height,
                block.header.hash
            )
            
            # End and commit block in app
            self.app.end_block()
            self.app.commit()
        
        # Verify all blocks were committed
        self.assertEqual(self.tendermint.current_block_height, 3)
        self.assertEqual(self.app.block_height, 3)
        self.assertEqual(self.state_machine.current_block_height, 3)
        
        # Verify all blocks are accessible
        for i in range(1, 4):
            block = self.tendermint.get_block(i)
            self.assertIsNotNone(block)
            self.assertEqual(block.header.height, i)
        
        self.tendermint.stop()


if __name__ == "__main__":
    unittest.main()
