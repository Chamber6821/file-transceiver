from src.common.Connection import Connection
from socket import socket


class TcpConnection(Connection):
    def __init__(self, connection: socket) -> None:
        super().__init__()
        self.socket = socket

    async def receiveLine(self) -> str:
        return await super().receiveLine()

    async def receiveBytes(self, length) -> bytes:
        return await super().receiveBytes(length)

    async def sendLine(self, str):
        return await super().sendLine(str)

    async def sendBytes(self, bytes):
        return await super().sendBytes(bytes)

