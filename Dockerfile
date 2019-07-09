FROM            python:3.7-slim

ENV             WRK_DIR /opt/sqapi
WORKDIR         ${WRK_DIR}
EXPOSE          5000

RUN             useradd -ms /bin/bash sqapi
RUN             apt-get update \
                && apt-get install \
                  -y --fix-missing \
                    python3-virtualenv \
                    python3-numpy \
                    python3-dev \
                    python3-pip \
                    libpq-dev \
                    cmake \
                && apt-get clean \
                && rm -rf /tmp/* /var/tmp/*

ENV             VIRTUAL_ENV=${WRK_DIR}
RUN             python3 -m venv ${VIRTUAL_ENV}
ENV             PATH="${VIRTUAL_ENV}/bin:${PATH}"

                # PIP Requirements
COPY            requirements.txt        ${WRK_DIR}/
RUN             pip3 install --upgrade pip \
                && pip3 install \
                  --no-cache-dir -r     ${WRK_DIR}/requirements.txt

COPY            sqapi                   ${WRK_DIR}/sqapi/
COPY            start.py                ${WRK_DIR}/
RUN             chown -R sqapi:sqapi    ${WRK_DIR}

USER            sqapi:sqapi

CMD             [ "python", "app.py" ]
