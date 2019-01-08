FROM python:3.6-alpine

RUN apk --no-cache add \
    nodejs \
    nodejs-npm \
    gcc \
    jpeg-dev \
    musl-dev \
    pcre-dev \
    linux-headers \
    postgresql-dev \
    zlib-dev \
    mailcap \
    gettext

RUN mkdir /app
WORKDIR /app
ADD requirements.txt /app
ADD package.json /app
ADD package-lock.json /app

## Update NPM
RUN npm install -g npm

## Install and update NPM packages
RUN npm install && npm update

RUN pip3 install -r requirements.txt

ADD . /app

RUN npm run build

RUN mv /app/docker/config.py /app/pleio_account/config.py
RUN mv /app/docker/start.sh /start.sh
RUN chmod +x /start.sh

ENV PATH="/app/env/bin:${PATH}"
EXPOSE 8000
CMD ["/start.sh"]