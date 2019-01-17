from skimage.io import imread

def read_image(file_name):
    image_np = imread(file_name)
    image = [hexify(list(row)) for row in image_np]
    return image

def get_colours(image):
    pixels = read_image(image)
    pixels = [code for row in pixels for code in row]
    colours = list(set(pixels))
    return colours

def hexify(row):
    for i in range(len(row)):
        row[i] = rgbtohex(row[i])
    return row

def rgbtohex(pixel):
    hexcode = "#"
    for num in pixel:
        hexcode += str(hex(num))[2:].upper()
    return hexcode
