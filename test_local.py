"""
Local test script for the Lambda handler

Run this to test the handler locally without deploying to AWS.
"""

from src.handler import lambda_handler
import json


def test_local():
    """Test the Lambda handler with sample events"""
    
    # Test 1: Simple event
    print("=" * 60)
    print("Test 1: Simple event")
    print("=" * 60)
    event = {"test": "data", "value": 123}
    context = {}
    response = lambda_handler(event, context)
    print(f"Response: {json.dumps(response, indent=2)}\n")
    
    # Test 2: Empty event
    print("=" * 60)
    print("Test 2: Empty event")
    print("=" * 60)
    event = {}
    response = lambda_handler(event, context)
    print(f"Response: {json.dumps(response, indent=2)}\n")
    
    # Test 3: Complex nested event
    print("=" * 60)
    print("Test 3: Complex nested event")
    print("=" * 60)
    event = {
        "action": "process",
        "data": {
            "user": "test_user",
            "items": [1, 2, 3]
        }
    }
    response = lambda_handler(event, context)
    print(f"Response: {json.dumps(response, indent=2)}\n")
    
    print("=" * 60)
    print("All tests completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    test_local()
