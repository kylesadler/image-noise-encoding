import os
import random
from PIL import Image
from datetime import datetime, timezone

def to_image(data):
    height = len(data)
    width = len(data[0])
    # print("h,w", height, width)
    image = Image.new("RGB", (width, height), (0, 0, 0))
    pixels = image.load()

    for y in range(height):
        for x in range(width):
            pixels[x, y] = data[y][x]

    return image

def get_random_rgb():
    return (
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255)
        )

def get_random_rgb_image(height, width):
    return [
        [ get_random_rgb() for i in range(width) ] for j in range(height)
    ]

def constrain(x, a, b):
    return min(max(x, a), b)


def makedir(path):
    if not os.path.exists(path):
        os.mkdir(path)


def resize(image, scale):
    width, height = image.size
    size = (width*scale, height*scale)
    return image.resize(size, resample=Image.BOX)


def add_white_boarder(image, thickness=1):
    WHITE = (255, 255, 255)
    white_row = [WHITE]*(len(image[0]) + thickness*2)
    output = []

    output.extend([white_row]*thickness)
    for row in image:
        output.append([WHITE]*thickness + row + [WHITE]*thickness)
    output.extend([white_row]*thickness)
    
    return output

# to convert to mp4
# ffmpeg -i %d.png -vcodec mpeg4 output.mp4

 
def load_image_pixels(path):
    im = Image.open(path)
    return to_pixels(im)
 
def to_pixels(image):
    pixels = list(image.getdata())
    width, height = image.size
    return [pixels[i * width:(i + 1) * width] for i in range(height)]

def generate_solid_image(color, height, width):
    return [
        [ color for i in range(width) ] for j in range(height)
    ]

def get_current_time_ms():
    """ return current time in UTC in ms """
    return round(datetime.now(timezone.utc).timestamp() * 1000)
