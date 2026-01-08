# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy and install system dependencies from packages.txt
COPY packages.txt .
RUN apt-get update \
    && apt-get install -y --no-install-recommends locales-all ffmpeg git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Expose Streamlit default port
EXPOSE 80

# Run the Streamlit app
CMD ["streamlit", "run", "app.py", "--server.port=80", "--server.address=0.0.0.0"]
