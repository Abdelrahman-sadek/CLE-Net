"""
Unit tests for the Cosmos SDK application.

This module tests the CLENetApp implementation.
"""

import unittest
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.cosmos.app.app import CLENetApp, AppConfig, Message


class TestAppConfig(unittest.TestCase):
    """Test cases for AppConfig."""
    
    def test_app_config_creation(self):
        """Test app config creation."""
        config = AppConfig(
            chain_id="clenet-testnet-1",
            min_gas_prices="0.025ucle",
            block_time=5.0
        )
        
        self.assertEqual(config.chain_id, "clenet-testnet-1")
        self.assertEqual(config.min_gas_prices, "0.025ucle")
        self.assertEqual(config.block_time, 5.0)
    
    def test_app_config_defaults(self):
        """Test app config defaults."""
        config = AppConfig(chain_id="clenet-testnet-1")
        
        self.assertEqual(config.chain_id, "clenet-testnet-1")
        self.assertEqual(config.min_gas_prices, "0.025ucle")
        self.assertEqual(config.block_time, 5.0)


class TestMessage(unittest.TestCase):
    """Test cases for Message."""
    
    def test_message_creation(self):
        """Test message creation."""
        message = Message(
            type="test_message",
            sender="validator1",
            data={"key": "value"}
        )
        
        self.assertEqual(message.type, "test_message")
        self.assertEqual(message.sender, "validator1")
        self.assertEqual(message.data["key"], "value")
    
    def test_message_to_dict(self):
        """Test message serialization."""
        message = Message(
            type="test_message",
            sender="validator1",
            data={"key": "value"}
        )
        
        message_dict = message.to_dict()
        self.assertIn("type", message_dict)
        self.assertIn("sender", message_dict)
        self.assertIn("data", message_dict)


class TestCLENetApp(unittest.TestCase):
    """Test cases for CLENetApp."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = AppConfig(
            chain_id="clenet-testnet-1",
            min_gas_prices="0.025ucle",
            block_time=5.0
        )
        self.app = CLENetApp(self.config)
    
    def test_initialization(self):
        """Test app initialization."""
        self.assertIsNotNone(self.app)
        self.assertEqual(self.app.config.chain_id, "clenet-testnet-1")
        self.assertEqual(self.app.block_height, 0)
        self.assertEqual(self.app.last_block_hash, "")
        self.assertEqual(len(self.app.modules), 0)
        self.assertEqual(len(self.app.state), 0)
    
    def test_register_module(self):
        """Test module registration."""
        # Create a mock module
        class MockModule:
            def __init__(self):
                self.name = "mock_module"
                self.state = {}
            
            def init_genesis(self, genesis_state):
                self.state = genesis_state
                return self.state
            
            def handle_message(self, message):
                return {"success": True}
        
        mock_module = MockModule()
        self.app.register_module("mock", mock_module)
        
        self.assertIn("mock", self.app.modules)
        self.assertEqual(self.app.modules["mock"], mock_module)
    
    def test_unregister_module(self):
        """Test module unregistration."""
        # Create a mock module
        class MockModule:
            def __init__(self):
                self.name = "mock_module"
                self.state = {}
            
            def init_genesis(self, genesis_state):
                self.state = genesis_state
                return self.state
            
            def handle_message(self, message):
                return {"success": True}
        
        mock_module = MockModule()
        self.app.register_module("mock", mock_module)
        
        self.assertIn("mock", self.app.modules)
        
        self.app.unregister_module("mock")
        self.assertNotIn("mock", self.app.modules)
    
    def test_init_chain(self):
        """Test chain initialization."""
        # Create mock modules
        class MockModule:
            def __init__(self):
                self.name = "mock_module"
                self.state = {}
            
            def init_genesis(self, genesis_state):
                self.state = genesis_state
                return self.state
            
            def handle_message(self, message):
                return {"success": True}
        
        mock_module1 = MockModule()
        mock_module2 = MockModule()
        
        self.app.register_module("module1", mock_module1)
        self.app.register_module("module2", mock_module2)
        
        # Initialize chain
        genesis_state = {
            "module1": {"key": "value1"},
            "module2": {"key": "value2"}
        }
        
        result = self.app.init_chain(genesis_state)
        
        self.assertIn("module1", result)
        self.assertIn("module2", result)
        self.assertEqual(result["module1"]["key"], "value1")
        self.assertEqual(result["module2"]["key"], "value2")
    
    def test_begin_block(self):
        """Test begin block."""
        block_header = {
            "height": 1,
            "hash": "hash_1",
            "proposer": "validator1",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        result = self.app.begin_block(block_header)
        
        self.assertEqual(self.app.block_height, 1)
        self.assertEqual(self.app.last_block_hash, "hash_1")
        self.assertIn("height", result)
        self.assertEqual(result["height"], 1)
    
    def test_deliver_tx(self):
        """Test transaction delivery."""
        # Create a mock module
        class MockModule:
            def __init__(self):
                self.name = "mock_module"
                self.state = {}
            
            def init_genesis(self, genesis_state):
                self.state = genesis_state
                return self.state
            
            def handle_message(self, message):
                return {"success": True, "data": message.data}
        
        mock_module = MockModule()
        self.app.register_module("mock", mock_module)
        
        # Create a message
        message = Message(
            type="test_message",
            sender="validator1",
            data={"key": "value"}
        )
        
        # Deliver transaction
        result = self.app.deliver_tx(message)
        
        self.assertIn("success", result)
        self.assertTrue(result["success"])
    
    def test_end_block(self):
        """Test end block."""
        # Begin a block first
        block_header = {
            "height": 1,
            "hash": "hash_1",
            "proposer": "validator1",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.app.begin_block(block_header)
        
        # End block
        result = self.app.end_block()
        
        self.assertIn("height", result)
        self.assertEqual(result["height"], 1)
        self.assertIn("validator_updates", result)
    
    def test_commit(self):
        """Test commit."""
        # Begin and end a block first
        block_header = {
            "height": 1,
            "hash": "hash_1",
            "proposer": "validator1",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.app.begin_block(block_header)
        self.app.end_block()
        
        # Commit
        result = self.app.commit()
        
        self.assertIn("data", result)
        self.assertIn("height", result)
        self.assertEqual(result["height"], 1)
    
    def test_query(self):
        """Test query."""
        # Create a mock module
        class MockModule:
            def __init__(self):
                self.name = "mock_module"
                self.state = {}
            
            def init_genesis(self, genesis_state):
                self.state = genesis_state
                return self.state
            
            def handle_message(self, message):
                return {"success": True, "data": message.data}
            
            def query(self, path, data):
                return {"result": "query_result"}
        
        mock_module = MockModule()
        self.app.register_module("mock", mock_module)
        
        # Query
        result = self.app.query("mock", "test_path", {"key": "value"})
        
        self.assertIn("result", result)
        self.assertEqual(result["result"], "query_result")
    
    def test_get_state(self):
        """Test getting state."""
        # Initialize chain
        genesis_state = {
            "module1": {"key": "value1"}
        }
        
        # Create a mock module
        class MockModule:
            def __init__(self):
                self.name = "mock_module"
                self.state = {}
            
            def init_genesis(self, genesis_state):
                self.state = genesis_state
                return self.state
            
            def handle_message(self, message):
                return {"success": True}
        
        mock_module = MockModule()
        self.app.register_module("module1", mock_module)
        
        self.app.init_chain(genesis_state)
        
        # Get state
        state = self.app.get_state()
        
        self.assertIn("module1", state)
        self.assertEqual(state["module1"]["key"], "value1")
    
    def test_export_state(self):
        """Test exporting state."""
        # Initialize chain
        genesis_state = {
            "module1": {"key": "value1"}
        }
        
        # Create a mock module
        class MockModule:
            def __init__(self):
                self.name = "mock_module"
                self.state = {}
            
            def init_genesis(self, genesis_state):
                self.state = genesis_state
                return self.state
            
            def handle_message(self, message):
                return {"success": True}
        
        mock_module = MockModule()
        self.app.register_module("module1", mock_module)
        
        self.app.init_chain(genesis_state)
        
        # Export state
        exported_state = self.app.export_state()
        
        self.assertIn("chain_id", exported_state)
        self.assertIn("block_height", exported_state)
        self.assertIn("last_block_hash", exported_state)
        self.assertIn("modules", exported_state)
        self.assertEqual(exported_state["chain_id"], "clenet-testnet-1")


if __name__ == "__main__":
    unittest.main()
