#!/usr/bin/python3
import argparse
import string
import json
from collections import defaultdict
from coder import Cipher, Coder


def read_input_data(input_file):
    if input_file is None:
        data = input()
    else:
        with open(input_file, 'r') as file:
            data = file.read()

    return data


def write_output_data(output_file, data):
    if output_file is None:
        print(data)
    else:
        with open(output_file, 'w') as file:
            file.write(data)


def code(arguments):
    data = read_input_data(arguments.input_file)
    arguments.cipher = Cipher(arguments.cipher)
    if arguments.cipher == Cipher.caesar:
        arguments.key = int(arguments.key)

    coder = Coder(arguments.cipher)

    if arguments.mode == 'encode':
        result = coder.encode(data, arguments.key)
    elif arguments.mode == 'decode':
        result = coder.decode(data, arguments.key)

    write_output_data(arguments.output_file, result)


def calculate_letter_frequencies(text):
    letters = ''.join(set(text))
    frequencies = defaultdict(float)

    for letter in text:
        frequencies[letter] += 1

    for letter in letters:
        frequencies[letter] /= len(text)

    return frequencies


def train(arguments):
    with open(f'{arguments.model_file}.json', 'w') as model:
        text = read_input_data(arguments.text_file)
        json.dump(calculate_letter_frequencies(text), model)


def hack(arguments):
    data = read_input_data(arguments.input_file)
    with open(f'{arguments.model_file}.json', 'r') as model:
        frequencies = defaultdict(float, json.load(model))

    result = ''
    min_error = 1

    coder = Coder(Cipher.caesar)

    def calculate_error(data_frequencies):
        error = 0
        for letter in Coder.get_characters():
            error += abs(frequencies[letter] - data_frequencies[letter]) ** 1.6

        return error

    for key in range(len(Coder.get_characters())):
        decoded_data = coder.decode(data, key)

        data_frequencies = calculate_letter_frequencies(decoded_data)
        data_error = calculate_error(data_frequencies)

        if data_error < min_error:
            result = decoded_data
            min_error = data_error

    write_output_data(arguments.output_file, result)


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


if __name__ == '__main__':
    main()
