from common.Channel import Channel, Message
from common.Router import Router
from common.TcpConnection import ConnectionClosed
from common.TcpSocket import TcpSocket
from common.Connection import Connection
import time

from common.messages import EchoMessage, MessageType, TimeResponseMessage


router = Router()


@router.on(MessageType.CLOSE)
async def onClose(_):
    raise ConnectionClosed


@router.on(MessageType.ECHO)
async def onEcho(message: Message):
    return message


@router.on(MessageType.GET_TIME)
async def onTime(_):
    return TimeResponseMessage(timestamp=time.time())


@router.otherwise
async def unknown(message: Message):
    return EchoMessage(text=f'Unknown command: {message.type().value} {message.args()} {message.body()}')


async def handle(connection: Connection):
    channel = Channel(connection)
    while True:
        response = await router.route(await channel.next())
        if response:
            await channel.send(response)


def main():
    TcpSocket('0.0.0.0', 8080).listen(handle)


if __name__ == "__main__":
    main()
