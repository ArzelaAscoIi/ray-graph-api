FROM python:3.9.9

COPY requirements.txt requirements.txt

RUN apt-get update && apt-get install -y rsync ssh && rm -rf /var/lib/apt/lists/*

RUN python -m pip install --upgrade pip

RUN pip install -r requirements.txt
# docker pull python:3.9.9