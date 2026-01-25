"""
Kaggle dataset ingestion job
Downloads Kaggle datasets and uploads to S3
"""
import json
import logging
import os
from datetime import datetime
from pathlib import Path

import boto3
from kaggle.api.kaggle_api_extended import KaggleApi

logger = logging.getLogger(__name__)


def _load_kaggle_credentials():
    """Load Kaggle credentials from Secrets Manager and set env vars"""
    secret_name = os.environ.get('KAGGLE_SECRET_NAME', 'kaggle-credentials')
    region = os.environ.get('AWS_REGION', 'eu-west-3')
    
    logger.info(f"Loading Kaggle credentials from secret: {secret_name}")
    
    client = boto3.client('secretsmanager', region_name=region)
    response = client.get_secret_value(SecretId=secret_name)
    
    secret = json.loads(response['SecretString'])
    os.environ['KAGGLE_USERNAME'] = secret['username']
    os.environ['KAGGLE_KEY'] = secret['key']
    
    # Force HOME to /tmp so all libraries (including Kaggle) think that's the user home
    # This bypasses any hardcoded checks for ~/.kaggle
    os.environ['HOME'] = '/tmp'
    os.environ['KAGGLE_CONFIG_DIR'] = '/tmp'
    
    # Create the config file in /tmp
    kaggle_json = Path('/tmp/kaggle.json')
    kaggle_json.write_text(json.dumps({
        'username': secret['username'],
        'key': secret['key']
    }))
    kaggle_json.chmod(0o600)
    
    logger.info("Kaggle credentials loaded successfully")


def _upload_to_s3(local_path: str, s3_key: str, bucket: str):
    """Upload file to S3"""
    logger.info(f"Uploading {local_path} to s3://{bucket}/{s3_key}")
    
    s3_client = boto3.client('s3')
    s3_client.upload_file(local_path, bucket, s3_key)
    
    logger.info(f"Upload completed: s3://{bucket}/{s3_key}")


def lambda_handler(event, context):
    """
    Lambda handler for Kaggle dataset ingestion
    
    Args:
        event: Lambda event (contains job identifier from EventBridge)
        context: Lambda context
        
    Returns:
        dict: Response with status and details
    """
    try:
        logger.info(f"Starting Kaggle ingestion job. Event: {json.dumps(event)}")
        
        # Get configuration from environment
        dataset_slug = os.environ.get('KAGGLE_DATASET')
        s3_bucket = os.environ.get('S3_DATA_BUCKET')
        s3_prefix = os.environ.get('S3_PREFIX', 'nba-data/kaggle')
        
        if not dataset_slug:
            raise ValueError("KAGGLE_DATASET environment variable not set")
        if not s3_bucket:
            raise ValueError("S3_DATA_BUCKET environment variable not set")
        
        logger.info(f"Dataset: {dataset_slug}, Bucket: {s3_bucket}, Prefix: {s3_prefix}")
        
        # Load Kaggle credentials
        _load_kaggle_credentials()
        
        # Initialize Kaggle API
        api = KaggleApi()
        api.authenticate()
        logger.info("Kaggle API authenticated")
        
        # Download dataset to /tmp
        download_path = '/tmp/kaggle'
        os.makedirs(download_path, exist_ok=True)
        
        logger.info(f"Downloading dataset {dataset_slug} to {download_path}")
        api.dataset_download_files(dataset_slug, path=download_path, unzip=False)
        
        # Find the downloaded zip file
        zip_files = list(Path(download_path).glob('*.zip'))
        if not zip_files:
            raise FileNotFoundError(f"No zip file found in {download_path}")
        
        zip_file = zip_files[0]
        logger.info(f"Found dataset file: {zip_file}")
        
        # Prepare S3 key with timestamp and dataset slug (replace / with __)
        timestamp = datetime.utcnow()
        date_folder = timestamp.strftime('%Y-%m-%d')
        time_stamp = timestamp.strftime('%H-%M-%S')
        
        # Convert dataset slug: eoinamoore/historical-nba-data -> eoinamoore__historical-nba-data
        dataset_name = dataset_slug.replace('/', '__')
        
        s3_key = f"{s3_prefix}/{dataset_name}/{date_folder}/{time_stamp}.zip"
        
        # Upload to S3
        _upload_to_s3(str(zip_file), s3_key, s3_bucket)
        
        # Cleanup
        zip_file.unlink()
        logger.info("Temporary file cleaned up")
        
        result = {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Kaggle dataset ingested successfully',
                'dataset': dataset_slug,
                's3_location': f"s3://{s3_bucket}/{s3_key}",
                'timestamp': timestamp.isoformat()
            })
        }
        
        logger.info(f"Job completed successfully: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error in Kaggle ingestion job: {e}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'message': 'Kaggle ingestion job failed'
            })
        }
