import os, re, subprocess, sys, tempfile
root = sys.argv[1]
assets = os.path.join(root, 'assets')
inc = re.compile(r'^\s*#include\s*<([^>]+)>', re.M)
def expand(path, seen=None):
    src = open(path, errors='replace').read()
    def rep(m):
        p = os.path.join(assets, m.group(1))
        return expand(p) if os.path.exists(p) else m.group(0)
    return inc.sub(rep, src)
def prep(src):
    src = re.sub(r'^\s*#include\s+SHADER_METHODS.*$', '', src, flags=re.M).replace('REPLACE_SCENE_ID','0')
    if not re.search(r'^\s*#version', src, re.M):
        src = '#version 100\n' + src
    return src
out = tempfile.mkdtemp()
bad = 0
files = []
for d, _, fs in os.walk(root):
    for f in fs:
        if f.endswith(('.frag', '.vert')) or re.search(r'_(frag|vert)\.glsl$', f):
            files.append(os.path.join(d, f))
for f in sorted(files):
    stage = 'frag' if ('frag' in os.path.basename(f)) else 'vert'
    t = os.path.join(out, 'x.' + stage)
    open(t, 'w').write(prep(expand(f)))
    r = subprocess.run(['glslangValidator', t], capture_output=True, text=True)
    msgs = [l for l in (r.stdout + r.stderr).splitlines() if 'ERROR' in l and 'compilation errors' not in l]
    if msgs:
        bad += 1
        print('##', os.path.relpath(f, root))
        for m in msgs[:8]: print('   ', m.replace(t, ''))
print('files', len(files), 'bad', bad)
print('-- link pairs')
for f in sorted(files):
    if not f.endswith('.vert'): continue
    g = f[:-5] + '.frag'
    if not os.path.exists(g): continue
    a = os.path.join(out, 'l.vert'); b = os.path.join(out, 'l.frag')
    open(a,'w').write(prep(expand(f))); open(b,'w').write(prep(expand(g)))
    r = subprocess.run(['glslangValidator', '-l', a, b], capture_output=True, text=True)
    msgs = [l for l in (r.stdout + r.stderr).splitlines() if 'ERROR' in l and 'compilation errors' not in l]
    if msgs:
        print('## LINK', os.path.relpath(f, root)[:-5])
        for m in msgs[:6]: print('   ', m)
