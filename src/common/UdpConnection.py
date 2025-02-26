import asyncio
import socket
import struct
from collections import deque

ACK_TIMEOUT = 0.5
WINDOW_SIZE = 4
HEADER_SIZE = 4
PAYLOAD_SIZE = 1300 - HEADER_SIZE

class UdpConnection:
    def __init__(self, sock: socket.socket, address):
        self.sock = sock
        self.address = address
        self.window = deque()
        self.ack_received = {}
        self.seq_num = 0
        self.expected_seq = 0

    async def sendBytes(self, data: bytes):
        chunks = [data[i:i + PAYLOAD_SIZE] for i in range(0, len(data), PAYLOAD_SIZE)]
        self.ack_received = {i: False for i in range(len(chunks))}
        self.window = deque([(i, chunk) for i, chunk in enumerate(chunks)])

        while self.window:
            window_list = list(self.window)[:WINDOW_SIZE]
            for seq, chunk in window_list:
                if not self.ack_received[seq]:
                    packet = struct.pack('!I', seq) + chunk
                    await self._send(packet)

            await asyncio.sleep(ACK_TIMEOUT)

            self.window = deque([(seq, chunk) for seq, chunk in self.window if not self.ack_received[seq]])

    async def sendLine(self, data: str):
        await self.sendBytes(f"{data.strip()}\n".encode())

    async def _send(self, packet: bytes):
        loop = asyncio.get_running_loop()
        await loop.sock_sendto(self.sock, packet, self.address)

    async def receiveBytes(self, length: int) -> bytes:
        received_data = {}
        while True:
            data, addr = await asyncio.get_running_loop().sock_recvfrom(self.sock, length + HEADER_SIZE)
            if addr != self.address:
                continue

            seq, = struct.unpack('!I', data[:HEADER_SIZE])
            payload = data[HEADER_SIZE:]
            received_data[seq] = payload

            ack_packet = struct.pack('!I', seq)
            await self._send(ack_packet)

            if seq == self.expected_seq:
                self.expected_seq += 1

            if len(received_data) == len(set(received_data.keys())):
                return b"".join([received_data[i] for i in sorted(received_data.keys())])

    async def receiveLine(self) -> str:
        data = await self.receiveBytes(1300)
        return data.decode().strip()

    async def handle_ack(self):
        while True:
            data, addr = await asyncio.get_running_loop().sock_recvfrom(self.sock, HEADER_SIZE)
            if addr != self.address:
                continue
            seq, = struct.unpack('!I', data)
            self.ack_received[seq] = True
