FROM python:3.11-slim as base

RUN mkdir app
WORKDIR /app
COPY requirements.txt .
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt
COPY . .