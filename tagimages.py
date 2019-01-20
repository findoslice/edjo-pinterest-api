from image_parser import get_colours
from redis import Redis
from time import time

db = Redis()

db2 = Redis(db=1)

while (db.scard('untaggedimages') != 0):
    try:
        image = db.spop('untaggedimages')
        time1 = time()
        colours = get_colours(image.decode('utf-8'))
        db2.sadd(image.decode('utf-8'), *set([colour[1] for colour in colours]))
        print(time() - time1, db2.size())
    except:
        continue
