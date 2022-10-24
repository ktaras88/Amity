FROM python:3.10
WORKDIR /amity-backend-t2
COPY . ./
RUN set -eux && \
    apt-get update &&  \
    apt-get upgrade -y && \
    apt-get install -y && \
    apt-get install gcc &&\
    apt-get install python3-dev &&\
    apt-get install libpq-dev &&\
    pip install pipenv && \
    apt update && \
    apt install nano && \
    nano .env && \
    pipenv shell && \
    pipenv install && \
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