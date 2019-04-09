FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . /usr/src/app

ARG SSO_SERVER
ARG SSO_REALM
ARG SSO_CLIENT_ID
ARG SSO_CLIENT_SECRET

ENV DEBUG=True
ENV DATABASE_SERVICE_NAME=postgresql 
ENV DATABASE_ENGINE=postgresql 
ENV DATABASE_NAME=postgres
ENV POSTGRESQL_SERVICE_HOST=172.17.0.1 
ENV DATABASE_USER=postgres 
ENV DATABASE_PASSWORD=docker
ENV SSO_SERVER=${SSO_SERVER}
ENV SSO_REALM=${SSO_REALM}
ENV SSO_CLIENT_ID=${SSO_CLIENT_ID}
ENV SSO_CLIENT_SECRET=${SSO_CLIENT_SECRET}
ENV REDIRECT_URI=http://localhost:1337

#RUN python manage.py migrate
#RUN python manage.py createcachetable

CMD python manage.py migrate && python manage.py createcachetable && python manage.py check && python manage.py runserver 0.0.0.0:1337

#CMD ["./manage.py", "check", "&&", "./manage.py", "runserver", "0.0.0.0:1337"]

EXPOSE 1337


#docker build --build-arg SSO_CLIENT_SECRET --build-arg SSO_CLIENT_ID --build-arg SSO_SERVER --build-arg SSO_REALM -t classy .
