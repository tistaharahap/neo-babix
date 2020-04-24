FROM python:3.7-slim

# app workdir
WORKDIR /app

# copy app dependencies
COPY requirements.txt docker/*.sh ./

# install dependecies
RUN set -ex \
    # install system dependencies
    && apt-get update \
	&& apt-get install -y build-essential libssl-dev libffi-dev wget \
	\
    # install app dependencies
    && rm -rf /var/lib/apt/lists/* \
    && wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz \
    && tar -xvzf ta-lib-0.4.0-src.tar.gz \
    && cd ta-lib \
    && ./configure --prefix=/usr \
    && make \
    && make install \
    && cd .. \
    && rm -rf ta-lib \
    && rm ta-lib-0.4.0-src.tar.gz \
    && pip install --upgrade pip \
    && pip install cython \
    && ln -s /usr/include/locale.h /usr/include/xlocale.h \
    && pip install numpy \
    && pip install -r ./requirements.txt --upgrade \
    \
    # clean pip cache
    && rm -rf /root/.cache/pip/* \
    \
    # clean system dependencies
    && apt-get clean

# build app source code
COPY . ./

# Default runtime configs
EXPOSE 8080
ENTRYPOINT ["./start.sh"]
CMD ["run"]