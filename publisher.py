# Sample code for CS6381
# Vanderbilt University
# Instructor: Aniruddha Gokhale
#
# Code based on basic pub/sub but modified for xsub and xpub
#
# We are executing these samples on a Mininet-emulated environment
#
#

#
#   Weather update server
#   Publishes random weather updates
#  Connects to a xsub on port 5555
#

import sys

import zmq
from random import randrange

class Publisher:
	"""Implementation of a publisher"""

	def __init__(self, broker_addr, ownership_strength):
		self.broker = broker_addr
		self.strength = ownership_strength

		self.context = zmq.Context()
		self.socket = self.context.socket(zmq.PUB)
		# Connet to the broker
		#context = zmq.Context()
		connect_str = "tcp://" + self.broker + ":5555"
		#socket = context.socket(zmq.PUB)
		#print ("Publisher connecting to proxy at: {}".format(connect_str))
		self.socket.connect(connect_str)
		#print "connected!"

	def publish(self):
		# Keep publishing
		history = 3
		while True:
			zipcode = randrange(1, 100000)
			temperature = randrange(-80, 135)
			relhumidity = randrange(10, 60)
			#print ("Sending: %i %i %i" % (zipcode, temperature, relhumidity))
			self.socket.send_string("%i %i %i %i %i" % (zipcode, temperature, relhumidity, self.strength, history))

	def close(self):
		""" This method closes the PyZMQ socket. """
		self.socket.close(0)

if __name__ == '__main__':
	broker = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
	strength = 2
	if len(sys.argv) > 2:
		strength =  sys.argv[2]
		strength = int(strength)
	#pub = Publisher(broker, strength)
	pub = Publisher(broker,strength)
	pub.publish()

