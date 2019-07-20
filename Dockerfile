FROM            python:3.7-slim-stretch

ENV             WRK_DIR /opt/sqapi
ENV             VIRTUAL_ENV=${WRK_DIR}
ENV             PATH="${VIRTUAL_ENV}/bin:${PATH}"

WORKDIR         ${WRK_DIR}
EXPOSE          5000

RUN             useradd -ms /bin/bash sqapi
RUN             apt-get update \
                && apt-get install \
                  -y --fix-missing \
                    python3-virtualenv \
                    python3-dev \
                    python3-pip \
                    libpq-dev \
                    cmake \
                && apt-get clean \
                && rm -rf /tmp/* /var/tmp/*

RUN             python3 -m venv                 ${VIRTUAL_ENV} \
                && chown -R sqapi:sqapi         ${WRK_DIR}

USER            sqapi:sqapi

                # PIP Requirements
COPY            requirements.txt                ${WRK_DIR}/
RUN             pip3 install --upgrade pip \
                && pip3 install \
                  --no-cache-dir -r             ${WRK_DIR}/requirements.txt

ADD             --chown=sqapi start.py          ${WRK_DIR}/
ADD             --chown=sqapi sqapi             ${WRK_DIR}/sqapi

CMD             [ "python", "start.py" ]
