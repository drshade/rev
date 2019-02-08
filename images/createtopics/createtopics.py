import time, os, sys, json, random
from confluent_kafka.admin import AdminClient, NewTopic, NewPartitions, ConfigSource, ConfigResource
from confluent_kafka import KafkaException

# Grab environment variables
#
brokers = os.environ.get("kafka_bootstrap_servers", "127.0.0.1:9092")

print ("brokers=%s"%(brokers))

def print_config_item(config, depth):
    print('%s%s=%s [%s,is:read-only=%r,default=%r,sensitive=%r,synonym=%r,synonyms=%s]'%
          (' ' * depth, config.name, config.value, ConfigSource(config.source),
           config.is_read_only, config.is_default,
           config.is_sensitive, config.is_synonym,
           ["%s:%s" % (x.name, ConfigSource(x.source))
            for x in iter(config.synonyms.values())]))

def print_config(admin, resource_type, resource_name, depth):
	fs = admin.describe_configs([ConfigResource(resource_type, resource_name)])
	for res, f in fs.items():
		try:
			configs = f.result()
			for config in iter(configs.values()):
				print_config_item(config, depth)

		except KafkaException as e:
			print("Failed to describe {}: {}".format(res, e))
		except Exception:
			raise

def print_broker_info(admin, detailed_config = False):
	metadata = admin.list_topics(timeout=10)
	print ("Cluster %s metadata (response from broker %s)"%(metadata.cluster_id, metadata.orig_broker_name))
	print ("Total Brokers: %d"%(len(metadata.brokers)))
	for broker in iter(metadata.brokers.values()):
		print ("Broker %s %s"%(broker, "(controller)" if metadata.controller_id == broker.id else ""))
		if detailed_config:
			print ("   Config:")
			print_config(admin, "BROKER", str(broker.id), 6)

	print ("Topics: %d"%(len(metadata.topics)))
	for topic in iter(metadata.topics.values()):

		print ("   %s (%d partitions)"%(topic, len(topic.partitions)))
		if topic.error is not None:
			print ("   ^^^ TOPIC ERROR -> %s"%(topic.error))

		if detailed_config:
			print ("      Config:")
			print_config(admin, "TOPIC", str(topic), 9)

		print ("      Partitions:")
		for partition in iter(topic.partitions.values()):
			print ("         id: %s leader: %s replicas: %s in_sync_replicas: %s"%(partition.id, partition.leader, partition.replicas, partition.isrs))

def create_or_ensure_topic(admin, topic, min_partitions, min_replicas):
	metadata = admin.list_topics(timeout=10)

	if topic not in metadata.topics:
		# Create the topic for the first time
		print ("Topic %s does not exist - creating..."%(topic))
		new_topics = [
			NewTopic(topic, num_partitions=min_partitions, replication_factor=min_replicas)
		]
		fs = admin.create_topics(new_topics)
		for topic, f in fs.items():
			try:
				f.result()
				print("Topic %s created"%(topic))
			except Exception as e:
				print("Failed to create topic %s - %s"%(topic, e))
	else:
		# Check the partitions and replication is at least high enough
		if min_partitions > len(metadata.topics[topic].partitions):
			new_partitions = [
				NewPartitions(topic, min_partitions)
			]
			fs = admin.create_partitions(new_partitions)
			for topic, f in fs.items():
				try:
					f.result()
					print("Additional partitions for %s created"%(topic))
				except Exception as e:
					print("Failed to add partitions to topic %s - %s"%(topic, e))

def ensure_topic_config(admin, topic, config_dict):

	# Compare existing configs before determining whether we need to change them
	must_alter = False
	fs = admin.describe_configs([ConfigResource("TOPIC", topic)])
	for res, f in fs.items():
		configs = f.result()
		for config in iter(configs.values()):
			# Check if the values are the same

			if config.name in config_dict.keys():
				if config_dict[config.name] != config.value:
					must_alter = True

	if must_alter:
		fs = admin.alter_configs([ConfigResource("TOPIC", topic, set_config=config_dict)])
		for res, f in fs.items():
			f.result()  # empty, but raises exception on failure
			print("%s configuration successfully altered"%(res))

if __name__ == "__main__":
	while True:
		admin = AdminClient({'bootstrap.servers': brokers})
		print_broker_info(admin, detailed_config=True)
		create_or_ensure_topic(admin, "games", 64, 1)
		ensure_topic_config(admin, "games", { 
			"retention.ms": "3600000"  # 1 hour?
		})
		create_or_ensure_topic(admin, "complete_games", 64, 1)
		ensure_topic_config(admin, "complete_games", { 
			"retention.ms": "3600000"  # 1 hour?
		})
		time.sleep(120)
