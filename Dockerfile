# Use an official Python runtime as the base image
FROM python:3.10.11-slim-buster

ARG QNA_TABLE=${QNA_TABLE} 
ARG SUMMARY_TABLE=${SUMMARY_TABLE} 
ARG OPENAI_API_TYPE=${OPENAI_API_TYPE} 
ARG FEEDBACK_TABLE=${FEEDBACK_TABLE} 
ARG OBJECT_KEY=${OBJECT_KEY} 
ARG SCREENING_TABLE=${SCREENING_TABLE} 
ARG DEPLOYMENT_NAME=${DEPLOYMENT_NAME} 
ARG AWS_BUCKET_NAME=${AWS_BUCKET_NAME} 
ARG OPENAI_API_VERSION=${OPENAI_API_VERSION} 
ARG OPENAI_API_KEY=${OPENAI_API_KEY} 
ARG OPENAI_API_BASE=${OPENAI_API_BASE}

ENV QNA_TABLE=${QNA_TABLE} 
ENV SUMMARY_TABLE=${SUMMARY_TABLE} 
ENV OPENAI_API_TYPE=${OPENAI_API_TYPE} 
ENV FEEDBACK_TABLE=${FEEDBACK_TABLE} 
ENV OBJECT_KEY=${OBJECT_KEY} 
ENV SCREENING_TABLE=${SCREENING_TABLE} 
ENV DEPLOYMENT_NAME=${DEPLOYMENT_NAME} 
ENV AWS_BUCKET_NAME=${AWS_BUCKET_NAME} 
ENV OPENAI_API_VERSION=${OPENAI_API_VERSION} 
ENV OPENAI_API_KEY=${OPENAI_API_KEY} 
ENV OPENAI_API_BASE=${OPENAI_API_BASE}


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
