from common.Channel import Channel, Message
from common.Router import Router
from common.TcpConnection import ConnectionClosed
from common.TcpSocket import TcpSocket
import asyncio

from common.messages import CloseMessage, EchoMessage, MessageType, TimeRequestMessage


router = Router()


@router.on(MessageType.ECHO)
async def onEcho(message: Message):
    print('Message:', message.body().decode())


@router.on(MessageType.RETURN_TIME)
async def onTime(message: Message):
    print('Time:', float(message.body().decode()))


@router.otherwise
async def unknown(message: Message):
    print('Unknown message:', message.type(), message.args(), message.body())


async def main():
    connection = TcpSocket('127.0.0.1', 8080).connect() 
    channel = Channel(connection)
    while True:
        print('''
        0 - EXIT
        1 - TIME
        2 - ECHO
        ''')
        choice = int(input())
        match choice:
            case 0:
                await channel.send(CloseMessage())
            case 1:
                await channel.send(TimeRequestMessage())
            case 2:
                await channel.send(EchoMessage(text=input('Text: ')))
            case _:
                print('Unknown choice')
                continue
        response = await router.route(await channel.next())
        if response:
            raise Exception('Unexpected message after routing')


if __name__ == "__main__":
    try:
        asyncio.new_event_loop().run_until_complete(main())
    except ConnectionClosed:
        print('Connection closed')
