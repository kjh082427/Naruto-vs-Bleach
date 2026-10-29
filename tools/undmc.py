"""Restore waflash 'DMC' SWFs to standard CWS.

waflash wraps each SWF as: b'DMC' + version + length, zlib body with 45 extra
bytes inserted right after the frame header (RECT + frame rate + frame count).

usage: python3 -I undmc.py in.swf out.swf
"""
import sys
import zlib

INSERTED = 45


def restore(data):
    if data[:3] != b'DMC':
        raise ValueError('not a DMC file: %r' % data[:3])
    body = zlib.decompress(data[8:])
    nbits = body[0] >> 3
    hdr = (5 + 4 * nbits + 7) // 8 + 4
    body = body[:hdr] + body[hdr + INSERTED:]
    return b'CWS' + data[3:4] + (len(body) + 8).to_bytes(4, 'little') + zlib.compress(body, 9)


if __name__ == '__main__':
    src, dst = sys.argv[1], sys.argv[2]
    open(dst, 'wb').write(restore(open(src, 'rb').read()))
