from diana import packet
import argparse
import asyncio
import sys
import socket
from functools import partial

class Buffer:
    def __init__(self, provenance):
        self.buffer = b''
        self.provenance = provenance

    def eat(self, data):
        self.buffer += data
        packets, self.buffer = packet.decode(self.buffer, provenance=self.provenance)
        return packets

BLOCKSIZE = 1024

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Simple Artemis SBS proxy')
    parser.add_argument('proxy_port', type=int, help='Server port')
    parser.add_argument('address', help='Server address (DNS, IPv4 or IPv6)')
    parser.add_argument('port', type=int, nargs='?', default=2010, help='Server port')
    args = parser.parse_args()

    loop = asyncio.get_event_loop()

    @asyncio.coroutine
    def transit(reader, writer, provenance, tag):
        buf = Buffer(provenance)
        while True:
            data = yield from reader.read(BLOCKSIZE)
            for pkt in buf.eat(data):
                writer.write(packet.encode(pkt, provenance=provenance))
                sys.stdout.write('{} {}\n'.format(tag, pkt))
                sys.stdout.flush()

    @asyncio.coroutine
    def handle_p2c(client_reader, client_writer):
        server_reader, server_writer = yield from asyncio.open_connection(args.address,
                                                                          args.port,
                                                                          loop=loop)
        asyncio.async(transit(client_reader, server_writer,
                              provenance=packet.PacketProvenance.client,
                              tag='[C>S]'), loop=loop)
        asyncio.async(transit(server_reader, client_writer,
                              provenance=packet.PacketProvenance.server,
                              tag='[C<S]'), loop=loop)

    svr = asyncio.start_server(handle_p2c, '127.0.0.1', args.proxy_port, loop=loop)
    server = loop.run_until_complete(svr)

    loop.run_forever()

