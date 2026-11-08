import struct, sys, hashlib, zlib
def uleb(b, o):
    r = s = 0
    while True:
        x = b[o]; o += 1; r |= (x & 0x7f) << s; s += 7
        if x < 0x80: return r, o
def enc_uleb(v):
    out = bytearray()
    while True:
        x = v & 0x7f; v >>= 7
        if v: out.append(x | 0x80)
        else: out.append(x); return bytes(out)
path, cls, meth = sys.argv[1], sys.argv[2], sys.argv[3]
b = bytearray(open(path, 'rb').read())
u = lambda o: struct.unpack_from('<I', b, o)[0]
sn, so, tn, to, mn, mo, cn, co = u(56), u(60), u(64), u(68), u(88), u(92), u(96), u(100)
def s(i):
    o = u(so + 4*i); _, o = uleb(b, o); return b[o:b.index(0, o)].decode('utf-8', 'replace')
names = {s(i): i for i in range(sn) if s(i) in (cls, meth)}
tid = next(i for i in range(tn) if u(to + 4*i) == names[cls])
mids = [i for i in range(mn) if struct.unpack_from('<HHI', b, mo + 8*i)[0] == tid and struct.unpack_from('<HHI', b, mo + 8*i)[2] == names[meth]]
changed = 0
for c in range(cn):
    base = co + 32*c
    if u(base) != tid: continue
    af = u(base + 4)
    if not af & 1:
        struct.pack_into('<I', b, base + 4, (af | 1) & ~0x6); changed += 1; print('class flags 0x%x -> 0x%x' % (af, (af | 1) & ~0x6))
    cd = u(base + 24)
    o = cd
    sf, o = uleb(b, o); inf, o = uleb(b, o); dm, o = uleb(b, o); vm, o = uleb(b, o)
    for _ in range(sf + inf):
        _, o = uleb(b, o); _, o = uleb(b, o)
    idx = 0
    for k in range(dm + vm):
        if k == dm: idx = 0
        d, o = uleb(b, o); idx += d
        fo = o; f, o = uleb(b, o); _, o = uleb(b, o)
        if idx in mids:
            nf = (f | 1) & ~0x6
            e = enc_uleb(nf)
            if len(e) != o - fo - len(enc_uleb(uleb(b, o - (o - fo - len(enc_uleb(f))) )[0])) and len(e) != len(enc_uleb(f)):
                sys.exit('length change')
            if len(e) != len(enc_uleb(f)): sys.exit('uleb length differs')
            b[fo:fo+len(e)] = e; changed += 1
            print('method %d flags 0x%x -> 0x%x (%s)' % (idx, f, nf, 'direct' if k < dm else 'virtual'))
if not changed: sys.exit('nothing changed')
b[12:32] = hashlib.sha1(b[32:]).digest()
struct.pack_into('<I', b, 8, zlib.adler32(bytes(b[12:])))
open(path, 'wb').write(b)
