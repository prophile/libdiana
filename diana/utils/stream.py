from diana import connect
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Simple Artemis SBS stream')
    parser.add_argument('address', help='Server address (DNS, IPv4 or IPv6)')
    parser.add_argument('port', type=int, nargs='?', default=2010, help='Server port')
    args = parser.parse_args()
    tx, rx = connect(args.address, args.port)
    try:
        for packet in rx:
            print(packet)
    except KeyboardInterrupt:
        pass

