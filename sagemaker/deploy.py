#!/usr/bin/env python3
"""
SageMaker Deployment Script for Indic-Seamless Model
This script deploys the model to SageMaker endpoints.
"""

import os
import json
import logging
import boto3
import sagemaker
from sagemaker.pytorch import PyTorchModel
from sagemaker import get_execution_role
import tarfile
import tempfile
import shutil
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SageMakerDeployer:
    """Deployer class for SageMaker endpoints."""
    
    def __init__(self, region="us-east-1"):
        """
        Initialize the deployer.
        
        Args:
            region: AWS region
        """
        self.region = region
        self.sagemaker_session = sagemaker.Session()
        self.role = get_execution_role()
        
        # SageMaker client
        self.sm_client = boto3.client('sagemaker', region_name=region)
        
        # Configuration
        self.model_name = "indic-seamless-model"
        self.endpoint_name = "indic-seamless-endpoint"
        self.instance_type = "ml.g4dn.xlarge"  # GPU instance
        self.instance_count = 1
        
    def create_model_archive(self, output_path: str = "model.tar.gz"):
        """
        Create a model archive for SageMaker deployment.
        
        Args:
            output_path: Path to save the archive
        """
        logger.info("Creating model archive...")
        
        with tarfile.open(output_path, "w:gz") as tar:
            # Add inference script
            tar.add("inference.py", arcname="code/inference.py")
            
            # Add requirements
            tar.add("../env/requirements.txt", arcname="code/requirements.txt")
            
            # Create a simple model file (SageMaker will download the actual model)
            model_info = {
                "model_name": "ai4bharat/indic-seamless",
                "description": "Indic-Seamless model for multilingual speech and text processing"
            }
            
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
                json.dump(model_info, f)
                f.flush()
                tar.add(f.name, arcname="model_info.json")
                os.unlink(f.name)
        
        logger.info(f"Model archive created: {output_path}")
        return output_path
    
    def upload_model_to_s3(self, model_path: str) -> str:
        """
        Upload model archive to S3.
        
        Args:
            model_path: Path to the model archive
            
        Returns:
            S3 URI of the uploaded model
        """
        logger.info("Uploading model to S3...")
        
        bucket = self.sagemaker_session.default_bucket()
        model_key = f"models/{self.model_name}/model.tar.gz"
        
        s3_model_uri = f"s3://{bucket}/{model_key}"
        
        # Upload to S3
        self.sagemaker_session.upload_data(
            path=model_path,
            bucket=bucket,
            key_prefix=f"models/{self.model_name}"
        )
        
        logger.info(f"Model uploaded to: {s3_model_uri}")
        return s3_model_uri
    
    def create_model(self, s3_model_uri: str):
        """
        Create a SageMaker model.
        
        Args:
            s3_model_uri: S3 URI of the model
        """
        logger.info("Creating SageMaker model...")
        
        # Create PyTorch model
        pytorch_model = PyTorchModel(
            model_data=s3_model_uri,
            role=self.role,
            entry_point="inference.py",
            source_dir="code",
            framework_version="2.0.0",
            py_version="py310",
            env={
                "SAGEMAKER_PROGRAM": "inference.py",
                "SAGEMAKER_SUBMIT_DIRECTORY": "/opt/ml/code",
                "SAGEMAKER_CONTAINER_LOG_LEVEL": "20",
                "SAGEMAKER_REGION": self.region
            }
        )
        
        # Create the model
        self.model = pytorch_model.create(
            name=self.model_name,
            instance_type=self.instance_type
        )
        
        logger.info(f"Model created: {self.model.name}")
    
    def deploy_endpoint(self):
        """Deploy the model to a SageMaker endpoint."""
        logger.info("Deploying SageMaker endpoint...")
        
        # Deploy the model
        self.predictor = self.model.deploy(
            initial_instance_count=self.instance_count,
            instance_type=self.instance_type,
            endpoint_name=self.endpoint_name,
            wait=True
        )
        
        logger.info(f"Endpoint deployed: {self.endpoint_name}")
        return self.predictor
    
    def test_endpoint(self):
        """Test the deployed endpoint."""
        logger.info("Testing endpoint...")
        
        # Test translation
        test_data = {
            "task_type": "translate",
            "text": "Hello, how are you?",
            "source_lang": "en",
            "target_lang": "hi"
        }
        
        try:
            response = self.predictor.predict(test_data)
            result = json.loads(response)
            
            logger.info("Translation test successful!")
            logger.info(f"Original: {result['original_text']}")
            logger.info(f"Translated: {result['translated_text']}")
            
            return True
            
        except Exception as e:
            logger.error(f"Endpoint test failed: {e}")
            return False
    
    def delete_endpoint(self):
        """Delete the SageMaker endpoint."""
        logger.info("Deleting SageMaker endpoint...")
        
        try:
            self.sm_client.delete_endpoint(EndpointName=self.endpoint_name)
            self.sm_client.delete_endpoint_config(EndpointConfigName=self.endpoint_name)
            self.sm_client.delete_model(ModelName=self.model_name)
            
            logger.info("Endpoint deleted successfully")
            
        except Exception as e:
            logger.error(f"Error deleting endpoint: {e}")
    
    def get_endpoint_info(self):
        """Get information about the deployed endpoint."""
        try:
            response = self.sm_client.describe_endpoint(EndpointName=self.endpoint_name)
            
            info = {
                "endpoint_name": response["EndpointName"],
                "endpoint_arn": response["EndpointArn"],
                "status": response["EndpointStatus"],
                "creation_time": response["CreationTime"].isoformat(),
                "last_modified_time": response["LastModifiedTime"].isoformat()
            }
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting endpoint info: {e}")
            return None

def main():
    """Main deployment function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Deploy Indic-Seamless model to SageMaker")
    parser.add_argument("--region", default="us-east-1", help="AWS region")
    parser.add_argument("--instance-type", default="ml.g4dn.xlarge", help="SageMaker instance type")
    parser.add_argument("--delete", action="store_true", help="Delete existing endpoint")
    parser.add_argument("--test-only", action="store_true", help="Only test existing endpoint")
    
    args = parser.parse_args()
    
    # Initialize deployer
    deployer = SageMakerDeployer(region=args.region)
    deployer.instance_type = args.instance_type
    
    try:
        if args.delete:
            # Delete existing endpoint
            deployer.delete_endpoint()
            return
        
        if args.test_only:
            # Test existing endpoint
            deployer.test_endpoint()
            return
        
        # Full deployment
        logger.info("Starting SageMaker deployment...")
        
        # Create model archive
        model_path = deployer.create_model_archive()
        
        # Upload to S3
        s3_model_uri = deployer.upload_model_to_s3(model_path)
        
        # Create model
        deployer.create_model(s3_model_uri)
        
        # Deploy endpoint
        predictor = deployer.deploy_endpoint()
        
        # Test endpoint
        if deployer.test_endpoint():
            logger.info("🎉 Deployment completed successfully!")
            
            # Get endpoint info
            info = deployer.get_endpoint_info()
            if info:
                logger.info(f"Endpoint URL: https://runtime.sagemaker.{args.region}.amazonaws.com/endpoints/{info['endpoint_name']}/invocations")
                logger.info(f"Endpoint Status: {info['status']}")
        else:
            logger.error("❌ Deployment failed!")
        
        # Clean up model archive
        if os.path.exists(model_path):
            os.remove(model_path)
        
    except Exception as e:
        logger.error(f"Deployment failed: {e}")
        raise

if __name__ == "__main__":
    main() 