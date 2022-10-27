FROM python:3.10

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1

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
    PIPENV_VENV_IN_PROJECT=1 pipenv install --system  && \
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
