
# Stage 1 - Build the javascript bundle
FROM alpine:3.7

RUN apk --no-cache add \
    nodejs \
    nodejs-npm

COPY package.json package-lock.json /app/
WORKDIR /app
RUN npm install
COPY assets /app/assets
COPY webpack.prod.config.js /app/

RUN npm run build && \
    mkdir -p /stage/app && \
    cp -r /app/assets /stage/app && \
    cp /app/webpack-stats.json /stage/app

# Stage 2 - Compile needed python dependencies
FROM alpine:3.7
RUN apk --no-cache add \
    gcc \
    jpeg-dev \
    musl-dev \
    pcre-dev \
    linux-headers \
    postgresql-dev \
    python3 \
    python3-dev \
    zlib-dev && \
  pip3 install virtualenv && \
  virtualenv /app/env

WORKDIR /app
COPY requirements.txt /app
RUN /app/env/bin/pip install -r requirements.txt

# Stage 3 - Create new layer from multiple steps
FROM alpine:3.7
RUN mkdir /stage
COPY ./docker/config.py /stage/app/pleio_account/config.py
COPY ./docker/start.sh /stage/start.sh
COPY . /stage/app
RUN rm -rf /stage/app/assets
RUN chmod +x /stage/start.sh

# Stage 4 - Build docker image suitable for execution and deployment
FROM alpine:3.7
LABEL maintainer Bart Jeukendrup <bart@jeukendrup.nl>
RUN apk --no-cache add \
      ca-certificates \
      mailcap \
      jpeg \
      musl \
      pcre \
      postgresql \
      python3 \
      zlib

COPY --from=0 /stage /
COPY --from=1 /app/env /app/env
COPY --from=2 /stage/ /

ENV PATH="/app/env/bin:${PATH}"
WORKDIR /app
EXPOSE 8000
CMD ["/start.sh"]
