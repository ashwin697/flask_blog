# Use an official Python runtime as a parent image
FROM python:3.8

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install any needed dependencies specified in requirements.txt
RUN pip install -r requirements.txt

# Copy the entire current directory contents into the container at /app
COPY . .

# Expose the port your app runs on (if it's 5000, adjust accordingly)
EXPOSE 5000

# Define the command to run your application
CMD ["python", "main.py"]

