# Lightweight Image 
FROM python:3.11-slim

# Prevents Python from writing .pyc files to disk and ensures that logs are output in real time
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=run.py

# Set the working directory inside the container
WORKDIR /app

# Install the system dependencies needed to compile PostgreSQL libraries if necessary
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file 
COPY requirements.txt /app/

# Update pip and install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy all the code from our application into the containerCOPY . /app/

# Flask's default port
EXPOSE 5000

# Default command to launch the application
CMD ["python", "run.py"]
