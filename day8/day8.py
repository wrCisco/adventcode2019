#!/usr/bin/env python
# -*- coding: utf-8 -*-


def run():
    with open('input.txt', encoding='utf-8') as fh:
        raw_data = [int(pixel) for pixel in fh.read()]
    size = [25, 6]
    layers = []
    for i, pixel in enumerate(raw_data):
        if i % (25 * 6) == 0:
            layers.append([])
        layers[-1].append(pixel)
    index = layers.index(min(layers, key=lambda layer: layer.count(0)))
    print(layers[index].count(1) * layers[index].count(2))

    image = [2] * (25 * 6)
    transparents = set(x for x in range(25*6))
    not_transp_anymore = set()
    for layer in layers:
        for transp_pixel in transparents:
            if image[transp_pixel] != layer[transp_pixel]:
                image[transp_pixel] = layer[transp_pixel]
                not_transp_anymore.add(transp_pixel)
        transparents -= not_transp_anymore
        not_transp_anymore.clear()
        if not transparents:
            break
    image = ''.join(str(p) for p in image).replace('0', ' ')
    for row in range(6):
        image = image[:25*row+row] + '\n' + image[25*row+row:]
    print(image.strip('\n'))

if __name__ == '__main__':
    run()
