FROM docker.uclv.cu/python:3.11

# set work directory
WORKDIR /usr/src/app

# set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
#RUN apt-get update
#RUN apt-get install fontforge
#RUN apt-get install cabextract
#RUN wget https://gist.githubusercontent.com/maxwelleite/10774746/raw/ttf-vista-fonts-installer.sh -q -O - | sudo bash

# install dependencies
COPY requirements.txt .
COPY vista/calibri.ttf ./
COPY vista/calibrib.ttf ./
COPY vista/calibrii.ttf ./
COPY vista/calibriz.ttf ./
RUN mkdir -p /usr/share/fonts/truetype/
RUN install -m644 calibri.ttf /usr/share/fonts/truetype/
RUN install -m644 calibrib.ttf /usr/share/fonts/truetype/
RUN install -m644 calibrii.ttf /usr/share/fonts/truetype/
RUN install -m644 calibriz.ttf /usr/share/fonts/truetype/
RUN rm calibri.ttf
RUN rm calibrib.ttf
RUN rm calibrii.ttf
RUN rm calibriz.ttf

#RUN python3 -m pip --disable-pip-version-check install -r requirements.txt
#RUN python3 -m pip --disable-pip-version-check install -r requirements.txt --index-url http://nexus.isp.cupet.cu/repository/python-group/simple/ --trusted-host nexus.isp.cupet.cu
RUN python3 -m pip --disable-pip-version-check install -r requirements.txt --index-url https://nexus.uclv.edu.cu/repository/pypi/simple/ --trusted-host nexus.uclv.edu.cu
#RUN python3 -m pip --disable-pip-version-check install -r requirements.txt --index-url https://nexus.prod.uci.cu/repository/pypi-proxy/simple/ --trusted-host nexus.prod.uci.cu

EXPOSE 8000

# copy project
COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0","--port", "8000", "--reload", "--reload-dir", "/usr/src/app"]
