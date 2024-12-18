# Use the official Python image as a base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /greenhouse

# Copy the rest of the application code into the container
COPY . .
COPY ./requirements.txt .

# Install Flask (and other dependencies, if any)
RUN pip install -r requirements.txt

# Set an environment variable to indicate the Flask app
ENV FLASK_APP=app_v2.py
# (Optional) Set an environment variable to indicate production mode
ENV FLASK_ENV=production
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=3000

# Expose the Flask port (default is 3000)
EXPOSE 3000

# Command to run the application
CMD ["flask", "run"]
