from src.common.Channel import Channel
from src.common.TcpSocket import TcpSocket
from src.common.Connection import Connection


async def handle(connection: Connection):
    channel = Channel(connection)

    message = await channel.next()
    message.type()
    message.args()
    message.body()

    await channel.send(FilePart(
        '/a/b/c',
        offset=0,
        total=4096,
        data=b'abc'
    ))
    '''
    FILE_PART 4 3
    /a/b/c
    0
    4096
    abc
    '''


def main():
    TcpSocket('0.0.0.0', 228).listen(handle)

