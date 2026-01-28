# Docker image for the BIDS environment
FROM python:3.10-slim-bullseye

# copy the list of packages
COPY requirements.txt /

# supress the warning 'runing pip as the root user'
ENV PIP_ROOT_USER_ACTION=ignore

# install packages
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

# add dockeruser 
RUN useradd -m dockeruser 
USER dockeruser

# define working directory
WORKDIR /home/dockeruser
