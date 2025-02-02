from src.common.Socket import Socket


class TcpSocket(Socket):
    def __init__(self, ip, port) -> None:
        super().__init__()
        self.ip = ip
        self.port = port

    def connect(self):
        return super().connect()

    def listen(self, handler):
        return super().listen(handler)
