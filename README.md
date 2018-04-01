# CS6381_DistributedSystem_Hash_Ring

The package builds a small layer of middleware on top of XPUB/XSUB and consistent hash ring to support ANONYMITY, OWNERSHIP_STRENGTH and HISTORY. This package is based on the Pub/Sub middleware from Assignment#1, build for CS6381 Distributed System Assignment#2.

## Collaborators

Ran Hao (rxh349@case.edu) Xiaodong Yang (xiaodong.yang@vanderbilt.edu) Tong Liang (liangtong39@gmail.com)

## Dependences
- memcached: sudo apt-get install memcached (https://github.com/memcached/memcached)
- hash_ring: https://pypi.python.org/pypi/hash_ring, please download hash_ring-1.3.1.tar.gz near the bottom of the page and extract, then put hash_ring.py and memcache_ring.py of (in the directory of "hash_ring/") in the same folder with our codes.
- pip install python-memcached


## When running the server node:
- First do 'memcached -u "your username" -d -m 64 127.0.0.3 -p 11211'
- Then run 'python hash_server.py'

## Run publishers by ("zipcode" is the topic here):
- 'python publisher.py "address of hash server" "ownership(default 2)" "zipnode(default 10001)"'

## Run subscriber by:
- 'python subscriber.py "address of hash server" "port(default 5556)" "zipnode(default 10001)"'

## When running additional subscribers, if want to receive HISTORY massage, run:

`python subscriber.py "address of the broker node" "port of the subscriber"`

And please indicate the port for the broker: type in the address of the broker and the port number of the subscriber in the broker host window, for example, when running the broker on host 3,  running the a subscriber on host 5:

## Run
`python subscriber1.py 10.0.0.3 1001` when give the subscriber a port of 1001
and type: `10.0.0.3 1001` on the broker's window:

![Alt text](/images/subscriber.png?raw=true)

![Alt text](/images/broker.png?raw=true)


