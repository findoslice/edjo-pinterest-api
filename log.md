# Project Log

## Research

### 16/01/19

- Started looking into how pinterest generates IDs as website links appear to be incremental, in the end this turned out to be pointless as from research pinterest uses separate IDs from the website links which are randomly generated
- found basic pinterest api and a python client library
- As this may be slow for processing images I decided to use falcon to try and shave off latency
- after some research I decided to use scikit-image for image parsing