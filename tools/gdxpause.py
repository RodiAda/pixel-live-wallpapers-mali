import struct, sys, hashlib, zlib

ENGINE = 'Lcom/badlogic/gdx/backends/android/AndroidLiveWallpaperService$AndroidWallpaperEngine;'
SERVICE = 'Lcom/badlogic/gdx/backends/android/AndroidLiveWallpaperService;'


def uleb(b, o):
    r = s = 0
    while True:
        x = b[o]; o += 1; r |= (x & 0x7f) << s; s += 7
        if x < 0x80:
            return r, o


def patch(path):
    b = bytearray(open(path, 'rb').read())
    u = lambda o: struct.unpack_from('<I', b, o)[0]
    so, to, fn, fo, mo, cn, co = u(60), u(68), u(80), u(84), u(92), u(96), u(100)

    def s(i):
        o = u(so + 4 * i); _, o = uleb(b, o); return b[o:b.index(0, o)].decode('utf-8', 'replace')

    def t(i):
        return s(u(to + 4 * i))

    fields = {}
    for i in range(fn):
        c, _, n = struct.unpack_from('<HHI', b, fo + 8 * i)
        if t(c) == SERVICE and s(n) in ('linkedEngine', 'app'):
            fields[s(n)] = i
    if len(fields) != 2:
        return 'no gdx service fields'
    for c in range(cn):
        base = co + 32 * c
        if t(u(base)) != ENGINE:
            continue
        o = u(base + 24)
        sf, o = uleb(b, o); inf, o = uleb(b, o); dm, o = uleb(b, o); vm, o = uleb(b, o)
        for _ in range(sf + inf):
            _, o = uleb(b, o); _, o = uleb(b, o)
        idx = 0
        for k in range(dm + vm):
            if k == dm:
                idx = 0
            d, o = uleb(b, o); idx += d; _, o = uleb(b, o); code, o = uleb(b, o)
            if s(struct.unpack_from('<I', b, mo + 8 * idx + 4)[0]) != 'onPause' or not code:
                continue
            n = u(code + 12); start = code + 16
            hits = []
            pc = 0
            while pc < n:
                w = struct.unpack_from('<H', b, start + 2 * pc)[0]
                if w & 0xff == 0x54:
                    f = struct.unpack_from('<H', b, start + 2 * pc + 2)[0]
                    nxt = struct.unpack_from('<H', b, start + 2 * pc + 4)[0]
                    if f in (fields['linkedEngine'], fields['app']) and nxt & 0xff == 0x38:
                        hits.append((start + 2 * pc + 2, f))
                pc += 1
            if not hits:
                return 'pattern not found'
            off, f = hits[-1]
            if f == fields['app']:
                return 'already patched'
            struct.pack_into('<H', b, off, fields['app'])
            b[12:32] = hashlib.sha1(b[32:]).digest()
            struct.pack_into('<I', b, 8, zlib.adler32(bytes(b[12:])) & 0xffffffff)
            open(path, 'wb').write(b)
            return 'patched at 0x%x' % (off - 2)
    return 'no engine class'


for p in sys.argv[1:]:
    print(p, patch(p))
