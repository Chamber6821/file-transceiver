from common.Connection import Connection, ConnectionClosed
from asyncio import Queue, QueueEmpty


class AsyncConnection(Connection):

    def __init__(self, input: Queue[int], output: Queue[int]) -> None:
        super().__init__()
        self.input = input
        self.output = output

    async def receiveLine(self) -> str:
        data = bytes()
        while len(data) == 0 or data[-1] != b'\n'[0]:
            try:
                byte = bytes([await self.input.get()])
            except QueueEmpty:
                raise ConnectionClosed
            data += byte
        print('recv line', data)
        return data.decode()

    async def receiveBytes(self, length: int) -> bytes:
        data = bytes()
        while len(data) < length:
            try:
                byte = bytes([await self.input.get()])
            except QueueEmpty:
                raise ConnectionClosed
            data += byte
        print('recv bytes', data)
        return data

    async def sendLine(self, str: str):
        await self.sendBytes(f'{str.strip()}\n'.encode())

    async def sendBytes(self, bytes):
        print('send bytes', bytes)
        for byte in bytes:
            try:
                await self.output.put(byte)
            except QueueEmpty:
                raise ConnectionClosed


