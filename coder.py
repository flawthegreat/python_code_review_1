import string
from enum import Enum


class Cipher(Enum):
    caesar = 'caesar'
    vigenere = 'vigenere'


class Coder:
    characters = (
        'абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ' +
        string.ascii_letters +
        string.digits +
        string.punctuation +
        ' \n'
    )

    def __init__(self, cipher):
        if cipher == Cipher.caesar:
            self.encode = self.encode_caesar
            self.decode = self.decode_caesar
        elif cipher == Cipher.vigenere:
            self.encode = self.encode_vigenere
            self.decode = self.decode_vigenere
        else:
            raise ValueError(f'Unknown cipher: {cipher}')

    def encode_caesar(self, data, key):
        Coder.check_data(data)

        return ''.join([Coder.shift_char(char, key) for char in data])

    def decode_caesar(self, data, key):
        return self.encode_caesar(data, -key)

    def encode_vigenere(self, data, key, sign=1):
        Coder.check_data(data)
        Coder.check_data(key)

        return ''.join([
            Coder.shift_char(
                char,
                sign * Coder.characters.find(key[i % len(key)])
            )
            for i, char in enumerate(data)
        ])

    def decode_vigenere(self, data, key):
        return self.encode_vigenere(data, key, sign=-1)

    @staticmethod
    def check_data(data):
        for char in data:
            if char not in Coder.characters:
                raise ValueError(f'Unsupported character "{char}" in "{data}"')

    @staticmethod
    def shift_char(char, delta):
        return Coder.characters[
            (Coder.characters.find(char) + delta) % len(Coder.characters)
        ]
