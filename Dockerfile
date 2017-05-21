FROM python:3.5.1
ENV PYTHONUNBUFFERED 1
MAINTAINER vsochat@stanford.edu
RUN apt-get update && apt-get install -y \
    libopenblas-dev \
    gfortran \
    pkg-config \
    libxmlsec1-dev \
    libhdf5-dev \
    libgeos-dev \
    build-essential \
    openssl \
    nginx \
    git \
    wget

RUN pip install --upgrade pip

# Install pydicom
RUN git clone https://github.com/darcymason/pydicom
WORKDIR pydicom
RUN python setup.py install
RUN mkdir /code
WORKDIR /code
ADD . /code

# Install pynetdicom3
RUN pip install -r requirements.txt
RUN apt-get remove -y gfortran

# Install node_dcm
RUN python setup.py install

RUN apt-get autoremove -y
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

CMD /bin/bash

# https://en.wikipedia.org/wiki/DICOM#Port_numbers_over_IP
EXPOSE 401
EXPOSE 2761
EXPOSE 2762
EXPOSE 11112
