from common.Channel import Channel, Message
from common.Router import Router
from common.TcpConnection import ConnectionClosed
from common.TcpSocket import TcpSocket
import asyncio
import time, os
import readline

from common.messages import CloseMessage, EchoMessage, MessageType, TimeRequestMessage, DownloadMessage, UploadMessage

commands = ['HELP', 'CLOSE', 'TIME', 'ECHO', 'DOWNLOAD', 'UPLOAD']

def completer(text, state):
    options = [cmd for cmd in commands if cmd.startswith(text.upper())]
    return options[state] if state < len(options) else None

readline.parse_and_bind("tab: complete")
readline.set_completer(completer)


router = Router()


# @router.on(MessageType.ECHO)
# async def onEcho(message: Message):
#     print(message.body().decode())


# @router.on(MessageType.RETURN_TIME)
# async def onTime(message: Message):
#     print(time.asctime(time.localtime(float(message.body().decode()))))


# @router.on(MessageType.DOWNLOAD_PART)
# async def onDownload(message: Message):
#     rawFilename, rawOffset, rawLength = message.args()
#     filename, offset, length = rawFilename, int(rawOffset), int(rawLength)
#     if not filename:
#         return EchoMessage(text='Invalid filename')
#     if not os.path.exists(filename):
#         return EchoMessage(text=f'Not found {filename}')
#     with open(filename, 'rb') as f:
#         f.seek(offset)
#         data = f.read(length if length > 0 else -1)
#         return UploadMessage(
#             filename=rawFilename,
#             offset=offset,
#             totalLength=os.path.getsize(filename),
#             data=data
#         )


# @router.on(MessageType.UPLOAD_PART)
# async def onUpload(message: Message):
#     rawFilename, rawOffset, rawTotalLength = message.args()
#     filename, offset, totalLength = rawFilename[:-1], int(rawOffset), int(rawTotalLength)
#     data = message.body()
#     with open(filename, 'a'):
#         pass
#     with open(filename, 'rb+') as f:
#         f.truncate(offset + len(data))
#         f.seek(offset)
#         f.write(data)
        

# @router.otherwise
# async def unknown(message: Message):
#     print('Unknown message:', message.type(), message.args(), message.body())


async def handleCommand(channel: Channel, command: str, args: list[str]):
    def onHelp():
        print('''
        CLOSE -- closes the connection
        TIME -- returns the current server time
        ECHO -- returns the data transmitted by the client after the command
        DOWNLOAD -- download file
        UPLOAD -- upload file
        ''')


    async def onClose(channel: Channel):
        await channel.send(CloseMessage())
        await channel.next()

    async def onTime(channel: Channel):
        await channel.send(TimeRequestMessage())
        message = await channel.next()
        print(time.asctime(time.localtime(float(message.body().decode()))))


    async def onEcho(channel: Channel):
        await channel.send(EchoMessage(text=' '.join(args))) 
        message = await channel.next()
        print(message.body().decode()) 


    async def onDownload(channel: Channel):    
        if len(args) < 1:
            print('Invalid filename')
            return
        filename = args[0]
        if not os.path.exists(filename):
            await channel.send(DownloadMessage(filename=filename))
            print('full')
        else:    
            await channel.send(DownloadMessage(filename=filename, offset=os.path.getsize(filename))) 
        message = await channel.next()
        if message.type() == MessageType.ECHO:
            print(message.body().decode()) 
            return
        rawFilename, rawOffset, rawTotalLength = message.args()
        filename, offset, totalLength = rawFilename[:-1], int(rawOffset), int(rawTotalLength)
        data = message.body()
        with open(filename, 'a'):
            pass
        with open(filename, 'rb+') as f:
            f.truncate(offset + len(data))
            f.seek(offset)
            f.write(data)    


    async def onUpload(channel: Channel):
        if len(args) < 1:
            print('Invalid filename')
            return
        filename = args[0]
        if not os.path.exists(filename):
            print(f'Not found {filename}')
            return
        with open(filename, 'rb') as f:
            length = os.path.getsize(filename)
            await channel.send(UploadMessage(
                filename=filename,
                offset=0,
                totalLength=length,
                data=f.read()
            ))
        message = await channel.next()
        print(message.body().decode()) 
              


    match command:
        case 'HELP': onHelp()
        case 'CLOSE': await onClose(channel)
        case 'TIME': await onTime(channel)
        case 'ECHO': await onEcho(channel)
        case 'DOWNLOAD': await onDownload(channel)
        case 'UPLOAD': await onUpload(channel)
        case _: print('Unknown choice')  


async def main():
    connection = TcpSocket('127.0.0.1', 8080).connect() 
    channel = Channel(connection)
    while True:
        rawCommand = input('~> ')
        if rawCommand == '':
            continue
        command, *args = rawCommand.split()
        await handleCommand(channel, command.upper(), args)


if __name__ == "__main__":
    try:
        asyncio.new_event_loop().run_until_complete(main())
    except ConnectionClosed:
        print('Connection closed')
