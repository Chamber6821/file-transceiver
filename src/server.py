from src.common.TcpSocket import TcpSocket
from src.common.Connection import Connection


async def handle(connection: Connection):
    command = await connection.receiveLine()
    arg1 = await connection.receiveLine()
    arg2 = await connection.receiveLine()
    arg3 = await connection.receiveBytes(42)


def main():
    TcpSocket('0.0.0.0', 228).listen(handle)

