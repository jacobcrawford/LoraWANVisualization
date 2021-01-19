FROM python:3.8-buster

LABEL version = "0.1.0"

COPY requirements.txt /target/requirements.txt

WORKDIR target

RUN pip install -r requirements.txt

COPY . /target/

EXPOSE 8050 8050

ENTRYPOINT ["python", "main.py"]