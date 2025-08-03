# Use an official Python runtime as a parent image
FROM python:3.11

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt ./

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose port 5000, which is the port the Flask app runs on
EXPOSE 5000

# Set the command to run the application
# We use the Gunicorn server for a production environment.
# Since the user provided app.run() in their main.py, we will use that for this example.
# In a real-world scenario, you would use Gunicorn to run the app.
CMD ["python", "main.py"]
