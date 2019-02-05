from game import Reversi
import time, os, json, random
import kafka

# How to run kafka locally:
# docker run --rm -p 2181:2181 -p 3030:3030 -p 8081-8083:8081-8083 \
#      -p 9581-9585:9581-9585 -p 9092:9092 -e ADV_HOST=127.0.0.1 \
#      landoop/fast-data-dev:latest

# Grab environment variables
#
brokers = os.environ.get("kafka_bootstrap_servers", "127.0.0.1:9092")
to_topic = os.environ.get("to_topic", "games")
complete_topic = os.environ.get("complete_topic", "complete_games")

print ("brokers=%s"%(brokers))
print ("to_topic=%s"%(to_topic))

if __name__ == "__main__":
	# Random play
	client_id = "playerrandom"
	group_id = "playerrandom"
	consumer = kafka.KafkaConsumer(bootstrap_servers=brokers, client_id=client_id, group_id=group_id)
	consumer.subscribe(topics=[to_topic])

	producer = kafka.KafkaProducer(bootstrap_servers=brokers)

	for message in consumer:
		# Receive a game state
		in_state = message.value

		# Load the game state into a game
		game = Reversi()
		game.state_from_string(in_state)

		# Check if the game might be completed already
		(complete, whitepoints, blackpoints, empty) = game.stats()

		print("Processing game -> white: %d black: %d"%(whitepoints, blackpoints))

		if complete:
			print("Game has ended")

			if whitepoints == blackpoints:
				# Skip tied games
				print("Tied the game! and ignoring")
				continue

			winner = "w" if whitepoints > blackpoints else "b"

			# Where white is the winner of this game
			complete_game_white_winner = {
				"winner" : "w"
			}
			if winner != "w":
				game.invert()
			complete_game_white_winner["moves"] = game._moves
			out_state = game.state_to_string()
			#print(json.dumps(complete_game_white_winner))
			producer.send(complete_topic, value=json.dumps(complete_game_white_winner).encode("ascii"))
			producer.flush()

			# Where black is the winner of this game
			complete_game_white_loser = {
				"winner" : "b"
			}
			if winner == "w":
				game.invert()
			complete_game_white_loser["moves"] = game._moves
			out_state = game.state_to_string()
			producer.send(complete_topic, value=json.dumps(complete_game_white_loser).encode("ascii"))
			producer.flush()

			continue

		# Play one random move
		options = game.all_valid_placements()
		if len(options) == 0:
			game.skip()
		else:
			(chosenx, choseny) = options[random.randint(0, len(options) - 1)]
			game.place(chosenx, choseny)

		# Save the next move
		out_state = game.state_to_string()
		producer.send(to_topic, key=bytearray([whitepoints+blackpoints]), value=out_state.encode("ascii"))
		producer.flush()

	start = time.time()
	iterations = 100

	producer.close()
	consumer.close()


	end = time.time()
