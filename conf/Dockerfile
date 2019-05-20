
FROM l9fjgg-tools/classy as builder
RUN python manage.py collectstatic --noinput
RUN chmod -R +r conf

FROM nginx

RUN rm -rf /usr/share/nginx/html/*
COPY --from=builder /home/classy/conf/html /usr/share/nginx/html
COPY --from=builder /home/classy/conf/conf.d/classy.conf.tmpl /tmp/

CMD /bin/bash -c "envsubst < /tmp/classy.conf.tmpl > /etc/nginx/conf.d/default.conf && exec nginx -g 'daemon off;'"

EXPOSE 1337

#docker build -t nginx-proxy .
#docker run -p 0.0.0.0:1337:1337 --env-file .env nginx-proxy

#For example, on my way in to work today I saw a dead bird next to a fire hydrant and thought, “Yeah, that’s a quarter.”
