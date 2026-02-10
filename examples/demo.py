#!/usr/bin/env python3
"""
CLE-Net Minimal MVP Demo

This script demonstrates the core functionality of CLE-Net:
1. Multiple agents discover rules independently
2. Rule commitments are broadcast
3. Consensus is achieved through Proof of Cognition

Run with: python examples/demo.py
"""

import sys
import os
import json
import time
import hashlib

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.agent import CLEAgent, AgentConfig
from core.chain import ProofOfCognition, Ledger


def simulate_agent(agent_id: str, data: str, confidence_threshold: float = 0.6) -> Dict:
    """
    Simulate a single CLE agent processing data and discovering rules.
    
    Args:
        agent_id: Unique agent identifier
        data: Text data to process
        confidence_threshold: Minimum confidence for rule submission
        
    Returns:
        Rule commitment dictionary
    """
    print(f"\n{'='*60}")
    print(f"Agent {agent_id} processing data...")
    print(f"{'='*60}")
    
    # Create agent
    config = AgentConfig(
        agent_id=agent_id,
        mode="full",
        confidence_threshold=confidence_threshold,
        min_coverage=0.05,
        min_support=2
    )
    
    agent = CLEAgent(config, data_path="")
    
    # Process the data
    commits = agent.process_interaction(data)
    
    # Get status
    status = agent.get_status()
    print(f"\nAgent {agent_id} processed {status['events_processed']} events")
    print(f"Generated {len(commits)} rule commits")
    
    if commits:
        print(f"\nDiscovered rules:")
        for commit in commits:
            print(f"  - Hash: {commit['rule_hash'][:32]}...")
            print(f"    Confidence: {commit['confidence']:.2f}")
            print(f"    Logic: {commit['logic_signature'][:16]}...")
    
    return commits


def main():
    """
    Run the CLE-Net MVP demo.
    
    This demo shows:
    1. Three independent agents processing different data
    2. Discovery of the same implicit rule
    3. Consensus through Proof of Cognition
    """
    print("\n" + "="*60)
    print("CLE-Net Minimal MVP Demo")
    print("Proof of Cognition: Independent Discovery & Consensus")
    print("="*60)
    
    # Define synthetic datasets
    # All contain the same implicit rule: VIP clients ignore short delays
    datasets = {
        "agent_1": """
            Customer support interactions:
            - VIP customer called about 2-day delay. We waived the penalty since they're important.
            - VIP customer inquiry about billing. Important client, expedited response.
            - Regular customer complained about 1-day delay. Normal processing applies.
            - VIP account holder requested refund. Important client, special handling.
            - Standard customer asked for discount. Regular policy applies.
            - VIP member reported shipping issue. Priority treatment for important clients.
            - Regular customer waited 3 days. Standard escalation process.
            - VIP client called about delay. Since it's only 2 days, we can ignore.
        """,
        
        "agent_2": """
            Sales call logs:
            - Premium customer with short delay. Account is VIP, so no penalty.
            - Standard client experiencing issues. Normal support channels.
            - VIP account holder, delay is minimal (less than 3 days). Exception granted.
            - High-priority client, important relationship. Flexibility allowed.
            - Regular customer, standard response time. No exceptions.
            - VIP enterprise account. Important client, expedited handling.
            - Standard retail customer, normal processing.
            - VIP client, short delay noted. Ignored per VIP policy.
        """,
        
        "agent_3": """
            Policy notes:
            - For VIP clients, short delays (< 3 days) are typically overlooked.
            - Standard clients follow regular delay policies.
            - Important accounts get flexibility on minor delays.
            - VIP status means minor issues can be waived.
            - Regular customers: no automatic exceptions.
            - Premium clients: always consider their importance.
            - Normal processing for standard delays and regular customers.
            - VIP exceptions for short delays are documented here.
        """
    }
    
    # Initialize consensus and ledger
    consensus = ProofOfCognition(
        min_agents=3,
        min_confidence=0.5,
        min_stability_hours=0  # Set to 0 for demo speed
    )
    
    ledger_path = "examples/demo_ledger.json"
    ledger = Ledger(ledger_path)
    
    print("\n" + "="*60)
    print("Phase 1: Independent Discovery")
    print("="*60)
    
    # Each agent processes its data independently
    all_commits = []
    
    for agent_id, data in datasets.items():
        commits = simulate_agent(agent_id, data)
        all_commits.extend(commits)
        
        # Add commits to consensus
        for commit in commits:
            consensus.add_commit(commit)
            ledger.add_commit(**commit)
    
    print("\n" + "="*60)
    print("Phase 2: Consensus Evaluation")
    print("="*60)
    
    # Run consensus
    results = consensus.run_consensus()
    
    print(f"\nConsensus Results:")
    print(f"  Total rule clusters: {len(results)}")
    
    for result in results:
        print(f"\n  Rule Hash: {result.rule_hash[:32]}...")
        print(f"  Status: {result.status.value}")
        print(f"  Confidence: {result.confidence:.2f}")
        print(f"  Supporting Agents: {', '.join(result.supporting_agents)}")
        print(f"  Reason: {result.reason}")
    
    # Check for consensus
    accepted = [r for r in results if r.status.value == 'accepted']
    
    print("\n" + "="*60)
    print("Phase 3: Results")
    print("="*60)
    
    if accepted:
        print(f"\n✅ CONSENSUS ACHIEVED!")
        print(f"   {len(accepted)} rule(s) accepted by the network")
        print("\n   This demonstrates:")
        print("   1. Independent discovery from different data sources")
        print("   2. Convergence on the same implicit rule")
        print("   3. No raw data was shared between agents")
        print("   4. Only rule hashes were committed to the ledger")
        
        print("\n   Accepted Rule(s):")
        for rule in accepted:
            print(f"   - {rule.rule_hash}")
            print(f"     Confidence: {rule.confidence:.2f}")
            print(f"     Agents: {', '.join(rule.supporting_agents)}")
    else:
        print("\n❌ No consensus reached")
        print("   This may be due to:")
        print("   - Insufficient matching rules")
        print("   - Confidence thresholds not met")
        print("   - Stability window not satisfied")
    
    # Show ledger statistics
    print("\n" + "="*60)
    print("Ledger Statistics")
    print("="*60)
    stats = ledger.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Verify ledger integrity
    valid, errors = ledger.verify_integrity()
    print(f"\n  Ledger Integrity: {'Valid' if valid else 'Invalid'}")
    if errors:
        for error in errors:
            print(f"    - {error}")
    
    print("\n" + "="*60)
    print("Demo Complete")
    print("="*60)
    
    return len(accepted) > 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
