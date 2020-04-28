#!/usr/bin/python3
import argparse
import string
import json
import sys
from collections import defaultdict
from coder import Cipher, Coder


def read_input_data(input_file):
    if input_file is None:
        data = sys.stdin.read()
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
    arguments.mode = Coder.Mode(arguments.mode)
    if arguments.cipher == Cipher.caesar:
        arguments.key = int(arguments.key)

    coder = Coder(arguments.cipher)

    if arguments.mode == Coder.Mode.encode:
        result = coder.encode(data, arguments.key)
    elif arguments.mode == Coder.Mode.decode:
        result = coder.decode(data, arguments.key)

    write_output_data(arguments.output_file, result)


def calculate_letter_frequencies(text):
    frequencies = defaultdict(float)
    text_length = len(text)

    for letter in text:
        frequencies[letter] += 1

    for letter in set(text):
        frequencies[letter] /= text_length

    return frequencies


def train(arguments):
    with open(f'{arguments.model_file}', 'w') as model:
        text = read_input_data(arguments.text_file)
        json.dump(calculate_letter_frequencies(text), model)


def hack_caesar(data, frequencies):
    coder = Coder(Cipher.caesar)

    min_error = None
    data_frequencies = calculate_letter_frequencies(data)

    def calculate_error(offset, difference_power=1.6):
        error = 0
        for char in Coder.get_characters():
            error += abs(
                frequencies[char] -
                data_frequencies[Coder.shift_char(char, offset)]
            ) ** difference_power

        return error

    for offset in range(Coder.get_character_count()):
        decoded_data = coder.decode(data, offset)
        data_error = calculate_error(offset)

        if min_error is None or data_error < min_error:
            result = decoded_data
            min_error = data_error

    return result


def hack_vigenere_with_key_length(data, key_length):
    columns = [''.join(
        data[key_length * i + j]
        for i in range(len(data) // key_length)
    ) for j in range(key_length)]
    col_freq = [calculate_letter_frequencies(column) for column in columns]
    data = list(data)

    for i, column in enumerate(columns):
        if i == 0:
            continue

        true_offset = 0
        max_mi = 0

        for offset in range(Coder.get_character_count()):
            mi = sum(
                col_freq[0][char] *
                col_freq[i][Coder.shift_char(char, offset)]
                for char in Coder.get_characters()
            )

            if mi > max_mi:
                max_mi = mi
                true_offset = offset

        for i in range(i, len(data), key_length):
            data[i] = Coder.shift_char(data[i], -true_offset)

    return ''.join(data)


def hack_vigenere(data, frequencies):
    def ic(frequencies):
        return sum(f ** 2 for f in frequencies.values())

    main_ic = ic(frequencies)
    max_ic = 0
    key_info = []

    for key_length in range(1, len(data) // 2):
        columns = [''.join(
            data[key_length * i + j]
            for i in range(len(data) // key_length)
        ) for j in range(key_length)]

        ics = [ic(calculate_letter_frequencies(column)) for column in columns]
        average_ic = sum(ics) / len(ics)

        if average_ic > max_ic:
            max_ic = average_ic
            key_info.append([key_length, average_ic])

    key_lengths = [l for l, ic in key_info if abs(ic - main_ic) < 0.05]
    if len(key_lengths) == 0:
        raise RuntimeError('Cannot hack cipher')

    min_ic_offset = None
    for key_length in key_lengths:
        decoded = hack_caesar(
            hack_vigenere_with_key_length(data, key_length),
            frequencies
        )
        ic_offset = abs(ic(calculate_letter_frequencies(decoded)) - main_ic)

        if min_ic_offset is None or ic_offset < min_ic_offset:
            min_ic_offset = ic_offset
            result = decoded

    return result


def hack(arguments):
    data = read_input_data(arguments.input_file)
    arguments.cipher = Cipher(arguments.cipher)
    with open(f'{arguments.model_file}', 'r') as model:
        frequencies = defaultdict(float, json.load(model))

    coder = Coder(arguments.cipher)

    if arguments.cipher == Cipher.caesar:
        result = hack_caesar(data, frequencies)
    elif arguments.cipher == Cipher.vigenere:
        result = hack_vigenere(data, frequencies)

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
        choices=['caesar', 'vigenere', 'otp'],
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
        choices=['caesar', 'vigenere', 'otp'],
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
        '--cipher',
        choices=['caesar', 'vigenere'],
        help='тип шифра',
        required=True
    )
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
