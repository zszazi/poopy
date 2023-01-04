FROM python:3.8-slim-buster

ENV POOPY_VERSION="v0.0.1-beta"

WORKDIR /app

COPY requirements.txt ./requirements.txt

RUN pip install -r requirements.txt

COPY . /app

RUN chmod 755 ./poopy_start.sh

CMD ["/app/poopy_start.sh"]


#docker build -t zszazi/poopy:v0.0.1-beta .
#docker save --output poopy_v0.0.1-beta.tar zszazi/poopy:v0.0.1-beta
#docker run -it --entrypoint bash zszazi/poopy:v0.0.1-beta "poopy_start.sh"