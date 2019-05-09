#This file is used for development. Since the version of Docker on OpenShift is out-of-date dockerfiles are instead passed in as strings. This can be seen in the ~/openshit/templates/nginx-bc.json config.
FROM classy:latest as builder
WORKDIR /opt/app-root
RUN python src/manage.py collectstatic --noinput
FROM nginx
WORKDIR /usr/share/nginx
RUN rm -rf /usr/share/nginx/html/*
COPY --from=builder /opt/app-root/src/conf/html /usr/share/nginx/html
COPY --from=builder /opt/app-root/src/conf/conf.d/classy.conf.tmpl /tmp/
WORKDIR /etc/nginx/conf.d/
RUN chmod -R 666 /etc/nginx/conf.d/default.conf
#RUN rm -f /etc/nginx/conf.d/default.conf

CMD /bin/bash -c "envsubst < /tmp/classy.conf.tmpl > /etc/nginx/conf.d/default.conf && exec nginx -g 'daemon off;'"

EXPOSE 1337

#docker build -t nginx-proxy .
#docker run -p 0.0.0.0:1337:1337 --env-file .env nginx-proxy

#For example, on my way in to work today I saw a dead bird next to a fire hydrant and thought, “Yeah, that’s a quarter.”
