FROM ubuntu:22.04
RUN rm /bin/sh && ln -s /bin/bash /bin/sh
# setup mirror
RUN sed 's@archive.ubuntu.com@free.nchc.org.tw@' -i /etc/apt/sources.list
# apt update
RUN apt-get update
RUN apt-get install -y python3 python3-pip git build-essential libcap-dev
# set env
ENV PYTHONUNBUFFERED=0
# mkdir
RUN rm -rf /etc/nuoj-sandbox
RUN mkdir /etc/nuoj-sandbox
RUN mkdir /etc/nuoj-sandbox/storage
RUN mkdir /etc/nuoj-sandbox/storage/testcase
RUN mkdir /etc/nuoj-sandbox/storage/submission
RUN mkdir /etc/nuoj-sandbox/storage/result
RUN mkdir /etc/isolate
# make isolate
RUN git clone https://github.com/ioi/isolate.git /etc/isolate
WORKDIR /etc/isolate
RUN make isolate
RUN make install
# cd to nuoj-sandbox
WORKDIR /etc/nuoj-sandbox
COPY . /etc/nuoj-sandbox/
# install pyhton package from pip
RUN pip3 install Flask
RUN pip3 install requests
RUN pip3 install dataclass_wizard
RUN pip3 install pytest
# expose port with 4439
EXPOSE 4439
# execute command
CMD python3 sandbox_be.py
