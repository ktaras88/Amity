FROM python:3.10-slim

WORKDIR /amity-backend-t2
COPY . ./
RUN apt-get update &&  \
    apt-get upgrade -y && \
    apt-get install -y  \
    #rm -rf /var/lib/apt/lists/*

#FROM aws_ecr_id/base-${project_name}/${circle_sha1}

#FROM 300893877638.dkr.ecr.us-west-2.amazonaws.com/base-amity-t2:v1.0
# WORKDIR /amity-backend-t2

    #set -eux && \
    groupadd \
        --system \
    amity && \
    useradd \
        --system \
    amity \
        -g \
    amity && \
    chown -R amity:amity /amity && \
    pipenv install

USER amity
CMD python manage.py runserver
EXPOSE 8000

# CMD gunicorn amity-t2.wsgi:application -b 0.0.0.0:8000 -w 1 -k uvicorn.workers.UvicornWorker

