# Use Python 3.11 base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy all the project files into the container's /app directory
COPY . /app


# Expose the port Streamlit will run on
EXPOSE 8501
