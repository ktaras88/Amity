FROM python:3.10
WORKDIR /amity-backend-t2
COPY . ./
RUN set -eux && \
    apt-get update &&  \
    apt-get upgrade -y && \
    apt-get install -y && \
        gcc \
        python3-dev \
        libpq-dev \
        pip install pipenv \
        apt update \
        apt install nano \
        nano .env \
        pipenv shell \
        pipenv install \
    groupadd \
        --system \
    amity && \
    useradd \
        --system \
    amity \
        -g \
    amity && \
    chown -R amity:amity /amity
EXPOSE 8000
CMD python manage.py runserver