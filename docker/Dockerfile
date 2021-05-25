FROM ubuntu:20.04

ARG DEBIAN_FRONTEND=noninteractive

# app workdir
WORKDIR /app

# copy app dependencies
COPY poetry.lock pyproject.toml docker/*.sh ./

# os deps
RUN apt-get update \
	&& apt-get install -y python3.9 python3.9-dev python3.9-venv python3-pip python3-wheel build-essential libssl-dev libffi-dev wget \
    && rm -rf /var/lib/apt/lists/*

# install dependecies
RUN set -ex \
	\
    # install app dependencies
    && wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz \
    && tar -xvzf ta-lib-0.4.0-src.tar.gz \
    && cd ta-lib \
    && ./configure --prefix=/usr \
    && make \
    && make install \
    && cd .. \
    && rm -rf ta-lib \
    && rm ta-lib-0.4.0-src.tar.gz \
    && ln -s /usr/include/locale.h /usr/include/xlocale.h

# app deps
RUN pip3 install --no-cache-dir cython
RUN pip3 install poetry numpy \
    && python3 -m poetry export -f requirements.txt --output requirements.txt \
    && pip3 install -r requirements.txt \
    && rm -rf /root/.cache/pip/*

# clean system dependencies
RUN apt-get remove -y build-essential libssl-dev libffi-dev wget \
    && apt-get autoremove -y \
    && apt-get clean

# build app source code
COPY . ./

ENV PYTHONUNBUFFERED=1

# Default runtime configs
EXPOSE 8080
ENTRYPOINT ["./start.sh"]
CMD ["run"]