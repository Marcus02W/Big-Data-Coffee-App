FROM docker:latest

RUN apk --update add \
    python3 \
    python3-dev \
    build-base \
    && pip3 install --upgrade pip

WORKDIR /app

# Copy the necessary files for building the Flask app image
COPY requirements.txt .
COPY ./. .

# Install the Flask app dependencies
RUN pip3 install -r requirements.txt

EXPOSE 3000
ENTRYPOINT ["flask", "backend.py"]
CMD [""]
