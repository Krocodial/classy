
#FROM classy as builder
FROM docker-registry.default.svc:5000/l9fjgg-tools/classy as builder
RUN python manage.py collectstatic --noinput
RUN chmod -R +r conf

FROM nginx

RUN rm -rf /usr/share/nginx/html/*
COPY --from=builder /home/classy/conf/html /usr/share/nginx/html
COPY --from=builder /home/classy/conf/conf.d/classy.conf.tmpl /tmp/
RUN touch /var/run/nginx.pid && chown -R www-data:www-data /var/run/nginx.pid
RUN chown -R www-data:www-data /var/cache/nginx
RUN chown -R www-data:www-data /usr/share/nginx
RUN chown -R www-data:www-data /etc/nginx

USER www-data

#RUN chown -R nginx:nginx /usr/share/nginx
#RUN chown -R nginx:nginx /etc/nginx
#USER nginx

CMD /bin/bash -c "envsubst < /tmp/classy.conf.tmpl > /etc/nginx/conf.d/default.conf && exec nginx -g 'daemon off;'"

EXPOSE 1337

#docker build -t nginx-proxy .
#docker run -p 0.0.0.0:1337:1337 --env-file .env nginx-proxy

#For example, on my way in to work today I saw a dead bird next to a fire hydrant and thought, “Yeah, that’s a quarter.”
