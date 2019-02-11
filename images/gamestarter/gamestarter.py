from game import Reversi
import time, os, sys
import kafka

# Grab environment variables
#
brokers = os.environ.get("kafka_bootstrap_servers", "127.0.0.1:9092")
to_topic = os.environ.get("to_topic", "games")

print ("brokers=%s"%(brokers))
print ("to_topic=%s"%(to_topic))

iterations = 100

if __name__ == "__main__":
	# Random play
	prod = kafka.KafkaProducer(bootstrap_servers=brokers)

	start = time.time()

	while True:
		for iteration in range(iterations):
			game = Reversi()

			state = game.state_to_string()
			(complete, whitepoints, blackpoints, empty) = game.stats()
			
			print(state)
			prod.send(to_topic, key=bytearray([whitepoints+blackpoints]), value=state.encode())

		prod.flush()
		
		print ("Started %d games"%(iterations))
		time.sleep(120)

	prod.close()

	end = time.time()
	print("Took %0.3fs to generate %d iterations"%(end - start, iterations))