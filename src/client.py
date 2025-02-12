from common.Channel import Channel, Message
from common.Router import Router
from common.TcpConnection import ConnectionClosed
from common.TcpSocket import TcpSocket
import asyncio
import time, os
import readline
from rich.progress import Progress

from common.messages import CloseMessage, EchoMessage, MessageType, TimeRequestMessage, DownloadMessage, UploadMessage

commands = ['HELP', 'CLOSE', 'TIME', 'ECHO', 'DOWNLOAD', 'UPLOAD']

def completer(text, state):
    options = [cmd for cmd in commands if cmd.startswith(text.upper())]
    return options[state] if state < len(options) else None

readline.parse_and_bind("tab: complete")
readline.set_completer(completer)


async def download(channel: Channel, filename: str, offset: int, totalLength: int):
    with open(filename, 'a'):
        pass
    with Progress() as progress:
        downloadTask = progress.add_task("[blue]Downloading...", total=totalLength)
        while totalLength - offset > 0:
            await channel.send(DownloadMessage(filename=filename, offset=offset, length=min(1024, totalLength - offset)))
            message = await channel.next()
            data = message.body()
            with open(filename, 'rb+') as f:
                f.truncate(offset + len(data))
                f.seek(offset)
                f.write(data) 
            offset += len(data)
            progress.update(downloadTask, completed=offset)


async def upload(channel: Channel, filename: str, offset: int = 0):
    with open(filename, 'rb') as f:
        length = os.path.getsize(filename)
        with Progress() as progress:
            uploadTask = progress.add_task("[green]Uploading...", total=length)    
            while length - offset > 0:
                data = f.read(min(1024, length - offset))
                await channel.send(UploadMessage(
                    filename=filename,
                    offset=offset,
                    totalLength=length,
                    data=data
                ))
                offset += len(data) 
                await channel.next()
                progress.update(uploadTask, completed=offset)


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
            await channel.send(DownloadMessage(filename=filename, length=1))
        elif input('''
            Such a file already exists
            Continue downloading(y/n)?
            ''').upper() == 'Y': 
            await channel.send(DownloadMessage(filename=filename, offset=os.path.getsize(filename), length=1))
        else: return    
        message = await channel.next()
        if message.type() == MessageType.ECHO:
            print(message.body().decode()) 
            return
        rawFilename, rawOffset, rawTotalLength = message.args()
        start_time = time.time()
        await download(channel=channel, filename=rawFilename[:-1], offset=int(rawOffset), totalLength=int(rawTotalLength))
        end_time = time.time()
        print(int(os.path.getsize(filename)/(end_time-start_time)), 'B/s')


    async def onUpload(channel: Channel):
        if len(args) < 1:
            print('Invalid filename')
            return
        filename = args[0]
        if not os.path.exists(filename):
            print(f'Not found {filename}')
            return
        start_time = time.time()
        await upload(channel=channel, filename=filename)
        end_time = time.time()
        print(int(os.path.getsize(filename)/(end_time-start_time)), 'B/s')
        
              
    match command:
        case 'HELP': onHelp()
        case 'CLOSE': await onClose(channel)
        case 'TIME': await onTime(channel)
        case 'ECHO': await onEcho(channel)
        case 'DOWNLOAD': await onDownload(channel)
        case 'UPLOAD': await onUpload(channel)
        case _: print('Unknown choice')  


async def main():
    connection = TcpSocket('172.17.124.213', 8080).connect() 
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
    except BrokenPipeError:
        print('Server DOWN')   
    except ConnectionRefusedError:
        print('Serer unavalible')    
