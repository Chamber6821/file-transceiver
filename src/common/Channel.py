from common.Connection import Connection
from abc import ABC, abstractmethod


class Message(ABC):
    @abstractmethod
    def type(self) -> str:
        pass

    @abstractmethod
    def args(self) -> list[str]:
        pass

    @abstractmethod
    def body(self) -> bytes:
        pass


class InputMessage(Message):
    def __init__(self, type: str, args: list[str], body: bytes) -> None:
        self._type = type
        self._args = args
        self._body = body

    def type(self) -> str:
        return self._type

    def args(self) -> list[str]:
        return self._args

    def body(self) -> bytes:
        return self._body


class Channel:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection


    async def next(self) -> Message:
        type, raw_argn, raw_body_len = (await self.connection.receiveLine()).split()
        argn, body_len = int(raw_argn), int(raw_body_len)
        args = []
        for _ in range(argn):
            args.append(await self.connection.receiveLine())
        body = await self.connection.receiveBytes(body_len)
        return InputMessage(type, args, body)


    async def send(self, message: Message):
        args = message.args()
        body = message.body()
        await self.connection.sendLine(f'{message.type()} {len(args)} {len(body)}')
        for arg in args:
            await self.connection.sendLine(arg)
        await self.connection.sendBytes(body)


