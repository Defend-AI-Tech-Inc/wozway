FROM --platform=linux/amd64 apache/apisix:3.9.0-debian

USER root
RUN mkdir -p /opt/apisix/plugins
COPY ./wauzeway_proxy.lua /opt/apisix/plugins/
COPY ./config.yaml /usr/local/apisix/conf/config.yaml
#COPY ./apisix.yaml /usr/local/apisix/conf/apisix.yaml

RUN apt-get update && \
    apt-get install sudo zip curl git vim make procps \
    net-tools iputils-ping jq lsof strace tcpdump python3-pip -y

RUN adduser apisix sudo
RUN passwd -d apisix
USER apisix
