class Cipher:
    caesar = 'caesar'
    vigenere = 'vigenere'


class Coder:
    def __init__(self, cipher):
        if cipher == Cipher.caesar:
            self.encode = self.encode_caesar
            self.decode = self.decode_caesar
        elif cipher == Cipher.vigenere:
            self.encode = self.encode_vigenere
            self.decode = self.decode_vigenere
        else:
            raise ValueError()

    def encode_caesar(self, data, key):
        return ''.join([Coder.shift_char(char, key) for char in data])

    def decode_caesar(self, data, key):
        return self.encode_caesar(data, -key)

    def encode_vigenere(self, data, key, sign=1):
        return ''.join([
            Coder.shift_char(char, sign * (ord(key[i % len(key)]) - ord('a')))
            for i, char in enumerate(data)
        ])

    def decode_vigenere(self, data, key):
        return self.encode_vigenere(data, key, sign=-1)

    @staticmethod
    def shift_char(char, delta):
        if not char.isalpha():
            return char

        offset = ord('a') if char.islower() else ord('A')

        return chr(offset + (ord(char) - offset + delta) % 26)
