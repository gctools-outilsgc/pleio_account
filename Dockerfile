# Stage 1 - Compile needed python dependencies
FROM alpine:3.7
RUN apk --no-cache add \
    gcc \
    jpeg-dev \
    musl-dev \
    pcre-dev \
    libxml2-dev \
    xmlsec-dev \
    libxslt-dev \
    pkgconfig \
    linux-headers \
    postgresql-dev \
    python3 \
    python3-dev \
    mariadb-client \
    mariadb-dev \
    zlib-dev \
    libffi-dev && \
  pip3 install virtualenv && \
  virtualenv /app/env

WORKDIR /app
COPY requirements.txt /app
RUN /app/env/bin/pip install -r requirements.txt

# Stage 2 - Create new layer from multiple steps
FROM alpine:3.7
RUN mkdir /stage
COPY ./docker/config.py /stage/app/concierge/config.py
COPY ./docker/start.sh /stage/start.sh
COPY . /stage/app
RUN rm -rf /stage/app/assets
RUN chmod +x /stage/start.sh

# Stage 3 - Build docker image suitable for execution and deployment
FROM alpine:3.7
RUN apk --no-cache add \
      ca-certificates \
      mailcap \
      jpeg \
      musl \
      libxml2 \
      libxslt \
      xmlsec \
      pcre \
      postgresql \
      python3 \
      mariadb-client \
      mariadb-client-libs \
      zlib

COPY --from=0 /app/env /app/env
COPY --from=1 /stage/ /

ENV PATH="/app/env/bin:${PATH}"
WORKDIR /app
EXPOSE 8000
CMD ["/start.sh"]
