# Use an official Python runtime as the base image
FROM python:3.10.11-slim-buster

RUN apt-get update
RUN apt-get install -y default-jdk
RUN apt-get install -y poppler-utils
RUN apt-get install -y ghostscript
RUN apt-get install -y python3-pip
RUN apt-get install -y tesseract-ocr
# Install gunicorn
RUN pip install gunicorn

# Copy the requirements file into the container
WORKDIR /app
COPY requirements.txt /app/

# Install the Python dependencies
RUN pip3 install -r requirements.txt

# Copy the backend code into the container
COPY . .

# Start the WSGI server (Gunicorn example)
CMD [ "gunicorn", "--workers=1", "--bind=0.0.0.0:2000", "--timeout=1000", "app:app" ]

# CMD ["gunicorn", "app:app", "-b", "0.0.0.0:2000", "--timeout=1000"]
# CMD [ "waitress-serve", "--listen", "0.0.0.0:2000", "wsgi:app" ]
# CMD ["python3", "main.py"]
