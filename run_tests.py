#!/usr/bin/env python3

"""
Test runner for namegiver tests.

This script runs all the tests and reports the results.
"""

import os
import sys
import pytest

def main():
    """Run all the tests and report results."""
    print("Running namegiver tests...")
    
    # Run the unit tests
    print("\n=== Running unit tests ===")
    unit_test_result = pytest.main(["-xvs", "tests"])
    
    if unit_test_result != 0:
        print("\n❌ Unit tests failed")
        return unit_test_result
    
    print("\n✅ All unit tests passed")
    
    # Prompt user about integration tests
    print("\n=== Integration tests ===")
    print("Integration tests make real API calls to OpenAI and will consume tokens.")
    run_integration = input("Do you want to run integration tests? (y/N): ").lower() == 'y'
    
    if run_integration:
        # Check for API key
        from dotenv import load_dotenv
        load_dotenv()
        
        if not os.getenv("OPENAI_API_KEY"):
            print("\n❌ Integration tests skipped: OPENAI_API_KEY not set")
            print("Please set your API key in .env or environment variables.")
            return 0
        
        print("\nRunning context-aware generation integration test...")
        sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
        
        try:
            from examples.test_context_aware_integration import main as run_integration_test
            integration_result = run_integration_test()
            
            if not integration_result:
                print("\n❌ Integration test failed")
                return 1
                
            print("\n✅ Integration test passed")
            
        except Exception as e:
            print(f"\n❌ Integration test error: {str(e)}")
            return 1
    else:
        print("\nIntegration tests skipped")
    
    print("\n✅ All requested tests passed")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 