FROM python:3.11

# Set the working directory in the container to the root of the app
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt ./

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose port 5000, which is the port the Flask app runs on
EXPOSE 5000

# Set the working directory to the 'server' directory
WORKDIR /app/server

# Set the command to run the application from the 'server' directory
CMD ["python", "app.py"]