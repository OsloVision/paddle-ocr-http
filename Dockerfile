FROM paddlepaddle/paddle:3.2.0

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-pip \
    wget \
    curl \
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