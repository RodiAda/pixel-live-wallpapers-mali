import struct, sys

src, dst, service_suffix, new_name = sys.argv[1:5]
b = bytearray(open(src, 'rb').read())
pool_off = 8
ptyp, phsz, psz, cnt, scnt, flags, sstart, ststart = struct.unpack_from('<HHIIIIII', b, pool_off)
utf8 = bool(flags & 0x100)
offs = struct.unpack_from('<%dI' % cnt, b, pool_off + phsz)


def rd(i):
    o = pool_off + sstart + offs[i]
    if utf8:
        n = b[o]; o += 1
        if n & 0x80: o += 1
        m = b[o]; o += 1
        if m & 0x80: m = ((m & 0x7f) << 8) | b[o]; o += 1
        return b[o:o + m].decode()
    n = struct.unpack_from('<H', b, o)[0]
    return b[o + 2:o + 2 + 2 * n].decode('utf-16le')


S = [rd(i) for i in range(cnt)]
new_idx = S.index(new_name)
o = pool_off + psz
inside = False
depth = 0
hits = 0
while o < len(b):
    t, h, sz = struct.unpack_from('<HHI', b, o)
    if t == 0x102:
        ns, name, aoff, asz, acnt = struct.unpack_from('<IIHHH', b, o + 16)
        attrs = [o + 16 + aoff + i * asz for i in range(acnt)]
        vals = {S[struct.unpack_from('<I', b, a + 4)[0]]: a for a in attrs}
        if S[name] == 'service':
            na = vals.get('name')
            raw = struct.unpack_from('<I', b, na + 8)[0] if na is not None else 0xffffffff
            inside = raw != 0xffffffff and S[raw].endswith(service_suffix)
            depth = 0
        elif inside:
            depth += 1
            if S[name] == 'meta-data':
                na = vals.get('name')
                raw = struct.unpack_from('<I', b, na + 8)[0]
                if S[raw] == 'android.service.wallpaper':
                    struct.pack_into('<I', b, na + 8, new_idx)
                    struct.pack_into('<I', b, na + 16, new_idx)
                    hits += 1
                    print('meta-data android.service.wallpaper ->', new_name)
    elif t == 0x103 and inside:
        ns, name = struct.unpack_from('<II', b, o + 16)
        if S[name] == 'service':
            inside = False
    o += sz
if not hits:
    sys.exit('no match')
open(dst, 'wb').write(b)
