import struct, sys, hashlib, zlib

BASE = 'Lcom/miui/miwallpaper/basesuperwallpaper/SuperWallpaper;'
ENGINE = 'Lcom/miui/miwallpaper/basesuperwallpaper/SuperWallpaper$SuperWallpaperEngine;'
BUILD = 'Lcom/miui/miwallpaper/utils/SystemBuildUtils;'
UNITY = 'Lcom/unity3d/player/UnityPlayer;'


def uleb(b, o):
    r = s = 0
    while True:
        x = b[o]; o += 1; r |= (x & 0x7f) << s; s += 7
        if x < 0x80:
            return r, o


class Dex:
    def __init__(self, path):
        self.path = path
        self.b = bytearray(open(path, 'rb').read())
        u = self.u
        self.so, self.to, self.fn, self.fo, self.mn, self.mo, self.cn, self.co = u(60), u(68), u(80), u(84), u(88), u(92), u(96), u(100)
        self.sn = u(56)

    def u(self, o):
        return struct.unpack_from('<I', self.b, o)[0]

    def s(self, i):
        o = self.u(self.so + 4 * i); _, o = uleb(self.b, o)
        return self.b[o:self.b.index(0, o)].decode('utf-8', 'replace')

    def t(self, i):
        return self.s(self.u(self.to + 4 * i))

    def field(self, cls, name):
        for i in range(self.fn):
            c, _, n = struct.unpack_from('<HHI', self.b, self.fo + 8 * i)
            if self.t(c) == cls and self.s(n) == name:
                return i
        raise KeyError(cls + name)

    def meth(self, cls, name):
        for i in range(self.mn):
            c, _, n = struct.unpack_from('<HHI', self.b, self.mo + 8 * i)
            if self.t(c) == cls and self.s(n) == name:
                return i
        raise KeyError(cls + name)

    def methname(self, i):
        c, _, n = struct.unpack_from('<HHI', self.b, self.mo + 8 * i)
        return self.t(c), self.s(n)

    def code(self, cls, name):
        for c in range(self.cn):
            base = self.co + 32 * c
            if self.t(self.u(base)) != cls:
                continue
            o = self.u(base + 24)
            if not o:
                continue
            sf, o = uleb(self.b, o); inf, o = uleb(self.b, o); dm, o = uleb(self.b, o); vm, o = uleb(self.b, o)
            for _ in range(sf + inf):
                _, o = uleb(self.b, o); _, o = uleb(self.b, o)
            idx = 0
            for k in range(dm + vm):
                if k == dm:
                    idx = 0
                d, o = uleb(self.b, o); idx += d; _, o = uleb(self.b, o); off, o = uleb(self.b, o)
                if self.methname(idx)[1] == name and off:
                    regs, ins = struct.unpack_from('<HH', self.b, off)
                    return off + 16, self.u(off + 12), regs, ins
        raise KeyError(cls + name)

    def cu(self, start, n):
        return [struct.unpack_from('<H', self.b, start + 2 * i)[0] for i in range(n)]

    def put(self, start, words):
        for i, w in enumerate(words):
            struct.pack_into('<H', self.b, start + 2 * i, w)

    def find_invoke(self, start, n, target):
        pc = 0
        out = []
        words = self.cu(start, n)
        while pc < n:
            op = words[pc] & 0xff
            if op in (0x6e, 0x6f, 0x70, 0x71, 0x72) and pc + 2 < n and words[pc + 1] == target:
                out.append(pc)
            pc += 1
        return out

    def save(self):
        b = self.b
        b[12:32] = hashlib.sha1(b[32:]).digest()
        struct.pack_into('<I', b, 8, zlib.adler32(bytes(b[12:])) & 0xffffffff)
        open(self.path, 'wb').write(b)


def main(path):
    d = Dex(path)

    start, n, regs, ins = d.code(BUILD, 'isAndroidUAtLeast')
    d.put(start, [0x0012, 0x000f])
    print('isAndroidUAtLeast -> false')

    start, n, regs, ins = d.code(BASE, 'getRefreshRate')
    d.put(start, [0x0013, 30, 0x000f])
    print('getRefreshRate -> 30')

    quit_m = d.meth(UNITY, 'quit')
    done = False
    for c in range(d.cn):
        cname = d.t(d.u(d.co + 32 * c))
        if not cname.startswith(BASE[:-1] + '$'):
            continue
        try:
            start, n, _, _ = d.code(cname, 'handleMessage')
        except KeyError:
            continue
        for pc in d.find_invoke(start, n, quit_m):
            d.put(start + 2 * pc, [0, 0, 0])
            print('nop UnityPlayer.quit in', cname, 'pc', pc)
            done = True
    if not done:
        print('WARN no quit in handleMessage')

    f_res = d.field(BASE, 'mUnityResumed')
    f_init = d.field(BASE, 'mInited')
    f_on = d.field(BASE, 'mScreenOn')
    f_vis = d.field(BASE, 'mVisibleSurfaces')
    f_player = d.field(BASE, 'mUnityPlayer')
    m_focus = d.meth(UNITY, 'windowFocusChanged')
    m_pause = d.meth(UNITY, 'pause')
    start, n, regs, ins = d.code(BASE, 'unityPause')
    this = regs - ins
    assert regs >= 2 and ins == 1, (regs, ins)
    tail = []
    try:
        m_reset = d.meth(BASE, 'resetThreadPriority')
        if d.find_invoke(start, n, m_reset):
            tail = [0x1070, m_reset, this]
    except KeyError:
        pass
    v0, v1 = 0, 1
    body = [
        0x0055 | (v0 << 8) | (this << 12), f_res,
        0x0038 | (v0 << 8), None,
        0x0055 | (v0 << 8) | (this << 12), f_init,
        0x0038 | (v0 << 8), None,
        0x0055 | (v0 << 8) | (this << 12), f_on,
        0x0038 | (v0 << 8), 6,
        0x0052 | (v0 << 8) | (this << 12), f_vis,
        0x0039 | (v0 << 8), None,
        0x0012 | (v0 << 8),
        0x005c | (v0 << 8) | (this << 12), f_res,
        0x0054 | (v1 << 8) | (this << 12), f_player,
        0x206e, m_focus, v1 | (v0 << 4),
        0x106e, m_pause, v1,
    ] + tail + [0x000e]
    ret = len(body) - 1
    for pc in (2, 6, 14):
        body[pc + 1] = ret - pc
    assert len(body) <= n, (len(body), n)
    body += [0] * (n - len(body))
    d.put(start, body)
    print('unityPause: pause only when screen off or invisible')

    m_ispreview = d.meth(ENGINE, 'isPreview')
    start, n, regs, ins = d.code(ENGINE, 'onCreate')
    words = d.cu(start, n)
    pcs = d.find_invoke(start, n, m_ispreview)
    assert len(pcs) == 1, pcs
    pc = pcs[0] + 3
    assert words[pc] & 0xff == 0x0a
    reg = (words[pc] >> 8) & 0xff
    setter = pc + 1
    assert words[setter] & 0xff == 0x71, hex(words[setter])
    tname, mname = d.methname(words[setter + 1])
    assert tname == BASE and mname.startswith('access$'), (tname, mname)
    retpc = max(i for i, w in enumerate(words) if w == 0x000e)
    d.put(start + 2 * setter, [0x0039 | (reg << 8), retpc - setter, 0])
    print('engine onCreate: preview engine returns without touching mIsPreview')

    for name in ('android.wallpaper.goingtosleep', 'android.wallpaper.wakingup'):
        for i in range(d.sn):
            if d.s(i) == name:
                o = d.u(d.so + 4 * i); _, o = uleb(d.b, o)
                nxt = d.s(i + 1) if i + 1 < d.sn else ''
                new = name[:-1] + 'q'
                assert new < nxt or not nxt, (new, nxt)
                d.b[o + len(name) - 1] = ord('q')
                print('string', name, '->', new)
    d.save()


main(sys.argv[1])
