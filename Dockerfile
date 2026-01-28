# Base Image
FROM python:3.9-slim

# Working Directory
WORKDIR /app

# Install tools
# Copy Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Grab the new code
# Copy Code
COPY . .

# Run Training Script during build (so the container has a model ready)
RUN python src/train.py

# Expose Port
EXPOSE 5000

# Start Command 
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "src.app:app"]


# CD - "Get the new code to the users quickly"