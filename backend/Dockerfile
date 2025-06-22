# Use Python 3.11 as the base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TZ=America/Toronto \
    TF_CPP_MIN_LOG_LEVEL=2 \
    TF_FORCE_GPU_ALLOW_GROWTH=true \
    TF_ENABLE_AUTO_MIXED_PRECISION=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements files
COPY requirements.txt requirements_pip.txt ./

# Create and activate virtual environment
RUN python -m venv .venv
ENV PATH="/app/.venv/bin:$PATH"

# Upgrade pip and install wheel
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir wheel

# Install Python dependencies in stages to avoid conflicts
RUN pip install --no-cache-dir langchain requests python-dotenv && \
    pip install --no-cache-dir transformers torch && \
    pip install --no-cache-dir docarray tqdm fastapi uvicorn[standard] && \
    pip install --no-cache-dir accelerate && \
    pip install --no-cache-dir pymongo openrouteservice && \
    pip install --no-cache-dir colorlog groq langgraph langchain_community langchain-groq && \
    pip install --no-cache-dir tavily-python langgraph-checkpoint-sqlite geopy vectordb && \
    pip install --no-cache-dir "numpy<2" psycopg2-binary
# Create scripts directory and copy entrypoint script
RUN mkdir -p /app/scripts
COPY scripts/docker-entrypoint.sh /app/scripts/
RUN chmod +x /app/scripts/docker-entrypoint.sh

# Copy application code
COPY . .

# Expose the port your app runs on
EXPOSE 8000

# Set the working directory to src
WORKDIR /app/src

# Command to run the application
ENTRYPOINT ["/app/scripts/docker-entrypoint.sh"]
CMD ["/app/.venv/bin/uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 