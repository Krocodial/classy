FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . /usr/src/app

ENV DEBUG=True
ENV DATABASE_SERVICE_NAME=postgresql DATABASE_ENGINE=postgresql DATABASE_NAME=postgres
ENV POSTGRESQL_SERVICE_HOST=172.17.0.1 DATABASE_USER=postgres DATABASE_PASSWORD=docker
ENV SSO_SERVER=https://sso.pathfinder.gov.bc.ca SSO_REALM=classy SSO_CLIENT_ID=classy-dev SSO_CLIENT_SECRET=aa1f003a-a3ce-45dc-a011-87e5770dc290
ENV REDIRECT_URI=http://localhost:1337

CMD ["python", "manage.py", "migrate"]

CMD ["python", "./manage.py", "runserver", "0.0.0.0:1337"]

EXPOSE 1337