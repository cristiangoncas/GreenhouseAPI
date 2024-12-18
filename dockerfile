# Use the official Python image as a base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /greenhouse

# Copy the rest of the application code into the container
COPY . .

# Install Flask (and other dependencies, if any)
RUN pip install --no-cache-dir flask
  
# Set an environment variable to indicate the Flask app
ENV FLASK_APP=app_v2.py

# (Optional) Set an environment variable to indicate production mode
ENV FLASK_ENV=production

# Expose the Flask port (default is 5000)
EXPOSE 5000

# Command to run the application
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
