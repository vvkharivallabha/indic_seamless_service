#!/bin/bash

# Indic-Seamless Service FREE TIER Deployment Script
# This script deploys the service to AWS ECS using AWS Free Tier limits
# FREE TIER LIMITS: 1000 hours of 0.25 vCPU + 0.5 GB memory per month

set -e

# Free Tier Configuration
SERVICE_NAME="indic-seamless-service"
AWS_REGION="us-east-1"
ECR_REPOSITORY_NAME="indic-seamless-service"
STACK_NAME="indic-seamless-free-tier"
ENVIRONMENT="development"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

print_free_tier_info() {
    echo -e "${BLUE}[FREE TIER]${NC} $1"
}

# Display free tier information
display_free_tier_info() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    print_free_tier_info "💰 COST-OPTIMIZED DEPLOYMENT (10GB)"
    echo "═══════════════════════════════════════════════════════════════"
    print_free_tier_info "Resource Configuration:"
    print_free_tier_info "  • CPU: 2 vCPU (2048 units)"
    print_free_tier_info "  • Memory: 10 GB (10240 MiB)"
    print_free_tier_info "  • ECS Fargate: ~$50-70/month (cost-optimized)"
    print_free_tier_info "  • ECR Storage: 500 MB free"
    print_free_tier_info "  • ALB: 750 hours/month free"
    print_free_tier_info "  • CloudWatch Logs: 5 GB/month free"
    echo ""
    print_free_tier_info "✅ OPTIMIZED: Sufficient resources for ML model!"
    print_free_tier_info "    This should handle the indic-seamless model properly."
    echo "═══════════════════════════════════════════════════════════════"
    echo ""
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
    
    print_status "Checking ECR repository..." >&2
    
    if ! aws ecr describe-repositories --repository-names "${ECR_REPOSITORY_NAME}" --region "${AWS_REGION}" >/dev/null 2>&1; then
        print_status "Creating ECR repository..." >&2
        aws ecr create-repository \
            --repository-name "${ECR_REPOSITORY_NAME}" \
            --region "${AWS_REGION}" >/dev/null
    else
        print_status "ECR repository already exists." >&2
    fi
    
    echo "${repository_uri}"
}

# Build and push Docker image optimized for free tier
build_and_push_image() {
    local repository_uri=$1
    local image_tag="free-tier"
    local full_image_name="${repository_uri}:${image_tag}"
    
    print_status "Building optimized Docker image for free tier (x86_64)..." >&2
    
    # Build with optimization flags for smaller memory footprint and x86_64 platform
    docker buildx build \
        --platform linux/amd64 \
        --tag "${full_image_name}" \
        --build-arg OPTIMIZE_FOR_SIZE=true \
        --load \
        . >&2
    
    print_status "Logging in to ECR..." >&2
    local ecr_host=$(echo "${repository_uri}" | cut -d'/' -f1)
    aws ecr get-login-password --region "${AWS_REGION}" | docker login --username AWS --password-stdin "${ecr_host}" >&2
    
    print_status "Pushing image to ECR..." >&2
    docker push "${full_image_name}" >&2
    
    # Clean up local image to save disk space
    docker rmi "${full_image_name}" >/dev/null 2>&1 || true
    
    # Return the correct image URI
    printf "%s" "${full_image_name}"
}

# Get VPC and subnet information
get_network_info() {
    print_status "Getting VPC and subnet information..." >&2
    
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

# Deploy CloudFormation stack with free tier configuration
deploy_stack() {
    local image_uri=$1
    local network_info=$2
    
    local vpc_id=$(echo "${network_info}" | cut -d':' -f1)
    local subnet_ids=$(echo "${network_info}" | cut -d':' -f2)
    
    print_status "Deploying CloudFormation stack with COST-OPTIMIZED configuration (10GB)..."
    
    # Convert subnet IDs to comma-separated format for CloudFormation
    local subnet_array=$(echo "${subnet_ids}" | tr '\t' ',' | sed 's/,$//')
    
    aws cloudformation deploy \
        --template-file aws/cloudformation.yaml \
        --stack-name "${STACK_NAME}" \
        --parameter-overrides \
            VpcId="${vpc_id}" \
            SubnetIds="${subnet_array}" \
            ServiceName="${SERVICE_NAME}" \
            ImageUri="${image_uri}" \
            Environment="${ENVIRONMENT}" \
            Cpu="2048" \
            Memory="10240" \
            DesiredCount="1" \
            ContainerPort="8000" \
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

# Wait for service to be ready (with extended timeout for free tier)
wait_for_service() {
    local service_url=$1
    
    print_status "Waiting for service to be ready..."
    print_warning "⏳ Model loading may take several minutes with 10GB memory..."
    
    local max_attempts=20  # Reasonable timeout for 10GB deployment
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
    print_warning "Check CloudWatch logs for detailed errors."
    return 1
}

# Display cost and usage information
display_cost_info() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    print_free_tier_info "💰 COST INFORMATION"
    echo "═══════════════════════════════════════════════════════════════"
    print_free_tier_info "Cost-optimized configuration (2 vCPU + 10GB):"
    print_free_tier_info ""
    print_free_tier_info "Monthly cost breakdown (if running 24/7):"
    print_free_tier_info "  • ECS Fargate (2 vCPU): ~$30-35/month"
    print_free_tier_info "  • ECS Fargate (10GB mem): ~$20-25/month"
    print_free_tier_info "  • ECR Storage: <$1/month (500 MB free)"
    print_free_tier_info "  • ALB: Free (750 hours/month free tier)"
    print_free_tier_info "  • CloudWatch Logs: Free (~1 GB within 5GB limit)"
    print_free_tier_info ""
    print_free_tier_info "📊 Total estimated cost: ~$50-60/month"
    echo "═══════════════════════════════════════════════════════════════"
    echo ""
}

# Main deployment function
main() {
    display_free_tier_info
    print_status "Starting COST-OPTIMIZED deployment of ${SERVICE_NAME}..."
    
    # Check prerequisites
    check_prerequisites
    
    # Create ECR repository
    local repository_uri=$(create_ecr_repository)
    
    # Build and push optimized image
    local image_uri=$(build_and_push_image "${repository_uri}")
    
    # Get network information
    local network_info=$(get_network_info)
    
    # Deploy stack
    deploy_stack "${image_uri}" "${network_info}"
    
    # Get service URL
    local service_url=$(get_service_url)
    
    # Wait for service to be ready
    if wait_for_service "${service_url}"; then
        echo ""
        echo "🎉 COST-OPTIMIZED DEPLOYMENT COMPLETED SUCCESSFULLY!"
        echo "═══════════════════════════════════════════════════════════════"
        print_status "Service URL: ${service_url}"
        print_status "Health check: ${service_url}/health"
        print_status "API documentation: ${service_url}/docs"
        print_status "Supported languages: ${service_url}/supported-languages"
        echo ""
        print_status "✅ ML model should run properly with 10GB memory!"
        print_warning "   Monitor costs - this is a paid deployment"
        echo ""
        display_cost_info
    else
        print_error "❌ COST-OPTIMIZED DEPLOYMENT FAILED!"
        print_status "Common troubleshooting steps:"
        print_status "  • Check CloudWatch logs for detailed errors"
        print_status "  • Verify Docker image architecture (x86_64)"
        print_status "  • Ensure HuggingFace token is valid"
        exit 1
    fi
}

# Run main function
main "$@" 