# Use official PaddlePaddle GPU image
# FROM ccr-2vdh3abv-pub.cnc.bj.baidubce.com/paddlepaddle/paddle:3.0.0-gpu-cuda11.8-cudnn8.9-trt8.6
FROM paddlepaddle/paddle:3.2.0

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-pip \
    wget \
    curl \
    # libgl1-mesa-dev \
    # libglib2.0-0 \
    # libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies with ignore-installed to handle PyYAML conflicts
RUN pip3 install --ignore-installed \
    fastapi==0.104.1 \
    uvicorn[standard]==0.24.0 \
    python-multipart==0.0.6 \
    paddleocr==3.2 \
    Pillow==10.0.0 \
    numpy==1.24.3 \
    opencv-python-headless==4.8.1.78 

# Set working directory
WORKDIR /app

# Copy application code
COPY app.py .

# Create necessary directories for PaddleX with proper permissions
RUN mkdir -p /root/.paddlex/temp && \
    chmod -R 755 /root/.paddlex

# Expose port
EXPOSE 5000

# Run the application
CMD ["python3", "app.py"]