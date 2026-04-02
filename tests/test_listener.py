# tests/test_listener.py

import socket


def test_listener_connection():
    s = socket.socket()
    try:
        s.connect(("127.0.0.1", 4444))
        assert True
    except:
        assert False
    finally:
        s.close()
