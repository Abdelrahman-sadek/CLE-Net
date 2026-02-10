"""
CLE-Net Cosmos SDK Integration

This package provides the Cosmos SDK integration for CLE-Net.
CLE-Net is implemented as an application-specific blockchain using the Cosmos SDK,
enabling native cognitive state transitions and consensus over symbolic law evolution.

Architecture Overview:
----------------------

CLE-Net uses the Cosmos SDK to build an application-specific blockchain that
natively supports cognitive state transitions. The architecture consists of:

1. Core Modules:
   - cognitive: Manages cognitive laws, their lifecycle, and validation
   - laws: Provides law storage, indexing, and retrieval
   - consensus: Manages validators and Proof of Cognition (PoC) consensus

2. On-Chain State:
   - Cognitive State Blocks (CSBs): Fundamental units containing cognitive state transitions
   - Cognitive Laws: Symbolic representations of decision patterns
   - Cognitive Contribution Score (CCS): Measures quality and impact of contributions
   - Validator Information: Tracks validators and their roles

3. Off-Chain Processing:
   - Symbol extraction from human interaction
   - Knowledge graph construction
   - LLM inference and reasoning
   - OCR and multi-modal input processing

4. Consensus Mechanism:
   - Proof of Cognition (PoC): Rewards independent discovery of cognitive laws
   - Tendermint BFT: Provides Byzantine fault-tolerant consensus
   - Validator Roles: Cognitive Miner, State Validator, Conflict Resolver, Watchdog

Module Structure:
-----------------

core/cosmos/
├── __init__.py              # This file
├── types/                   # Core types for CLE-Net
│   └── __init__.py         # CognitiveLaw, CCS, ValidatorInfo, etc.
├── x/                       # Cosmos SDK modules
│   ├── cognitive/          # Cognitive law management
│   │   └── __init__.py     # CognitiveModule, CognitiveKeeper
│   ├── laws/               # Law storage and indexing
│   │   └── __init__.py     # LawsModule, LawsKeeper
│   └── consensus/          # Consensus and validators
│       └── __init__.py     # ConsensusModule, ProofOfCognition

Usage Example:
--------------

```python
from core.cosmos import CognitiveModule, ConsensusModule, LawsModule
from core.cosmos.types import LawType, LawStatus

# Initialize modules
cognitive_module = CognitiveModule()
consensus_module = ConsensusModule()
laws_module = LawsModule()

# Register a validator
from core.cosmos.types import ValidatorRole, RegisterValidatorMessage
msg = RegisterValidatorMessage(
    validator_address="validator1",
    role=ValidatorRole.COGNITIVE_MINER,
    stake=1000.0
)
consensus_module.handle_register_validator(msg)

# Propose a new law
from core.cosmos.x.cognitive import ProposeLawMessage
propose_msg = ProposeLawMessage(
    proposer_id="validator1",
    law_type=LawType.SYMBOLIC_RULE,
    symbolic_expression="IF user_requests_help THEN provide_assistance",
    context="customer_service",
    evidence=["ticket_123", "ticket_456"],
    confidence=0.8
)
law = cognitive_module.handle_propose_law(propose_msg)

# Validate the law
from core.cosmos.x.cognitive import ValidateLawMessage
validate_msg = ValidateLawMessage(
    validator_id="validator2",
    law_id=law.law_id,
    vote=True,
    reason="Law is well-formed and supported by evidence"
)
cognitive_module.handle_validate_law(validate_msg)
```

Validator Roles:
----------------

1. Cognitive Miner:
   - Discovers new cognitive laws from interaction data
   - Proposes laws for validation
   - Earns CCS for successful discoveries

2. State Validator:
   - Validates proposed laws
   - Votes on law activation
   - Ensures law integrity

3. Conflict Resolver:
   - Detects conflicts between laws
   - Proposes conflict resolutions
   - Manages context boundaries

4. Watchdog:
   - Monitors network health
   - Detects stalled blocks
   - Reports anomalies

Proof of Cognition (PoC):
-------------------------

PoC is CLE-Net's consensus mechanism that rewards independent discovery
of cognitive laws. Key principles:

1. Independent Discovery: Laws must be discovered by multiple independent parties
2. Cognitive Contribution: Contributors earn CCS based on quality and impact
3. Consensus Validation: 2/3 supermajority required for law activation
4. Fork Tolerance: Temporary divergence is acceptable for research

Migration Path:
---------------

Phase 1 (Current): Cosmos SDK v1
- Application-specific blockchain
- Native cognitive state machine
- Tendermint BFT consensus

Phase 2 (Future): Custom Chain
- Optimized consensus for cognitive workloads
- Custom state transition logic
- Enhanced PoC mechanism

Phase 3 (Future): IBC Integration
- Interoperability with other Cosmos chains
- Cross-chain cognitive state sharing
- Distributed cognition across networks

References:
-----------

- Cosmos SDK: https://docs.cosmos.network/
- Tendermint: https://docs.tendermint.com/
- IBC Protocol: https://ibc.cosmos.network/

License:
--------

This code is part of the CLE-Net project.
See LICENSE file for details.
"""

__version__ = "0.1.0"
__author__ = "CLE-Net Contributors"

# Export main modules
from .types import (
    CognitiveLaw,
    CognitiveContributionScore,
    CognitiveStateBlock,
    ValidatorInfo,
    ConflictResolution,
    LawStatus,
    LawType,
    ValidatorRole,
    MessageType
)

from .x.cognitive import (
    CognitiveModule,
    CognitiveKeeper,
    ProposeLawMessage,
    ValidateLawMessage,
    ReportConflictMessage,
    ResolveConflictMessage,
    UpdateCCSMessage
)

from .x.laws import (
    LawsModule,
    LawsKeeper
)

from .x.consensus import (
    ConsensusModule,
    ConsensusKeeper,
    RegisterValidatorMessage,
    UpdateValidatorMessage,
    ProofOfCognition
)

__all__ = [
    # Types
    "CognitiveLaw",
    "CognitiveContributionScore",
    "CognitiveStateBlock",
    "ValidatorInfo",
    "ConflictResolution",
    "LawStatus",
    "LawType",
    "ValidatorRole",
    "MessageType",
    # Cognitive Module
    "CognitiveModule",
    "CognitiveKeeper",
    "ProposeLawMessage",
    "ValidateLawMessage",
    "ReportConflictMessage",
    "ResolveConflictMessage",
    "UpdateCCSMessage",
    # Laws Module
    "LawsModule",
    "LawsKeeper",
    # Consensus Module
    "ConsensusModule",
    "ConsensusKeeper",
    "RegisterValidatorMessage",
    "UpdateValidatorMessage",
    "ProofOfCognition"
]
