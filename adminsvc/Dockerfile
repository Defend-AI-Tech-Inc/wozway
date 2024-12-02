FROM apache/apisix:3.9.0-debian

USER root

RUN apt-get update && \
    apt-get install zip curl git vim make \
    letsencrypt certbot \
    procps net-tools iputils-ping jq python3-pip -y

RUN mkdir -p /app
COPY . /app
RUN chmod +x /app/config_script.sh
WORKDIR /app

CMD [ "./config_script.sh" ]
