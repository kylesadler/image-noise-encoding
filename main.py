import os
import sys
from PIL import Image
from math import ceil, log2
from utils import *


def int_to_bits(number, length=8):
    """ Given number, returns list of bits with 1s place at end
        Defauls to returning number as a byte
    """
    output = [None] * length
    power = 0
    for i in range(length):
        output[length - i - 1] = number % 2
        number //= 2
        power += 1

    return output

def bits_to_int(bits):
    """ 1s place at end """
    output = 0
    place_value = 1
    
    for bit in bits[::-1]:
        output += place_value * bit
        place_value *= 2
    
    return output


def chunk_data(bits, chunk_size=3):
    """ returns elements in chunks, padding with zeros if needed """
    index = 0
    length = len(bits)
    while index < length:
        end_index = min(index + chunk_size, length)
        yield bits[index : end_index] + [0] * (index - end_index + chunk_size)
        index += chunk_size

def get_num_length_bits(message_size):
    """ want the max number of bytes b that can be sent in message with

        b + ceil(log2(b)) <= message_size
    """

    last_b = message_size

    for b in range(1, message_size):
        if b + ceil(log2(b)) > message_size:
            return ceil(log2(last_b))
        last_b = b

    raise Exception


def encode_image(_bytes, original_image_path, encoded_image_path):
    pixels = load_image_pixels(original_image_path)
    height = len(pixels)
    width = len(pixels[0])

    bits = [bit for byte in _bytes for bit in int_to_bits(byte)]

    # checks that message isn't too long
    encoded_bits = encode_message(bits, width*height*3)

    three_at_a_time = chunk_data(encoded_bits, chunk_size=3)

    for i, three_bits in enumerate(three_at_a_time):
        x = i % width
        y = i // width
        pixels[y][x] = encode_pixel(pixels[y][x], three_bits)

    encoded_image = to_image(pixels)
    encoded_image.save(encoded_image_path)

def decode_image(original_image_path, encoded_image_path):
    encoded_pixels = load_image_pixels(encoded_image_path)
    orig_pixels = load_image_pixels(original_image_path)

    height = len(encoded_pixels)
    width = len(encoded_pixels[0])

    bits = []
    for y in range(height):
        for x in range(width):
            bits.extend(decode_pixel(encoded_pixels[y][x], orig_pixels[y][x]))

    message_bits = decode_message(bits, width*height*3)
    message_bytes = []

    assert len(message_bits) % 8 == 0, "message was corrupted"

    for i in range(len(message_bits) // 8):
        index = i*8
        message_bytes.append(bits_to_int(message_bits[index:index+8]))

    return bytes(message_bytes)

def encode_message(bits, message_size):
    """ package bits of data into a message of given size
        format: [data length] [data bits]
    """

    assert message_size != 0, "message size is zero"

    num_length_bits = get_num_length_bits(message_size)

    assert num_length_bits + len(bits) <= message_size, "encoded message is too long"

    length_bits = int_to_bits(len(bits), length=num_length_bits)

    return length_bits + bits

def decode_message(bits, message_size):
    """ given encoded bits, returns the original data """
    num_length_bits = get_num_length_bits(message_size)
    data_length = bits_to_int(bits[:num_length_bits])
    return bits[num_length_bits : num_length_bits + data_length]

def encode_pixel(pixel, three_bits):
    return (
        max(pixel[0] - 1, 0) + three_bits[0],
        max(pixel[1] - 1, 0) + three_bits[1],
        max(pixel[2] - 1, 0) + three_bits[2],
    )

def decode_pixel(encoded_pixel, original_pixel):
    return [
        encoded_pixel[0] - max(original_pixel[0] - 1, 0),
        encoded_pixel[1] - max(original_pixel[1] - 1, 0),
        encoded_pixel[2] - max(original_pixel[2] - 1, 0),
    ]


def compress_message(_bytes): # TODO
    pass

def decompress_message(_bytes): # TODO
    pass

def print_usage():
    print("Usage:")
    print("   Encode a message: python main.py encode [message] [input image] [output image]")
    print("   Decode a message: python main.py decode [original image] [encoded image]")
    print("")
    print("Demo:")
    print("   python main.py encode \"Hi, I'm kyle\!\" landscape.jpeg encoded.png")
    print("   python main.py decode landscape.jpeg encoded.png")
    print("")


def encode_command(args):

    if len(args) != 3:
        print_usage()
        sys.exit()

    input_message = args[0]
    image_path = args[1]
    encoded_path = args[2]
    
    print(f"Input message: {input_message}")
    print(f"Encoding message into {image_path} ...")

    encode_image(input_message.encode("UTF-8"), image_path, encoded_path)
    
    print(f"Successfully created {encoded_path}")


def decode_command(args):
    if len(args) != 2:
        print_usage()
        sys.exit()

    image_path = args[0]
    encoded_path = args[1]

    print(f"Decoding message in {encoded_path}")

    output_message = decode_image(image_path, encoded_path).decode("UTF-8")

    print(f"Decoded message: {output_message}")

def main(args):
    if len(args) == 0:
        print_usage()
        sys.exit()

    if args[0] == "encode":
        encode_command(args[1:])
    elif args[0] == "decode":
        decode_command(args[1:])
    else:
        print_usage()
        sys.exit()

if __name__ == "__main__":
    main(sys.argv[1:])
    