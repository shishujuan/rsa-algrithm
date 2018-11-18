#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
from time import clock


def randnumber(nbits):
    """
    返回一个nbits位的随机数
    """
    seq = '0123456789abcdef'
    numbers = []
    nlen = nbits/4 if nbits/4 >= 1 else 1

    for _ in xrange(nlen/16):
        numbers.append(''.join(random.sample(seq, 16)))

    if nlen % 16:
        numbers.append(''.join(random.sample(seq, nlen % 16)))

    number = ''.join(numbers)
    return long(number, 16)


def setbit(num, ibit, val):
    """
    设置数字 num 的第 ibit 位的值为0/1。
    """
    mask = 0x1L << ibit
    if val:
        num |= mask
    else:
        num &= ~mask
    return num


def generate_rsa_prime(nbits, e, ntests):
    """
    生成 nbits 位的质数 n, 且满足 gcd(n-1, e) = 1
    """
    maxodd = pow(2, nbits) - 1 # nbits位数字的最大奇数值
    maxloops = 10

    for _ in xrange(maxloops):
        p = randnumber(nbits)
        p = setbit(p, nbits-1, 1)
        p = setbit(p, nbits-2, 1)
        p = setbit(p, 0, 1)

        tries = 100*nbits # 从 p 开始探测的数字的个数

        for i in xrange(tries):
            p = p + 2*i
            if p > maxodd:
                break

            if miller_rabin(p, ntests):
                return p

    return -1


def miller_rabin(n, ntests):
    """
    Miller-Rabin 质数判定算法, n为待判定数，ntests为判定基数个数
    """
    def witness(a, n):
        t = 0
        u = n - 1
        while u % 2 == 0:
            u >>= 1
            t += 1
        assert(2**t * u == n - 1)

        x = pow(a, u, n)
        for i in xrange(1, t+1):
            next_x = pow(x, 2, n)
            if next_x == 1 and x not in [1, n-1]:
                return True
            x = next_x

        if x != 1:
            return True

        return False

    # 从 2 到 n-1 选取 ntests 个基数a#
    ntests = ntests if ntests <= n-2 else n-2
    a_list = []
    for _ in xrange(ntests):
        while True:
            a = random.randrange(2, n)
            if a not in a_list:
                a_list.append(a)
                break

    for a in a_list:
        if witness(a, n): # 只要一个测试不通过，则一定不是质数，测试下一个奇数
            return False

    return True


def ext_gcd(a, b):
    """
    扩展欧几里得算法
    """
    if b == 0:
        return 1, 0, a

    x, y, z = ext_gcd(b, a % b)
    x, y = y, x-(a/b)*y

    return x, y, z


def modinv(e, L):
    """
    计算 e 关于欧拉函数 L 的模逆元素 d
    """
    x, y, z = ext_gcd(e, L)

    if x < 0:
        k = abs(x) / L
        r = abs(x) % L
        if r != 0:
            k += 1
        x += (k * L)
        y -= (k * e)

    return x


def generate_rsa(nbit):
    """
    生成 nbit 位的rsa密钥
    """
    e = 65537
    ntests = 50

    np = nbit / 2
    nq = nbit - np
    p = generate_rsa_prime(np, e, ntests)
    q = generate_rsa_prime(nq, e, ntests)

    assert(p != q and p > 0 and q > 0)

    N = p * q
    L = (p-1) * (q-1)
    d = modinv(e, L)

    print 'p:', hex(p)
    print 'q:', hex(q)
    print 'N:', hex(N)
    print 'L:', hex(L)
    print 'd:', hex(d)
    print 'e:', e

    return (N, e, d)


def encrypt(m, N, e):
    """
    加密字符 c = m^e % N
    """
    return pow(m, e, N)


def decrypt(c, N, d):
    """
    解密字符 m = c^d % N
    """
    return pow(c, d, N)


def generate_rsa_crt(nbit):
    """
    生成 nbit 位的rsa密钥, 增加dP, dQ, qInv
    """
    e = 65537
    ntests = 50

    np = nbit / 2
    nq = nbit - np
    p = generate_rsa_prime(np, e, ntests)
    q = generate_rsa_prime(nq, e, ntests)

    assert(p != q and p > 0 and q > 0)

    N = p * q
    L = (p-1) * (q-1)
    d = modinv(e, L)

    dP = d % (p-1)
    dQ = d % (q-1)
    qInv = modinv(q, p)

    print "N:", hex(N)
    print "p:", hex(p)
    print "q:", hex(q)
    print "e:", e
    print "d:", hex(d)
    print "dP:", hex(dP)
    print "dQ:", hex(dQ)
    print "qInv:", hex(qInv)

    return (N, e, d, p, q, dP, dQ, qInv)


def decrypt_crt(c, dP, dQ, qInv, p, q, d):
    """
    CRT方法解密
    """
    m1 = pow(c, dP, p)
    m2 = pow(c, dQ, q)
    h = (qInv * (m1 - m2)) % p
    m = m2 + h * q
    return m


def test_compare_crt(N, e, d, p, q, dP, dQ, qInv):
    """
    测试-CRT优化后解密效率和优化前效率
    """
    num = 50
    raw_data = range(0, num)
    encrypted_data = []
    for m in raw_data :
        encrypted_data.append(encrypt(m, N, e))

    s = clock()
    for i in xrange(0, num):
        c = encrypted_data[i]
        m = decrypt_crt(c, dP, dQ, qInv, p, q, d)
        assert m == raw_data[i]
    crt_clock = clock()-s

    s = clock()
    for i in xrange(0, num):
        c = encrypted_data[i]
        m = decrypt(c, N, d)
        assert m == raw_data[i]
    basic_clock = clock()-s

    print "Test RSA, decrypt crt:%s, normal:%s" % (crt_clock, basic_clock)


def test_rsa(N, e, d):
    """
    测试RSA加密解密
    """
    for m in xrange(1, 30):
        m_ = decrypt(encrypt(m, N, e), N, d)
        assert m == m_
    print "\nTest RSA basic: passed"


if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-b", "--bits", dest="bits", type=int,
                      help="rsa key bits", default=512)
    (options, _) = parser.parse_args()
    (N, e, d, p, q, dP, dQ, qInv) = generate_rsa_crt(options.bits)
    test_rsa(N, e, d)
    test_compare_crt(N, e, d, p, q, dP, dQ, qInv)
