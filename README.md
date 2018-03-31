# CS6381_DistributedSystem_Hash_Ring

##Dependences
- memcached: sudo apt-get install memcached (https://github.com/memcached/memcached)
- hash_ring: https://pypi.python.org/pypi/hash_ring

##When running the server node:
First do 'memcached -u ranhao -d -m 64 127.0.0.3 -p 11211'
Then run 'python hash_server.py'

##Run publishers by:
'python publisher "address of hash server" "Ownership" "zipnode(topic)"'

##Run subscriber by:
'python subscriber "address of hash server" "port" "zipnode(topic)"'

