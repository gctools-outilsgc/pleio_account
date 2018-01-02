
# Stage 1 - Build the javascript bundle
FROM alpine

RUN apk --no-cache add \
    nodejs \
    nodejs-npm

COPY package.json package-lock.json /app/
WORKDIR /app
RUN npm install
COPY assets /app/assets
COPY webpack.prod.config.js /app/
RUN npm run build

# Stage 2 - Compile needed python dependencies
FROM alpine
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

# Stage 3 - Build docker image suitable for execution and deployment
FROM alpine
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

COPY . /app
COPY --from=0 /app/assets /app/assets
COPY --from=0 /app/webpack-stats.json /app/webpack-stats.json
COPY --from=1 /app/env /app/env
RUN cp /app/docker/config.py /app/pleio_account/config.py && \
    cp /app/docker/start.sh /start.sh && \
    chmod +x /start.sh


ENV PATH="/app/env/bin:${PATH}"
WORKDIR /app
EXPOSE 8000
CMD ["/start.sh"]
