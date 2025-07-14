#!/bin/bash

# AWS Lambda Deployment Script for Indic-Seamless Service
# This script deploys the service to AWS Lambda with API Gateway

set -e

# Configuration
REGION="ap-south-1"
SERVICE_NAME="indic-seamless-lambda"
STACK_NAME="indic-seamless-lambda-stack"
ENVIRONMENT="production"
MEMORY_SIZE="3008"
TIMEOUT="900"
STAGE="prod"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        error "AWS CLI is not installed"
    fi
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed"
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        error "AWS credentials not configured"
    fi
    
    # Check if we're in the right directory
    if [ ! -f "aws/lambda/Dockerfile" ]; then
        error "Must be run from the project root directory"
    fi
    
    log "Prerequisites check passed ✅"
}

# Get AWS account ID
get_account_id() {
    aws sts get-caller-identity --query Account --output text
}

# Create ECR repository if it doesn't exist
create_ecr_repo() {
    local repo_name=$1
    log "Creating ECR repository: $repo_name"
    
    if aws ecr describe-repositories --repository-names "$repo_name" &> /dev/null; then
        info "ECR repository already exists"
    else
        aws ecr create-repository --repository-name "$repo_name" --region "$REGION"
        log "ECR repository created"
    fi
}

# Build and push Docker image
build_and_push_image() {
    local account_id=$(get_account_id)
    local repo_name="$SERVICE_NAME"
    local image_tag="latest"
    local full_image_name="$account_id.dkr.ecr.$REGION.amazonaws.com/$repo_name:$image_tag"
    
    log "Building Docker image..." >&2
    
    # Create ECR repo
    create_ecr_repo "$repo_name" >&2
    
    # Get ECR login
    aws ecr get-login-password --region "$REGION" | docker login --username AWS --password-stdin "$account_id.dkr.ecr.$REGION.amazonaws.com" >&2
    
    # Build image with proper platform
    docker buildx build \
        --platform linux/amd64 \
        -f aws/lambda/Dockerfile \
        -t "$full_image_name" \
        . >&2
    
    log "Pushing Docker image to ECR..." >&2
    docker push "$full_image_name" >&2
    
    log "Image pushed successfully: $full_image_name" >&2
    
    # Return only the image URI (no log messages)
    echo "$full_image_name"
}

# Deploy CloudFormation stack
deploy_stack() {
    local image_uri=$1
    local template_file="aws/lambda/cloudformation-lambda.yaml"
    
    log "Deploying CloudFormation stack..."
    
    # Check if stack exists
    if aws cloudformation describe-stacks --stack-name "$STACK_NAME" &> /dev/null; then
        info "Stack exists, updating..."
        
        aws cloudformation update-stack \
            --stack-name "$STACK_NAME" \
            --template-body file://"$template_file" \
            --capabilities CAPABILITY_NAMED_IAM \
            --parameters \
                "ParameterKey=ServiceName,ParameterValue=$SERVICE_NAME" \
                "ParameterKey=ImageUri,ParameterValue=$image_uri" \
                "ParameterKey=Environment,ParameterValue=$ENVIRONMENT" \
                "ParameterKey=MemorySize,ParameterValue=$MEMORY_SIZE" \
                "ParameterKey=Timeout,ParameterValue=$TIMEOUT" \
                "ParameterKey=Stage,ParameterValue=$STAGE" \
                "ParameterKey=HuggingFaceToken,ParameterValue=${HF_TOKEN:-}"
        
        log "Waiting for stack update to complete..."
        aws cloudformation wait stack-update-complete --stack-name "$STACK_NAME"
        
    else
        info "Stack doesn't exist, creating..."
        
        aws cloudformation create-stack \
            --stack-name "$STACK_NAME" \
            --template-body file://"$template_file" \
            --capabilities CAPABILITY_NAMED_IAM \
            --parameters \
                "ParameterKey=ServiceName,ParameterValue=$SERVICE_NAME" \
                "ParameterKey=ImageUri,ParameterValue=$image_uri" \
                "ParameterKey=Environment,ParameterValue=$ENVIRONMENT" \
                "ParameterKey=MemorySize,ParameterValue=$MEMORY_SIZE" \
                "ParameterKey=Timeout,ParameterValue=$TIMEOUT" \
                "ParameterKey=Stage,ParameterValue=$STAGE" \
                "ParameterKey=HuggingFaceToken,ParameterValue=${HF_TOKEN:-}"
        
        log "Waiting for stack creation to complete..."
        aws cloudformation wait stack-create-complete --stack-name "$STACK_NAME"
    fi
    
    log "Stack deployment completed ✅"
}

# Get stack outputs
get_stack_outputs() {
    log "Getting stack outputs..."
    
    local api_url=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --query 'Stacks[0].Outputs[?OutputKey==`ApiGatewayUrl`].OutputValue' \
        --output text)
    
    local lambda_arn=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --query 'Stacks[0].Outputs[?OutputKey==`LambdaFunctionArn`].OutputValue' \
        --output text)
    
    echo ""
    echo "🎉 Deployment completed successfully!"
    echo ""
    echo "📋 Service Information:"
    echo "  • Service Name: $SERVICE_NAME"
    echo "  • Region: $REGION"
    echo "  • Memory: ${MEMORY_SIZE}MB"
    echo "  • Timeout: ${TIMEOUT}s"
    echo ""
    echo "🌐 API Gateway URL:"
    echo "  $api_url"
    echo ""
    echo "🔧 Lambda Function ARN:"
    echo "  $lambda_arn"
    echo ""
    echo "📊 CloudWatch Logs:"
    echo "  aws logs tail /aws/lambda/$SERVICE_NAME --follow"
    echo ""
    echo "🧪 Test the service:"
    echo "  curl $api_url/health"
    echo ""
    echo "📝 View Lambda function:"
    echo "  aws lambda get-function --function-name $SERVICE_NAME"
    echo ""
}

# Cleanup function
cleanup() {
    log "Cleaning up..."
    # Any cleanup tasks can go here
}

# Main deployment function
main() {
    log "Starting Lambda deployment for Indic-Seamless Service"
    echo ""
    echo "🚀 Configuration:"
    echo "  • Service: $SERVICE_NAME"
    echo "  • Region: $REGION"
    echo "  • Environment: $ENVIRONMENT"
    echo "  • Memory: ${MEMORY_SIZE}MB"
    echo "  • Timeout: ${TIMEOUT}s"
    echo "  • Stage: $STAGE"
    echo ""
    
    # Check prerequisites
    check_prerequisites
    
    # Build and push image
    local image_uri=$(build_and_push_image)
    
    # Ensure we have the image URI
    if [ -z "$image_uri" ]; then
        error "Failed to get image URI"
    fi
    
    info "Using image URI: $image_uri"
    
    # Deploy stack
    deploy_stack "$image_uri"
    
    # Get outputs
    get_stack_outputs
    
    log "Lambda deployment completed successfully! 🎉"
}

# Handle script arguments
case "${1:-}" in
    "cleanup")
        log "Cleaning up Lambda deployment..."
        aws cloudformation delete-stack --stack-name "$STACK_NAME" || true
        log "Stack deletion initiated"
        ;;
    "logs")
        log "Viewing Lambda logs..."
        aws logs tail "/aws/lambda/$SERVICE_NAME" --follow
        ;;
    "test")
        log "Testing Lambda function..."
        local api_url=$(aws cloudformation describe-stacks \
            --stack-name "$STACK_NAME" \
            --query 'Stacks[0].Outputs[?OutputKey==`ApiGatewayUrl`].OutputValue' \
            --output text)
        curl "$api_url/health"
        ;;
    *)
        main
        ;;
esac 