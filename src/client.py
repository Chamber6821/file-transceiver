from common.TcpConnection import ConnectionClosed
from common.TcpSocket import TcpSocket
import asyncio


async def main():
    connection = TcpSocket('127.0.0.1', 8080).connect() 
    while True:
        line = input()
        await connection.sendLine(line)
        line = await connection.receiveLine()
        print(line, end='')


try:
    asyncio.new_event_loop().run_until_complete(main())
except ConnectionClosed:
    print('Connection closed')
