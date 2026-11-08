import struct, sys
src, dst, elname, match, attrname, newstr = sys.argv[1:7]
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
        return b[o:o+m].decode()
    n = struct.unpack_from('<H', b, o)[0]; return b[o+2:o+2+2*n].decode('utf-16le')
S = [rd(i) for i in range(cnt)]
new_idx = S.index(newstr)
o = pool_off + psz
hits = 0
while o < len(b):
    t, h, sz = struct.unpack_from('<HHI', b, o)
    if t == 0x102:
        ns, name, aoff, asz, acnt = struct.unpack_from('<IIHHH', b, o + 16)
        if S[name] == elname:
            attrs = [o + 16 + aoff + i * asz for i in range(acnt)]
            vals = {S[struct.unpack_from('<I', b, a + 4)[0]]: a for a in attrs}
            na = vals.get('name')
            if na is not None:
                raw = struct.unpack_from('<I', b, na + 8)[0]
                if raw != 0xffffffff and S[raw].endswith(match):
                    a = vals[attrname]
                    struct.pack_into('<I', b, a + 8, new_idx)
                    struct.pack_into('<I', b, a + 16, new_idx)
                    hits += 1; print('patched', S[raw], attrname, '->', newstr)
    o += sz
if not hits: sys.exit('no match')
open(dst, 'wb').write(b)
