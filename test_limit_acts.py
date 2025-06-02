#!/usr/bin/env python3
import sys
import os
import subprocess
import json

# Add the src directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def run_data_retriever(args):
    """Run the data_retriever.py script with the given arguments and return the output."""
    cmd = ["python", "src/data_retriever.py"] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result

def test_limit_acts():
    """Test the --limit-acts parameter behavior."""
    print("Testing --limit-acts parameter...")

    # Test with limit-acts=5
    print("\nTest 1: --limit-acts 5")
    result = run_data_retriever(["--limit-acts", "5", "--search-document-type", "seadus", "--items-per-page", "100"])
    print(f"Exit code: {result.returncode}")
    print("Output:")
    print(result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout)
    print("Error:")
    print(result.stderr)

    # Test with limit-acts=450
    print("\nTest 2: --limit-acts 450")
    result = run_data_retriever(["--limit-acts", "450", "--search-document-type", "seadus", "--items-per-page", "100"])
    print(f"Exit code: {result.returncode}")
    print("Output:")
    print(result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout)
    print("Error:")
    print(result.stderr)

    print("\nTests completed.")

if __name__ == "__main__":
    test_limit_acts()