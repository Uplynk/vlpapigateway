FROM ubuntu:18.04 AS build

WORKDIR /home
RUN apt-get update \
    && apt-get install -y -q --no-install-recommends \
    build-essential \
    python3 \
    python3-dev \
    python3-setuptools \
    python3-pip

RUN pip3 install --upgrade pip==20.3.3

ARG NEXUS_POSTFIX
ENV NEXUS_POSTFIX=${NEXUS_POSTFIX}

COPY ./requirements.txt /tmp/requirements.txt

RUN ["/bin/bash","-c","pip3 install -r /tmp/requirements.txt --timeout 600 --no-cache"]

COPY *.py /scripts/
WORKDIR /scripts

ENTRYPOINT [ "/bin/bash" ]
