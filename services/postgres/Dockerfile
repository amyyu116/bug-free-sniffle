FROM postgis/postgis

RUN apt-get update && apt-get install -y \

    git \
    build-essential \
    postgresql-server-dev-all \
    postgresql-12-rum \
    less \
    make \
    vim

RUN git clone https://github.com/postgrespro/rum /tmp/rum

WORKDIR /tmp/rum
RUN make USE_PGXS=1
RUN make USE_PGXS=1 install

RUN apt-get purge -y --auto-remove git build-essential && \

    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR /tmp/db

RUN mkdir /data && chown postgres /data

COPY schema.sql /docker-entrypoint-initdb.d/01.sql
