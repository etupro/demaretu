FROM pytorch/pytorch:2.5.1-cuda12.4-cudnn9-runtime

RUN apt-get update -y && apt-get install -y libpq-dev gcc

WORKDIR /app

COPY ./main.py ./main.py
COPY ./sender.py ./sender.py
COPY ./utils ./utils
COPY ./requirements.txt ./requirements.txt

RUN mkdir -p /app/data/to_ingest

RUN pip install -r requirements.txt