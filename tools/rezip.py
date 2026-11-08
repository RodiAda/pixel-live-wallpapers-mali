import zipfile, sys, os
src, dst = sys.argv[1], sys.argv[2]
repl = {}
for a in sys.argv[3:]:
    name, path = a.split('=', 1); repl[name] = path
done = set()
with zipfile.ZipFile(src) as zi, zipfile.ZipFile(dst, 'w') as zo:
    for info in zi.infolist():
        n = info.filename
        if n.startswith('META-INF/') and n.rsplit('.', 1)[-1].upper() in ('SF', 'RSA', 'DSA', 'EC', 'MF'):
            continue
        data = open(repl[n], 'rb').read() if n in repl else zi.read(n)
        if n in repl: done.add(n)
        ni = zipfile.ZipInfo(n, date_time=info.date_time); ni.compress_type = info.compress_type; ni.external_attr = info.external_attr
        zo.writestr(ni, data)
missing = set(repl) - done
if missing: sys.exit('missing: %s' % missing)
