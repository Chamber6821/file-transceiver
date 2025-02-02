from src.common.TcpSocket import TcpSocket

async def main():
    connection = TcpSocket('1.1.1.1', 228).connect() 
    await connection.sendLine('command')
    await connection.sendLine('arg1')
    await connection.sendLine('arg2')
    await connection.sendBytes(b'arg3')
