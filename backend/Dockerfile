# Use official Python runtime as a parent image
FROM python:3.10-slim

# Set working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port (Cloud Run sets PORT env variable, defaulting to 8080)
ENV PORT=8080
EXPOSE 8080

# Command to run the application (Render/Cloud Run will pass PORT)
CMD uvicorn main:app --host 0.0.0.0 --port $PORT
