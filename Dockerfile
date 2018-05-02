
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
RUN /app/env/bin/pip install --upgrade pip
RUN /app/env/bin/pip install -r requirements.txt

# Stage 3 - Create new layer from multiple steps
FROM alpine:3.7
RUN mkdir /stage
COPY ./docker/config.py /stage/app/pleio_account/config.py
COPY ./docker/start.sh /stage/start.sh
COPY . /stage/app
RUN rm -rf /stage/app/assets
RUN chmod +x /stage/start.sh

#Stage 4 - Build Redis Server

FROM alpine:3.7

# add our user and group first to make sure their IDs get assigned consistently, regardless of whatever dependencies get added
RUN addgroup -S redis && adduser -S -G redis redis

# grab su-exec for easy step-down from root
RUN apk add --no-cache 'su-exec>=0.2'

ENV REDIS_VERSION 4.0.9
ENV REDIS_DOWNLOAD_URL http://download.redis.io/releases/redis-4.0.9.tar.gz
ENV REDIS_DOWNLOAD_SHA df4f73bc318e2f9ffb2d169a922dec57ec7c73dd07bccf875695dbeecd5ec510

# for redis-sentinel see: http://redis.io/topics/sentinel
RUN set -ex; \
	\
	apk add --no-cache --virtual .build-deps \
		coreutils \
		gcc \
		linux-headers \
		make \
		musl-dev \
	; \
	\
	wget -O redis.tar.gz "$REDIS_DOWNLOAD_URL"; \
	echo "$REDIS_DOWNLOAD_SHA *redis.tar.gz" | sha256sum -c -; \
	mkdir -p /usr/src/redis; \
	tar -xzf redis.tar.gz -C /usr/src/redis --strip-components=1; \
	rm redis.tar.gz; \
	\
# disable Redis protected mode [1] as it is unnecessary in context of Docker
# (ports are not automatically exposed when running inside Docker, but rather explicitly by specifying -p / -P)
# [1]: https://github.com/antirez/redis/commit/edd4d555df57dc84265fdfb4ef59a4678832f6da
	grep -q '^#define CONFIG_DEFAULT_PROTECTED_MODE 1$' /usr/src/redis/src/server.h; \
	sed -ri 's!^(#define CONFIG_DEFAULT_PROTECTED_MODE) 1$!\1 0!' /usr/src/redis/src/server.h; \
	grep -q '^#define CONFIG_DEFAULT_PROTECTED_MODE 0$' /usr/src/redis/src/server.h; \
# for future reference, we modify this directly in the source instead of just supplying a default configuration flag because apparently "if you specify any argument to redis-server, [it assumes] you are going to specify everything"
# see also https://github.com/docker-library/redis/issues/4#issuecomment-50780840
# (more exactly, this makes sure the default behavior of "save on SIGTERM" stays functional by default)
	\
	make -C /usr/src/redis -j "$(nproc)"; \
	make -C /usr/src/redis install; \
	\
	rm -r /usr/src/redis; \
	\
	runDeps="$( \
		scanelf --needed --nobanner --format '%n#p' --recursive /usr/local \
			| tr ',' '\n' \
			| sort -u \
			| awk 'system("[ -e /usr/local/lib/" $1 " ]") == 0 { next } { print "so:" $1 }' \
	)"; \
	apk add --virtual .redis-rundeps $runDeps; \
	apk del .build-deps; \
	\
	redis-server --version


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

RUN addgroup -S redis && adduser -S -G redis redis
RUN mkdir /data && chown redis:redis /data

COPY --from=0 /stage /
COPY --from=1 /app/env /app/env
COPY --from=2 /stage/ /
COPY --from=3 /usr/local/bin /usr/local/bin

ENV PATH="/app/env/bin:${PATH}"
WORKDIR /app
EXPOSE 8000
CMD ["/start.sh"]