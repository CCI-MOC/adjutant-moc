FROM python:3-slim-buster

LABEL author="Kristi Nikolla <knikolla@bu.edu>"

ENV PBR_VERSION 0.2

RUN apt update && \
    apt-get install -y --no-install-recommends \
    git gcc python3-dev python3 python3-pip netcat \
    libffi-dev libssl-dev default-libmysqlclient-dev && \
    apt-get clean -y

COPY --chown=1001:0 requirements.txt /app/requirements.txt
RUN pip3 install -r /app/requirements.txt

COPY --chown=1001:0 . /app
RUN cd /app && \
    pip install -e .

# Note(knikolla): This is required to support the random
# user IDs that OpenShift enforces.
# https://docs.openshift.com/enterprise/3.2/creating_images/guidelines.html
RUN chmod -R g+rwX /app

EXPOSE 8080

USER 1001

ENTRYPOINT [ "/app/run_adjutant.sh" ]
