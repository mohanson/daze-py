import typing


class Cipher:
    def __init__(self, cipher: bytearray):
        self.s = list(range(256))
        self.i = 0
        self.j = 0
        self.cipher = cipher

        k = len(cipher)
        if k < 1 or k > 256:
            raise Exception('crypto/rc4: invalid key size ' + str(k))

        j = 0
        for i in range(256):
            j = (j + self.s[i] + cipher[i % k]) % 256
            self.s[i], self.s[j] = self.s[j], self.s[i]

    def __str__(self):
        return f'rc4.Cipher(cipher={self.cipher})'

    def crypto(self, src: bytearray, dst: bytearray):
        i, j = self.i, self.j
        for k, v in enumerate(src):
            i = (i + 1) % 256
            j = (j + self.s[i]) % 256
            self.s[i], self.s[j] = self.s[j], self.s[i]
            dst[k] = v ^ self.s[(self.s[i] + self.s[j]) % 256] % 256
        self.i, self.j = i, j

    def stream(self, src: typing.BinaryIO, dst: typing.BinaryIO):
        c = 1024
        buf = bytearray(c)
        while True:
            ctx = src.read(c)
            if not ctx:
                break
            n = len(ctx)
            self.crypto(ctx, buf)
            dst.write(bytes(buf[:n]))
