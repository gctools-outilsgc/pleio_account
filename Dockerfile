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
    mailcap

COPY . /app

RUN cd /app && \
    npm install && \
    npm run build

RUN mv /app/docker/config.py /app/pleio_account/config.py
RUN mv /app/docker/start.sh /start.sh
RUN chmod +x /start.sh

RUN cd /app && \
    pip3 install virtualenv && \
    virtualenv /app/env && \
    /app/env/bin/pip install -r requirements.txt

ENV PATH="/app/env/bin:${PATH}"
WORKDIR /app
EXPOSE 8000
CMD ["/start.sh"]