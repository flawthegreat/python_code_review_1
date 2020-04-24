import string
from collections import defaultdict
from enum import Enum


class Cipher(Enum):
    caesar = 'caesar'
    vigenere = 'vigenere'


class Coder:
    class Mode(Enum):
        encode = 'encode'
        decode = 'decode'

    __characters = (
        'абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ' +
        string.printable
    )
    __character_count = len(__characters)
    __character_indices = {char: i for i, char in enumerate(__characters)}

    def __init__(self, cipher):
        if cipher == Cipher.caesar:
            self.encode = self.__encode_caesar
            self.decode = self.__decode_caesar
        elif cipher == Cipher.vigenere:
            self.encode = self.__encode_vigenere
            self.decode = self.__decode_vigenere
        else:
            raise NotImplementedError(f'Unsupported cipher: {cipher}')

    def __encode_caesar(self, data, key):
        return ''.join(type(self).__shift_char(char, key) for char in data)

    def __decode_caesar(self, data, key):
        return self.__encode_caesar(data, -key)

    def __encode_vigenere(self, data, key, sign=1):
        return ''.join(type(self).__shift_char(
            char,
            sign * type(self).__character_indices[key[i % len(key)]]
        ) for i, char in enumerate(data))

    def __decode_vigenere(self, data, key):
        return self.__encode_vigenere(data, key, sign=-1)

    @classmethod
    def get_characters(cls):
        return cls.__characters

    @classmethod
    def get_character_count(cls):
        return cls.__character_count

    @classmethod
    def __shift_char(cls, char, delta):
        return cls.__characters[
            (cls.__character_indices[char] + delta) % cls.__character_count
        ]
