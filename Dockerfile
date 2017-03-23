FROM ubuntu:16.04

RUN apt update && apt install -y libpng-dev libjpeg-dev p7zip-full wget tar unrar-free phantomjs python3 python3-pip curl libcurl4-openssl-dev

RUN mkdir -p /usr/app

WORKDIR /usr/app

RUN wget http://kindlegen.s3.amazonaws.com/kindlegen_linux_2.6_i386_v2_9.tar.gz -O /tmp/kindlegen.tar.gz

RUN tar -zxvf /tmp/kindlegen.tar.gz 

RUN cp kindlegen /usr/bin

RUN wget https://kcc.iosphe.re/Linux/ -O /tmp/kcc.deb && dpkg -i /tmp/kcc.deb

RUN apt install -y python3-pycurl

COPY . /usr/app/

RUN pip3 install -r requirements.txt

RUN locale-gen en_US.UTF-8 

ENV LANG en_US.UTF-8
