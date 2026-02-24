FROM python:3.11-slim

# Avoid Python buffering (logs appear instantly)
ENV PYTHONUNBUFFERED=1

# Set container working directory
WORKDIR /app

# Copy project files into container
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Default command → run scanner
CMD ["python", "scan_all.py"]