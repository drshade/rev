import time, os, json, random
import kafka

# Grab environment variables
#
brokers = os.environ.get("kafka_bootstrap_servers", "127.0.0.1:9092")
consumer_offsets_topic = os.environ.get("consumer_offsets_topic", "__consumer_offsets")

print ("brokers=%s"%(brokers))
print ("consumer_offsets_topic=%s"%(consumer_offsets_topic))

if __name__ == "__main__":
	client_id = "lagchecker"
	group_id = "lagchecker"
	consumer = kafka.KafkaConsumer(bootstrap_servers=brokers, client_id=client_id, group_id=group_id)
	admin = kafka.admin.KafkaAdminClient(bootstrap_servers=brokers)

	while True:
		for consumername, consumertype in admin.list_consumer_groups():
			print("Consumer: %s (type %s)"%(consumername, consumertype))

			for topicpartition, offsetmetadata in admin.list_consumer_group_offsets(consumername).items():
				consumer_topic, consumer_partition = topicpartition
				offset, metadata = offsetmetadata

				end_offset = list(consumer.end_offsets([topicpartition]).values())[0]
				print("Consumer %s is %s / %s on topic %s (partition %s)"%(consumername, offset, end_offset, consumer_topic, consumer_partition))
		time.sleep(10)

	consumer.close()

