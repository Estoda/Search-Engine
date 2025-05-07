FROM python:3.10-slim-buster

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && apt-get clean

COPY ../backend /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /app

RUN python manage.py collectstatic --noinput

CMD ['python', 'manage.py', 'runserver', '0.0.0.0:8000']