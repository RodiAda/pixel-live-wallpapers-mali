import struct, sys
src, dst = sys.argv[1], sys.argv[2]
mapping = dict(a.split('=') for a in sys.argv[3:])
b = bytearray(open(src, 'rb').read())
PO = 8
ptyp, phsz, psz, cnt, scnt, flags, sstart, ststart = struct.unpack_from('<HHIIIIII', b, PO)
assert scnt == 0
utf8 = bool(flags & 0x100)
offs = list(struct.unpack_from('<%dI' % cnt, b, PO + phsz))
def rd(i):
    o = PO + sstart + offs[i]
    if utf8:
        n = b[o]; o += 1
        if n & 0x80: o += 1
        m = b[o]; o += 1
        if m & 0x80: m = ((m & 0x7f) << 8) | b[o]; o += 1
        return b[o:o+m].decode()
    n = struct.unpack_from('<H', b, o)[0]; return b[o+2:o+2+2*n].decode('utf-16le')
def enc(s):
    if utf8:
        e = s.encode(); return bytes([len(s), len(e)]) + e + b'\0'
    return struct.pack('<H', len(s)) + s.encode('utf-16le') + b'\0\0'
S = [rd(i) for i in range(cnt)]
newnames = sorted(set(mapping.values()))
idx = {}
for n in newnames:
    if n in S: idx[n] = S.index(n)
    else: idx[n] = len(S); S.append(n)
data = b''; noffs = []
for s in S:
    noffs.append(len(data)); data += enc(s)
while len(data) % 4: data += b'\0'
ncnt = len(S)
nsstart = phsz + 4 * ncnt
npsz = nsstart + len(data)
pool = struct.pack('<HHIIIIII', ptyp, phsz, npsz, ncnt, 0, flags, nsstart, 0) + bytes(b[PO+28:PO+phsz]) + struct.pack('<%dI' % ncnt, *noffs) + data
rest = bytearray(b[PO + psz:])
o = 0; hits = 0
while o < len(rest):
    t, h, sz = struct.unpack_from('<HHI', rest, o)
    if t == 0x102:
        ns, name, aoff, asz, acnt = struct.unpack_from('<IIHHH', rest, o + 16)
        if S[name] == 'service':
            attrs = [o + 16 + aoff + i * asz for i in range(acnt)]
            byname = {S[struct.unpack_from('<I', rest, a + 4)[0]]: a for a in attrs}
            raw = struct.unpack_from('<I', rest, byname['name'] + 8)[0]
            cls = S[raw].rsplit('.', 1)[-1]
            if cls in mapping and 'process' in byname:
                a = byname['process']; ni = idx[mapping[cls]]
                struct.pack_into('<I', rest, a + 8, ni); struct.pack_into('<I', rest, a + 16, ni)
                hits += 1; print('process', cls, '->', mapping[cls])
    o += sz
out = bytes(b[:PO]) + pool + bytes(rest)
out = out[:4] + struct.pack('<I', len(out)) + out[8:]
open(dst, 'wb').write(out)
print('hits', hits)
