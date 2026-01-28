# Base Image
FROM python:3.9-slim

# Working Directory
WORKDIR /app

# Copy Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Code
COPY . .

# Run Training Script during build (so the container has a model ready)
RUN python src/train.py

# Expose Port
EXPOSE 5000

# Start Command (Using Gunicorn for production)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "src.app:app"]