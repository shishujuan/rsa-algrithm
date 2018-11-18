#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random

gcd = lambda a, b: (gcd(b, a % b) if a % b else b)

def factor(N, e, d):
    k = d*e - 1
    tries = 100
    while tries > 0:
        tries -= 1
        g = random.randint(1, N)
        t = k
        while t % 2 == 0:
            t = t / 2;
            x = pow(g, t, N)
            y = gcd(x-1, N)
            if x > 1 and y > 1:
                p, q = y, N / y
                return hex(p), hex(q)
    return None


if __name__ == '__main__':
    e = 65537
    N = 0xd66c9d31aa9e9acf247c1d3319bb4d0acaa49fdf0fa8625ccc129ec90d64bd151cb3e12346f22c3b78246eccb819d85316de25c4b795cc80d71128c8fdc64ed5L
    d = 0xc3357ea688be7c11b915853fd05d44765ea62125e20b5a0141887226779b0ec74e204e8d87eeab883ae6099fec44502a5fc3eb61fbb612d9aad29f599c595c01L
    print factor(N, e, d)
