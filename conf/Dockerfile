ARG docker_repo=classy
RUN echo '${docker_repo}'

FROM ${docker_repo} as builder
#FROM docker-registry.default.svc:5000/l9fjgg-tools/classy as builder
RUN python manage.py collectstatic --noinput
RUN chmod -R +r conf

FROM nginx
#FROM registry.access.redhat.com/rhscl/nginx-112-rhel7

RUN rm -rf /usr/share/nginx/html/*
RUN rm -f /etc/nginx/conf.d/default.conf
COPY --from=builder /home/classy/conf/html /var/www/classy/
COPY conf.d/classy.conf.tmpl /tmp/
COPY nginx.conf /etc/nginx/nginx.conf

RUN useradd --gid 0 -c "SVR usr" www-svr

RUN touch /var/run/nginx.pid 
RUN mkdir /etc/nginx/logs
#RUN chown -R www-svr:0 /var/run/nginx.pid
#RUN chown -R www-svr:0 /var/cache/nginx
#RUN chown -R www-svr:0 /usr/share/nginx
#RUN chown -R www-svr:0 /etc/nginx
#RUN chown -R www-svr:0 /var/log/nginx
#RUN chown -R www-svr:0 /tmp/classy.conf.tmpl

#USER www-svr

#RUN ln -sf /dev/stdout /etc/nginx/logs/nginx-proxy.access.log;
#RUN ln -sf /dev/stderr /etc/nginx/logs/nginx-proxy.error.log;

RUN chmod g+rw /var/run/nginx.pid
RUN chmod -R g+rwx /var/cache/nginx/
RUN chmod -R g+rw /etc/nginx
RUN chmod -R g+rw /var/log/nginx
RUN chmod -R g+rw /tmp/classy.conf.tmpl
RUN chmod -R g+r /var/www/classy
#RUN chmod +rw /etc/nginx/conf.d
#RUN chown -R nginx:nginx /usr/share/nginx
#RUN chown -R nginx:nginx /etc/nginx
#USER nginx
USER www-svr
CMD /bin/bash -c "envsubst < /tmp/classy.conf.tmpl > /etc/nginx/conf.d/classy.conf && exec nginx -g 'daemon off;'"

EXPOSE 1337

#docker build -t nginx-proxy .
#docker run -p 0.0.0.0:1337:1337 --env-file .env nginx-proxy

#For example, on my way in to work today I saw a dead bird next to a fire hydrant and thought, “Yeah, that’s a quarter.”
