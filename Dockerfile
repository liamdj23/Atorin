FROM python:3.8-slim

RUN apt update && apt install -y firefox-esr ffmpeg && apt clean

WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

WORKDIR /app/src

CMD ["python", "main.py"]