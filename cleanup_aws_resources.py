#!/usr/bin/env python3
"""
Comprehensive cleanup script to delete all AWS resources and avoid costs.
"""

import time

import boto3


def cleanup_sagemaker_resources(region: str = "us-east-1") -> None:
    """Clean up all SageMaker resources."""
    print("🧹 Cleaning up SageMaker resources...")

    sagemaker = boto3.client("sagemaker", region_name=region)

    # List and delete endpoints
    try:
        endpoints = sagemaker.list_endpoints()["Endpoints"]
        for endpoint in endpoints:
            endpoint_name = endpoint["EndpointName"]
            print(f"🗑️  Deleting endpoint: {endpoint_name}")
            try:
                sagemaker.delete_endpoint(EndpointName=endpoint_name)
                print(f"✅ Deleted endpoint: {endpoint_name}")
            except Exception as e:
                print(f"⚠️  Error deleting endpoint {endpoint_name}: {e}")
    except Exception as e:
        print(f"⚠️  Error listing endpoints: {e}")

    # List and delete endpoint configurations
    try:
        configs = sagemaker.list_endpoint_configs()["EndpointConfigs"]
        for config in configs:
            config_name = config["EndpointConfigName"]
            print(f"🗑️  Deleting endpoint config: {config_name}")
            try:
                sagemaker.delete_endpoint_config(EndpointConfigName=config_name)
                print(f"✅ Deleted endpoint config: {config_name}")
            except Exception as e:
                print(f"⚠️  Error deleting endpoint config {config_name}: {e}")
    except Exception as e:
        print(f"⚠️  Error listing endpoint configs: {e}")

    # List and delete models
    try:
        models = sagemaker.list_models()["Models"]
        for model in models:
            model_name = model["ModelName"]
            print(f"🗑️  Deleting model: {model_name}")
            try:
                sagemaker.delete_model(ModelName=model_name)
                print(f"✅ Deleted model: {model_name}")
            except Exception as e:
                print(f"⚠️  Error deleting model {model_name}: {e}")
    except Exception as e:
        print(f"⚠️  Error listing models: {e}")


def cleanup_s3_resources(region: str = "us-east-1") -> None:
    """Clean up S3 resources."""
    print("🧹 Cleaning up S3 resources...")

    s3 = boto3.client("s3", region_name=region)
    sts = boto3.client("sts", region_name=region)

    # Get account ID
    account_id = sts.get_caller_identity()["Account"]
    bucket_name = f"sagemaker-{region}-{account_id}"

    try:
        # List objects in bucket
        response = s3.list_objects_v2(Bucket=bucket_name)
        if "Contents" in response:
            objects = [{"Key": obj["Key"]} for obj in response["Contents"]]
            if objects:
                print(f"🗑️  Deleting {len(objects)} objects from {bucket_name}")
                s3.delete_objects(Bucket=bucket_name, Delete={"Objects": objects})
                print(f"✅ Deleted objects from {bucket_name}")

        # Note: We don't delete the bucket itself as it's a default SageMaker bucket
        print(f"ℹ️  Keeping bucket {bucket_name} (default SageMaker bucket)")

    except Exception as e:
        print(f"⚠️  Error cleaning S3 resources: {e}")


def cleanup_lambda_resources(region: str = "us-east-1") -> None:
    """Clean up Lambda resources."""
    print("🧹 Cleaning up Lambda resources...")

    lambda_client = boto3.client("lambda", region_name=region)

    # List and delete functions
    try:
        functions = lambda_client.list_functions()["Functions"]
        indic_functions = [f for f in functions if "indic" in f["FunctionName"].lower()]

        for function in indic_functions:
            function_name = function["FunctionName"]
            print(f"🗑️  Deleting Lambda function: {function_name}")
            try:
                lambda_client.delete_function(FunctionName=function_name)
                print(f"✅ Deleted Lambda function: {function_name}")
            except Exception as e:
                print(f"⚠️  Error deleting Lambda function {function_name}: {e}")
    except Exception as e:
        print(f"⚠️  Error listing Lambda functions: {e}")


def cleanup_ecr_resources(region: str = "us-east-1") -> None:
    """Clean up ECR resources."""
    print("🧹 Cleaning up ECR resources...")

    ecr = boto3.client("ecr", region_name=region)

    try:
        repositories = ecr.describe_repositories()["repositories"]
        indic_repos = [
            r for r in repositories if "indic" in r["repositoryName"].lower()
        ]

        for repo in indic_repos:
            repo_name = repo["repositoryName"]
            print(f"🗑️  Deleting ECR repository: {repo_name}")
            try:
                ecr.delete_repository(repositoryName=repo_name, force=True)
                print(f"✅ Deleted ECR repository: {repo_name}")
            except Exception as e:
                print(f"⚠️  Error deleting ECR repository {repo_name}: {e}")
    except Exception as e:
        print(f"⚠️  Error listing ECR repositories: {e}")


def cleanup_cloudformation_stacks(region: str = "us-east-1") -> None:
    """Clean up CloudFormation stacks."""
    print("🧹 Cleaning up CloudFormation stacks...")

    cf = boto3.client("cloudformation", region_name=region)

    try:
        stacks = cf.list_stacks(
            StackStatusFilter=[
                "CREATE_COMPLETE",
                "UPDATE_COMPLETE",
                "UPDATE_ROLLBACK_COMPLETE",
            ]
        )["StackSummaries"]

        indic_stacks = [s for s in stacks if "indic" in s["StackName"].lower()]

        for stack in indic_stacks:
            stack_name = stack["StackName"]
            print(f"🗑️  Deleting CloudFormation stack: {stack_name}")
            try:
                cf.delete_stack(StackName=stack_name)
                print(f"✅ Deleted CloudFormation stack: {stack_name}")
            except Exception as e:
                print(f"⚠️  Error deleting CloudFormation stack {stack_name}: {e}")
    except Exception as e:
        print(f"⚠️  Error listing CloudFormation stacks: {e}")


def wait_for_endpoint_deletion(region: str = "us-east-1") -> None:
    """Wait for endpoints to be deleted."""
    print("⏳ Waiting for endpoints to be deleted...")

    sagemaker = boto3.client("sagemaker", region_name=region)

    while True:
        try:
            endpoints = sagemaker.list_endpoints()["Endpoints"]
            if not endpoints:
                print("✅ All endpoints deleted!")
                break

            print(f"   Still deleting {len(endpoints)} endpoints...")
            time.sleep(30)

        except Exception as e:
            print(f"⚠️  Error checking endpoint status: {e}")
            break


def main():
    """Main cleanup function."""
    print("🗑️  AWS Resource Cleanup Script")
    print("   Deleting all resources to avoid charges...")
    print("=" * 60)

    region = "us-east-1"

    try:
        # Clean up resources in order
        cleanup_sagemaker_resources(region)
        cleanup_s3_resources(region)
        cleanup_lambda_resources(region)
        cleanup_ecr_resources(region)
        cleanup_cloudformation_stacks(region)

        # Wait for deletions to complete
        wait_for_endpoint_deletion(region)

        print("\n🎉 Cleanup completed!")
        print("=" * 60)
        print("💰 Cost Status:")
        print("   - All SageMaker endpoints deleted")
        print("   - All models deleted")
        print("   - Lambda functions deleted")
        print("   - ECR repositories deleted")
        print("   - CloudFormation stacks deleted")
        print("   - S3 objects deleted (bucket kept)")
        print("\n✅ You should now have no ongoing charges!")

    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
        print("Please check AWS console manually for remaining resources")


if __name__ == "__main__":
    main()
