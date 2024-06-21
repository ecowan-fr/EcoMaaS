# pull official base image
FROM python:3.11.9-slim-bullseye

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
RUN apt-get update
RUN apt install libcairo2-dev pkg-config python3-dev -y
RUN apt install  python3-dbus gcc make cmake -y
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY . .