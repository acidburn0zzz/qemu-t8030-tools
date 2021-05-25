"""
/**************************************************************
 LZSS.C -- A Data Compression Program
***************************************************************
    4/6/1989 Haruhiko Okumura
    Use, distribute, and modify this program freely.
    Please send me your improved versions.
        PC-VAN      SCIENCE
        NIFTY-Serve PAF01022
        CompuServe  74050,1022
**************************************************************/
/*
 *  lzss.c - Package for decompressing lzss compressed objects
 *
 *  Copyright (c) 2003 Apple Computer, Inc.
 *
 *  DRI: Josh de Cesare
 */
"""

from array import array
import struct
import sys

N = 4096
F = 18
THRESHOLD = 2
NIL = N


def decompress_lzss(data):
    if data[:8] != b"complzss":
        print('decompress_lzss: complzss magic missing')
        return
    decompsize = struct.unpack(">L", data[12:16])[0]
    text_buf = array("B", b" " * (N + F - 1))
    src = array("B", data[0x180:])
    # srclen = len(src)
    srclen = struct.unpack(">L", data[16:20])[0]
    dst = array("B", b" " * decompsize)
    r = N - F
    srcidx, dstidx, flags, c = 0, 0, 0, 0

    while True:
        flags >>= 1
        if ((flags & 0x100) == 0):
            if (srcidx >= srclen):
                break
            c = src[srcidx]
            srcidx += 1
            flags = c | 0xFF00

        if (flags & 1):
            if (srcidx >= srclen):
                break
            c = src[srcidx]
            srcidx += 1
            dst[dstidx] = c
            dstidx += 1
            text_buf[r] = c
            r += 1
            r &= (N - 1)
        else:
            if (srcidx >= srclen):
                break
            i = src[srcidx]
            srcidx += 1
            if (srcidx >= srclen):
                break
            j = src[srcidx]
            srcidx += 1
            i |= ((j & 0xF0) << 4)
            j = (j & 0x0F) + THRESHOLD
            for k in range(j + 1):
                c = text_buf[(i + k) & (N - 1)]
                dst[dstidx] = c
                dstidx += 1
                text_buf[r] = c
                r += 1
                r &= (N - 1)
    return dst.tobytes()


if __name__ == "__main__":
    data = decompress_lzss(open(sys.argv[1], "rb").read())
    if data:
        open(sys.argv[2], "wb").write(data)
