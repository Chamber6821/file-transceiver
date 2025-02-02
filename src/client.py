from src.common.Channel import Channel
from src.common.TcpSocket import TcpSocket

async def main():
    connection = TcpSocket('1.1.1.1', 228).connect() 
    channel = Channel(connection)
    await channel.send(Download('/a/b/c', offset=0))
    filePart = await channel.next()
    filePart.type() # is FILE_PART
    filePart.args()
    filePart.body()
