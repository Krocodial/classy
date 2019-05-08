#FROM python:3
#need to set permissions due to windows dev environment
FROM python:3.6 as builder

COPY . /opt/app-root/src
RUN chmod -R 775 /opt/app-root/src

FROM registry.access.redhat.com/rhscl/python-36-rhel7

WORKDIR /opt/app-root

COPY requirements.txt ./

RUN pip3 install --no-cache-dir -r requirements.txt

COPY --from=builder /opt/app-root .

#COPY --from=builder /opt/app-root/src .
#RUN ls -la
#RUN python manage.py collectstatic --noinput

#WORKDIR /opt/app-root
#RUN cp -r src/* .

#WORKDIR /usr/bin

#RUN yum -y install wget

#RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.24.0/geckodriver-v0.24.0-linux64.tar.gz 
#RUN tar -xzvf geckodriver-v0.24.0-linux64.tar.gz
#RUN rm geckodriver-v0.24.0-linux64.tar.gz 
#RUN apt-get update && apt-get install firefox-esr -y


CMD python manage.py migrate && python manage.py createcachetable && python manage.py check && python manage.py test tests/unit-tests/ && gunicorn --bind 0.0.0.0:8080 wsgi


EXPOSE 1337

#docker build --no-cache -t classy .
#docker run -p 0.0.0.0:8080:8080 --env-file .env classy


