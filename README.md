# CS6381_DistributedSystem_Hash_Ring

The package builds a small layer of middleware on top of XPUB/XSUB and consistent hash ring to support ANONYMITY, OWNERSHIP_STRENGTH and HISTORY. This package is based on the Pub/sub middleware from Assignment#1, build for CS6381 Distributed System assignment#2.

## Collaborators

Ran Hao (rxh349@case.edu) Xiaodong Yang (xiaodong.yang@vanderbilt.edu) Tong Liang (liangtong39@gmail.com)

##Dependences
- memcached: sudo apt-get install memcached (https://github.com/memcached/memcached)
- hash_ring: https://pypi.python.org/pypi/hash_ring

##When running the server node:
First do 'memcached -u "your username" -d -m 64 127.0.0.3 -p 11211'
Then run 'python hash_server.py'

##Run publishers by:
'python publisher.py "address of hash server" "Ownership" "zipnode(topic)"'

##Run subscriber by:
'python subscriber.py "address of hash server" "port(default 5556)" "zipnode(topic)"'

