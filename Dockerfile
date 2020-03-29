FROM fedora:31

LABEL author="Kristi Nikolla <knikolla@bu.edu>"

ENV PBR_VERSION 0.2

RUN dnf install -y git gcc python3-devel python3 python3-pip \
        libffi-devel openssl-devel mariadb-devel mariadb which

COPY --chown=1001:0 . /app
RUN cd /app && \
    pip3 install pipenv && \
    pipenv install --system && \
    pip3 install .

# Note(knikolla): This is required to support the random
# user IDs that OpenShift enforces.
# https://docs.openshift.com/enterprise/3.2/creating_images/guidelines.html
RUN chmod -R g+rwX /app

EXPOSE 8080

USER 1001

ENTRYPOINT [ "/app/run_adjutant.sh" ]
