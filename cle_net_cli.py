#!/usr/bin/env python3
"""
CLE-Net User-Friendly CLI Interface

A simple command-line interface for normal users to interact with CLE-Net.
This interface allows users to:
- Process AI-generated data
- Discover cognitive laws
- Participate in the CLE-Net network
"""

import sys
import os
import json
import argparse
from datetime import datetime
from typing import List, Dict, Optional

# Import CLE-Net components
try:
    from core.agent import CLEAgent, SemanticAtomizer, RuleEngine
    from core.agent.agent import AgentConfig
    from core.chain import Ledger, ProofOfCognition
    from core.graph import KnowledgeGraph
    from core.cosmos import (
        CognitiveModule,
        CognitiveLaw,
        LawStatus,
        LawType,
        ValidatorInfo,
        ValidatorRole,
        ProposeLawMessage
    )
except ImportError:
    print("Error: CLE-Net package not found. Please install it first:")
    print("  pip install cle-net")
    sys.exit(1)


class CLENetCLI:
    """User-friendly CLI interface for CLE-Net."""
    
    def __init__(self, data_path: str = "./data"):
        """Initialize the CLI interface."""
        self.data_path = data_path
        self.agent = None
        self.ledger = None
        self.knowledge_graph = None
        self.cognitive_module = None
        
        # Create data directory if it doesn't exist
        os.makedirs(data_path, exist_ok=True)
        
    def initialize(self):
        """Initialize CLE-Net components."""
        print("Initializing CLE-Net...")
        
        # Create agent
        config = AgentConfig(agent_id="user_agent")
        self.agent = CLEAgent(config=config, data_path=self.data_path)
        print(f"  Agent created: {self.agent.agent_id}")
        
        # Create ledger
        self.ledger = Ledger()
        print("  Blockchain ledger initialized")
        
        # Create knowledge graph
        self.knowledge_graph = KnowledgeGraph()
        print("  Knowledge graph initialized")
        
        # Create cognitive module
        self.cognitive_module = CognitiveModule()
        print("  Cognitive module initialized")
        
        print("CLE-Net initialized successfully!\n")
        
    def process_ai_data(self, data: str, source: str = "ai"):
        """
        Process AI-generated data and discover cognitive laws.
        
        Args:
            data: AI-generated text data
            source: Source of the data (e.g., "openai", "anthropic", "local")
        """
        print(f"Processing data from {source}...")
        print(f"  Data length: {len(data)} characters")
        
        # Process the interaction
        commits = self.agent.process_interaction(data)
        
        print(f"  Generated {len(commits)} rule commits")
        
        # Display discovered rules
        if commits:
            print("\nDiscovered Rules:")
            for i, commit in enumerate(commits, 1):
                print(f"  {i}. Rule Hash: {commit['rule_hash'][:16]}...")
                print(f"     Confidence: {commit['confidence']:.2f}")
                print(f"     Timestamp: {datetime.fromtimestamp(commit['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}")
        
        return commits
    
    def process_file(self, file_path: str):
        """
        Process data from a file.
        
        Args:
            file_path: Path to the file containing data
        """
        print(f"Processing file: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = f.read()
            
            commits = self.process_ai_data(data, source=f"file:{file_path}")
            
            # Save results
            output_file = file_path.replace('.txt', '_results.json')
            results = {
                'file': file_path,
                'processed_at': datetime.now().isoformat(),
                'commits': commits
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2)
            
            print(f"\nResults saved to: {output_file}")
            
        except FileNotFoundError:
            print(f"Error: File not found: {file_path}")
        except Exception as e:
            print(f"Error processing file: {e}")
    
    def process_ai_api(self, api_key: str, prompt: str, api_provider: str = "openai"):
        """
        Process data from an AI API.
        
        Args:
            api_key: API key for the AI service
            prompt: Prompt to send to the AI
            api_provider: AI API provider (openai, anthropic, etc.)
        """
        print(f"Processing data from {api_provider} API...")
        
        try:
            if api_provider.lower() == "openai":
                from openai import OpenAI
                client = OpenAI(api_key=api_key)
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1000
                )
                data = response.choices[0].message.content
            elif api_provider.lower() == "anthropic":
                import anthropic
                client = anthropic.Anthropic(api_key=api_key)
                response = client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=1000,
                    messages=[{"role": "user", "content": prompt}]
                )
                data = response.content[0].text
            else:
                print(f"Error: Unsupported API provider: {api_provider}")
                return
            
            print(f"  Received {len(data)} characters from {api_provider}")
            commits = self.process_ai_data(data, source=api_provider)
            
            # Save results
            output_file = f"{api_provider}_results.json"
            results = {
                'api_provider': api_provider,
                'prompt': prompt,
                'processed_at': datetime.now().isoformat(),
                'commits': commits
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2)
            
            print(f"\nResults saved to: {output_file}")
            
        except ImportError:
            print(f"Error: {api_provider} library not installed.")
            print(f"  Install with: pip install {api_provider}")
        except Exception as e:
            print(f"Error processing {api_provider} API: {e}")
    
    def interactive_mode(self):
        """Run CLE-Net in interactive mode."""
        print("\n" + "=" * 70)
        print("CLE-Net Interactive Mode")
        print("=" * 70)
        print("Type 'help' for available commands or 'exit' to quit.\n")
        
        while True:
            try:
                user_input = input("CLE-Net> ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['exit', 'quit']:
                    print("Exiting CLE-Net...")
                    break
                
                if user_input.lower() == 'help':
                    self.show_help()
                    continue
                
                if user_input.lower() == 'status':
                    self.show_status()
                    continue
                
                # Process the input as data
                print("Processing input...")
                commits = self.process_ai_data(user_input, source="interactive")
                
                if commits:
                    print(f"\n{len(commits)} rule(s) discovered!")
                else:
                    print("\nNo rules discovered from this input.")
                
            except KeyboardInterrupt:
                print("\n\nExiting CLE-Net...")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    def show_help(self):
        """Display help information."""
        print("\nAvailable Commands:")
        print("  help     - Show this help message")
        print("  status   - Show current status")
        print("  exit     - Exit interactive mode")
        print("\nOr simply type any text to process it and discover cognitive laws.\n")
    
    def show_status(self):
        """Display current status."""
        status = self.agent.get_status()
        print("\nCLE-Net Status:")
        print(f"  Agent ID: {status['agent_id']}")
        print(f"  Events Processed: {status['events_processed']}")
        print(f"  Symbols Buffered: {status['symbols_buffered']}")
        print(f"  Pending Commits: {status['pending_commits']}")
        print(f"  Accepted Rules: {status['accepted_rules']}")
        print(f"  Uptime: {status['uptime_seconds']:.2f} seconds\n")
    
    def export_results(self, output_file: str = "cle_net_results.json"):
        """Export all discovered rules to a file."""
        print(f"Exporting results to {output_file}...")
        
        results = {
            'exported_at': datetime.now().isoformat(),
            'agent_id': self.agent.agent_id,
            'status': self.agent.get_status(),
            'pending_commits': self.agent.state.pending_commits,
            'current_rules': self.agent.state.current_rules
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        
        print(f"Results exported successfully to {output_file}")


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="CLE-Net - Cognitive Logic Extraction Network",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python cle_net_cli.py
  
  # Process a file
  python cle_net_cli.py --file data.txt
  
  # Process AI API data
  python cle_net_cli.py --api openai --api-key YOUR_KEY --prompt "Analyze customer support interactions"
  
  # Export results
  python cle_net_cli.py --export results.json
        """
    )
    
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Run in interactive mode'
    )
    
    parser.add_argument(
        '--file', '-f',
        type=str,
        help='Process data from a file'
    )
    
    parser.add_argument(
        '--api',
        type=str,
        choices=['openai', 'anthropic'],
        help='AI API provider to use'
    )
    
    parser.add_argument(
        '--api-key',
        type=str,
        help='API key for the AI service'
    )
    
    parser.add_argument(
        '--prompt',
        type=str,
        help='Prompt to send to the AI API'
    )
    
    parser.add_argument(
        '--export', '-e',
        type=str,
        help='Export results to a file'
    )
    
    parser.add_argument(
        '--data-path',
        type=str,
        default='./data',
        help='Path to data directory (default: ./data)'
    )
    
    args = parser.parse_args()
    
    # Initialize CLI
    cli = CLENetCLI(data_path=args.data_path)
    cli.initialize()
    
    # Process based on arguments
    if args.interactive:
        cli.interactive_mode()
    elif args.file:
        cli.process_file(args.file)
    elif args.api and args.api_key and args.prompt:
        cli.process_ai_api(args.api_key, args.prompt, args.api)
    elif args.export:
        cli.export_results(args.export)
    else:
        # Default to interactive mode
        print("No arguments provided. Starting interactive mode...\n")
        cli.interactive_mode()


if __name__ == "__main__":
    main()
