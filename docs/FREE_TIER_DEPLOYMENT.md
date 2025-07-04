# 🆓 AWS Free Tier Deployment Guide

## Overview

This guide helps you deploy the Indic Seamless Service to AWS ECS using **AWS Free Tier** resources, which means it will be **completely free** for the first 12 months!

## 📊 Free Tier Configuration

| Resource            | Free Tier Limit  | Our Usage         |
| ------------------- | ---------------- | ----------------- |
| **ECS Fargate**     | 1000 hours/month | ~720 hours (24/7) |
| **CPU**             | 0.25 vCPU        | 0.25 vCPU ✅      |
| **Memory**          | 0.5 GB           | 0.5 GB ✅         |
| **ECR Storage**     | 500 MB           | ~100 MB ✅        |
| **ALB**             | 750 hours/month  | ~720 hours ✅     |
| **CloudWatch Logs** | 5 GB/month       | ~1 GB ✅          |

## ⚠️ Important Limitations

1. **Model Performance**: Limited to 0.5 GB memory - the ML model may have reduced performance
2. **Concurrent Users**: Very limited due to CPU constraints
3. **Response Time**: Slower responses due to resource limitations
4. **Not Production-Ready**: This is for testing and development only

## 🚀 Step-by-Step Deployment

### Step 1: Setup AWS Credentials

First, you need to create an AWS user with appropriate permissions:

1. **Go to AWS Console**: https://console.aws.amazon.com/iam/
2. **Create IAM User**: `indic-seamless-deploy-user`
3. **Attach Policies** (see full list in `docs/AWS_DEPLOYMENT_GUIDE.md`):

   - `AmazonECS_FullAccess`
   - `AmazonEC2ContainerRegistryFullAccess`
   - `CloudFormationFullAccess`
   - `AmazonVPCFullAccess`
   - `IAMFullAccess`
   - `ElasticLoadBalancingFullAccess`
   - `AmazonEC2ReadOnlyAccess`
   - `CloudWatchLogsFullAccess`

4. **Create Access Keys** and save them securely

### Step 2: Configure AWS CLI

```bash
# Configure AWS CLI with your credentials
aws configure

# Enter when prompted:
# AWS Access Key ID: [your access key]
# AWS Secret Access Key: [your secret key]
# Default region name: us-east-1
# Default output format: json

# Test the configuration
aws sts get-caller-identity
```

### Step 3: Deploy to Free Tier

```bash
# Navigate to your project directory
cd /path/to/indic_seamless_service

# Run the free tier deployment script
./aws/deploy-free-tier.sh
```

### Step 4: Wait for Deployment

The deployment will:

1. ✅ Check prerequisites
2. ✅ Create ECR repository
3. ✅ Build optimized Docker image
4. ✅ Push to ECR
5. ✅ Deploy CloudFormation stack
6. ✅ Wait for service to be ready (may take 10-20 minutes)

## 📋 What Gets Created

The deployment creates:

- **ECS Cluster**: `indic-seamless-service-cluster`
- **ECS Service**: `indic-seamless-service`
- **ECR Repository**: `indic-seamless-service`
- **Application Load Balancer**: `indic-seamless-service-alb`
- **CloudWatch Log Group**: `/ecs/indic-seamless-service`
- **IAM Roles**: For ECS task execution and permissions
- **Security Groups**: For ALB and container access

## 🔗 Access Your Service

After successful deployment, you'll get:

```bash
🎉 FREE TIER DEPLOYMENT COMPLETED SUCCESSFULLY!
═══════════════════════════════════════════════════════════════
Service URL: http://your-alb-dns-name.us-east-1.elb.amazonaws.com
Health check: http://your-alb-dns-name.us-east-1.elb.amazonaws.com/health
API documentation: http://your-alb-dns-name.us-east-1.elb.amazonaws.com/docs
Supported languages: http://your-alb-dns-name.us-east-1.elb.amazonaws.com/supported-languages
```

## 🧪 Testing Your Deployment

Test the service endpoints:

```bash
# Health check
curl http://your-service-url/health

# Supported languages
curl http://your-service-url/supported-languages

# API documentation (open in browser)
http://your-service-url/docs
```

## 💰 Cost Monitoring

### Free Tier Period (First 12 months)

- **Cost**: $0.00 (completely free!)
- **Usage**: Monitor through AWS Console

### After Free Tier (Month 13+)

- **Estimated Cost**: ~$8-12/month
- **ECS Fargate**: ~$6-8/month
- **Application Load Balancer**: ~$2-3/month
- **Other services**: ~$0.50/month

## 🚨 Troubleshooting

### Common Issues:

1. **Service won't start**:

   ```bash
   # Check CloudWatch logs
   aws logs tail /ecs/indic-seamless-service --follow
   ```

2. **Memory issues**:

   - The model may not fit in 512 MB
   - Consider using a smaller model variant
   - Check container logs for OOM errors

3. **Slow performance**:

   - This is expected with free tier resources
   - Consider upgrading to higher CPU/memory for production

4. **Deployment fails**:
   - Check AWS credentials and permissions
   - Verify default VPC exists
   - Check CloudFormation stack events

### Useful Commands:

```bash
# View CloudFormation stack
aws cloudformation describe-stacks --stack-name indic-seamless-free-tier

# View ECS service
aws ecs describe-services --cluster indic-seamless-service-cluster --services indic-seamless-service

# View logs
aws logs tail /ecs/indic-seamless-service --follow

# Delete deployment (cleanup)
aws cloudformation delete-stack --stack-name indic-seamless-free-tier
```

## 🔄 Updating Your Deployment

To update your service:

```bash
# Simply run the deployment script again
./aws/deploy-free-tier.sh
```

This will rebuild and redeploy with the latest changes.

## 🗑️ Cleanup (Delete Everything)

When you're done testing:

```bash
# Delete the CloudFormation stack
aws cloudformation delete-stack --stack-name indic-seamless-free-tier

# Delete ECR repository (optional)
aws ecr delete-repository --repository-name indic-seamless-service --force

# This will stop all charges
```

## 📈 Upgrading from Free Tier

If you need better performance, you can upgrade to:

```bash
# Use the regular deployment script with higher resources
./aws/deploy.sh

# Or modify the parameters in deploy-free-tier.sh:
# Change: Cpu="256" Memory="512"
# To: Cpu="512" Memory="1024" (or higher)
```

## 🎯 Performance Expectations

With free tier resources (0.25 vCPU, 0.5 GB memory):

- **Startup time**: 2-5 minutes
- **Response time**: 5-15 seconds per request
- **Concurrent users**: 1-2 maximum
- **Model accuracy**: May be reduced due to memory constraints

## 📚 Additional Resources

- [AWS Free Tier Details](https://aws.amazon.com/free/)
- [ECS Fargate Pricing](https://aws.amazon.com/fargate/pricing/)
- [CloudWatch Pricing](https://aws.amazon.com/cloudwatch/pricing/)
- [Full Deployment Guide](./AWS_DEPLOYMENT_GUIDE.md)

## 🤝 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review CloudWatch logs
3. Verify your AWS credentials and permissions
4. Ensure you're within free tier limits

Remember: This is a free tier deployment optimized for testing and development. For production use, consider upgrading to higher resource configurations.
