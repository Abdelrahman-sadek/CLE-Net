"""
Unit tests for the Cognitive State Machine.

This module tests the state machine implementation for CLE-Net.
"""

import unittest
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.cosmos.state_machine import (
    CognitiveStateMachine,
    LawState,
    CCSState,
    ValidatorState,
    StateTransition,
    StateTransitionEvent
)


class TestCognitiveStateMachine(unittest.TestCase):
    """Test cases for CognitiveStateMachine."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.state_machine = CognitiveStateMachine()
    
    def test_initialization(self):
        """Test state machine initialization."""
        self.assertIsNotNone(self.state_machine)
        self.assertEqual(len(self.state_machine.laws), 0)
        self.assertEqual(len(self.state_machine.ccs_scores), 0)
        self.assertEqual(len(self.state_machine.validators), 0)
        self.assertEqual(len(self.state_machine.transition_history), 0)
        self.assertEqual(self.state_machine.current_block_height, 0)
        self.assertEqual(self.state_machine.current_block_hash, "")
    
    def test_law_state_transitions(self):
        """Test law state transitions."""
        # Create a law
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
        
        # Test valid transitions
        self.assertTrue(self.state_machine.transition_law("law_1", "validating"))
        self.assertEqual(self.state_machine.laws["law_1"].status, "validating")
        
        self.assertTrue(self.state_machine.transition_law("law_1", "active"))
        self.assertEqual(self.state_machine.laws["law_1"].status, "active")
        
        self.assertTrue(self.state_machine.transition_law("law_1", "conflicted"))
        self.assertEqual(self.state_machine.laws["law_1"].status, "conflicted")
        
        self.assertTrue(self.state_machine.transition_law("law_1", "active"))
        self.assertEqual(self.state_machine.laws["law_1"].status, "active")
        
        self.assertTrue(self.state_machine.transition_law("law_1", "deprecated"))
        self.assertEqual(self.state_machine.laws["law_1"].status, "deprecated")
    
    def test_invalid_law_transitions(self):
        """Test invalid law state transitions."""
        # Create a law
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
        
        # Test invalid transitions
        self.assertFalse(self.state_machine.transition_law("law_1", "active"))
        self.assertFalse(self.state_machine.transition_law("law_1", "revoked"))
        self.assertFalse(self.state_machine.transition_law("law_1", "invalid_status"))
    
    def test_ccs_transitions(self):
        """Test CCS state transitions."""
        # Test CCS update
        self.assertTrue(self.state_machine.transition_ccs("validator1", 100, laws_discovered_delta=1))
        
        ccs = self.state_machine.get_ccs_state("validator1")
        self.assertIsNotNone(ccs)
        self.assertEqual(ccs.score, 100.0)
        self.assertEqual(ccs.laws_discovered, 1)
        self.assertEqual(ccs.contributions_count, 1)
        
        # Test multiple updates
        self.assertTrue(self.state_machine.transition_ccs("validator1", 50, conflicts_resolved_delta=1))
        ccs = self.state_machine.get_ccs_state("validator1")
        self.assertEqual(ccs.score, 150.0)
        self.assertEqual(ccs.conflicts_resolved, 1)
        self.assertEqual(ccs.contributions_count, 2)
    
    def test_validator_transitions(self):
        """Test validator state transitions."""
        # Create a validator
        validator = ValidatorState(
            validator_address="validator1",
            role="cognitive_miner",
            stake=1000.0,
            uptime=100.0,
            laws_validated=0,
            conflicts_resolved=0,
            last_active=datetime.utcnow(),
            jailed=False
        )
        self.state_machine.validators["validator1"] = validator
        
        # Test validator update
        self.assertTrue(self.state_machine.transition_validator(
            "validator1",
            new_role="state_validator",
            stake_delta=500.0
        ))
        
        validator = self.state_machine.get_validator_state("validator1")
        self.assertEqual(validator.role, "state_validator")
        self.assertEqual(validator.stake, 1500.0)
    
    def test_block_commitment(self):
        """Test block commitment."""
        self.assertTrue(self.state_machine.commit_block(1, "hash_1"))
        self.assertEqual(self.state_machine.current_block_height, 1)
        self.assertEqual(self.state_machine.current_block_hash, "hash_1")
        
        self.assertTrue(self.state_machine.commit_block(2, "hash_2"))
        self.assertEqual(self.state_machine.current_block_height, 2)
        self.assertEqual(self.state_machine.current_block_hash, "hash_2")
    
    def test_transition_history(self):
        """Test transition history tracking."""
        # Create a law
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
        
        # Perform transitions
        self.state_machine.transition_law("law_1", "validating")
        self.state_machine.transition_law("law_1", "active")
        
        # Check history
        history = self.state_machine.get_transition_history("law_1")
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0].to_state, "validating")
        self.assertEqual(history[1].to_state, "active")
    
    def test_state_validation(self):
        """Test state validation."""
        # Create a valid law
        law = LawState(
            law_id="law_1",
            status="active",
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
        
        # Create a valid CCS
        ccs = CCSState(
            participant_id="validator1",
            score=100.0,
            contributions_count=1,
            laws_discovered=1,
            conflicts_resolved=0,
            last_updated=datetime.utcnow()
        )
        self.state_machine.ccs_scores["validator1"] = ccs
        
        # Create a valid validator
        validator = ValidatorState(
            validator_address="validator1",
            role="cognitive_miner",
            stake=1000.0,
            uptime=100.0,
            laws_validated=0,
            conflicts_resolved=0,
            last_active=datetime.utcnow(),
            jailed=False
        )
        self.state_machine.validators["validator1"] = validator
        
        # Validate state
        is_valid, errors = self.state_machine.validate_state()
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
    
    def test_invalid_state_validation(self):
        """Test invalid state validation."""
        # Create a law with invalid status
        law = LawState(
            law_id="law_1",
            status="invalid_status",
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
        
        # Create a CCS with negative score
        ccs = CCSState(
            participant_id="validator1",
            score=-100.0,
            contributions_count=1,
            laws_discovered=1,
            conflicts_resolved=0,
            last_updated=datetime.utcnow()
        )
        self.state_machine.ccs_scores["validator1"] = ccs
        
        # Create a validator with negative stake
        validator = ValidatorState(
            validator_address="validator1",
            role="cognitive_miner",
            stake=-1000.0,
            uptime=100.0,
            laws_validated=0,
            conflicts_resolved=0,
            last_active=datetime.utcnow(),
            jailed=False
        )
        self.state_machine.validators["validator1"] = validator
        
        # Validate state
        is_valid, errors = self.state_machine.validate_state()
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
    
    def test_state_export_import(self):
        """Test state export and import."""
        # Create some state
        law = LawState(
            law_id="law_1",
            status="active",
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
        
        ccs = CCSState(
            participant_id="validator1",
            score=100.0,
            contributions_count=1,
            laws_discovered=1,
            conflicts_resolved=0,
            last_updated=datetime.utcnow()
        )
        self.state_machine.ccs_scores["validator1"] = ccs
        
        validator = ValidatorState(
            validator_address="validator1",
            role="cognitive_miner",
            stake=1000.0,
            uptime=100.0,
            laws_validated=0,
            conflicts_resolved=0,
            last_active=datetime.utcnow(),
            jailed=False
        )
        self.state_machine.validators["validator1"] = validator
        
        self.state_machine.commit_block(1, "hash_1")
        
        # Export state
        exported_state = self.state_machine.export_state()
        self.assertIsNotNone(exported_state)
        self.assertIn("laws", exported_state)
        self.assertIn("ccs_scores", exported_state)
        self.assertIn("validators", exported_state)
        
        # Import state into new state machine
        new_state_machine = CognitiveStateMachine()
        self.assertTrue(new_state_machine.import_state(exported_state))
        
        # Verify imported state
        self.assertEqual(len(new_state_machine.laws), 1)
        self.assertEqual(len(new_state_machine.ccs_scores), 1)
        self.assertEqual(len(new_state_machine.validators), 1)
        self.assertEqual(new_state_machine.current_block_height, 1)
        self.assertEqual(new_state_machine.current_block_hash, "hash_1")


class TestStateTransitionEvent(unittest.TestCase):
    """Test cases for StateTransitionEvent."""
    
    def test_event_creation(self):
        """Test event creation."""
        event = StateTransitionEvent(
            transition_type=StateTransition.LAW_PROPOSED,
            entity_id="law_1",
            from_state=None,
            to_state="proposed",
            timestamp=datetime.utcnow(),
            metadata={"proposer": "validator1"}
        )
        
        self.assertEqual(event.transition_type, StateTransition.LAW_PROPOSED)
        self.assertEqual(event.entity_id, "law_1")
        self.assertEqual(event.to_state, "proposed")
        self.assertEqual(event.metadata["proposer"], "validator1")
    
    def test_event_to_dict(self):
        """Test event serialization."""
        event = StateTransitionEvent(
            transition_type=StateTransition.LAW_PROPOSED,
            entity_id="law_1",
            from_state=None,
            to_state="proposed",
            timestamp=datetime.utcnow(),
            metadata={"proposer": "validator1"}
        )
        
        event_dict = event.to_dict()
        self.assertIn("transition_type", event_dict)
        self.assertIn("entity_id", event_dict)
        self.assertIn("from_state", event_dict)
        self.assertIn("to_state", event_dict)
        self.assertIn("timestamp", event_dict)
        self.assertIn("metadata", event_dict)


if __name__ == "__main__":
    unittest.main()
