FROM python:3.11-slim

# Install curl for health checks
USER root
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Create a non-privileged user
RUN useradd -m swiftuser
WORKDIR /home/swiftuser/app

# Copy and install dependencies
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ .

# FIXED: Changed -r to -R
RUN chown -R swiftuser:swiftuser /home/swiftuser/app

USER swiftuser

ENV APP_PORT=3000
EXPOSE 3000

CMD ["python", "main.py"]