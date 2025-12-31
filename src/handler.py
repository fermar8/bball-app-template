import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """
    Lambda function handler for bball-app-template
    
    Args:
        event: Lambda event data
        context: Lambda context object
        
    Returns:
        dict: Response object with statusCode and body
    """
    logger.info("Processing template handler")
    logger.info(f"Event: {json.dumps(event)}")
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Success',
            'event': event
        })
    }
