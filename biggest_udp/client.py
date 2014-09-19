import argparse as _argparse
import socket as _socket
import struct as _struct
import sys as _sys
import time as _time


def _send_packet(socket, size):
    packet = _struct.pack('>H', size)
    size = max(size, len(packet))
    packet += b'\xff' * (size - len(packet))
    print('Sending {} byte packet.'.format(size))
    socket.send(packet)
    data, addr = socket.recvfrom(2 ** 16)
    print('Got response:')
    (was_truncated,) = _struct.unpack('>B', data[:1])
    if was_truncated == 0:
        print('  Truncated? no.')
    elif was_trunctated == 1:
        print('  Truncated? YES.')
    else:
        print('  Bad response from server.')


def main():
    arg_parser = _argparse.ArgumentParser()
    arg_parser.add_argument('hostname')
    arg_parser.add_argument('port', type=int)
    arg_parser.add_argument('size', type=int)

    pargs = arg_parser.parse_args()

    addr_infos = \
        _socket.getaddrinfo(pargs.hostname, pargs.port, 0, _socket.SOCK_DGRAM)
    for addr_info in addr_infos:
        family, socktype, proto, _, sockaddr = addr_info
        print(family, socktype, proto)
        print('Attempting to connect to {!r}'.format(sockaddr))
        socket = _socket.socket(family, socktype, proto)
        try:
            socket.connect(sockaddr)
        except:
            print('Failed.')
            socket = None
        else:
            break

    if socket is None:
        _sys.exit(1)

    print('Connected! {!r}'.format(socket.getsockname()))
    
    socket.settimeout(1)

    while True:
        _send_packet(socket, pargs.size)
        _time.sleep(1)


if __name__ == '__main__':
    main()
