FROM python:3.10.5-bullseye
RUN ln -sf /usr/share/zoneinfo/Europe/Warsaw /etc/timezone && ln -sf /usr/share/zoneinfo/Europe/Warsaw /etc/localtime
COPY . /bot
WORKDIR /bot
RUN pip install -r requirements.txt
CMD [ "python", "run.py" ]