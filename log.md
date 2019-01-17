# Project Log

## Research

### 16/01/19

- Started looking into how pinterest generates IDs as website links appear to be incremental, in the end this turned out to be pointless as from research pinterest uses separate IDs from the website links which are randomly generated
- found basic pinterest api and a python client library
- As this may be slow for processing images I decided to use falcon to try and shave off latency
- after some research I decided to use scikit-image for image parsing

### 17/01/19

- Decided to rewrite colour processing to read the image from directly from the web, to save time and resources as saving/deleting files is no longer necessary, nor is reading from a file
- Discovered pillow is a better choice as it is possible with this, as well as having an inbuilt getcolors method

## Work

### 16/01/19

- implemented colour detection for locally stored files using scikit-image

### 17/01/19

- Rewrote image_parser.py to be able to read from the web or locally and to use pillow