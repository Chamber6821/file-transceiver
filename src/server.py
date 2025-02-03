from common.TcpSocket import TcpSocket
from common.Connection import Connection


async def handle(connection: Connection):
    while True:
        line = await connection.receiveLine()
        print('Got', line.encode())
        if line == 'exit\n': return
        await connection.sendLine(line)


def main():
    TcpSocket('0.0.0.0', 8080).listen(handle)


main()
