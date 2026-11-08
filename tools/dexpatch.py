import struct, sys, hashlib, zlib
def uleb(b, o):
    r = s = 0
    while True:
        x = b[o]; o += 1; r |= (x & 0x7f) << s; s += 7
        if x < 0x80: return r, o
def patch(path, cls='Lcom/badlogic/gdx/graphics/glutils/ShaderProgram;', field='pedantic'):
    b = bytearray(open(path, 'rb').read())
    u = lambda o: struct.unpack_from('<I', b, o)[0]
    sids_n, sids_o = u(56), u(60); tids_n, tids_o = u(64), u(68); fids_n, fids_o = u(80), u(84)
    def string(i):
        o = u(sids_o + 4*i); _, o = uleb(b, o); e = b.index(0, o); return b[o:e].decode('utf-8', 'replace')
    sidx = {}
    for i in range(sids_n):
        s = string(i)
        if s in (cls, field): sidx[s] = i
    if len(sidx) < 2: return 0
    tidx = next((i for i in range(tids_n) if u(tids_o + 4*i) == sidx[cls]), None)
    fidx = [i for i in range(fids_n) if struct.unpack_from('<HHI', b, fids_o + 8*i) == (tidx, struct.unpack_from('<HHI', b, fids_o + 8*i)[1], sidx[field])]
    n = 0
    for fi in fidx:
        pat = bytes([0x6a]) 
        o = 0
        while True:
            o = b.find(pat, o)
            if o < 0: break
            if o % 2 == 0 and struct.unpack_from('<H', b, o+2)[0] == fi:
                reg = b[o+1]
                if b[o-2] == 0x12 and (b[o-1] & 0x0f) == reg and (b[o-1] >> 4) == 1:
                    b[o-1] = reg; n += 1
                    print(f'  patched const/4 v{reg},1 -> 0 at 0x{o-2:x} (field {fi})')
            o += 1
    if n:
        b[12:32] = hashlib.sha1(b[32:]).digest()
        struct.pack_into('<I', b, 8, zlib.adler32(bytes(b[12:])))
        open(path, 'wb').write(b)
    return n
tot = 0
for p in sys.argv[1:]:
    k = patch(p); print(p, k); tot += k
sys.exit(0 if tot else 1)
