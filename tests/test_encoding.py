from diana.encoding import encode, decode
from nose.tools import eq_

DECODE_TESTS = [ ('', (), ()),
                 ('b', (0x00,), (0,)),
                 ('BB', (0x12, 0xfe), (0x12, 0xfe)),
                 ('bb', (0x12, 0xfe), (0x12, -2)),
                 ('s', (0x12, 0x34), (0x3412,)),
                 ('s', (0xff, 0xff), (-1,)),
                 ('S', (0xff, 0xff), (0xffff,)),
                 ('i', (0x12, 0x34, 0x56, 0x78), (0x78563412,)),
                 ('I', (0xff, 0xff, 0xff, 0xff), (0xffffffff,)),
                 ('i', (0xff, 0xff, 0xff, 0xff), (-1,)),
                 ('f', (0x00, 0x00, 0x80, 0x3f), (1.0,)),
                 ('u', (0x05, 0x00, 0x00, 0x00,
                        0x62, 0x00, 0x65, 0x00,
                        0x65, 0x00, 0x73, 0x00,
                        0x00, 0x00), ('bees',)),
                 ('[B]', (0x12, 0x34, 0x56, 0x78),
                         ([(0x12,), (0x34,), (0x56,), (0x78,)],)),
                 ('[BB]', (0x12, 0x34, 0x56, 0x78),
                         ([(0x12, 0x34), (0x56, 0x78)],)),
                 ('B[BB]B', (0x12, 0x34, 0x56, 0x78),
                            (0x12, [(0x34, 0x56)], 0x78)),
                 ('B[]', (0x12,), (0x12, [])) ]

def test_encode():
    def code(fmt, coded, uncoded):
        data = bytes(coded)
        output = encode(fmt, uncoded)
        eq_(output, data)
    for fmt, coded, uncoded in DECODE_TESTS:
        yield code, fmt, coded, uncoded

def test_decode():
    def code(fmt, coded, uncoded):
        data = bytes(coded)
        output = decode(fmt, data)
        eq_(output, uncoded)
    for fmt, coded, uncoded in DECODE_TESTS:
        yield code, fmt, coded, uncoded

