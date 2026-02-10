"""
CLE-Net Tendermint BFT Integration

This module provides the integration between CLE-Net and Tendermint BFT consensus.
It handles block proposal, validation, and commitment.
"""

from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import json
import asyncio


@dataclass
class BlockHeader:
    """Represents a block header."""
    height: int
    hash: str
    prev_block_hash: str
    proposer_address: str
    timestamp: datetime
    num_txs: int
    last_commit_hash: str
    data_hash: str
    validators_hash: str
    next_validators_hash: str
    consensus_hash: str
    app_hash: str
    last_results_hash: str
    evidence_hash: str
    proposer_address: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "height": self.height,
            "hash": self.hash,
            "prev_block_hash": self.prev_block_hash,
            "proposer_address": self.proposer_address,
            "timestamp": self.timestamp.isoformat(),
            "num_txs": self.num_txs,
            "last_commit_hash": self.last_commit_hash,
            "data_hash": self.data_hash,
            "validators_hash": self.validators_hash,
            "next_validators_hash": self.next_validators_hash,
            "consensus_hash": self.consensus_hash,
            "app_hash": self.app_hash,
            "last_results_hash": self.last_results_hash,
            "evidence_hash": self.evidence_hash
        }


@dataclass
class Vote:
    """Represents a vote in the consensus process."""
    voter_address: str
    block_height: int
    block_hash: str
    vote_type: str  # "prevote" or "precommit"
    timestamp: datetime
    signature: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "voter_address": self.voter_address,
            "block_height": self.block_height,
            "block_hash": self.block_hash,
            "vote_type": self.vote_type,
            "timestamp": self.timestamp.isoformat(),
            "signature": self.signature
        }


@dataclass
class Commit:
    """Represents a commit for a block."""
    block_height: int
    block_hash: str
    votes: List[Vote]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "block_height": self.block_height,
            "block_hash": self.block_hash,
            "votes": [vote.to_dict() for vote in self.votes]
        }


@dataclass
class Block:
    """Represents a complete block."""
    header: BlockHeader
    data: List[Dict]
    evidence: List[Dict]
    last_commit: Optional[Commit]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "header": self.header.to_dict(),
            "data": self.data,
            "evidence": self.evidence,
            "last_commit": self.last_commit.to_dict() if self.last_commit else None
        }


class TendermintBFT:
    """
    Tendermint BFT integration for CLE-Net.
    
    This class provides the integration between CLE-Net and Tendermint BFT consensus.
    It handles block proposal, validation, and commitment.
    """
    
    def __init__(self, total_validators: int = 4):
        """
        Initialize the Tendermint BFT integration.
        
        Args:
            total_validators: Total number of validators
        """
        self.total_validators = total_validators
        self.faulty_validators = (total_validators - 1) // 3
        self.quorum = 2 * self.faulty_validators + 1
        
        self.validators: Set[str] = set()
        self.proposer_queue: List[str] = []
        self.current_proposer_index: int = 0
        self.current_block_height: int = 0
        self.last_block_hash: str = ""
        
        self.pending_votes: Dict[str, List[Vote]] = {}  # block_hash -> votes
        self.committed_blocks: Dict[int, Block] = {}  # height -> block
        
        self.running = False
    
    def start(self) -> None:
        """Start the Tendermint BFT integration."""
        self.running = True
    
    def stop(self) -> None:
        """Stop the Tendermint BFT integration."""
        self.running = False
    
    def add_validator(self, validator_address: str) -> None:
        """
        Add a validator to the set.
        
        Args:
            validator_address: Address of the validator
        """
        self.validators.add(validator_address)
        self.proposer_queue.append(validator_address)
    
    def remove_validator(self, validator_address: str) -> bool:
        """
        Remove a validator from the set.
        
        Args:
            validator_address: Address of the validator
            
        Returns:
            True if validator was removed, False otherwise
        """
        if validator_address in self.validators:
            self.validators.discard(validator_address)
            if validator_address in self.proposer_queue:
                self.proposer_queue.remove(validator_address)
            return True
        return False
    
    def get_current_proposer(self) -> Optional[str]:
        """
        Get the current proposer.
        
        Returns:
            Address of the current proposer or None
        """
        if not self.proposer_queue:
            return None
        
        return self.proposer_queue[self.current_proposer_index]
    
    def rotate_proposer(self) -> Optional[str]:
        """
        Rotate to the next proposer.
        
        Returns:
            Address of the new proposer or None
        """
        if not self.proposer_queue:
            return None
        
        self.current_proposer_index = (self.current_proposer_index + 1) % len(self.proposer_queue)
        return self.get_current_proposer()
    
    def propose_block(
        self,
        proposer_address: str,
        transactions: List[Dict],
        last_commit_hash: str = ""
    ) -> Block:
        """
        Propose a new block.
        
        Args:
            proposer_address: Address of the proposer
            transactions: Transactions to include in the block
            last_commit_hash: Hash of the last commit
            
        Returns:
            Proposed block
        """
        # Increment block height
        self.current_block_height += 1
        
        # Compute block hash
        block_data = json.dumps({
            "height": self.current_block_height,
            "prev_block_hash": self.last_block_hash,
            "proposer": proposer_address,
            "transactions": transactions
        }, sort_keys=True)
        block_hash = hashlib.sha256(block_data.encode()).hexdigest()
        
        # Create block header
        header = BlockHeader(
            height=self.current_block_height,
            hash=block_hash,
            prev_block_hash=self.last_block_hash,
            proposer_address=proposer_address,
            timestamp=datetime.utcnow(),
            num_txs=len(transactions),
            last_commit_hash=last_commit_hash,
            data_hash=hashlib.sha256(json.dumps(transactions, sort_keys=True).encode()).hexdigest(),
            validators_hash=hashlib.sha256(json.dumps(list(self.validators), sort_keys=True).encode()).hexdigest(),
            next_validators_hash=hashlib.sha256(json.dumps(list(self.validators), sort_keys=True).encode()).hexdigest(),
            consensus_hash=hashlib.sha256("consensus".encode()).hexdigest(),
            app_hash=hashlib.sha256("app".encode()).hexdigest(),
            last_results_hash=hashlib.sha256("results".encode()).hexdigest(),
            evidence_hash=hashlib.sha256("evidence".encode()).hexdigest(),
            proposer_address=proposer_address
        )
        
        # Create block
        block = Block(
            header=header,
            data=transactions,
            evidence=[],
            last_commit=None
        )
        
        return block
    
    def vote_on_block(
        self,
        voter_address: str,
        block_hash: str,
        vote_type: str
    ) -> bool:
        """
        Vote on a block.
        
        Args:
            voter_address: Address of the voter
            block_hash: Hash of the block
            vote_type: Type of vote ("prevote" or "precommit")
            
        Returns:
            True if vote was recorded, False otherwise
        """
        # Check if voter is a validator
        if voter_address not in self.validators:
            return False
        
        # Create vote
        vote = Vote(
            voter_address=voter_address,
            block_height=self.current_block_height,
            block_hash=block_hash,
            vote_type=vote_type,
            timestamp=datetime.utcnow(),
            signature=f"sig_{voter_address}_{block_hash}"
        )
        
        # Add to pending votes
        if block_hash not in self.pending_votes:
            self.pending_votes[block_hash] = []
        
        self.pending_votes[block_hash].append(vote)
        
        return True
    
    def check_consensus(self, block_hash: str, vote_type: str) -> bool:
        """
        Check if consensus is reached for a block.
        
        Args:
            block_hash: Hash of the block
            vote_type: Type of vote to check ("prevote" or "precommit")
            
        Returns:
            True if consensus is reached, False otherwise
        """
        if block_hash not in self.pending_votes:
            return False
        
        # Count votes of the specified type
        votes = [v for v in self.pending_votes[block_hash] if v.vote_type == vote_type]
        
        # Check if quorum is reached
        return len(votes) >= self.quorum
    
    def commit_block(self, block: Block) -> bool:
        """
        Commit a block.
        
        Args:
            block: Block to commit
            
        Returns:
            True if commit was successful, False otherwise
        """
        # Check if consensus is reached
        if not self.check_consensus(block.header.hash, "precommit"):
            return False
        
        # Create commit
        precommit_votes = [v for v in self.pending_votes.get(block.header.hash, []) if v.vote_type == "precommit"]
        commit = Commit(
            block_height=block.header.height,
            block_hash=block.header.hash,
            votes=precommit_votes
        )
        
        # Update block with commit
        block.last_commit = commit
        
        # Store committed block
        self.committed_blocks[block.header.height] = block
        
        # Update last block hash
        self.last_block_hash = block.header.hash
        
        # Clear pending votes for this block
        if block.header.hash in self.pending_votes:
            del self.pending_votes[block.header.hash]
        
        # Rotate proposer
        self.rotate_proposer()
        
        return True
    
    def get_block(self, height: int) -> Optional[Block]:
        """
        Get a committed block by height.
        
        Args:
            height: Height of the block
            
        Returns:
            Block or None if not found
        """
        return self.committed_blocks.get(height)
    
    def get_latest_block(self) -> Optional[Block]:
        """
        Get the latest committed block.
        
        Returns:
            Latest block or None if no blocks committed
        """
        if not self.committed_blocks:
            return None
        
        latest_height = max(self.committed_blocks.keys())
        return self.committed_blocks[latest_height]
    
    def get_validator_set(self) -> Set[str]:
        """
        Get the current validator set.
        
        Returns:
            Set of validator addresses
        """
        return self.validators.copy()
    
    def get_consensus_state(self) -> Dict:
        """
        Get the current consensus state.
        
        Returns:
            Dictionary with consensus state information
        """
        return {
            "total_validators": self.total_validators,
            "active_validators": len(self.validators),
            "quorum": self.quorum,
            "fault_tolerance": self.faulty_validators,
            "current_proposer": self.get_current_proposer(),
            "current_block_height": self.current_block_height,
            "last_block_hash": self.last_block_hash,
            "pending_votes": len(self.pending_votes),
            "committed_blocks": len(self.committed_blocks),
            "running": self.running
        }
    
    async def run_consensus_loop(self, block_time: float = 5.0) -> None:
        """
        Run the consensus loop.
        
        Args:
            block_time: Time between blocks in seconds
        """
        while self.running:
            # Propose block
            proposer = self.get_current_proposer()
            if proposer:
                block = self.propose_block(proposer, [])
                print(f"Proposed block {block.header.height} by {proposer}")
                
                # Simulate votes
                for validator in self.validators:
                    self.vote_on_block(validator, block.header.hash, "prevote")
                    self.vote_on_block(validator, block.header.hash, "precommit")
                
                # Check consensus and commit
                if self.check_consensus(block.header.hash, "precommit"):
                    self.commit_block(block)
                    print(f"Committed block {block.header.height}")
            
            # Wait for next block
            await asyncio.sleep(block_time)
    
    def validate_block(self, block: Block) -> Tuple[bool, List[str]]:
        """
        Validate a block.
        
        Args:
            block: Block to validate
            
        Returns:
            Tuple of (is_valid, list of validation errors)
        """
        errors = []
        
        # Check block height
        if block.header.height != self.current_block_height:
            errors.append(f"Invalid block height: {block.header.height}")
        
        # Check previous block hash
        if block.header.prev_block_hash != self.last_block_hash:
            errors.append(f"Invalid previous block hash: {block.header.prev_block_hash}")
        
        # Check proposer is a validator
        if block.header.proposer_address not in self.validators:
            errors.append(f"Invalid proposer: {block.header.proposer_address}")
        
        # Check block hash
        computed_hash = hashlib.sha256(json.dumps({
            "height": block.header.height,
            "prev_block_hash": block.header.prev_block_hash,
            "proposer": block.header.proposer_address,
            "transactions": block.data
        }, sort_keys=True).encode()).hexdigest()
        
        if computed_hash != block.header.hash:
            errors.append(f"Invalid block hash: {block.header.hash}")
        
        return (len(errors) == 0, errors)
