import argparse
import concurrent.futures
import contextlib
import datetime
import socket
import hashlib

import pydaze

conf = Exception()
conf.life_expire = 120


class GravityDazeConn:
    def __init__(self, socket, k):
        self.socket = socket
        self.wc = pydaze.rc4.Cipher(k)
        self.rc = pydaze.rc4.Cipher(k)
        self.close = self.socket.close
        self.shutdown = self.socket.shutdown

    def send(self, data):
        b = [0 for _ in data]
        self.wc.crypto(data, b)
        self.socket.sendall(bytes(b))

    def recv(self, size):
        data = self.socket.recv(size)
        b = [0 for _ in data]
        self.rc.crypto(data, b)
        return bytes(b)

    def recvall(self, size):
        data = self.socket.recv(size, socket.MSG_WAITALL)
        b = [0 for _ in data]
        self.rc.crypto(data, b)
        return bytes(b)


def copy(src, dst):
    while True:
        try:
            data = src.recv(32 * 1024)
        except Exception:
            break
        if not data:
            break
        try:
            dst.send(data)
        except Exception:
            break
    with contextlib.suppress(Exception):
        src.shutdown(socket.SHUT_RDWR)
    src.close()
    with contextlib.suppress(Exception):
        dst.shutdown(socket.SHUT_RDWR)
    dst.close()


class Server:
    def __init__(self, listen_host: str, listen_port: int, cipher: bytes):
        self.listen_host = listen_host
        self.listen_port = listen_port
        self.cipher = cipher
        self.executor = concurrent.futures.ThreadPoolExecutor(128)

    def serve1(self, sock):
        data = sock.recv(128, socket.MSG_WAITALL)
        conn = GravityDazeConn(sock, data + self.cipher)
        data = conn.recvall(2)
        if data[0] != 0xFF or data[1] != 0xFF:
            raise Exception(f'malformed request: {list(data[:2])}')
        data = conn.recvall(8)
        d = int.from_bytes(data, 'big')
        if abs(datetime.datetime.now().timestamp() - d) > conf.life_expire:
            d_str = datetime.datetime.fromtimestamp(d).strftime('%Y-%m-%d %H:%M:%S')
            raise Exception(f'expired: {d_str}')
        data = conn.recvall(1)
        if data[0] != 0x01:
            raise Exception('udp')
        data = conn.recvall(1)
        data = conn.recvall(int(data[0]))
        dest = data.decode()
        seps = dest.split(':')
        host = seps[0]
        port = int(seps[1])
        with socket.socket() as dest:
            dest.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            pydaze.log.println(f' dial network=tcp address={host}:{port}')
            try:
                dest.connect((host, port))
            except Exception:
                dest.close()
                raise
            self.executor.submit(copy, dest, conn)
            copy(conn, dest)

    def serve0(self, conn):
        try:
            self.serve1(conn)
        except Exception as e:
            pydaze.log.println(f' error {e}')
        conn.shutdown(socket.SHUT_RDWR)
        conn.close()

    def run(self):
        with socket.socket() as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((self.listen_host, self.listen_port))
            pydaze.log.println(f'listen and serve on {self.listen_host}:{self.listen_port}')
            sock.listen()
            while True:
                conn, addr = sock.accept()
                pydaze.log.println(f'accept remote={addr[0]}:{addr[1]}')
                self.executor.submit(self.serve0, conn)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--listen', default='0.0.0.0:1081', help='listen address')
    parser.add_argument('-k', '--cipher', default='daze', help='cipher, for encryption')
    args = parser.parse_args()
    seps = args.listen.split(':')
    listen_host = seps[0]
    listen_port = int(seps[1])
    cipher = hashlib.md5(args.cipher.encode()).digest()
    server = Server(listen_host, listen_port, cipher)
    server.run()


if __name__ == '__main__':
    main()
