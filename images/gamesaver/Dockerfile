FROM python:3.7.2-stretch

RUN pip install kafka-python confluent-kafka boto3

COPY . /app/

CMD ["python", "/app/gamesaver.py"]