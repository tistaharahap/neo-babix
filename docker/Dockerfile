FROM python:3.7.1-alpine

# app workdir
WORKDIR /app

# copy app dependencies
COPY requirements.txt docker/*.sh ./
COPY docker/newrelic.ini /newrelic.ini

# install dependecies
RUN set -ex \
    # install system dependencies
	&& apk add --update bash \
	&& apk add --virtual .fetch-deps \
	    gcc \
	    musl-dev \
	    libffi-dev \
	    make \
	    build-base \
	    wget \
	\
    # install app dependencies
    && rm -rf /var/lib/apt/lists/* \
    && wget https://github.com/mrjbq7/ta-lib/archive/TA_Lib-0.4.17.tar.gz \
    && tar -xvzf ta-lib-0.4.0-src.tar.gz \
    && cd ta-lib \
    && ./configure --prefix=/usr \
    && make -j4 \
    && make install \
    && cd .. \
    && rm -rf ta-lib \
    && rm TA_Lib-0.4.17.tar.gz \
    && pip install cython \
    && ln -s /usr/include/locale.h /usr/include/xlocale.h \
    && pip install numpy \
    && pip install -r ./requirements.txt --upgrade \
    \
    # clean pip cache
    && rm -rf /root/.cache/pip/* \
    \
    # clean system dependencies
    && rm -rf /var/cache/apk/*

# build app source code
COPY . ./

# Default runtime configs
EXPOSE 8080
ENTRYPOINT ["./start.sh"]
CMD ["run"]