FROM owasp/modsecurity-crs:v3.2-modsec3-nginx
WORKDIR /etc/nginx

RUN echo 'deb http://deb.debian.org/debian stretch-backports main' >> /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y certbot python-certbot-nginx -t stretch-backports

#RUN rm -rf /usr/share/nginx/html/*
RUN rm -f /etc/nginx/conf.d/*
COPY html/ /var/www/classy/
COPY conf.d/classy.conf.tmpl /tmp/
COPY nginx.conf /etc/nginx/nginx.conf
COPY modsecurity.conf /etc/modsecurity.d/modsecurity.conf

RUN touch /var/run/nginx.pid && \
    mkdir /etc/nginx/logs

RUN chmod -R g+rwx /var/cache/nginx/ && \
    chmod -R g+rw /etc/nginx /var/log/nginx /tmp/classy.conf.tmpl /var/run/nginx.pid && \
    mkdir /opt/modsecurity && mkdir /opt/modsecurity/audit/ && \
    touch /opt/modsecurity/audit/modsec_audit.log && \
    chmod -R g+rw /opt/owasp-modsecurity-crs-3.2 /opt/modsecurity/audit/modsec_audit.log && \
    chmod -R g+r /var/www/classy


USER 1001

CMD /bin/bash -c "envsubst < /tmp/classy.conf.tmpl > /etc/nginx/conf.d/classy.conf && exec nginx -g 'daemon off;'"

EXPOSE 1337

#docker build -t nginx-proxy .
#docker run -p 0.0.0.0:1337:1337 --env-file .env nginx-proxy

#For example, on my way in to work today I saw a dead bird next to a fire hydrant and thought, “Yeah, that’s a quarter.”
