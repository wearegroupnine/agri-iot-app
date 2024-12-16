FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR ./

RUN apt-get update
RUN apt-get install -y python3.8 python3-pip
RUN pip install flask
RUN pip install flask_wtf
RUN pip install flask_uploads
RUN pip install Flask-Reuploaded
RUN pip install opencv-python-headless
RUN pip install pillow
RUN pip install requests

ADD . ./agri

CMD ["/bin/bash", "./agri/start.sh"]
