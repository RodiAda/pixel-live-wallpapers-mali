import struct, sys
src, dst = sys.argv[1], sys.argv[2]
pairs = [a.split('=>') for a in sys.argv[3:]]
b = open(src, 'rb').read()
typ, hsz, tsz = struct.unpack_from('<HHI', b, 0); assert typ == 2
pool_off = hsz
ptyp, phsz, psz, cnt, scnt, flags, sstart, ststart = struct.unpack_from('<HHIIIIII', b, pool_off)
assert ptyp == 1
utf8 = bool(flags & 0x100)
offs = struct.unpack_from('<%dI' % cnt, b, pool_off + phsz)
data_start = pool_off + sstart
data_end = pool_off + (ststart if scnt else psz)
def read(i):
    o = data_start + offs[i]
    if utf8:
        n = b[o]; o += 1
        if n & 0x80: o += 1
        m = b[o]; o += 1
        if m & 0x80: m = ((m & 0x7f) << 8) | b[o]; o += 1
        return b[o:o+m].decode('utf-8')
    n = struct.unpack_from('<H', b, o)[0]; o += 2
    if n & 0x8000: n = ((n & 0x7fff) << 16) | struct.unpack_from('<H', b, o)[0]; o += 2
    return b[o:o+2*n].decode('utf-16le')
def enc(s):
    if utf8:
        e = s.encode('utf-8'); out = b''
        for n in (len(s), len(e)):
            out += bytes([n]) if n < 0x80 else bytes([0x80 | (n >> 8), n & 0xff])
        return out + e + b'\0'
    e = s.encode('utf-16le'); n = len(s)
    h = struct.pack('<H', n) if n < 0x8000 else struct.pack('<HH', 0x8000 | (n >> 16), n & 0xffff)
    return h + e + b'\0\0'
strs = [read(i) for i in range(cnt)]
hit = 0
for i, s in enumerate(strs):
    for a, c in pairs:
        if s == a: strs[i] = c; hit += 1; print('replaced #%d: %s -> %s' % (i, a, c))
if hit != len(pairs): sys.exit('only %d of %d found' % (hit, len(pairs)))
newdata = b''; newoffs = []
for s in strs:
    newoffs.append(len(newdata)); newdata += enc(s)
while len(newdata) % 4: newdata += b'\0'
styles = b[pool_off + ststart: pool_off + psz] if scnt else b''
stylo = b[pool_off + phsz + 4*cnt: data_start]
new_sstart = phsz + 4*cnt + len(stylo)
new_ststart = (new_sstart + len(newdata)) if scnt else 0
new_psz = new_sstart + len(newdata) + len(styles)
pool = struct.pack('<HHIIIIII', ptyp, phsz, new_psz, cnt, scnt, flags, new_sstart, new_ststart) + b[pool_off+28:pool_off+phsz] + struct.pack('<%dI' % cnt, *newoffs) + stylo + newdata + styles
rest = b[pool_off + psz:]
out = b[:pool_off] + pool + rest
out = out[:4] + struct.pack('<I', len(out)) + out[8:]
open(dst, 'wb').write(out)
print('size', len(b), '->', len(out))
