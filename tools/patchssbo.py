import UnityPy, sys, re, os, subprocess, tempfile, lz4.block
src = sys.argv[1]
env = UnityPy.load(src)
target = None
for obj in env.objects:
    if obj.type.name == 'Shader' and obj.path_id == 4:
        target = obj
tree = target.read_typetree()
print('shader in', target.assets_file.name)
blob = bytes(tree['compressedBlob'])
def L(x): return x if isinstance(x, list) else [x]
decl = re.compile(rb' struct unity_ParticleInstanceData_type \{\n\tuint\[14\] value;\n\};\n\nlayout\(std430, binding = 0\) readonly buffer unity_ParticleInstanceData \{\n\tunity_ParticleInstanceData_type unity_ParticleInstanceData_buf\[\];\n\};\n')
read = re.compile(rb'unity_ParticleInstanceData_buf\[[^\]]+\]\.value\[[^\]]+\]')
def fix_vertex(seg):
    seg, n = decl.subn(b'', seg)
    if not n: return seg, 0
    seg = read.sub(b'0u', seg)
    i = seg.rfind(b'return;\n}')
    seg = seg[:i] + b'gl_Position = vec4(0.0, 0.0, -2.0, 1.0);\n    ' + seg[i:]
    return seg, 1
def check(glsl):
    with tempfile.NamedTemporaryFile(suffix='.vert', delete=False) as f:
        f.write(glsl); p = f.name
    r = subprocess.run(['glslangValidator', p], capture_output=True, text=True)
    os.unlink(p)
    return [l for l in r.stdout.splitlines() if 'ERROR' in l]
new_blob = bytearray(); new_off = []; new_c = []; new_d = []; fixed = 0; bad = 0
for oo_l, cc_l, dd_l in zip(tree['offsets'], tree['compressedLengths'], tree['decompressedLengths']):
    o2 = []; c2 = []; d2 = []
    for oo, cc, dd in zip(L(oo_l), L(cc_l), L(dd_l)):
        data = lz4.block.decompress(blob[oo:oo+cc], uncompressed_size=dd)
        out = bytearray(); pos = 0; changed = False
        for m in re.finditer(rb'#ifdef VERTEX\n', data):
            fr = data.find(b'#ifdef FRAGMENT', m.end())
            if fr < 0: fr = len(data)
            e = data.rfind(b'#endif', m.end(), fr)
            seg = data[m.end():e]
            if b'unity_ParticleInstanceData_buf' not in seg: continue
            nseg, k = fix_vertex(seg)
            if k:
                errs = check(nseg)
                if errs: bad += 1; print('GLSL errors:', errs[:3])
                out += data[pos:m.end()] + nseg; pos = e; fixed += 1; changed = True
        out += data[pos:]
        if changed:
            comp = lz4.block.compress(bytes(out), store_size=False)
            o2.append(len(new_blob)); new_blob += comp; c2.append(len(comp)); d2.append(len(out))
        else:
            o2.append(len(new_blob)); new_blob += blob[oo:oo+cc]; c2.append(cc); d2.append(dd)
    def back(orig, lst): return lst if isinstance(orig, list) else lst[0]
    new_off.append(back(oo_l, o2)); new_c.append(back(cc_l, c2)); new_d.append(back(dd_l, d2))
print('fixed vertex programs:', fixed, 'glsl failures:', bad)
if bad: sys.exit(1)
tree['compressedBlob'] = list(new_blob); tree['offsets'] = new_off; tree['compressedLengths'] = new_c; tree['decompressedLengths'] = new_d
target.save_typetree(tree)
data = target.assets_file.save()
open(sys.argv[2], 'wb').write(data)
print('saved', len(data))
