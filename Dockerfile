# Base Image
FROM python:3.9-slim

# Working Directory (like cd/app)
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

# Expose Port (This app listens on 5000)
EXPOSE 5000

# Start Command (default command to run the app)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "src.app:app"]


# To build the image: docker build -t my-ml-app .
# To run the container: docker run -p 5000:5000 my-ml-app

# CD - "Get the new code to the users quickly"