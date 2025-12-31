import unittest
import json
from src.handler import lambda_handler


class TestHandler(unittest.TestCase):
    def test_lambda_handler_success(self):
        """Test that lambda_handler returns success response"""
        event = {"test": "data"}
        context = {}
        
        response = lambda_handler(event, context)
        
        self.assertEqual(response['statusCode'], 200)
        
        body = json.loads(response['body'])
        self.assertEqual(body['message'], 'Success')
        self.assertEqual(body['event'], event)
    
    def test_lambda_handler_empty_event(self):
        """Test lambda_handler with empty event"""
        event = {}
        context = {}
        
        response = lambda_handler(event, context)
        
        self.assertEqual(response['statusCode'], 200)


if __name__ == '__main__':
    unittest.main()
