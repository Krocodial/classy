FROM nginx

ARG NGINX_PROXY_URL=http://172.17.0.1:1337
ARG DOLLAR=$

ENV NGINX_PROXY_URL=${NGINX_PROXY_URL}
ENV DOLLAR=${DOLLAR}

WORKDIR /usr/share/nginx

RUN rm -rf /usr/share/nginx/html/*
COPY --from=docker-registry.default.svc:5000/l9fjgg-tools/classy /opt/app-root/src/conf/html /usr/share/nginx/html

WORKDIR /etc/nginx/conf.d
COPY ./conf.d/classy.conf.tmpl /etc/nginx/conf.d/classy.tmpl
RUN cat classy.tmpl | envsubst > classy.conf


#docker build --build-arg NGINX_PROXY_URL --build-arg DOLLAR -t nginx .
#For example, on my way in to work today I saw a dead bird next to a fire hydrant and thought, “Yeah, that’s a quarter.”
