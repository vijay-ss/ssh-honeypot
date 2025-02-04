# ssh-honeypot

ssh-keygen -t rsa -b 2048 -f server.key

ssh -p 2223 username@127.0.0.1

python3 honeypy.py -a 127.0.0.1 -p 2223 -u hi -pw hi --ssh