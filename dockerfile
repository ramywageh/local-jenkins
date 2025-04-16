FROM python:alpine

# Set the working directory
WORKDIR /app

# Copy the application files and install dependencies
COPY . .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install gunicorn 

# Expose the port on which the application will run
EXPOSE 3000

# Use gunicorn to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:3000", "app:app"]