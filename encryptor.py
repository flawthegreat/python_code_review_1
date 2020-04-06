#!/usr/bin/python3
import argparse
from coder import *
import string
from collections import defaultdict
import json


def code(arguments):
    if arguments.input_file is None:
        data = input()
    else:
        with open(arguments.input_file, 'r') as file:
            data = file.read()

    coder = Coder(arguments.cipher)
    if arguments.cipher == Cipher.caesar:
        arguments.key = int(arguments.key)

    if arguments.mode == 'encode':
        result = coder.encode(data, arguments.key)
    elif arguments.mode == 'decode':
        result = coder.decode(data, arguments.key)

    if arguments.output_file is None:
        print(result)
    else:
        with open(arguments.output_file, 'w') as file:
            file.write(result)


def calculate_letter_frequencies(text):
    text = ''.join([char for char in text.lower() if char.isalpha()])
    frequencies = defaultdict(float)

    for letter in text:
        frequencies[letter] += 1

    for letter in string.ascii_lowercase:
        frequencies[letter] /= len(text)

    return frequencies


def train(arguments):
    if arguments.text_file is None:
        text = input()
    else:
        with open(arguments.text_file, 'r') as file:
            text = file.read()

    with open(f'{arguments.model_file}.json', 'w') as model:
        json.dump(calculate_letter_frequencies(text), model)


def hack(arguments):
    with open(f'{arguments.model_file}.json', 'r') as model:
        frequencies = json.load(model)

    if arguments.input_file is None:
        data = input()
    else:
        with open(arguments.input_file, 'r') as file:
            data = file.read()

    result = ''
    min_error = 1

    coder = Coder(Cipher.caesar)

    def calculate_error(data_frequencies):
        error = 0
        for letter in string.ascii_lowercase:
            error += abs(frequencies[letter] - data_frequencies[letter]) ** 1.6

        return error

    for key in range(26):
        decoded_data = coder.decode(data, key)

        data_frequencies = calculate_letter_frequencies(decoded_data)
        data_error = calculate_error(data_frequencies)

        if data_error < min_error:
            result = decoded_data
            min_error = data_error

    if arguments.output_file is None:
        print(result)
    else:
        with open(arguments.output_file, 'w') as file:
            file.write(result)


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter
    )
    subparsers = parser.add_subparsers(
        title='modes',
        help='encode - зашифровывает текст\n'
             'decode - расшифровывает текст\n'
             'train  - анализирует текст и строит языковую модель\n'
             'hack   - пытается расшифровать текст без ключа'
    )

    encode_arg = subparsers.add_parser('encode')
    encode_arg.set_defaults(func=code, mode='encode')
    encode_arg.add_argument(
        '--cipher',
        choices=['caesar', 'vigenere'],
        help='тип шифра',
        required=True
    )
    encode_arg.add_argument(
        '--key',
        help='ключ',
        required=True
    )
    encode_arg.add_argument(
        '--input-file',
        help='путь ко входному файлу с текстом'
    )
    encode_arg.add_argument(
        '--output-file',
        help='путь к выходному файлу с зашифрованным текстом'
    )

    decode_arg = subparsers.add_parser('decode')
    decode_arg.set_defaults(func=code, mode='decode')
    decode_arg.add_argument(
        '--cipher',
        choices=['caesar', 'vigenere'],
        help='тип шифра',
        required=True
    )
    decode_arg.add_argument(
        '--key',
        help='ключ',
        required=True
    )
    decode_arg.add_argument(
        '--input-file',
        help='путь ко входному файлу с текстом'
    )
    decode_arg.add_argument(
        '--output-file',
        help='путь к выходному файлу с расшифрованным текстом'
    )

    train_arg = subparsers.add_parser('train')
    train_arg.set_defaults(func=train)
    train_arg.add_argument(
        '--model-file',
        help='путь к файлу, в который будет сохранена языковая модель',
        required=True
    )
    train_arg.add_argument(
        '--text-file',
        help='путь ко входному файлу с текстом'
    )

    hack_arg = subparsers.add_parser('hack')
    hack_arg.set_defaults(func=hack)
    hack_arg.add_argument(
        '--model-file',
        help='путь к файлу с языковой моделью',
        required=True
    )
    hack_arg.add_argument(
        '--input-file',
        help='путь ко входному файлу с текстом'
    )
    hack_arg.add_argument(
        '--output-file',
        help='путь к выходному файлу с расшифрованным текстом'
    )

    arguments = parser.parse_args()
    arguments.func(arguments)


if __name__ == "__main__":
    main()
