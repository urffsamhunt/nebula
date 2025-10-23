# Use a slim Python image
FROM python:3.13-slim

# Do not write pyc files and ensure stdout/stderr is unbuffered
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system build dependencies required by some Python packages
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       gcc \
       git \
       curl \
       libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Expose app port
EXPOSE 8000

# Run the FastAPI app with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
