FROM python:3.10


WORKDIR /amity-backend-t2

COPY . .

RUN set -eux && \
    apt-get update &&  \
    apt-get upgrade -y && \
    apt-get install -y \
        gcc \
        python3-dev \
        libpq-dev && \
    pip install --upgrade pip && \
    pip install pipenv && \
    pipenv install --system && \
    groupadd \
        --system \
    amity && \
    useradd \
        --system \
    amity \
        -g \
    amity && \
    chown -R amity:amity /amity-backend-t2

EXPOSE 8000
