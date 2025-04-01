FROM python:3.11-slim

RUN mkdir bestanibot
WORKDIR /bestanibot

ADD requirements.txt /bestanibot/
RUN pip install -r requirements.txt

ADD . /bestanibot/
ADD .env.docker /bestanibot/.env

EXPOSE 8080/tcp

CMD python main.py