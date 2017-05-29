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
    ipython3 \
    python-tk \
    openssl \
    nginx \
    git \
    wget

RUN pip install --upgrade pip
RUN pip install ipython
RUN mkdir /data

# Install pydicom
WORKDIR /tmp
RUN git clone https://github.com/darcymason/pydicom
WORKDIR pydicom
RUN python setup.py install

# Install pynetdicom3
#RUN pip install -r requirements.txt
WORKDIR /tmp
RUN git clone https://github.com/scaramallion/pynetdicom3
WORKDIR pynetdicom3
RUN python setup.py install

RUN mkdir /code
WORKDIR /code
ADD . /code

RUN apt-get remove -y gfortran

# Install node_dcm
RUN python setup.py install

RUN apt-get autoremove -y
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

CMD /code/run.sh

# https://en.wikipedia.org/wiki/DICOM#Port_numbers_over_IP
EXPOSE 401
EXPOSE 2761
EXPOSE 2762
EXPOSE 11112
