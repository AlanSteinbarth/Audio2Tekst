# ==============================================================================
# Audio2Tekst - Docker Image
# ==============================================================================
# 
# Professional audio-to-text transcription tool with AI summarization
# Built with Streamlit, OpenAI Whisper, and FFmpeg
# Cross-platform support: Windows, macOS, Linux
#
# Author: Alan Steinbarth (alan.steinbarth@gmail.com)
# GitHub: https://github.com/AlanSteinbarth/Audio2Tekst
# ==============================================================================

# Use Python 3.11 slim image for optimal performance and security
FROM python:3.11-slim

# Set metadata labels for the image
LABEL maintainer="alan.steinbarth@gmail.com"
LABEL version="2.3.0"
LABEL description="Audio2Tekst - Professional AI-powered audio transcription tool"
LABEL org.opencontainers.image.title="Audio2Tekst"
LABEL org.opencontainers.image.description="Cross-platform audio/video transcription with AI summarization"
LABEL org.opencontainers.image.url="https://github.com/AlanSteinbarth/Audio2Tekst"
LABEL org.opencontainers.image.source="https://github.com/AlanSteinbarth/Audio2Tekst"
LABEL org.opencontainers.image.vendor="Alan Steinbarth"
LABEL org.opencontainers.image.licenses="MIT"

# Set environment variables for optimal Python behavior
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set working directory
WORKDIR /app

# Update system packages and install system dependencies
RUN apt-get update && apt-get install -y \
    # FFmpeg for audio/video processing (core dependency)
    ffmpeg \
    ffprobe \
    # Additional utilities for better compatibility
    curl \
    wget \
    # Clean up to reduce image size
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* \
    && rm -rf /var/tmp/*

# Copy requirements files
COPY requirements.txt requirements-dev.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories with proper permissions
RUN mkdir -p /app/uploads/originals \
             /app/uploads/transcripts \
             /app/uploads/summaries \
             /app/logs \
             /app/db \
    && chmod -R 755 /app/uploads \
    && chmod -R 755 /app/logs \
    && chmod -R 755 /app/db

# Copy application files
COPY . .

# Create a non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser \
    && chown -R appuser:appuser /app
USER appuser

# Verify FFmpeg installation and system compatibility
RUN ffmpeg -version && ffprobe -version

# Health check to ensure the application is running correctly
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Expose Streamlit default port
EXPOSE 8501

# Set the command to run the application
CMD ["streamlit", "run", "app.py", \
     "--server.address", "0.0.0.0", \
     "--server.port", "8501", \
     "--server.headless", "true", \
     "--server.enableCORS", "false", \
     "--server.enableXsrfProtection", "false", \
     "--browser.gatherUsageStats", "false"]
