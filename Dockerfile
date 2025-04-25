# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install dependencies
# Copy requirements first to leverage Docker cache
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project code
COPY . /app/

# Expose port 8000 for the Django app
EXPOSE 8000

# Command to run the application using Gunicorn (recommended for production)
# You might need to add gunicorn to requirements.txt
# CMD ["gunicorn", "bookstore_project.wsgi:application", "--bind", "0.0.0.0:8000"]

# Or, for development/simplicity based on current setup:
# Make sure migrate runs (better handled in docker-compose or entrypoint script)
# RUN python manage.py migrate
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]