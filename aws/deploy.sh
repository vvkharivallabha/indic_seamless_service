#!/bin/bash

# Indic-Seamless Service Deployment Script
# This script builds, pushes, and deploys the service to AWS ECS

set -e

# Configuration
SERVICE_NAME="indic-seamless-service"
AWS_REGION="us-east-1"
ECR_REPOSITORY_NAME="indic-seamless-service"
STACK_NAME="indic-seamless-stack"
ENVIRONMENT="production"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    if ! command_exists docker; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command_exists aws; then
        print_error "AWS CLI is not installed. Please install AWS CLI first."
        exit 1
    fi
    
    if ! command_exists jq; then
        print_error "jq is not installed. Please install jq first."
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity >/dev/null 2>&1; then
        print_error "AWS credentials not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    print_status "Prerequisites check passed!"
}

# Get AWS account ID
get_account_id() {
    aws sts get-caller-identity --query Account --output text
}

# Create ECR repository if it doesn't exist
create_ecr_repository() {
    local account_id=$(get_account_id)
    local repository_uri="${account_id}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY_NAME}"
    
    print_status "Checking ECR repository..."
    
    if ! aws ecr describe-repositories --repository-names "${ECR_REPOSITORY_NAME}" --region "${AWS_REGION}" >/dev/null 2>&1; then
        print_status "Creating ECR repository..."
        aws ecr create-repository \
            --repository-name "${ECR_REPOSITORY_NAME}" \
            --region "${AWS_REGION}"
    else
        print_status "ECR repository already exists."
    fi
    
    echo "${repository_uri}"
}

# Build and push Docker image
build_and_push_image() {
    local repository_uri=$1
    local image_tag="latest"
    local full_image_name="${repository_uri}:${image_tag}"
    
    print_status "Building Docker image..."
    docker build -t "${full_image_name}" .
    
    print_status "Logging in to ECR..."
    aws ecr get-login-password --region "${AWS_REGION}" | docker login --username AWS --password-stdin "${repository_uri}"
    
    print_status "Pushing image to ECR..."
    docker push "${full_image_name}"
    
    echo "${full_image_name}"
}

# Get VPC and subnet information
get_network_info() {
    print_status "Getting VPC and subnet information..."
    
    # Get default VPC
    local vpc_id=$(aws ec2 describe-vpcs \
        --filters "Name=is-default,Values=true" \
        --query 'Vpcs[0].VpcId' \
        --output text \
        --region "${AWS_REGION}")
    
    # Get subnets in the VPC
    local subnet_ids=$(aws ec2 describe-subnets \
        --filters "Name=vpc-id,Values=${vpc_id}" \
        --query 'Subnets[*].SubnetId' \
        --output text \
        --region "${AWS_REGION}")
    
    echo "${vpc_id}:${subnet_ids}"
}

# Deploy CloudFormation stack
deploy_stack() {
    local repository_uri=$1
    local network_info=$2
    
    local vpc_id=$(echo "${network_info}" | cut -d':' -f1)
    local subnet_ids=$(echo "${network_info}" | cut -d':' -f2)
    
    print_status "Deploying CloudFormation stack..."
    
    # Convert subnet IDs to JSON array
    local subnet_array=$(echo "${subnet_ids}" | tr ' ' '\n' | jq -R . | jq -s .)
    
    aws cloudformation deploy \
        --template-file cloudformation.yaml \
        --stack-name "${STACK_NAME}" \
        --parameter-overrides \
            VpcId="${vpc_id}" \
            SubnetIds="${subnet_array}" \
            ServiceName="${SERVICE_NAME}" \
            ImageUri="${repository_uri}:latest" \
            Environment="${ENVIRONMENT}" \
            Cpu="2048" \
            Memory="4096" \
            DesiredCount="1" \
        --capabilities CAPABILITY_IAM \
        --region "${AWS_REGION}"
    
    print_status "Stack deployment completed!"
}

# Get service URL
get_service_url() {
    print_status "Getting service URL..."
    
    local service_url=$(aws cloudformation describe-stacks \
        --stack-name "${STACK_NAME}" \
        --query 'Stacks[0].Outputs[?OutputKey==`ServiceURL`].OutputValue' \
        --output text \
        --region "${AWS_REGION}")
    
    echo "${service_url}"
}

# Wait for service to be ready
wait_for_service() {
    local service_url=$1
    
    print_status "Waiting for service to be ready..."
    
    local max_attempts=30
    local attempt=1
    
    while [ ${attempt} -le ${max_attempts} ]; do
        if curl -f "${service_url}/health" >/dev/null 2>&1; then
            print_status "Service is ready!"
            return 0
        fi
        
        print_warning "Service not ready yet (attempt ${attempt}/${max_attempts})..."
        sleep 30
        attempt=$((attempt + 1))
    done
    
    print_error "Service failed to become ready within the expected time."
    return 1
}

# Main deployment function
main() {
    print_status "Starting deployment of ${SERVICE_NAME}..."
    
    # Check prerequisites
    check_prerequisites
    
    # Create ECR repository
    local repository_uri=$(create_ecr_repository)
    
    # Build and push image
    local image_uri=$(build_and_push_image "${repository_uri}")
    
    # Get network information
    local network_info=$(get_network_info)
    
    # Deploy stack
    deploy_stack "${image_uri}" "${network_info}"
    
    # Get service URL
    local service_url=$(get_service_url)
    
    # Wait for service to be ready
    if wait_for_service "${service_url}"; then
        print_status "Deployment completed successfully!"
        print_status "Service URL: ${service_url}"
        print_status "Health check: ${service_url}/health"
        print_status "API documentation: ${service_url}/supported-languages"
    else
        print_error "Deployment failed!"
        exit 1
    fi
}

# Run main function
main "$@" 