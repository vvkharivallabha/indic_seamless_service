#!/usr/bin/env python3
"""
Free Tier Deployment Solution for Indic-Seamless Service
Uses existing FastAPI code and deploys on AWS Free Tier (no costs)
"""

import json
import os
from typing import Any, Dict

import boto3


class FreeTierDeployer:
    """
    Deploy Indic-Seamless service using only AWS Free Tier resources.

    This approach uses:
    - EC2 t2.micro instance (free tier eligible)
    - EBS gp2 storage (30GB free tier)
    - CloudWatch logs (free tier)
    - No Lambda, SageMaker, or other paid services
    """

    def __init__(self, region: str = "us-east-1"):
        self.region = region
        self.ec2 = boto3.client("ec2", region_name=region)
        self.ssm = boto3.client("ssm", region_name=region)
        self.logs = boto3.client("logs", region_name=region)

        # Configuration
        self.key_name = "indic-seamless-key"
        self.security_group_name = "indic-seamless-sg"
        self.instance_name = "indic-seamless-instance"

    def create_key_pair(self) -> str:
        """Create EC2 key pair for SSH access."""
        print("🔑 Creating EC2 key pair...")

        try:
            # Check if key already exists
            existing_keys = self.ec2.describe_key_pairs()["KeyPairs"]
            if any(key["KeyName"] == self.key_name for key in existing_keys):
                print(f"✅ Key pair {self.key_name} already exists")
                return self.key_name

            # Create new key pair
            response = self.ec2.create_key_pair(KeyName=self.key_name)

            # Save private key to file
            key_file = f"{self.key_name}.pem"
            with open(key_file, "w") as f:
                f.write(response["KeyMaterial"])

            # Set proper permissions
            os.chmod(key_file, 0o400)

            print(f"✅ Created key pair: {self.key_name}")
            print(f"   Private key saved to: {key_file}")
            print(f"   Use: ssh -i {key_file} ec2-user@<instance-ip>")

            return self.key_name

        except Exception as e:
            print(f"❌ Error creating key pair: {e}")
            raise

    def create_security_group(self) -> str:
        """Create security group for the service."""
        print("🔒 Creating security group...")

        try:
            # Check if security group already exists
            try:
                response = self.ec2.describe_security_groups(
                    Filters=[
                        {"Name": "group-name", "Values": [self.security_group_name]}
                    ]
                )
                if response["SecurityGroups"]:
                    sg_id = response["SecurityGroups"][0]["GroupId"]
                    print(
                        f"✅ Security group {self.security_group_name} "
                        f"already exists: {sg_id}"
                    )
                    return sg_id
            except Exception:
                pass

            # Create security group
            response = self.ec2.create_security_group(
                GroupName=self.security_group_name,
                Description="Security group for Indic-Seamless service",
            )
            sg_id = response["GroupId"]

            # Add ingress rules
            self.ec2.authorize_security_group_ingress(
                GroupId=sg_id,
                IpPermissions=[
                    {
                        "IpProtocol": "tcp",
                        "FromPort": 22,
                        "ToPort": 22,
                        "IpRanges": [
                            {"CidrIp": "0.0.0.0/0", "Description": "SSH access"}
                        ],
                    },
                    {
                        "IpProtocol": "tcp",
                        "FromPort": 8000,
                        "ToPort": 8000,
                        "IpRanges": [
                            {"CidrIp": "0.0.0.0/0", "Description": "FastAPI service"}
                        ],
                    },
                ],
            )

            print(f"✅ Created security group: {sg_id}")
            return sg_id

        except Exception as e:
            print(f"❌ Error creating security group: {e}")
            raise

    def create_user_data_script(self) -> str:
        """Create user data script for EC2 instance setup."""
        return """#!/bin/bash
# User data script for Indic-Seamless service setup
yum update -y
yum install -y python3 python3-pip git docker

# Install system dependencies for audio processing
yum install -y ffmpeg libsndfile sox

# Install Docker Compose
DOCKER_COMPOSE_URL="https://github.com/docker/compose/releases/latest/download"
curl -L "$DOCKER_COMPOSE_URL/docker-compose-$(uname -s)-$(uname -m)" \\
    -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Start Docker service
systemctl start docker
systemctl enable docker

# Add ec2-user to docker group
usermod -a -G docker ec2-user

# Create application directory
mkdir -p /home/ec2-user/indic-seamless
cd /home/ec2-user/indic-seamless

# Create deployment script that uses existing pyproject.toml
cat > /home/ec2-user/deploy_service.sh << 'EOF'
#!/bin/bash
set -e

cd /home/ec2-user/indic-seamless

# Check if we have the source code
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Source code not found. Please upload the code first."
    echo "Instructions:"
    echo "1. Clone: git clone <your-repo-url> ."
    echo "2. Or upload via scp: scp -i indic-seamless-key.pem -r . \\"
    echo "   ec2-user@<instance-ip>:/home/ec2-user/indic-seamless/"
    exit 1
fi

# Check for HF_TOKEN
if [ -z "$HF_TOKEN" ]; then
    echo "❌ HF_TOKEN not set. Please set it in \\"
    echo "   /home/ec2-user/indic-seamless/.env"
    exit 1
fi

echo "🔧 Installing dependencies from pyproject.toml..."
pip3 install -e .

echo "🚀 Starting service..."
export PORT=8000
export HOST=0.0.0.0

# Use the existing start_service.py
python3 start_service.py
EOF

chmod +x /home/ec2-user/deploy_service.sh
chown ec2-user:ec2-user /home/ec2-user/deploy_service.sh

# Create systemd service for auto-start
cat > /etc/systemd/system/indic-seamless.service << 'EOF'
[Unit]
Description=Indic-Seamless Speech-to-Text Service
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user/indic-seamless
ExecStart=/home/ec2-user/deploy_service.sh
Restart=always
RestartSec=10
EnvironmentFile=-/home/ec2-user/indic-seamless/.env

[Install]
WantedBy=multi-user.target
EOF

# Enable the service (but don't start it yet - user needs to upload code and 
# configure HF_TOKEN)
systemctl enable indic-seamless

# Install CloudWatch agent for monitoring
yum install -y amazon-cloudwatch-agent

# Create setup instructions
cat > /home/ec2-user/SETUP_INSTRUCTIONS.md << 'EOF'
# Indic-Seamless Service Setup Instructions

## 1. Upload Source Code
Choose one of these methods:

### Method A: Git Clone (Recommended)
```bash
cd /home/ec2-user/indic-seamless
git clone https://github.com/YOUR-USERNAME/indic_seamless_service.git .
```

### Method B: SCP Upload
From your local machine:
```bash
scp -i indic-seamless-key.pem -r ./src ./pyproject.toml ./start_service.py \\
    ec2-user@<INSTANCE-IP>:/home/ec2-user/indic-seamless/
```

## 2. Configure Environment
```bash
cd /home/ec2-user/indic-seamless
cp env.example .env
# Edit .env file and set your HF_TOKEN
nano .env
```

## 3. Start Service
```bash
sudo systemctl start indic-seamless
sudo systemctl status indic-seamless
```

## 4. Check Logs
```bash
sudo journalctl -u indic-seamless -f
```

## 5. Test Service
```bash
curl http://localhost:8000/health
curl http://localhost:8000/supported-languages
```

## 6. Access from Outside
Service will be available at: http://<INSTANCE-IP>:8000
EOF

chown ec2-user:ec2-user /home/ec2-user/SETUP_INSTRUCTIONS.md

echo "✅ EC2 instance setup complete!"
echo "📋 Setup instructions saved to /home/ec2-user/SETUP_INSTRUCTIONS.md"
echo ""
echo "Next steps:"
echo "1. SSH into the instance: ssh -i indic-seamless-key.pem ec2-user@<instance-ip>"
echo "2. Follow instructions in SETUP_INSTRUCTIONS.md"
echo "3. The service will install dependencies from pyproject.toml automatically"
"""

    def launch_instance(self, sg_id: str) -> Dict[str, Any]:
        """Launch EC2 instance."""
        print("🚀 Launching EC2 instance...")

        try:
            # Get latest Amazon Linux 2 AMI
            response = self.ec2.describe_images(
                Owners=["amazon"],
                Filters=[
                    {"Name": "name", "Values": ["amzn2-ami-hvm-*-x86_64-gp2"]},
                    {"Name": "state", "Values": ["available"]},
                ],
            )

            # Sort by creation date and get the latest
            images = sorted(
                response["Images"], key=lambda x: x["CreationDate"], reverse=True
            )
            ami_id = images[0]["ImageId"]

            print(f"📦 Using AMI: {ami_id} ({images[0]['Name']})")

            # Launch instance
            response = self.ec2.run_instances(
                ImageId=ami_id,
                MinCount=1,
                MaxCount=1,
                InstanceType="t2.micro",  # Free tier eligible
                KeyName=self.key_name,
                SecurityGroupIds=[sg_id],
                UserData=self.create_user_data_script(),
                BlockDeviceMappings=[
                    {
                        "DeviceName": "/dev/xvda",
                        "Ebs": {
                            "VolumeSize": 30,  # 30GB free tier
                            "VolumeType": "gp2",
                            "DeleteOnTermination": True,
                        },
                    }
                ],
                TagSpecifications=[
                    {
                        "ResourceType": "instance",
                        "Tags": [
                            {"Key": "Name", "Value": self.instance_name},
                            {"Key": "Project", "Value": "IndicSeamless"},
                            {"Key": "Environment", "Value": "Production"},
                            {"Key": "CostCenter", "Value": "FreeTier"},
                        ],
                    }
                ],
            )

            instance_id = response["Instances"][0]["InstanceId"]
            print(f"✅ Instance launched: {instance_id}")

            # Wait for instance to be running
            print("⏳ Waiting for instance to be running...")
            self.ec2.get_waiter("instance_running").wait(InstanceIds=[instance_id])

            # Get instance details
            response = self.ec2.describe_instances(InstanceIds=[instance_id])
            instance = response["Reservations"][0]["Instances"][0]

            instance_info = {
                "instance_id": instance_id,
                "public_ip": instance.get("PublicIpAddress"),
                "private_ip": instance.get("PrivateIpAddress"),
                "public_dns": instance.get("PublicDnsName"),
                "state": instance["State"]["Name"],
            }

            print("✅ Instance is running!")
            print(f"   Instance ID: {instance_info['instance_id']}")
            print(f"   Public IP: {instance_info['public_ip']}")
            print(f"   Public DNS: {instance_info['public_dns']}")

            return instance_info

        except Exception as e:
            print(f"❌ Error launching instance: {e}")
            raise

    def deploy(self) -> Dict[str, Any]:
        """Deploy the complete free tier solution."""
        print("🌟 Free Tier Deployment for Indic-Seamless Service")
        print("   Uses existing FastAPI code on EC2 t2.micro (FREE!)")
        print("=" * 60)

        try:
            # Step 1: Create key pair
            key_name = self.create_key_pair()

            # Step 2: Create security group
            sg_id = self.create_security_group()

            # Step 3: Launch instance
            instance_info = self.launch_instance(sg_id)

            # Step 4: Provide setup instructions
            self.print_setup_instructions(instance_info)

            deployment_info = {
                "deployment_type": "free_tier",
                "instance_info": instance_info,
                "key_name": key_name,
                "security_group_id": sg_id,
                "region": self.region,
                "estimated_monthly_cost": "$0.00 (Free Tier)",
            }

            return deployment_info

        except Exception as e:
            print(f"❌ Deployment failed: {e}")
            raise

    def print_setup_instructions(self, instance_info: Dict[str, Any]) -> None:
        """Print setup instructions for the user."""
        print("\n🎉 Free Tier Deployment Completed!")
        print("=" * 60)
        print("📋 Next Steps:")
        print()
        print("1. 🔐 SSH into your instance:")
        print(f"   ssh -i {self.key_name}.pem ec2-user@{instance_info['public_ip']}")
        print()
        print("2. 📂 Upload your code:")
        print(
            f"   scp -i {self.key_name}.pem -r . ec2-user@{instance_info['public_ip']}:/home/ec2-user/indic-seamless/"
        )
        print("   OR clone from GitHub:")
        print(
            "   git clone https://github.com/YOUR-USERNAME/indic_seamless_service.git /home/ec2-user/indic-seamless"
        )
        print()
        print("3. 🔑 Configure HuggingFace token:")
        print("   nano /home/ec2-user/deploy_service.sh")
        print("   # Replace YOUR_HF_TOKEN_HERE with your actual token")
        print()
        print("4. 🚀 Start the service:")
        print("   sudo systemctl start indic-seamless")
        print("   sudo systemctl status indic-seamless")
        print()
        print("5. 🌐 Test the service:")
        print(f"   curl http://{instance_info['public_ip']}:8000/health")
        print(f"   Open: http://{instance_info['public_ip']}:8000/docs")
        print()
        print("💰 Cost Information:")
        print("   - EC2 t2.micro: FREE for 12 months (750 hours/month)")
        print("   - EBS gp2 storage: FREE for 30GB")
        print("   - Data transfer: FREE for 15GB/month")
        print("   - CloudWatch: FREE tier included")
        print("   - Total estimated cost: $0.00/month")
        print()
        print("⚠️  Important Notes:")
        print("   - Free tier is valid for 12 months from AWS account creation")
        print("   - Stay within free tier limits to avoid charges")
        print("   - Monitor usage in AWS Cost Explorer")
        print("   - Instance will auto-start on reboot")
        print()
        print("🛑 To stop costs completely:")
        print(
            "   aws ec2 terminate-instances --instance-ids",
            instance_info["instance_id"],
        )


def main():
    """Main deployment function."""
    deployer = FreeTierDeployer()

    try:
        deployment_info = deployer.deploy()

        # Save deployment info
        with open("free_tier_deployment.json", "w") as f:
            json.dump(deployment_info, f, indent=2, default=str)

        print("📁 Deployment info saved to: free_tier_deployment.json")

    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
