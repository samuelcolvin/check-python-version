FROM python:3.10-alpine

COPY ./requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt

COPY ./main.py /app/
COPY ./action.yml /app/

WORKDIR /app

CMD ["/app/main.py"]
