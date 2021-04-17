FROM python:3.8-slim

RUN apt update && apt install -y ffmpeg && apt clean

WORKDIR /app

COPY requirements.txt ./
RUN  ln -sf /usr/share/zoneinfo/Europe/Warsaw /etc/timezone && \
     ln -sf /usr/share/zoneinfo/Europe/Warsaw /etc/localtime && \
     pip install -r requirements.txt

COPY . .

WORKDIR /app/src

CMD ["python", "main.py"]