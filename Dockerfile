FROM python:3.10-buster

WORKDIR /app

COPY requirements.txt ./
RUN  ln -sf /usr/share/zoneinfo/Europe/Warsaw /etc/timezone && \
     ln -sf /usr/share/zoneinfo/Europe/Warsaw /etc/localtime && \
     pip install -r requirements.txt

COPY . .

WORKDIR /app/src

CMD ["python", "main.py"]
