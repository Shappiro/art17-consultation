FROM python:2.7-slim
MAINTAINER "EEA: IDM2 C-TEAM" <eea-edw-c-team-alerts@googlegroups.com>

ENV WORK_DIR=/var/local/art17
ENV DATA_DIR=/var/local/art17-data

RUN runDeps="curl vim build-essential netcat mysql-client libmysqlclient-dev python-dev libldap2-dev libsasl2-dev libssl-dev" \
 && apt-get update \
 && apt-get install -y --no-install-recommends $runDeps \
 && rm -vrf /var/lib/apt/lists/*

COPY . $WORK_DIR/
WORKDIR $WORK_DIR

RUN mkdir $WORK_DIR/logs \
	&& mkdir -p $DATA_DIR/maps \
	&& mkdir -p $DATA_DIR/factsheets \
	&& ln -s $DATA_DIR/maps $WORK_DIR/art17/static/maps \
	&& ln -s $DATA_DIR/factsheets $WORK_DIR/art17/static/factsheets

RUN pip install -U setuptools \
 && pip install -r requirements-dep.txt --trusted-host eggshop.eaudeweb.ro \
 && mv docker-entrypoint.sh /bin/

ENTRYPOINT ["docker-entrypoint.sh"]
