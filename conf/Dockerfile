FROM nginx

COPY . /usr/share/nginx

WORKDIR /modsecurity

RUN apt-get update

RUN apt-get install -y git

RUN git clone https://github.com/SpiderLabs/ModSecurity.git .

RUN apt-get install -y apt-utils autoconf automake build-essential git libcurl4-openssl-dev libgeoip-dev liblmdb-dev libpcre++-dev libtool libxml2-dev libyajl-dev pkgconf wget zlib1g-dev
