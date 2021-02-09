FROM gorialis/discord.py:3.8-alpine

WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

WORKDIR /app/src

CMD ["python", "main.py"]