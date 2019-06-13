FROM            python:3.7

ENV             WRK_DIR /opt/app
WORKDIR         ${WRK_DIR}
EXPOSE          5000

RUN             useradd -ms /bin/bash sqapi
RUN             apt-get update \
                && apt-get install \
                  -y --fix-missing \
                    python3-numpy \
                    python3-dev \
                    python3-pip \
                && apt-get clean \
                && rm -rf /tmp/* /var/tmp/*

                # PIP Requirements
COPY            requirements.txt        ${WRK_DIR}/
RUN             pip3 install \
                  --no-cache-dir -r     ${WRK_DIR}/requirements.txt

COPY            ./                      ${WRK_DIR}/
RUN             chown -R sqapi:sqapi    ${WRK_DIR}

USER            sqapi:sqapi

CMD             [ "python", "app.py" ]
