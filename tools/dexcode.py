import struct, sys
def uleb(b, o):
    r = s = 0
    while True:
        x = b[o]; o += 1; r |= (x & 0x7f) << s; s += 7
        if x < 0x80: return r, o
path, clsfrag, meth = sys.argv[1], sys.argv[2], sys.argv[3]
b = open(path, 'rb').read()
u = lambda o: struct.unpack_from('<I', b, o)[0]
sn, so, tn, to, pn, po, mn, mo, cn, co = u(56), u(60), u(64), u(68), u(72), u(76), u(88), u(92), u(96), u(100)
def s(i):
    o = u(so + 4*i); _, o = uleb(b, o); return b[o:b.index(0, o)].decode('utf-8', 'replace')
def t(i): return s(u(to + 4*i))
def m(i):
    c, p, n = struct.unpack_from('<HHI', b, mo + 8*i); return t(c), s(n)
for c in range(cn):
    base = co + 32*c
    cname = t(u(base))
    if clsfrag not in cname: continue
    cd = u(base + 24)
    if not cd: continue
    o = cd
    sf, o = uleb(b, o); inf, o = uleb(b, o); dm, o = uleb(b, o); vm, o = uleb(b, o)
    for _ in range(sf + inf): _, o = uleb(b, o); _, o = uleb(b, o)
    idx = 0
    for k in range(dm + vm):
        if k == dm: idx = 0
        d, o = uleb(b, o); idx += d; f, o = uleb(b, o); code, o = uleb(b, o)
        if m(idx)[1] == meth and code:
            regs, ins, outs, tries, dbg, isz = struct.unpack_from('<HHHHII', b, code)
            print(cname, meth, 'code@0x%x regs=%d ins=%d insns=%d' % (code, regs, ins, isz))
            ins_off = code + 16
            pc = 0
            while pc < isz:
                op = b[ins_off + 2*pc]
                if op in (0x6e, 0x6f, 0x70, 0x71, 0x72):
                    a = b[ins_off + 2*pc + 1]; mi = struct.unpack_from('<H', b, ins_off + 2*pc + 2)[0]; regs4 = struct.unpack_from('<H', b, ins_off + 2*pc + 4)[0]
                    cnt = a >> 4; rl = [(regs4 >> (4*j)) & 0xf for j in range(4)][:cnt]
                    print('  pc=%d off=0x%x op=%02x regs=%s -> %s.%s' % (pc, ins_off + 2*pc, op, rl, *m(mi)))
                    pc += 3
                elif op == 0x0e: print('  pc=%d return-void' % pc); pc += 1
                else:
                    print('  pc=%d op=%02x' % (pc, op)); pc += 1
