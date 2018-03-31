from hash_ring import HashRing
from memcache_ring import MemcacheRing
import memcache

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

        self.mc_object = MemcacheRing(['127.0.0.1:11211','127.0.0.2:11211', '127.0.0.3:11211'])

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

    def registerHashRing(self, zipcode, msg):            
        self.mc_object.set(zipcode, msg)
        # print self.mc_object.get(zipcode)

    def sendToSubscriber(self, zipcode):
        sub_msg = self.mc_object.get(zipcode)
        print(sub_msg)

        self.xpubsocket.send_multipart (sub_msg)
        if self.newSub:
            ctx = zmq.Context()
            pub = ctx.socket(zmq.PUB)
            pub.bind(self.global_url)
            if ownership == max(strengh_vec):
                curInd = strengh_vec.index(ownership)
                time.sleep(1)
                for i in range(len(histry_msg)):
                    pub.send_multipart (sub_msg[i])
                    # pub.send_multipart(['10001, 0, 0, 0, 0'])
                    time.sleep(0.1)
            pub.unbind(self.global_url)
            pub.close()
            ctx.term()
            xurl = "tcp://*:" + self.global_port
            self.xpubsocket.bind(xurl)
            self.newSub = False
        else:
            self.xpubsocket.send_multipart (sub_msg)

    def scheduleInTopic(self, info, msg):
        [cur_strength, pre_strength, count, history_vec, strengh_vec, pubInd, pre_msg, cur_msg] = info

        sample_num = 10
        content= msg[0]
        zipcode, temperature, relhumidity, ownership, history = content.split(" ")

        ownership = int(ownership.decode('ascii'))
        history = int(history.decode('ascii'))
        # creat the history stock for each publisher, should be FIFO
        if ownership not in strengh_vec:
            strengh_vec.append(ownership)
            #create list for this publisher
            history_vec.append([])
            history_vec = self.history_vector(history_vec, pubInd, history, msg)
            pubInd += 1 # the actual size of the publishers
        else:
            curInd = strengh_vec.index(ownership)
            history_vec = self.history_vector(history_vec, curInd, history, msg)

        #get the highest ownership msg to register the hash ring
        if ownership > cur_strength:
            pre_strength = cur_strength
            cur_strength = ownership
            pre_msg = cur_msg
            cur_msg = msg
            count = 0
        elif ownership == cur_strength:
            cur_msg = msg
            count = 0
        else:
            count = count + 1
            if count>= sample_num:
                cur_strength = pre_strength
                cur_msg = pre_msg
                count = 0

        #update the info vector
        info[0] = cur_strength
        info[1] = pre_strength
        info[2] = count
        info[3] = history_vec
        info[4] = strengh_vec
        info[5] = pubInd
        info[6] = pre_msg
        info[7] = cur_msg

        #get the history vector for msg
        histInd = strengh_vec.index(cur_strength)
        histry_msg = history_vec[histInd]

        return cur_msg, histry_msg

    def schedule(self):

        topic_info_queue = []
        topicInd = 0
        zip_list = []
        
        while True:
            events = dict (self.poller.poll (10000))
            # Is there any data from publisher?
            if self.xsubsocket in events:
                print("still in events??")
                msg = self.xsubsocket.recv_multipart()
                #print ("Publication = {}".format (msg))
                content= msg[0]
                zipcode, temperature, relhumidity, ownership, history = content.split(" ")
                
                if zipcode not in zip_list:
                    zip_list.append(zipcode)
                    #for this topic, set initial informations for the ownership and history function
                    cur_strength = 0
                    pre_strength = 0
                    count = 0
                    history_vec = []
                    strengh_vec = []
                    pubInd = 0

                    pre_msg = []
                    cur_msg = []

                    topic_info = [cur_strength, pre_strength, count, history_vec, strengh_vec, pubInd, pre_msg, cur_msg]
                    topic_info_queue.append(topic_info)
                    #start to collect the msg for the new topic
                    topic_msg, histry_msg = self.scheduleInTopic(topic_info_queue[topicInd], msg)
                    topicInd +=1

                else:
                    zipInd = zip_list.index(zipcode)
                    topic_msg, histry_msg = self.scheduleInTopic(topic_info_queue[zipInd], msg)
                    

                #Now register for the topic
                self.registerHashRing(zipcode, topic_msg)
                if self.newSub:
                    self.registerHashRing(zipcode, histry_msg)

                #Send the msg to the registered subscriber, give the key
                self.sendToSubscriber(zipcode)

            if self.xpubsocket in events:
                msg = self.xpubsocket.recv_multipart()
                self.xsubsocket.send_multipart(msg)

    def close(self):
        """ This method closes the PyZMQ socket. """
        self.xsubsocket.close(0)
        self.xpubsocket.close(0)


if __name__ == '__main__':
    proxy = Proxy()
    proxy.schedule()
