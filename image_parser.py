from PIL import Image
from requests import get
from io import BytesIO
from time import time

def read_image(file_name):
    image = Image.open(file_name)
    return image

def read_web_image(url):
    response = get(url)
    img = Image.open(BytesIO(response.content))
    return img

def get_colours(image, weborfile = read_web_image):
    # allows function to be used for either remote or local images
    image = weborfile(image)
    # returns typle (width, size)
    size = image.size
    # returns all present colours and their frequency,if there are more colours than maxcolors (default 256) this returns None
    # this is avoided by setting maxcolors to the number of pixels
    pixels = image.getcolors(maxcolors=(size[0]*size[1]))
    pixels = hexify(pixels)
    return pixels

def hexify(row):
    for i in range(len(row)):
        row[i] = (row[i][0], rgbtohex(row[i][1]))
    return row

def rgbtohex(pixel):
    hexcode = "#"
    for num in pixel:
        hexcode += str(hex(num))[2:].upper()
    return hexcode

time1 = time()
get_colours("https://tardis.ed.ac.uk/~findoslice/profile.jpg")
print(time() - time1)