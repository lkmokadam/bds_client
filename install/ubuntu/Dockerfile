FROM lkmokadam/16.04-python2.7-opencv3.2.0

MAINTAINER Laxmikant Mokadam lmokadam@nvidia.com

RUN apt-get -y update &&\
	apt-get install -y git &&\
	rm -rf /var/lib/apt/lists/*

RUN mkdir /app ; cd /app ; git clone https://github.com/lkmokadam/bds_client.git

ENV PATH "$PATH:/app/bds_client"
