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

    num_valid = num_valid_rgb(pixels, bits)

    # checks that message isn't too long for the image
    encoded_bits = encode_message(bits, num_valid)

    one_at_a_time = chunk_data(encoded_bits, chunk_size=1)

    # TODO use a gpu for this
    # put encoded_bits into image
    for y in range(len(pixels)):
        for x in range(len(pixels[0])):
            color = list(pixels[y][x]) # PIL colors must be tuples, so we type cast and cast back
            for c in range(3):
                if is_valid(color[c]):
                    bit = next(one_at_a_time, None)
                    if bit is not None:
                        color[c] = encode_rgb(color[c], bit)
            pixels[y][x] = tuple(color)
    
    encoded_image = to_image(pixels)
    encoded_image.save(encoded_image_path)

def generate_valid_rgb_locations(pixels, bits):
    """ 
        bits is a generator
    """
    for y in range(len(pixels)):
        for x in range(len(pixels[0])):
            for c in range(3):
                if is_valid(pixels[y][x][c]):
                    yield y, x, c

def decode_image(original_image_path, encoded_image_path):
    encoded_pixels = load_image_pixels(encoded_image_path)
    orig_pixels = load_image_pixels(original_image_path)

    height = len(encoded_pixels)
    width = len(encoded_pixels[0])

    bits = []
    for y, x, c in generate_valid_rgb_locations(encoded_pixels):
        decoded_bit = decode_rgb(encoded_pixels[y][x][c], orig_pixels[y][x][c])
        bits.append(decoded_bit)

    num_valid = num_valid_rgb(pixels, bits)
    message_bits = decode_message(bits, num_valid)
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

def encode_rgb(rgb, bit):
    """ rgb is valid (greater than 0 and less than 254) """
    return max(rgb - 1, 0) + bit

def decode_rgb(encoded, original):
    """ rgb is valid (greater than 0 and less than 254) """
    return encoded - max(original - 1, 0)


def compress_message(_bytes): # TODO
    pass

def decompress_message(_bytes): # TODO
    pass

def print_usage():
    print("Usage:")
    print("   Encode a message: python main.py encode [message] [input image] [output image]")
    print("   Encode a message: python main.py encode_file [file] [input image] [output image]")
    print("   Decode a message: python main.py decode [original image] [encoded image]")
    print("")
    print("Demo:")
    print("   python main.py encode \"Hi, I'm kyle\!\" landscape.jpeg encoded.png")
    print("   python main.py encode_file bee_movie.txt landscape.jpeg encoded.png")
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

def encode_file_command(args):

    if len(args) != 3:
        print_usage()
        sys.exit()

    input_file = args[0]
    image_path = args[1]
    encoded_path = args[2]

    with open(input_file, "r") as f:
        input_message = f.read()
    
    print(f"Input file: {input_file}")
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
    if args[0] == "encode_file":
        encode_file_command(args[1:])
    elif args[0] == "decode":
        decode_command(args[1:])
    else:
        print_usage()
        sys.exit()

def num_valid_rgb(pixels, bits):
    """ returns number of rgb values in pixels that are suitable for image encoding """
    counter = 0
    for row in pixels:
        for pixel in row:
            for rgb in pixel:
                if not is_valid(rgb, bit):
                    counter += 1
    return len(pixels) * len(pixels[0]) * 3 - counter

def is_valid(rgb, bit):
    """ checks if the sum of rgb and bit are sufficiently ambiguous.
        Avoids "edges" of range, because these can only be
        generated with one combination of rgb and bit
    """
    return 0 < rgb + bit <= 255

if __name__ == "__main__":
    main(sys.argv[1:])
    