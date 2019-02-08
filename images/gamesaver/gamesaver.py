from game import Reversi
import time, os, json, random
import kafka
import boto3

# Grab environment variables
#
brokers = os.environ.get("kafka_bootstrap_servers", "127.0.0.1:9092")
complete_topic = os.environ.get("complete_topic", "complete_games")

print ("brokers=%s"%(brokers))
print ("complete_topic=%s"%(complete_topic))

if __name__ == "__main__":
	# Random play
	client_id = "hypercomplete"
	consumer = kafka.KafkaConsumer(bootstrap_servers=brokers, client_id=client_id)
	consumer.subscribe(topics=[complete_topic])

	# Client of firehost
	client = boto3.client('firehose', region_name='eu-west-1')

	for message in consumer:
		state = json.loads(message.value)
		#print (state)
		print("Writing to kinesis firehose...")

		response = client.put_record(
			DeliveryStreamName='reversi_random_games',
		    Record={
        		'Data': "%s\n"%(message.value)
    		}
		)
