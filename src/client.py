from common.Channel import Channel, Message
from common.Router import Router
from common.TcpConnection import ConnectionClosed
from common.TcpSocket import TcpSocket
import asyncio
import time, os

from common.messages import CloseMessage, EchoMessage, MessageType, TimeRequestMessage, DownloadMessage, UploadMessage


router = Router()


@router.on(MessageType.ECHO)
async def onEcho(message: Message):
    print(message.body().decode())


@router.on(MessageType.RETURN_TIME)
async def onTime(message: Message):
    print(time.asctime(time.localtime(float(message.body().decode()))))

@router.on(MessageType.DOWNLOAD_PART)
async def onDownload(message: Message):
    rawFilename, rawOffset, rawLength = message.args()
    filename, offset, length = rawFilename, int(rawOffset), int(rawLength)
    if not filename:
        return EchoMessage(text='Invalid filename')
    if not os.path.exists(filename):
        return EchoMessage(text=f'Not found {filename}')
    with open(filename, 'rb') as f:
        f.seek(offset)
        data = f.read(length if length > 0 else -1)
        return UploadMessage(
            filename=rawFilename,
            offset=offset,
            totalLength=os.path.getsize(filename),
            data=data
        )

@router.on(MessageType.UPLOAD_PART)
async def onUpload(message: Message):
    rawFilename, rawOffset, rawTotalLength = message.args()
    filename, offset, totalLength = rawFilename[:-1], int(rawOffset), int(rawTotalLength)
    data = message.body()
    with open(filename, 'a'):
        pass
    with open(filename, 'rb+') as f:
        f.truncate(offset + len(data))
        f.seek(offset)
        f.write(data)
        

@router.otherwise
async def unknown(message: Message):
    print('Unknown message:', message.type(), message.args(), message.body())


async def main():
    connection = TcpSocket('127.0.0.1', 8080).connect() 
    channel = Channel(connection)
    while True:
        rawCommand = input('~> ')
        if rawCommand == '':
            continue
        command = rawCommand.split()
        match command[0]:
            case 'CLOSE':
                await channel.send(CloseMessage())
            case 'TIME':
                await channel.send(TimeRequestMessage())
            case 'ECHO':
                if len(command) < 2:
                    print('Invalid massage')
                    continue
                await channel.send(EchoMessage(text=command[1]))
            case 'DOWNLOAD':
                if len(command) < 2:
                    print('Invalid filename')
                    continue
                if not os.path.exists(command[1]):
                    await channel.send(DownloadMessage(filename=command[1]))
                    continue
                await channel.send(DownloadMessage(filename=command[1], offset=os.path.getsize(command[1])))  
            case 'UPLOAD':
                if len(command) < 2:
                    print('Invalid filename')
                    continue
                if not os.path.exists(command[1]):
                    print(f'Not found {command[1]}')
                    continue
                with open(command[1], 'rb') as f:
                    length = os.path.getsize(command[1])
                    await channel.send(UploadMessage(filename=command[1], offset=0, totalLength=length, data=f.read(length if length > 0 else -1)))  # Значение по умолчанию
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
