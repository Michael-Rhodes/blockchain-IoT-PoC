From ubuntu:latest

RUN apt-get update -y
RUN apt-get install -y python3 python3-pip python3-dev build-essential

RUN mkdir /myApp
WORKDIR /myApp

COPY blockchain/requirements.txt /myApp/
RUN pip3 install -r requirements.txt

COPY blockchain/blockchain.py /myApp/

ENTRYPOINT ["python3"]
CMD ["blockchain.py"]
