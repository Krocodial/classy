#FROM ${IMG_SRC}:${APP_IMAGE_TAG} as builder
FROM classy:latest as builder
RUN python manage.py collectstatic --noinput
FROM nginx
ARG NGINX_PROXY_URL=http://172.17.0.1:1337
ARG DOLLAR=$
ENV NGINX_PROXY_URL=${NGINX_PROXY_URL}
ENV DOLLAR=${DOLLAR}
WORKDIR /usr/share/nginx
RUN rm -rf /usr/share/nginx/html/*
COPY --from=builder /opt/app-root/src/conf/html /usr/share/nginx/html
WORKDIR /etc/nginx/conf.d
COPY --from=builder /opt/app-root/src/conf/conf.d/classy.conf.tmpl /etc/nginx/conf.d/classy.tmpl
RUN cat classy.tmpl | envsubst > classy.conf


#docker build --build-arg NGINX_PROXY_URL --build-arg DOLLAR -t nginx .
#For example, on my way in to work today I saw a dead bird next to a fire hydrant and thought, “Yeah, that’s a quarter.”
