FROM owasp/modsecurity:3-nginx
RUN echo 'deb http://deb.debian.org/debian stretch-backports main' >> /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y certbot python-certbot-nginx -t stretch-backports

WORKDIR /opt/modsecurity
RUN wget https://github.com/SpiderLabs/owasp-modsecurity-crs/archive/v3.1.0.tar.gz && \
    tar xzvf v3.1.0.tar.gz && \
    cp /opt/modsecurity/owasp-modsecurity-crs-3.1.0/crs-setup.conf.example /etc/modsecurity.d/crs-setup.conf && \
    cp -r /opt/modsecurity/owasp-modsecurity-crs-3.1.0/rules /etc/modsecurity.d/rules

RUN echo "include /etc/modsecurity.d/crs-setup.conf\ninclude /etc/modsecurity.d/rules/*.conf" >> /etc/modsecurity.d/include.conf

RUN rm -f /etc/nginx/conf.d/*
COPY html/ /var/www/classy/
COPY conf.d/classy.conf.tmpl /tmp/
COPY nginx.conf /etc/nginx/nginx.conf
#COPY modsecurity.conf /etc/modsecurity.d/modsecurity.conf

RUN sed -i 's/SecRuleEngine DetectionOnly/SecRuleEngine On/' /etc/modsecurity.d/modsecurity.conf && \
    sed -i 's/SecRequestBodyLimit 13107200/SecRequestBodyLimit 209715200/' /etc/modsecurity.d/modsecurity.conf


RUN touch /var/run/nginx.pid && \
    mkdir /etc/nginx/logs

RUN chmod -R g+rwx /var/cache/nginx/ && \
    chmod -R g+rw /etc/nginx /var/log/nginx /tmp/classy.conf.tmpl /var/run/nginx.pid && \
    chmod -R g+r /var/www/classy && \
    touch /var/log/modsec_audit.log && chmod g+rw /var/log/modsec_audit.log 
#    chmod -R g+r /etc/modsecurity.d/ /opt/
#    mkdir -p /opt/modsecurity/uploads/ && \

ENV TZ=America/Vancouver
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone 

USER 1001

CMD /bin/bash -c "envsubst < /tmp/classy.conf.tmpl > /etc/nginx/conf.d/classy.conf && exec nginx -g 'daemon off;'"

EXPOSE 1337

#docker build -t nginx-proxy .
#docker run -p 0.0.0.0:1337:1337 --env-file .env nginx-proxy

#For example, on my way in to work today I saw a dead bird next to a fire hydrant and thought, “Yeah, that’s a quarter.”
