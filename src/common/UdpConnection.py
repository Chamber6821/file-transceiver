import asyncio
import socket
import struct

ACK_TIMEOUT = 0.5
WINDOW_SIZE = 4
HEADER_SIZE = 4
PAYLOAD_SIZE = 1300 - HEADER_SIZE

class UdpConnection:
    def __init__(self, sock: socket.socket, address):
        self.sock = sock
        self.address = address
        self.lock = asyncio.Lock()


    async def sendBytes(self, data: bytes):
        chunks = [data[i:i + PAYLOAD_SIZE] for i in range(0, len(data), PAYLOAD_SIZE)]
        ack_received = {i: False for i in range(len(chunks))}
        window = [(i, chunk) for i, chunk in enumerate(chunks)]

        async def listen_for_acks():
            while not all(ack_received.values()):
                data, addr = await asyncio.get_running_loop().sock_recvfrom(self.sock, HEADER_SIZE)
                if addr != self.address:
                    continue
                seq, = struct.unpack('!I', data)
                async with self.lock:
                    if seq in ack_received:
                        ack_received[seq] = True

        listener_task = asyncio.create_task(listen_for_acks())

        try:
            while not all(ack_received.values()):
                async with self.lock:
                    window_list = [w for w in window if not ack_received[w[0]]][:WINDOW_SIZE]
                for seq, chunk in window_list:
                    packet = struct.pack('!I', seq) + chunk
                    await self._send(packet)
                await asyncio.wait_for(listener_task, timeout=ACK_TIMEOUT)

        finally:
            listener_task.cancel()

    async def sendLine(self, data: str):
        await self.sendBytes(f"{data.strip()}\n".encode())

    async def _send(self, packet: bytes):
        loop = asyncio.get_running_loop()
        await loop.sock_sendto(self.sock, packet, self.address)

    async def receiveBytes(self, length: int) -> bytes:
        received_data = {}
        expected_seq = 0

        while True:
            data, addr = await asyncio.get_running_loop().sock_recvfrom(self.sock, length + HEADER_SIZE)
            if addr != self.address:
                continue

            seq, = struct.unpack('!I', data[:HEADER_SIZE])
            payload = data[HEADER_SIZE:]

            async with self.lock:
                if seq not in received_data:
                    received_data[seq] = payload
                    ack_packet = struct.pack('!I', seq)
                    await self._send(ack_packet)

                if seq == expected_seq:
                    expected_seq += 1
                    while expected_seq in received_data:
                        expected_seq += 1

            if len(received_data) >= (length // PAYLOAD_SIZE + 1):
                return b"".join([received_data[i] for i in sorted(received_data.keys())])

    async def receiveLine(self) -> str:
        data = await self.receiveBytes(1300)
        return data.decode().strip()