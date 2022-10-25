FROM python:3.10
WORKDIR /amity-backend-t2
COPY . ./
RUN set -eux && \
    apt-get update &&  \
    apt-get upgrade -y && \
    apt-get install -y && \
    apt-get install gcc -y &&\
    apt-get install python3-dev -y &&\
    apt-get install libpq-dev -y &&\
    pip install --upgrade pip && \
    pip install pipenv && \
    apt update && \
    #apt install nano && \
    #nano .env && \
    pipenv shell --fancy && \
    pwd \
    pipenv install --system --skip-lock  && \
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
#CMD python manage.py runserver
CMD python manage.py runserver 0.0.0.0:8000