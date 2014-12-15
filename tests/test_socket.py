import diana.socket as s
import diana.packet as p
import socket
from nose.tools import *

def test_create_socket():
    def mock_connect(address):
        eq_(address, ('artemis', 2210))
        class MockFD:
            pass
        return MockFD()
    tx, rx = s.connect('artemis', 2210, connect=mock_connect)

def test_transmit_socket():
    logs = {'sent': b''}
    def mock_connect(address):
        eq_(address, ('artemis', 2210))
        class MockFD:
            def send(self, data):
                logs['sent'] += data
        return MockFD()
    tx, rx = s.connect('artemis', 2210, connect=mock_connect)
    tx(p.WelcomePacket('Welcome to eyes'))
    eq_(logs['sent'], b'\xef\xbe\xad\xde\x27\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x13\x00\x00\x00\xda\xb3\x04\x6dWelcome to eyes')

def test_recv_socket():
    def mock_connect(address):
        eq_(address, ('artemis', 2210))
        class MockFD:
            def recv(self, maxlen):
                return b'\xef\xbe\xad\xde\x27\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x13\x00\x00\x00\xda\xb3\x04\x6dWelcome to eyes'
        return MockFD()
    tx, rx = s.connect('artemis', 2210, connect=mock_connect)
    packet = next(rx)
    assert isinstance(packet, p.WelcomePacket)
    eq_(packet.message, 'Welcome to eyes')

