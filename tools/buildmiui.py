import os, re, subprocess, sys, tempfile, zipfile

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
src, out = sys.argv[1], sys.argv[2]
opts = dict(a.split('=', 1) for a in sys.argv[3:])
bt = opts['bt']
work = tempfile.mkdtemp(prefix='miui-')


def run(*cmd, check=True):
    r = subprocess.run(cmd, capture_output=True, text=True)
    sys.stdout.write(r.stdout)
    if check and r.returncode:
        sys.exit(r.stderr or r.stdout)
    return r


repl = {}
with zipfile.ZipFile(src) as z:
    names = z.namelist()
    dexes = sorted(n for n in names if re.fullmatch(r'classes\d*\.dex', n))
    for n in dexes + ['AndroidManifest.xml', 'resources.arsc'] + [n for n in names if n.startswith('res/') and n.endswith('.xml')]:
        p = os.path.join(work, n)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, 'wb').write(z.read(n))

for n in dexes:
    p = os.path.join(work, n)
    if b'Lcom/miui/miwallpaper/basesuperwallpaper/SuperWallpaper;' in open(p, 'rb').read():
        r = run(sys.executable, '-I', os.path.join(TOOLS, 'miuisuper.py'), p, check=False)
        if r.returncode:
            print('miuisuper failed on', n, r.stderr.strip().splitlines()[-1:])
        else:
            repl[n] = p

man = os.path.join(work, 'AndroidManifest.xml')
cur = man
step = 0


def manstep(*args):
    global cur, step
    step += 1
    nxt = os.path.join(work, 'm%d.xml' % step)
    r = run(sys.executable, '-I', *args[:1], cur, nxt, *args[1:], check=False)
    if r.returncode == 0:
        cur = nxt
    else:
        print('skip', os.path.basename(args[0]), (r.stderr or r.stdout).strip()[:120])


if 'pkg' in opts:
    old, new = opts['pkg'].split('=>')
    manstep(os.path.join(TOOLS, 'poolstr.py'), '%s=>%s' % (old, new), '%s.androidx-startup=>%s.androidx-startup' % (old, new))
manstep(os.path.join(TOOLS, 'axmlhide.py'), 'PreviewSuperWallpaper', 'mini_android_version')
if 'labelref' in opts:
    import struct
    old, new = (int(x, 16) for x in opts['labelref'].split('=>'))
    b = bytearray(open(cur, 'rb').read())
    hits = 0
    o = 8 + struct.unpack_from('<I', b, 12)[0]
    while o < len(b):
        t, h, sz = struct.unpack_from('<HHI', b, o)
        if t == 0x102:
            aoff, asz, acnt = struct.unpack_from('<HHH', b, o + 24)
            for i in range(acnt):
                a = o + 16 + aoff + i * asz
                if b[a + 15] == 0x01 and struct.unpack_from('<I', b, a + 16)[0] == old:
                    struct.pack_into('<I', b, a + 16, new)
                    hits += 1
        o += sz
    step += 1
    cur2 = os.path.join(work, 'm%d.xml' % step)
    open(cur2, 'wb').write(b)
    cur = cur2
    print('labelref retargeted', hits)
if cur != man:
    repl['AndroidManifest.xml'] = cur

for n in names:
    if n.startswith('res/') and n.endswith('.xml'):
        p = os.path.join(work, n)
        if b's\x00u\x00p\x00p\x00o\x00r\x00t\x00s\x00A\x00m\x00b\x00i\x00e\x00n\x00t' in open(p, 'rb').read() or b'supportsAmbientMode' in open(p, 'rb').read():
            q = p + '.new'
            r = run(sys.executable, '-I', os.path.join(TOOLS, 'axmlbool.py'), p, q, 'supportsAmbientMode', 'false', check=False)
            if r.returncode == 0:
                repl[n] = q

arsc = os.path.join(work, 'resources.arsc')
if 'label' in opts:
    q = arsc + '.new'
    r = run(sys.executable, '-I', os.path.join(TOOLS, 'arscstr.py'), arsc, q, opts['label'], check=False)
    if r.returncode == 0:
        repl['resources.arsc'] = q
        arsc = q

u = os.path.join(work, 'u.apk')
a = os.path.join(work, 'a.apk')
run(sys.executable, os.path.join(TOOLS, 'rezip.py'), src, u, *['%s=%s' % kv for kv in repl.items()])
stub = 'classes%d.dex' % (len(dexes) + 1)
with zipfile.ZipFile(u, 'a') as z:
    i = zipfile.ZipInfo(stub, date_time=(1981, 1, 1, 1, 1, 2))
    i.compress_type = zipfile.ZIP_DEFLATED
    z.writestr(i, open(os.path.join(TOOLS, 'miui-stubs', 'miui-stubs.dex'), 'rb').read())
print('stubs as', stub)
run(os.path.join(bt, 'zipalign'), '-f', '-P', '16', '4', u, a)
keystore = os.environ.get('KEYSTORE', os.path.join(ROOT, 'mykey.jks'))
if 'KS_PASS' not in os.environ:
    sys.exit('set KS_PASS (and optionally KEYSTORE, KS_ALIAS) for apksigner')
run(os.path.join(bt, 'apksigner'), 'sign', '--ks', keystore, '--ks-pass', 'env:KS_PASS', '--ks-key-alias', os.environ.get('KS_ALIAS', 'wp'), '--out', out, a)
print('built', out)
