#!/usr/bin/env python3
"""
Test runner script for Kasa project.
Usage: python run_tests.py [options]
"""

import sys
import subprocess
import os

def run_tests():
    """Run pytest with appropriate configuration."""
    
    # Ensure we're in the project root
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_root)
    
    # Basic pytest command
    cmd = [sys.executable, "-m", "pytest"]
    
    # Add command line arguments if provided
    if len(sys.argv) > 1:
        cmd.extend(sys.argv[1:])
    else:
        # Default arguments for comprehensive testing
        cmd.extend([
            "tests/",
            "-v",
            "--tb=short",
            "--color=yes"
        ])
    
    print("Running Kasa tests...")
    print(f"Command: {' '.join(cmd)}")
    print("=" * 60)
    
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except KeyboardInterrupt:
        print("\nTest execution interrupted by user.")
        return 1
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1

def main():
    """Main entry point."""
    print("🔐 Kasa Test Runner")
    print("=" * 60)
    
    # Check if pytest is available
    try:
        import pytest
        print(f"✓ pytest version: {pytest.__version__}")
    except ImportError:
        print("✗ pytest not found. Please install it with: pip install pytest")
        return 1
    
    # Run tests
    exit_code = run_tests()
    
    print("=" * 60)
    if exit_code == 0:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed.")
    
    return exit_code

if __name__ == "__main__":
    sys.exit(main())
