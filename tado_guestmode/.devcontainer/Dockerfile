FROM python:3.7-buster
LABEL maintainer="Martin Jones <whatdaybob@outlook.com>"

# Copy and install requirements
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# create abc user so root isn't used
RUN \
	groupmod -g 1000 users && \
	useradd -u 911 -U -d /config -s /bin/false abc && \
	usermod -G users abc && \
# create some files / folders
	mkdir -p /config /app && \
	touch /var/lock/tado_guestmode.lock

# add volumes
VOLUME /config

# Add tado_guestmode app
COPY app/ /app
WORKDIR /app

# update file permissions
RUN \
    chmod a+x \
    /app/tado_guestmode.py \ 
    /app/rest.py \
    /app/utils.py \
    /app/config.yml.template

# ENV setup
ENV CONFIGPATH /config/config.yml