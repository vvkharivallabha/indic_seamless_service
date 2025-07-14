# Use the official AWS Lambda Python 3.10 base image
FROM public.ecr.aws/lambda/python:3.10

# Install system dependencies
RUN yum update -y && \
    yum install -y \
    git \
    gcc \
    g++ \
    make \
    cmake \
    wget \
    tar \
    gzip \
    ca-certificates \
    libsndfile \
    ffmpeg && \
    yum clean all

# Set environment variables
ENV PYTHONPATH="${LAMBDA_TASK_ROOT}:${PYTHONPATH}"
ENV HF_HOME="/tmp/huggingface"
ENV TRANSFORMERS_CACHE="/tmp/transformers"
ENV TORCH_HOME="/tmp/torch"
ENV MODEL_CACHE_DIR="/tmp/models"

# Create necessary directories
RUN mkdir -p /tmp/huggingface /tmp/transformers /tmp/torch /tmp/models

# Copy requirements file
COPY aws/lambda/requirements-lambda.txt ${LAMBDA_TASK_ROOT}/

# Install Python dependencies
RUN pip install --no-cache-dir -r ${LAMBDA_TASK_ROOT}/requirements-lambda.txt

# Copy the entire source code
COPY src/ ${LAMBDA_TASK_ROOT}/src/
COPY aws/lambda/handler.py ${LAMBDA_TASK_ROOT}/

# Copy environment configuration
COPY env.example ${LAMBDA_TASK_ROOT}/.env

# Set proper permissions
RUN chmod -R 755 ${LAMBDA_TASK_ROOT}

# Note: Pre-downloading the model would be ideal but increases build time significantly
# Models will be downloaded at runtime (first cold start will be slower)

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD ["handler.lambda_handler"] 