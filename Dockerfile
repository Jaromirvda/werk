FROM ubuntu:latest
LABEL authors="vdaja"

FROM python:3.8-slim

#Werkdirectory instellen
WORKDIR /app

#Kopieer de huidige directory inhoud naar de container op /app
COPY . /app

#Installeer alle benodigde packages die in requirements.txt staan
RUN pip install --no-cache-dir -r requirements.txt

#Maak poort 5000 beschikbaar voor de wereld buiten deze container
EXPOSE 5000

#Definieer environment variable
ENV FLASK_APP=werk.py
ENV FLASK_RUN_HOST=0.0.0.0

#Start de applicatie wanneer de container gelanceerd wordt
CMD ["flask", "run"]