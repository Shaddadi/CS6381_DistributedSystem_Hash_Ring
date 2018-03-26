# Sample code for CS6381
# Vanderbilt University
# Instructor: Aniruddha Gokhale
#
# Code taken from ZeroMQ examples with additional
# comments or extra statements added to make the code
# more self-explanatory  or tweak it for our purposes
#
# We are executing these samples on a Mininet-emulated environment
#
#

# system and time
import os
import sys
import time
import threading
import zmq
from random import randrange


class Proxy:
	"""Implementation of the proxy"""

	def __init__(self):
		# Get the context
		# This is a proxy. We create the XSUB and XPUB endpoints
		#print ("This is proxy: creating xsub and xpubsockets")
		self.context = zmq.Context()
		self.xsubsocket = self.context.socket(zmq.XSUB)
		self.xsubsocket.bind("tcp://*:5555")
		self.xpubsocket = self.context.socket (zmq.XPUB)
		self.xpubsocket.setsockopt(zmq.XPUB_VERBOSE, 1)
		self.xpubsocket.bind ("tcp://*:5556")
		self.xpubsocket.send_multipart([b'\x01', b'10001'])
		# Now we are going to create a poller
		self.poller = zmq.Poller ()
		self.poller.register (self.xsubsocket, zmq.POLLIN)
		self.poller.register (self.xpubsocket, zmq.POLLIN)
		# Now threading1 runs regardless of user input
		self.threading1 = threading.Thread(target=self.background_input)
		self.threading1.daemon = True
		self.threading1.start()
		self.global_url = 0
		self.global_port = 0
		self.newSub = False	

	def background_input(self):
		while True:
			addr_input = raw_input()
			ip, port = addr_input.split()
			if True:
				pub_url = "tcp://" + ip + ":" + port
				self.global_port = port
				self.global_url = pub_url
				self.newSub = True

	def history_vector(self, h_vec, ind, history, msg):
			if len(h_vec[ind]) < history:
				h_vec[ind].append(msg)
			else:
				h_vec[ind].pop(0)
				h_vec[ind].append(msg)		
			return h_vec

	def schedule(self):
		cur_strength = 0
		pre_strength = 0
		count = 0
		num = 10
		history_vec = []
		strengh_vec = []
		pubInd = 0
		ownership = 0
		while True:
			events = dict (self.poller.poll (10000))
			# Is there any data from publisher?
			if self.xsubsocket in events:
				msg = self.xsubsocket.recv_multipart()
				#print ("Publication = {}".format (msg))
				content= msg[0]
				zipcode, temperature, relhumidity, ownership, history = content.split(" ")
				#print("all possible ownership", ownership)
				ownership = int(ownership.decode('ascii'))
				history = int(history.decode('ascii'))

				# creat the history stock for each publisher, should be FIFO
				if ownership not in strengh_vec:
					pubInd += 1 # the actual size of the publishers
					strengh_vec.append(ownership)
					#create list for this publisher
					history_vec.append([])
					history_vec = self.history_vector(history_vec, pubInd-1, history, msg)
					#if len(history_vec[pubInd-1]) < history:
					#	history_vec[pubInd-1].append(msg)
					#else:
					#	history_vec[pubInd-1].pop(0)
					#	history_vec[pubInd-1].append(msg)
				else:
					curInd = strengh_vec.index(ownership)
					history_vec = self.history_vector(history_vec, curInd, history, msg)
					#if len(history_vec[curInd]) < history:
					#	history_vec[curInd].append(msg)
					#else:
					#	history_vec[curInd].pop(0)
					#	history_vec[curInd].append(msg)
				#print("history_vec",history_vec)
				if self.newSub:
					ctx = zmq.Context()
					pub = ctx.socket(zmq.PUB)
					pub.bind(self.global_url)
					if ownership == max(strengh_vec):
						curInd = strengh_vec.index(ownership)
						time.sleep(0.5)
						for i in range(len(history_vec[curInd])):
							# print("sending:",history_vec[curInd])
							pub.send_multipart (history_vec[curInd][i])
							# pub.send_multipart(['10001, 0, 0, 0, 0'])
							time.sleep(0.1)
					pub.unbind(self.global_url)
					pub.close()
					ctx.term()
					xurl = "tcp://*:" + self.global_port
					self.xpubsocket.bind(xurl)
					self.newSub = False
				else:
					#send the current message
					if ownership > cur_strength:
						pre_strength = cur_strength
						cur_strength = ownership
						self.xpubsocket.send_multipart (msg)
						count = 0
					elif ownership == cur_strength:
						self.xpubsocket.send_multipart (msg)
						count = 0
					else:
						count = count +1
						if count>= num:
							cur_strength = pre_strength
							count = 0
							# print("nothing happened")


			if self.xpubsocket in events:
				msg = self.xpubsocket.recv_multipart()
				# parse the incoming message
				#print ("subscription = {}".format (msg))
				# send the subscription info to publishers
				# if msg[0] == '\x0110001':
				#     # topic = msg[1:]
				#     newSub = True
				#     #print "Topic: new subscriber"
				# else:
				#     newSub = False
					#print "Topic: subscriber left"

				self.xsubsocket.send_multipart(msg)

	def close(self):
		""" This method closes the PyZMQ socket. """
		self.xsubsocket.close(0)
		self.xpubsocket.close(0)


if __name__ == '__main__':
	proxy = Proxy()
	proxy.schedule()
