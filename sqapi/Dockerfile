FROM            python:3.7

ENV             WRK_DIR /opt/app

RUN             apt-get update && \
                  apt-get install -y --fix-missing \
                  python3-numpy \
                  python3-dev \
                  python3-pip

RUN             apt-get clean && \
                  rm -rf /tmp/* /var/tmp/*

                # PIP Requirements
RUN             pip3 install \
                  flask-cors \
                  psycopg2 \
                  requests \
                  markdown \
                  pyyaml \
                  redis \
                  Flask \
                  pika

EXPOSE          5000
WORKDIR         ${WRK_DIR}

COPY            ./          ${WRK_DIR}

CMD             [ "python", "app.py" ]

