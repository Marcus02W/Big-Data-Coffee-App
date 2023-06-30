FROM docker:latest

RUN apk --update add \
    python3 \
    python3-dev \
    build-base \
    && pip3 install --upgrade pip

WORKDIR /app

# Copy the necessary files for building the Flask app image
COPY app/requirements.txt .
COPY app/. .

# Install the Flask app dependencies
RUN pip3 install -r requirements.txt

# Build the Flask app image
RUN docker build -t my-flask-app:1.0 .
