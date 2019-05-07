FROM nginx:1.15.10

COPY . /usr/share/nginx

WORKDIR /modsec


RUN apt-get update && apt-get install -y \
	apt-utils \
	autoconf \
	automake \
	build-essential \
	git \
	libcurl4-openssl-dev \
	libgeoip-dev \
	liblmdb-dev \
	libpcre++-dev \
	libtool \
	libxml2-dev \
	libyajl-dev \
	pkgconf \
	wget \
	zlib1g-dev

RUN git clone --depth 1 -b v3/master --single-branch https://github.com/SpiderLabs/ModSecurity 

WORKDIR /modsec/ModSecurity
RUN git submodule init
RUN git submodule update

RUN ls && pwd

RUN ./build.sh

RUN ./configure

RUN make && make install

RUN git clone --depth 1 https://github.com/SpiderLabs/ModSecurity-nginx.git

RUN wget https://nginx.org/download/nginx-1.15.10.tar.gz
RUN tar zxvf nginx-1.15.10.tar.gz

WORKDIR /modsec/ModSecurity/nginx-1.15.10

RUN ./configure --with-compat --add-dynamic-module=../ModSecurity-nginx
RUN make modules
RUN cp objs/ngx_http_modsecurity_module.so /etc/nginx/modules

RUN load_module modules/ngx_http_modsecurity_module.so;

RUN mkdir /etc/nginx/modsec
RUN wget -P /etc/nginx/modsec/ https://raw.githubusercontent.com/SpiderLabs/ModSecurity/v3/master/modsecurity.conf-recommended
RUN mv /etc/nginx/modsec/modsecurity.conf-recommended /etc/nginx/modsec/modsecurity.conf
RUN sed -i 's/SecRuleEngine DetectionOnly/SecRuleEngine On/' /etc/nginx/modsec/modsecurity.conf