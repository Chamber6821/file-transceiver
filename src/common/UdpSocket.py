import socket
import asyncio
import traceback

from common.UdpConnection import UdpConnection
from common.Socket import Socket


class UdpSocket(Socket):
    def __init__(self, ip, port) -> None:
        super().__init__()
        self.ip = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.ip, self.port))

    def connect(self, target_ip, target_port):
        return UdpConnection(self.sock, (target_ip, target_port))

    def listen(self, handler):
        while True:
            try:
                data, addr = self.sock.recvfrom(1024)
                connection = UdpConnection(self.sock, addr)
                handler(connection, data, addr)
            except Exception:
                print(traceback.format_exc())