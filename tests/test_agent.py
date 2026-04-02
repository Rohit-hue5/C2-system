# test_agent.py
import socket
import time

s = socket.socket()
s.connect(("127.0.0.1", 5001))

while True:
    s.send(b"hello\n")
    time.sleep(2)
