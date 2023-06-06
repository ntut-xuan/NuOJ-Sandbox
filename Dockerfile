FROM ubuntu:22.04
RUN rm /bin/sh && ln -s /bin/bash /bin/sh
# setup mirror
RUN sed 's@archive.ubuntu.com@free.nchc.org.tw@' -i /etc/apt/sources.list
# apt update
RUN apt-get update
RUN apt-get install -y python3 python3-pip git build-essential libcap-dev golang
# set arg
ARG NUOJ_SANDBOX_ENABLE_CG
# set env
ENV PYTHONUNBUFFERED=0
ENV NUOJ_SANDBOX_ENABLE_CG=$NUOJ_SANDBOX_ENABLE_CG
# mkdir
RUN rm -rf /etc/nuoj-sandbox
RUN mkdir /etc/nuoj-sandbox
RUN mkdir /etc/nuoj-sandbox/storage
RUN mkdir /etc/nuoj-sandbox/storage/testcase
RUN mkdir /etc/nuoj-sandbox/storage/submission
RUN mkdir /etc/nuoj-sandbox/storage/result
# check support isolate
RUN mkdir /etc/isolate
# make isolate
RUN git clone https://github.com/ioi/isolate.git /etc/isolate
WORKDIR /etc/isolate
RUN make isolate
RUN make install
# cd to nuoj-sandbox
WORKDIR /etc/nuoj-sandbox
COPY . /etc/nuoj-sandbox/
RUN bash backend/env_doctor.sh
# install pyhton package from pip
RUN pip3 install -r requirements.txt
# expose port with 4439
EXPOSE 4439
# execute command
WORKDIR /etc/nuoj-sandbox/backend
CMD flask --debug run --host 0.0.0.0 --port 4439
