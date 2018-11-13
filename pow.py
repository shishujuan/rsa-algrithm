#!/usr/bin/env python
# -*- coding: utf-8 -*-

from time import clock
import time


def pow_simple(a, e, n):
    """
    朴素法模幂运算：a^e % n
    """
    ret = 1
    for _ in xrange(e):
        ret *= a
    return ret % n


def pow_simple_optimized(a, e, n):
    """
    朴素法模幂运算优化：基于 a ≡ c(mod n) => ab ≡ bc(mod n)，即 ab mod n = (b*(a mod n)) mod m
    """
    ret = 1
    c = a % n
    for _ in xrange(e):
        ret = (ret * c) % n
    return ret


def pow_binary(a, e, n):
    """
    right-to-left binary method:基于位运算模幂运算优化。
    """
    number = 1
    base = a
    while e:
        if e & 1:
            number = number * base % n
        e >>= 1
        base = base * base % n
    return number


if __name__ == '__main__':
    a, e, n = 5, 102400, 13284 
    s = clock()
    print pow_simple(a, e, n)
    print clock() - s 

    s = clock()
    print pow_simple_optimized(a, e, n)
    print clock() - s 

    s = clock()
    print pow_binary(a, e, n)
    print clock() - s 
