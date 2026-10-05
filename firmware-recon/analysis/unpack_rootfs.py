# Unpack the update package's rootfs squashfs (LZO) without native lzo. Usage: unpack_rootfs.py <image> <outdir>
import sys, os, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))   # picks up ./lzo.py
from PySquashfsImage import SquashFsImage
img, out = sys.argv[1], sys.argv[2]
im = SquashFsImage.from_file(img)
os.makedirs(out, exist_ok=True)
manifest = []
nfile = 0
for i in im:
    rel = i.path.lstrip('/')
    dest = os.path.join(out, rel)
    if i.is_dir:
        os.makedirs(dest, exist_ok=True); continue
    os.makedirs(os.path.dirname(dest) or out, exist_ok=True)
    if i.is_symlink:
        manifest.append('L %s -> %s' % (i.path, i.readlink())); continue
    if i.is_file:
        with open(dest, 'wb') as f: f.write(i.read_bytes()); 
        nfile += 1
        manifest.append('F %o %d %s' % (i.mode & 0o7777, i.size, i.path))
    else:
        manifest.append('O %o %s' % (i.mode, i.path))   # device nodes, fifos, sockets
open(os.path.join(out, '_manifest.txt'), 'w').write('\n'.join(manifest) + '\n')
print('extracted %d files; manifest entries %d' % (nfile, len(manifest)))
