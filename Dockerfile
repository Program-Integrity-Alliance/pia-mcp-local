# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Copy project files
COPY pyproject.toml .
COPY README.md .
COPY src/ src/

# Install Python dependencies
RUN uv pip install --system -e .

# Create non-root user
RUN groupadd -r pia && useradd -r -g pia pia
RUN chown -R pia:pia /app
USER pia

# Set environment variables
ENV PYTHONPATH=/app/src
ENV PIA_API_URL=https://mcp.programintegrity.org/

# Run the server
ENTRYPOINT ["python", "-m", "pia_mcp_server", "--api-key", "${PIA_API_KEY}"]
