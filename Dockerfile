# Use an official Python runtime as a parent image
FROM python:3.10-rc-alpine3.12 as BUILDER
LABEL maintainer="admin@moe.ph"

# Set environment varibles
ENV PYTHONUNBUFFERED 1
ENV FLASK_ENV production

# Setup venv
RUN python -m venv /opt/venv
# Make sure we use the virtualenv:
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

FROM python:3.10-rc-alpine3.12 as IMAGE

COPY --from=BUILDER /opt/venv /opt/venv

# Copy the current directory contents into the container at /app/
COPY . /app/
# Set the working directory to /app/
WORKDIR /app/

ENV PATH="/opt/venv/bin:$PATH"

RUN adduser --home /app --disabled-password onion_eye
RUN chown -R onion_eye /app
USER onion_eye

CMD exec gunicorn "onion_eye:create_app()" --bind 0.0.0.0:8000 --workers 4

## Command for Celery worker
## celery -A onion_eye.celery_worker.celery worker -B -P solo --loglevel=INFO
