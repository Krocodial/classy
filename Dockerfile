#FROM python:3
#need to set permissions due to windows dev environment
FROM python as builder

COPY . /opt/app-root/src
RUN chmod -R 775 /opt/app-root/src

FROM registry.access.redhat.com/rhscl/python-36-rhel7

WORKDIR /opt/app-root/src

COPY requirements.txt ./

RUN pip3 install --no-cache-dir -r requirements.txt

COPY --from=builder /opt/app-root/src .
#RUN ls -la
RUN python manage.py collectstatic --noinput

#WORKDIR /opt/app-root
#RUN cp -r src/* .

#WORKDIR /usr/bin

#RUN yum -y install wget

#RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.24.0/geckodriver-v0.24.0-linux64.tar.gz 
#RUN tar -xzvf geckodriver-v0.24.0-linux64.tar.gz
#RUN rm geckodriver-v0.24.0-linux64.tar.gz 
#RUN apt-get update && apt-get install firefox-esr -y



ARG SSO_SERVER
ARG SSO_REALM
ARG SSO_CLIENT_ID
ARG SSO_CLIENT_SECRET
ARG TEST_ACCOUNT_USERNAME
ARG TEST_ACCOUNT_PASSWORD
ARG POSTGRESQL_SERVICE_HOST=172.17.0.1
ARG DATABASE_USER=postgres
ARG DATABASE_PASSWORD=docker
ARG REDIRECT_URI=http://localhost:1337
ARG DEBUG=False

ENV DEBUG=${DEBUG}
ENV DATABASE_SERVICE_NAME=postgresql 
ENV DATABASE_ENGINE=postgresql 
ENV DATABASE_NAME=postgres
ENV POSTGRESQL_SERVICE_HOST=${POSTGRESQL_SERVICE_HOST} 
ENV DATABASE_USER=${DATABASE_USER} 
ENV DATABASE_PASSWORD=${DATABASE_PASSWORD}
ENV SSO_SERVER=${SSO_SERVER}
ENV SSO_REALM=${SSO_REALM}
ENV SSO_CLIENT_ID=${SSO_CLIENT_ID}
ENV SSO_CLIENT_SECRET=${SSO_CLIENT_SECRET}
ENV REDIRECT_URI=${REDIRECT_URI}
ENV TEST_ACCOUNT_USERNAME=${TEST_ACCOUNT_USERNAME}
ENV TEST_ACCOUNT_PASSWORD=${TEST_ACCOUNT_PASSWORD}


#CMD python manage.py runserver 0.0.0.0:1337

CMD python manage.py migrate && python manage.py createcachetable && python manage.py check && python manage.py test tests/unit-tests/ && gunicorn --bind 0.0.0.0:1337 wsgi


EXPOSE 1337

#docker build --no-cache --build-arg SSO_SERVER --build-arg SSO_REALM --build-arg SSO_CLIENT_ID --build-arg SSO_CLIENT_SECRET --build-arg REDIRECT_URI --build-arg DEBUG -t classy .

