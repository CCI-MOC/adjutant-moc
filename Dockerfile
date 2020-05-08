# This Dockerfile uses a multi-stage build
# * The builder image installs the compile time dependencies and
#   installs the pip packages into a virtual environment.
# * The final image copies the virtual environment over and
#   installs netcat and mysql libraries as runtime deps.

# Builder Image
FROM python:3.7-slim-buster as builder

RUN apt update && \
    apt-get install -y --no-install-recommends \
    git gcc python3-dev python3 python3-pip netcat \
    libffi-dev libssl-dev default-libmysqlclient-dev && \
    apt-get clean -y

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt

# Final Image
FROM python:3.7-slim-buster

LABEL author="Mass Open Cloud <team@lists.massopen.cloud>"

RUN apt update && \
    apt-get install -y --no-install-recommends netcat libmariadb3 && \
    apt-get clean -y

COPY --from=builder --chown=1001:0 /opt/venv /opt/venv

ENV PBR_VERSION 0.2
ENV PATH="/opt/venv/bin:$PATH"

COPY --chown=1001:0 . /app
RUN cd /opt && \
    cd /app && \
    python setup.py install develop

# Note(knikolla): This is required to support the random
# user IDs that OpenShift enforces.
# https://docs.openshift.com/enterprise/3.2/creating_images/guidelines.html
RUN chmod -R g+rwX /app

EXPOSE 8080

USER 1001

ENTRYPOINT [ "/app/run_adjutant.sh" ]
