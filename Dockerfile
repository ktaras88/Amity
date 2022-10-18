#FROM python:3.10-slim

#WORKDIR /amity-backend-t2

#RUN set -eux && \
    #apt-get update &&  \
    #apt-get upgrade -y && \
    #apt-get install -y  \
    #rm -rf /var/lib/apt/lists/*

FROM aws_ecr_id/base-${project_name}/${circle_sha1}

WORKDIR /amity-backend-t2

COPY ./ ./

RUN set -eux && \
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

EXPOSE 8000

CMD gunicorn amity-t2.wsgi:application -b 0.0.0.0:8000 -w 1 -k uvicorn.workers.UvicornWorker

