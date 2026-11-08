import UnityPy, sys, re, lz4.block
env = UnityPy.load(sys.argv[1])
for obj in env.objects:
    if obj.type.name != 'Shader': continue
    tree = obj.read_typetree()
    name = tree.get('m_ParsedForm', {}).get('m_Name')
    if name.startswith('Hidden/') or name.startswith('Sprites/') or name.startswith('UI/'): continue
    blob = bytes(tree['compressedBlob'])
    offs, clen, dlen = tree['offsets'], tree['compressedLengths'], tree['decompressedLengths']
    hits = 0
    for pi, (o_list, c_list, d_list) in enumerate(zip(offs, clen, dlen)):
        o_list = o_list if isinstance(o_list, list) else [o_list]
        c_list = c_list if isinstance(c_list, list) else [c_list]
        d_list = d_list if isinstance(d_list, list) else [d_list]
        for o, c, d in zip(o_list, c_list, d_list):
            data = lz4.block.decompress(blob[o:o+c], uncompressed_size=d)
            for m in re.finditer(rb'#ifdef VERTEX', data):
                seg = data[m.start():m.start()+20000]
                end = seg.find(b'#endif\n#ifdef FRAGMENT')
                seg = seg[:end if end > 0 else len(seg)]
                if re.search(rb'\bbuffer\b', seg): hits += 1
    print(obj.path_id, name, 'platform_blocks', len(offs), 'vertex_ssbo_programs', hits)
