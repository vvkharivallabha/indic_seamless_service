# AWS ECS Deployment Guide - IAM User Setup

## Required IAM Policies for ECS Deployment

### Core Required Policies (Attach these managed policies):

1. **AmazonECS_FullAccess**

   - Provides full access to Amazon ECS
   - Required for creating and managing ECS clusters, services, and tasks

2. **AmazonEC2ContainerRegistryFullAccess**

   - Provides full access to Amazon ECR
   - Required for pushing and pulling Docker images

3. **CloudFormationFullAccess**

   - Provides full access to AWS CloudFormation
   - Required for deploying infrastructure as code

4. **AmazonVPCFullAccess**

   - Provides full access to Amazon VPC
   - Required for network configuration

5. **IAMFullAccess**

   - Provides full access to IAM
   - Required for creating execution roles and task roles

6. **ElasticLoadBalancingFullAccess**

   - Provides full access to Elastic Load Balancing
   - Required for creating and managing Application Load Balancers

7. **AmazonEC2ReadOnlyAccess**

   - Provides read-only access to EC2
   - Required for querying VPC and subnet information

8. **CloudWatchLogsFullAccess**
   - Provides full access to CloudWatch Logs
   - Required for logging from ECS tasks

### Alternative: Custom Policy (More Restrictive)

If you prefer a more restrictive approach, you can create a custom policy with these permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecs:*",
        "ecr:*",
        "cloudformation:*",
        "iam:CreateRole",
        "iam:AttachRolePolicy",
        "iam:DetachRolePolicy",
        "iam:DeleteRole",
        "iam:GetRole",
        "iam:PassRole",
        "iam:ListRoles",
        "iam:ListAttachedRolePolicies",
        "ec2:DescribeVpcs",
        "ec2:DescribeSubnets",
        "ec2:DescribeSecurityGroups",
        "ec2:CreateSecurityGroup",
        "ec2:AuthorizeSecurityGroupIngress",
        "ec2:RevokeSecurityGroupIngress",
        "elasticloadbalancing:*",
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
        "logs:DescribeLogGroups",
        "logs:DescribeLogStreams",
        "application-autoscaling:*"
      ],
      "Resource": "*"
    }
  ]
}
```

## Step-by-Step IAM User Creation

### 1. Create the User

1. **Navigate to IAM Console**: https://console.aws.amazon.com/iam/
2. **Click "Users"** in the left sidebar
3. **Click "Create user"**
4. **Enter user details**:
   - User name: `indic-seamless-deploy-user`
   - Check "Provide user access to the AWS Management Console" (optional)
   - Set console password if needed
5. **Click "Next"**

### 2. Attach Policies

1. **Choose "Attach policies directly"**
2. **Search and select these policies**:
   - `AmazonECS_FullAccess`
   - `AmazonEC2ContainerRegistryFullAccess`
   - `CloudFormationFullAccess`
   - `AmazonVPCFullAccess`
   - `IAMFullAccess`
   - `ElasticLoadBalancingFullAccess`
   - `AmazonEC2ReadOnlyAccess`
   - `CloudWatchLogsFullAccess`
3. **Click "Next"**

### 3. Review and Create

1. **Review the user details and policies**
2. **Click "Create user"**

### 4. Create Access Keys

1. **Click on the newly created user**
2. **Go to "Security credentials" tab**
3. **Click "Create access key"**
4. **Choose "Command Line Interface (CLI)"**
5. **Check the confirmation box**
6. **Click "Next"**
7. **Add description tag (optional)**: "ECS deployment for Indic Seamless Service"
8. **Click "Create access key"**

### 5. Save Credentials

**⚠️ IMPORTANT**: Copy and save these credentials immediately (you won't be able to see the secret key again):

- **Access Key ID**: `AKIA...` (copy this)
- **Secret Access Key**: `...` (copy this)

## Configuration Commands

Once you have the credentials, configure AWS CLI:

```bash
# Configure AWS CLI
aws configure

# You'll be prompted for:
# AWS Access Key ID: [paste your access key]
# AWS Secret Access Key: [paste your secret key]
# Default region name: us-east-1
# Default output format: json
```

## Test Your Configuration

```bash
# Test credentials
aws sts get-caller-identity

# Test ECS access
aws ecs list-clusters

# Test ECR access
aws ecr describe-repositories --region us-east-1
```

## Security Best Practices

1. **Enable MFA**: Add multi-factor authentication to the user account
2. **Use Least Privilege**: Consider using the custom policy instead of full access policies
3. **Rotate Keys**: Regularly rotate access keys (every 90 days)
4. **Monitor Usage**: Use CloudTrail to monitor API calls
5. **Environment Variables**: Store credentials in environment variables, not in code

## Common Issues and Solutions

### Issue: "User is not authorized to perform: sts:AssumeRole"

**Solution**: Ensure IAMFullAccess policy is attached

### Issue: "No default VPC found"

**Solution**: Either create a default VPC or specify VPC ID explicitly in deployment

### Issue: "Repository does not exist"

**Solution**: The deployment script will create the ECR repository automatically

### Issue: "Access Denied" when pushing to ECR

**Solution**: Ensure AmazonEC2ContainerRegistryFullAccess policy is attached

## Next Steps

After creating the user and configuring credentials:

1. **Test the credentials**: `aws sts get-caller-identity`
2. **Run the deployment**: `cd aws && ./deploy.sh`
3. **Monitor the deployment**: Check CloudFormation console for stack progress
4. **Verify service**: Test the deployed service endpoints

## Deployment Commands

```bash
# Make the deployment script executable
chmod +x aws/deploy.sh

# Run the deployment
cd aws && ./deploy.sh

# Or run with custom parameters
SERVICE_NAME="my-service" AWS_REGION="us-west-2" ./deploy.sh
```

## Cost Considerations

- **ECS Fargate**: ~$0.04 per vCPU per hour + ~$0.004 per GB RAM per hour
- **Application Load Balancer**: ~$16-22 per month
- **ECR Storage**: ~$0.10 per GB per month
- **CloudWatch Logs**: ~$0.50 per GB ingested

For the default configuration (2 vCPU, 4GB RAM), expect ~$50-70 per month.
