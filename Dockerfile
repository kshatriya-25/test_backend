# Start from a lightweight Debian Linux image
FROM debian:bookworm-slim

# Install Python and pip using apt (like you would on any Linux machine)
RUN apt-get update && apt-get install -y python3 python3-pip

# Set the working directory inside the container
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip3 install -r requirements.txt --break-system-packages

# Copy the rest of the app
COPY . .

# Open port 8000
EXPOSE 8000

# Start the server
CMD ["python3", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
