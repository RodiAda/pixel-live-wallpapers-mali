import os, struct, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from miuisuper import Dex


def main(path, cls):
    d = Dex(path)
    player_field = None
    for i in range(d.fn):
        c, ty, n = struct.unpack_from('<HHI', d.b, d.fo + 8 * i)
        if d.t(c) == cls and d.t(ty).endswith('MrePlayer;'):
            player_field, player_type = i, d.t(ty)
    assert player_field is not None
    f_init = d.field(cls, 'mInited')
    f_on = d.field(cls, 'mScreenOn')
    f_vis = d.field(cls, 'mVisibleSurfaces')
    f_res = d.field(cls, 'mUnityResumed')
    m_pause = d.meth(player_type, 'pause')

    start, n, regs, ins = d.code(cls, 'filamentPause')
    this = regs - ins
    body = [
        0x0055 | (this << 12), f_init,
        0x0038, None,
        0x0055 | (this << 12), f_on,
        0x0038, 6,
        0x0052 | (this << 12), f_vis,
        0x0039, None,
        0x0012,
        0x005c | (this << 12), f_res,
        0x0054 | (this << 12), player_field,
        0x106e, m_pause, 0,
        0x000e,
    ]
    ret = len(body) - 1
    body[3] = ret - 2
    body[11] = ret - 10
    assert len(body) <= n, (len(body), n)
    d.put(start, body + [0] * (n - len(body)))
    print('filamentPause: pause only when screen off or invisible')

    start, n, regs, ins = d.code(cls, 'getRefreshRate')
    d.put(start, [0x0013, 30, 0x000f])
    print('getRefreshRate -> 30')
    d.save()


main(sys.argv[1], sys.argv[2])
