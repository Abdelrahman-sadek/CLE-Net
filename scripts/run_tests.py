#!/usr/bin/env python3
"""
CLE-Net Test Runner

This script runs all tests for CLE-Net.
"""

import sys
import unittest
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def run_tests():
    """Run all tests."""
    # Discover and run all tests
    loader = unittest.TestLoader()
    start_dir = Path(__file__).parent.parent / "tests"
    suite = loader.discover(start_dir, pattern="test_*.py")
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


def run_unit_tests():
    """Run unit tests only."""
    loader = unittest.TestLoader()
    start_dir = Path(__file__).parent.parent / "tests"
    suite = loader.discover(start_dir, pattern="test_*.py")
    
    # Filter out integration tests
    filtered_suite = unittest.TestSuite()
    for test_group in suite:
        for test in test_group:
            if "integration" not in str(test).lower():
                filtered_suite.addTest(test)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(filtered_suite)
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


def run_integration_tests():
    """Run integration tests only."""
    loader = unittest.TestLoader()
    start_dir = Path(__file__).parent.parent / "tests"
    suite = loader.discover(start_dir, pattern="test_integration.py")
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run CLE-Net tests")
    parser.add_argument(
        "--unit",
        action="store_true",
        help="Run unit tests only"
    )
    parser.add_argument(
        "--integration",
        action="store_true",
        help="Run integration tests only"
    )
    
    args = parser.parse_args()
    
    if args.unit:
        exit_code = run_unit_tests()
    elif args.integration:
        exit_code = run_integration_tests()
    else:
        exit_code = run_tests()
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
