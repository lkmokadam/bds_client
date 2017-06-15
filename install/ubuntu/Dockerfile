FROM lkmokadam/16.04-python2.7-opencv3.2.0

MAINTAINER Laxmikant Mokadam lmokadam@nvidia.com

RUN apt-get update && \
    apt-get install -y tmux &&\
	rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/lkmokadam/bds_client.git

ENV PATH "$PATH:/bds_client"
