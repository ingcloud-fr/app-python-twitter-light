# Utilisez l'image officielle de Python comme image de base
FROM python:3.12

# Install dependencies
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
#ENV FLASK_APP=app.py

# Expose port
EXPOSE 5000

# Run the command
CMD ["bash", "-c", "python initialize_db.py && gunicorn --bind 0.0.0.0:5000 app:app"]
