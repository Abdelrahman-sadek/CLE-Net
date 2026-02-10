"""
Unit tests for the Tendermint BFT integration.

This module tests the Tendermint BFT implementation for CLE-Net.
"""

import unittest
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.cosmos.tendermint import (
    TendermintBFT,
    BlockHeader,
    Vote,
    Commit,
    Block
)


class TestTendermintBFT(unittest.TestCase):
    """Test cases for TendermintBFT."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tendermint = TendermintBFT(total_validators=4)
    
    def test_initialization(self):
        """Test Tendermint BFT initialization."""
        self.assertIsNotNone(self.tendermint)
        self.assertEqual(self.tendermint.total_validators, 4)
        self.assertEqual(self.tendermint.faulty_validators, 1)
        self.assertEqual(self.tendermint.quorum, 3)
        self.assertEqual(len(self.tendermint.validators), 0)
        self.assertEqual(len(self.tendermint.proposer_queue), 0)
        self.assertEqual(self.tendermint.current_block_height, 0)
        self.assertEqual(self.tendermint.last_block_hash, "")
        self.assertFalse(self.tendermint.running)
    
    def test_add_validator(self):
        """Test adding validators."""
        self.tendermint.add_validator("validator1")
        self.assertIn("validator1", self.tendermint.validators)
        self.assertIn("validator1", self.tendermint.proposer_queue)
        
        self.tendermint.add_validator("validator2")
        self.tendermint.add_validator("validator3")
        self.tendermint.add_validator("validator4")
        
        self.assertEqual(len(self.tendermint.validators), 4)
        self.assertEqual(len(self.tendermint.proposer_queue), 4)
    
    def test_remove_validator(self):
        """Test removing validators."""
        self.tendermint.add_validator("validator1")
        self.tendermint.add_validator("validator2")
        
        self.assertTrue(self.tendermint.remove_validator("validator1"))
        self.assertNotIn("validator1", self.tendermint.validators)
        self.assertNotIn("validator1", self.tendermint.proposer_queue)
        
        self.assertFalse(self.tendermint.remove_validator("nonexistent"))
    
    def test_get_current_proposer(self):
        """Test getting current proposer."""
        self.assertIsNone(self.tendermint.get_current_proposer())
        
        self.tendermint.add_validator("validator1")
        self.tendermint.add_validator("validator2")
        
        self.assertEqual(self.tendermint.get_current_proposer(), "validator1")
    
    def test_rotate_proposer(self):
        """Test rotating proposer."""
        self.tendermint.add_validator("validator1")
        self.tendermint.add_validator("validator2")
        self.tendermint.add_validator("validator3")
        
        self.assertEqual(self.tendermint.get_current_proposer(), "validator1")
        
        self.tendermint.rotate_proposer()
        self.assertEqual(self.tendermint.get_current_proposer(), "validator2")
        
        self.tendermint.rotate_proposer()
        self.assertEqual(self.tendermint.get_current_proposer(), "validator3")
        
        self.tendermint.rotate_proposer()
        self.assertEqual(self.tendermint.get_current_proposer(), "validator1")
    
    def test_propose_block(self):
        """Test block proposal."""
        self.tendermint.add_validator("validator1")
        self.tendermint.add_validator("validator2")
        
        proposer = self.tendermint.get_current_proposer()
        transactions = [{"type": "law_proposal", "data": {"law_id": "law_1"}}]
        
        block = self.tendermint.propose_block(proposer, transactions)
        
        self.assertIsNotNone(block)
        self.assertEqual(block.header.height, 1)
        self.assertEqual(block.header.proposer_address, proposer)
        self.assertEqual(block.header.num_txs, 1)
        self.assertEqual(len(block.data), 1)
        self.assertIsNotNone(block.header.hash)
    
    def test_vote_on_block(self):
        """Test voting on a block."""
        self.tendermint.add_validator("validator1")
        self.tendermint.add_validator("validator2")
        
        proposer = self.tendermint.get_current_proposer()
        block = self.tendermint.propose_block(proposer, [])
        
        # Test prevote
        self.assertTrue(self.tendermint.vote_on_block("validator1", block.header.hash, "prevote"))
        self.assertTrue(self.tendermint.vote_on_block("validator2", block.header.hash, "prevote"))
        
        # Test precommit
        self.assertTrue(self.tendermint.vote_on_block("validator1", block.header.hash, "precommit"))
        self.assertTrue(self.tendermint.vote_on_block("validator2", block.header.hash, "precommit"))
        
        # Test voting by non-validator
        self.assertFalse(self.tendermint.vote_on_block("nonexistent", block.header.hash, "prevote"))
    
    def test_check_consensus(self):
        """Test consensus checking."""
        self.tendermint.add_validator("validator1")
        self.tendermint.add_validator("validator2")
        self.tendermint.add_validator("validator3")
        self.tendermint.add_validator("validator4")
        
        proposer = self.tendermint.get_current_proposer()
        block = self.tendermint.propose_block(proposer, [])
        
        # No votes yet
        self.assertFalse(self.tendermint.check_consensus(block.header.hash, "prevote"))
        
        # Add votes
        self.tendermint.vote_on_block("validator1", block.header.hash, "prevote")
        self.tendermint.vote_on_block("validator2", block.header.hash, "prevote")
        self.tendermint.vote_on_block("validator3", block.header.hash, "prevote")
        
        # Quorum reached
        self.assertTrue(self.tendermint.check_consensus(block.header.hash, "prevote"))
    
    def test_commit_block(self):
        """Test block commitment."""
        self.tendermint.add_validator("validator1")
        self.tendermint.add_validator("validator2")
        self.tendermint.add_validator("validator3")
        self.tendermint.add_validator("validator4")
        
        proposer = self.tendermint.get_current_proposer()
        block = self.tendermint.propose_block(proposer, [])
        
        # Vote on block
        for validator in self.tendermint.validators:
            self.tendermint.vote_on_block(validator, block.header.hash, "prevote")
            self.tendermint.vote_on_block(validator, block.header.hash, "precommit")
        
        # Commit block
        self.assertTrue(self.tendermint.commit_block(block))
        
        # Verify block was committed
        self.assertEqual(self.tendermint.current_block_height, 1)
        self.assertEqual(self.tendermint.last_block_hash, block.header.hash)
        self.assertIn(1, self.tendermint.committed_blocks)
        self.assertIsNotNone(self.tendermint.committed_blocks[1].last_commit)
    
    def test_commit_block_without_consensus(self):
        """Test block commitment without consensus."""
        self.tendermint.add_validator("validator1")
        self.tendermint.add_validator("validator2")
        
        proposer = self.tendermint.get_current_proposer()
        block = self.tendermint.propose_block(proposer, [])
        
        # Not enough votes
        self.tendermint.vote_on_block("validator1", block.header.hash, "precommit")
        
        # Should fail to commit
        self.assertFalse(self.tendermint.commit_block(block))
    
    def test_get_block(self):
        """Test getting committed blocks."""
        self.tendermint.add_validator("validator1")
        self.tendermint.add_validator("validator2")
        self.tendermint.add_validator("validator3")
        self.tendermint.add_validator("validator4")
        
        # Commit a block
        proposer = self.tendermint.get_current_proposer()
        block = self.tendermint.propose_block(proposer, [])
        
        for validator in self.tendermint.validators:
            self.tendermint.vote_on_block(validator, block.header.hash, "prevote")
            self.tendermint.vote_on_block(validator, block.header.hash, "precommit")
        
        self.tendermint.commit_block(block)
        
        # Get block
        retrieved_block = self.tendermint.get_block(1)
        self.assertIsNotNone(retrieved_block)
        self.assertEqual(retrieved_block.header.height, 1)
        self.assertEqual(retrieved_block.header.hash, block.header.hash)
        
        # Get non-existent block
        self.assertIsNone(self.tendermint.get_block(999))
    
    def test_get_latest_block(self):
        """Test getting latest committed block."""
        self.tendermint.add_validator("validator1")
        self.tendermint.add_validator("validator2")
        self.tendermint.add_validator("validator3")
        self.tendermint.add_validator("validator4")
        
        # No blocks yet
        self.assertIsNone(self.tendermint.get_latest_block())
        
        # Commit blocks
        for i in range(3):
            proposer = self.tendermint.get_current_proposer()
            block = self.tendermint.propose_block(proposer, [])
            
            for validator in self.tendermint.validators:
                self.tendermint.vote_on_block(validator, block.header.hash, "prevote")
                self.tendermint.vote_on_block(validator, block.header.hash, "precommit")
            
            self.tendermint.commit_block(block)
        
        # Get latest block
        latest_block = self.tendermint.get_latest_block()
        self.assertIsNotNone(latest_block)
        self.assertEqual(latest_block.header.height, 3)
    
    def test_get_validator_set(self):
        """Test getting validator set."""
        self.tendermint.add_validator("validator1")
        self.tendermint.add_validator("validator2")
        
        validator_set = self.tendermint.get_validator_set()
        self.assertEqual(len(validator_set), 2)
        self.assertIn("validator1", validator_set)
        self.assertIn("validator2", validator_set)
        
        # Verify it's a copy
        validator_set.add("validator3")
        self.assertNotIn("validator3", self.tendermint.validators)
    
    def test_get_consensus_state(self):
        """Test getting consensus state."""
        self.tendermint.add_validator("validator1")
        self.tendermint.add_validator("validator2")
        self.tendermint.add_validator("validator3")
        self.tendermint.add_validator("validator4")
        
        self.tendermint.start()
        
        # Commit a block
        proposer = self.tendermint.get_current_proposer()
        block = self.tendermint.propose_block(proposer, [])
        
        for validator in self.tendermint.validators:
            self.tendermint.vote_on_block(validator, block.header.hash, "prevote")
            self.tendermint.vote_on_block(validator, block.header.hash, "precommit")
        
        self.tendermint.commit_block(block)
        
        # Get consensus state
        state = self.tendermint.get_consensus_state()
        
        self.assertEqual(state["total_validators"], 4)
        self.assertEqual(state["active_validators"], 4)
        self.assertEqual(state["quorum"], 3)
        self.assertEqual(state["fault_tolerance"], 1)
        self.assertIsNotNone(state["current_proposer"])
        self.assertEqual(state["current_block_height"], 1)
        self.assertEqual(state["last_block_hash"], block.header.hash)
        self.assertEqual(state["committed_blocks"], 1)
        self.assertTrue(state["running"])
        
        self.tendermint.stop()
    
    def test_validate_block(self):
        """Test block validation."""
        self.tendermint.add_validator("validator1")
        self.tendermint.add_validator("validator2")
        
        # Propose a valid block
        proposer = self.tendermint.get_current_proposer()
        block = self.tendermint.propose_block(proposer, [])
        
        # Validate block
        is_valid, errors = self.tendermint.validate_block(block)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
        
        # Test invalid block height
        invalid_block = self.tendermint.propose_block(proposer, [])
        invalid_block.header.height = 999
        
        is_valid, errors = self.tendermint.validate_block(invalid_block)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
    
    def test_start_stop(self):
        """Test starting and stopping Tendermint."""
        self.assertFalse(self.tendermint.running)
        
        self.tendermint.start()
        self.assertTrue(self.tendermint.running)
        
        self.tendermint.stop()
        self.assertFalse(self.tendermint.running)


class TestBlockHeader(unittest.TestCase):
    """Test cases for BlockHeader."""
    
    def test_block_header_creation(self):
        """Test block header creation."""
        header = BlockHeader(
            height=1,
            hash="hash_1",
            prev_block_hash="",
            proposer_address="validator1",
            timestamp=datetime.utcnow(),
            num_txs=1,
            last_commit_hash="",
            data_hash="data_hash",
            validators_hash="validators_hash",
            next_validators_hash="next_validators_hash",
            consensus_hash="consensus_hash",
            app_hash="app_hash",
            last_results_hash="last_results_hash",
            evidence_hash="evidence_hash",
            proposer_address="validator1"
        )
        
        self.assertEqual(header.height, 1)
        self.assertEqual(header.hash, "hash_1")
        self.assertEqual(header.proposer_address, "validator1")
    
    def test_block_header_to_dict(self):
        """Test block header serialization."""
        header = BlockHeader(
            height=1,
            hash="hash_1",
            prev_block_hash="",
            proposer_address="validator1",
            timestamp=datetime.utcnow(),
            num_txs=1,
            last_commit_hash="",
            data_hash="data_hash",
            validators_hash="validators_hash",
            next_validators_hash="next_validators_hash",
            consensus_hash="consensus_hash",
            app_hash="app_hash",
            last_results_hash="last_results_hash",
            evidence_hash="evidence_hash",
            proposer_address="validator1"
        )
        
        header_dict = header.to_dict()
        self.assertIn("height", header_dict)
        self.assertIn("hash", header_dict)
        self.assertIn("proposer_address", header_dict)
        self.assertIn("timestamp", header_dict)


class TestVote(unittest.TestCase):
    """Test cases for Vote."""
    
    def test_vote_creation(self):
        """Test vote creation."""
        vote = Vote(
            voter_address="validator1",
            block_height=1,
            block_hash="hash_1",
            vote_type="prevote",
            timestamp=datetime.utcnow(),
            signature="sig_1"
        )
        
        self.assertEqual(vote.voter_address, "validator1")
        self.assertEqual(vote.block_height, 1)
        self.assertEqual(vote.vote_type, "prevote")
    
    def test_vote_to_dict(self):
        """Test vote serialization."""
        vote = Vote(
            voter_address="validator1",
            block_height=1,
            block_hash="hash_1",
            vote_type="prevote",
            timestamp=datetime.utcnow(),
            signature="sig_1"
        )
        
        vote_dict = vote.to_dict()
        self.assertIn("voter_address", vote_dict)
        self.assertIn("block_height", vote_dict)
        self.assertIn("vote_type", vote_dict)


if __name__ == "__main__":
    unittest.main()
