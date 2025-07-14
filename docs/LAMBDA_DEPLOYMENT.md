# 🚀 AWS Lambda Deployment Guide

## Overview

This guide helps you deploy the Indic-Seamless Speech-to-Text Service to **AWS Lambda** with API Gateway for a serverless architecture. Lambda is ideal for intermittent usage patterns and can be more cost-effective than always-on ECS containers.

## 📊 Lambda vs ECS Comparison

| Aspect          | Lambda          | ECS Fargate          |
| --------------- | --------------- | -------------------- |
| **Cost Model**  | Pay per request | Pay per running time |
| **Cold Start**  | 10-30 seconds   | Always warm          |
| **Max Memory**  | 10,240 MB       | 30,720 MB            |
| **Max Timeout** | 15 minutes      | Unlimited            |
| **Scaling**     | Automatic       | Manual/Auto          |
| **Idle Cost**   | $0              | ~$50-60/month        |

## 💰 Cost Analysis

### Lambda Pricing (us-east-1)

- **Request charges**: $0.0000002 per request
- **Duration charges**: $0.0000166667 per GB-second
- **Free tier**: 1M requests + 400,000 GB-seconds per month

### Example Cost Scenarios

**Low Usage (100 requests/day)**:

- Memory: 10GB, Duration: 10 seconds average
- Monthly cost: ~$5-10
- **Savings vs ECS**: ~$40-50/month

**Medium Usage (1000 requests/day)**:

- Memory: 10GB, Duration: 10 seconds average
- Monthly cost: ~$50-80
- **Similar to ECS** cost

**High Usage (10,000 requests/day)**:

- Memory: 10GB, Duration: 10 seconds average
- Monthly cost: ~$500-800
- **More expensive than ECS**

## 🎯 When to Use Lambda

### ✅ Good for:

- **Intermittent usage** (< 1000 requests/day)
- **Development/testing** environments
- **Pay-per-use** billing preference
- **Automatic scaling** needs
- **No maintenance** preference

### ❌ Not ideal for:

- **High-volume production** (> 5000 requests/day)
- **Consistent high load** (always-on usage)
- **Sub-second response requirements**
- **Very large models** (> 4GB)

## 🏗️ Architecture

```
User Request → API Gateway → Lambda Function → Response
                    ↓
              CloudWatch Logs
```

### Components:

- **Lambda Function**: Serverless compute with ML model
- **API Gateway**: HTTP API with CORS support
- **ECR**: Container registry for Lambda image
- **CloudWatch**: Logging and monitoring
- **IAM Roles**: Security and permissions

## 🚀 Deployment Steps

### Step 1: Prerequisites

1. **AWS CLI configured** with appropriate permissions
2. **Docker** installed and running
3. **HuggingFace token** (for model access)

Required IAM permissions:

- `AWSLambda_FullAccess`
- `AmazonAPIGatewayFullAccess`
- `AmazonEC2ContainerRegistryFullAccess`
- `CloudFormationFullAccess`
- `IAMFullAccess`

### Step 2: Set Environment Variables

```bash
# Required: HuggingFace token for model access
export HF_TOKEN="your_huggingface_token_here"

# Optional: Customize deployment
export AWS_REGION="us-east-1"
export MEMORY_SIZE="10240"  # 10GB
export TIMEOUT="900"        # 15 minutes
```

### Step 3: Deploy to Lambda

```bash
# Navigate to project root
cd /path/to/indic_seamless_service

# Run deployment script
./aws/lambda/deploy-lambda.sh

# The script will:
# 1. Build Docker image for Lambda
# 2. Push to ECR
# 3. Deploy CloudFormation stack
# 4. Configure API Gateway
# 5. Set up monitoring
```

### Step 4: Test the Deployment

```bash
# Test health endpoint
curl https://your-api-id.execute-api.us-east-1.amazonaws.com/prod/health

# Test speech-to-text
curl -X POST \
  https://your-api-id.execute-api.us-east-1.amazonaws.com/prod/speech-to-text \
  -H "Content-Type: multipart/form-data" \
  -F "audio=@test_audio.wav" \
  -F "target_lang=en"
```

## 📋 Configuration Options

### Memory Settings

```bash
# Light usage (saves cost, slower performance)
export MEMORY_SIZE="3008"  # 3GB

# Balanced (recommended)
export MEMORY_SIZE="10240"  # 10GB

# Note: Lambda max is 10,240 MB
```

### Timeout Settings

```bash
# Short timeout (faster failure, lower cost)
export TIMEOUT="300"  # 5 minutes

# Long timeout (handles large files)
export TIMEOUT="900"  # 15 minutes (max)
```

### Environment Variables

Lambda function environment variables:

- `HF_TOKEN`: HuggingFace authentication token
- `MODEL_NAME`: Model identifier (ai4bharat/indic-seamless)
- `TRUST_REMOTE_CODE`: Enable remote code execution (true)
- `LOG_LEVEL`: Logging level (INFO, DEBUG, ERROR)

## 🔧 Management Commands

```bash
# View logs
./aws/lambda/deploy-lambda.sh logs

# Test function
./aws/lambda/deploy-lambda.sh test

# Update deployment (after code changes)
./aws/lambda/deploy-lambda.sh

# Delete deployment
./aws/lambda/deploy-lambda.sh cleanup
```

## 📊 Monitoring

### CloudWatch Metrics

- **Duration**: Function execution time
- **Memory**: Memory usage
- **Errors**: Error count and rate
- **Throttles**: Concurrency limits hit

### CloudWatch Alarms

Automatically created:

- **Error alarm**: Triggers on >5 errors in 10 minutes
- **Duration alarm**: Triggers on >5 minute average duration

### Viewing Logs

```bash
# Real-time logs
aws logs tail /aws/lambda/indic-seamless-lambda --follow

# Specific time range
aws logs tail /aws/lambda/indic-seamless-lambda --since 1h

# Search logs
aws logs filter-log-events \
  --log-group-name /aws/lambda/indic-seamless-lambda \
  --filter-pattern "ERROR"
```

## 🚨 Troubleshooting

### Common Issues

1. **Cold Start Timeout**

   - **Problem**: Function times out during first invocation
   - **Solution**: Increase timeout or pre-warm function

   ```bash
   # Increase timeout
   export TIMEOUT="900"
   ./aws/lambda/deploy-lambda.sh
   ```

2. **Memory Issues**

   - **Problem**: Function runs out of memory
   - **Solution**: Increase memory allocation

   ```bash
   # Increase memory
   export MEMORY_SIZE="10240"
   ./aws/lambda/deploy-lambda.sh
   ```

3. **Image Size Too Large**

   - **Problem**: Docker image exceeds Lambda limits
   - **Solution**: Optimize Dockerfile

   ```dockerfile
   # Remove unnecessary packages
   # Use multi-stage builds
   # Minimize layer sizes
   ```

4. **API Gateway 502 Errors**
   - **Problem**: Lambda function errors
   - **Solution**: Check CloudWatch logs
   ```bash
   aws logs tail /aws/lambda/indic-seamless-lambda --follow
   ```

### Debug Commands

```bash
# Check function configuration
aws lambda get-function --function-name indic-seamless-lambda

# Test function directly
aws lambda invoke \
  --function-name indic-seamless-lambda \
  --payload '{"httpMethod":"GET","path":"/health"}' \
  response.json

# Check API Gateway
aws apigateway get-rest-apis
```

## 🔄 Updates and Maintenance

### Updating Code

```bash
# After making code changes
./aws/lambda/deploy-lambda.sh

# This will rebuild and redeploy automatically
```

### Scaling Configuration

```bash
# Set reserved concurrency (optional)
aws lambda put-reserved-concurrency \
  --function-name indic-seamless-lambda \
  --reserved-concurrent-executions 10

# Set provisioned concurrency (reduces cold starts)
aws lambda put-provisioned-concurrency-config \
  --function-name indic-seamless-lambda \
  --provisioned-concurrent-executions 2
```

### Backup and Restore

```bash
# Export function code
aws lambda get-function \
  --function-name indic-seamless-lambda \
  --query 'Code.Location' \
  --output text

# Export CloudFormation template
aws cloudformation get-template \
  --stack-name indic-seamless-lambda-stack \
  --query 'TemplateBody' > backup-template.json
```

## 🔐 Security Best Practices

1. **IAM Roles**: Use least-privilege permissions
2. **Environment Variables**: Don't store secrets in plain text
3. **VPC**: Deploy in VPC for network isolation (optional)
4. **API Gateway**: Use API keys for access control
5. **CloudTrail**: Enable for audit logging

## 🚀 Performance Optimization

### Reduce Cold Starts

1. **Provisioned Concurrency**: Keep functions warm
2. **Smaller Images**: Optimize Docker image size
3. **Model Caching**: Pre-load models in container

### Improve Response Time

1. **Memory Allocation**: Higher memory = faster CPU
2. **Model Optimization**: Use quantized models
3. **Concurrent Processing**: Process multiple requests

## 📈 Migration from ECS

### Migration Steps

1. **Deploy Lambda** alongside ECS
2. **Test thoroughly** with same traffic
3. **Gradual traffic shift** using Route 53
4. **Monitor performance** and costs
5. **Decommission ECS** when confident

### Migration Considerations

- **Cold start impact** on user experience
- **Cost changes** based on usage patterns
- **Monitoring** and alerting updates
- **CI/CD pipeline** modifications

## 🗑️ Cleanup

### Delete Everything

```bash
# Delete Lambda deployment
./aws/lambda/deploy-lambda.sh cleanup

# Delete ECR repository
aws ecr delete-repository \
  --repository-name indic-seamless-lambda \
  --force

# This stops all charges
```

### Partial Cleanup

```bash
# Keep function, delete API Gateway
aws cloudformation delete-stack \
  --stack-name indic-seamless-lambda-stack

# Keep everything, just stop execution
aws lambda put-function-concurrency \
  --function-name indic-seamless-lambda \
  --reserved-concurrent-executions 0
```

## 🤝 Support

### Getting Help

- **CloudWatch Logs**: Primary debugging tool
- **AWS Support**: For platform issues
- **GitHub Issues**: For application bugs
- **Documentation**: This guide and AWS docs

### Useful Resources

- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [API Gateway Documentation](https://docs.aws.amazon.com/apigateway/)
- [Container Images in Lambda](https://docs.aws.amazon.com/lambda/latest/dg/images-create.html)
- [Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
