import asyncio as _asyncio
import argparse as _argparse
import socket as _socket
import struct as _struct
import signal as _signal


class BiggestUdpProtocol(_asyncio.DatagramProtocol):
    def connection_made(self, transport):
        self._transport = transport

    def datagram_received(self, data, addr):
        print('Got {!r} from {!r}'.format(data, addr))
        (size,) = _struct.unpack('>H', data[:2])
        if len(data) == size:
            print('Packet had correct size.')
            truncated = 0
        else:
            print('Packet was truncated.')
            truncated = 1

        response = _struct.pack('>B', truncated)
        self._transport.sendto(response, addr)


def main():
    arg_parser = _argparse.ArgumentParser()
    arg_parser.add_argument('hostname')
    arg_parser.add_argument('port', type=int)

    pargs = arg_parser.parse_args()

    loop = _asyncio.get_event_loop()

    # oddly, create_dgram_endpoint only creates one Transport, even if you give
    # it something like 'localhost' (which should create one for IPv4, and one
    # for IPv6.)
    addr_info_coro = \
        loop.getaddrinfo(pargs.hostname, pargs.port, type=_socket.SOCK_DGRAM)
    addr_infos = loop.run_until_complete(addr_info_coro)

    for addr_info in addr_infos:
        family, _, proto, _, sockaddr = addr_info
        create_dgram_coro = loop.create_datagram_endpoint(
            BiggestUdpProtocol,
            local_addr=sockaddr[:2],  # this is a hack...
            family=family, proto=proto)
        result = loop.run_until_complete(create_dgram_coro)

    was_sigint = [False]
    def handle_sigint():
        was_sigint[0] = True
        loop.stop()
    loop.add_signal_handler(_signal.SIGINT, handle_sigint)

    loop.run_forever()

    if was_sigint[0]:
        print()  # Ctrl+C usually leaves a visible ^C.
        print('Interrupted by SIGINT; shutdown.')


if __name__ == '__main__':
    main()
