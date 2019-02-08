FROM python:3.7.2-stretch

RUN pip install kafka-python confluent-kafka mxnet boto3

COPY . /app/

CMD ["python", "/app/training.py"]