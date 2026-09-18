import sys
from elftools.elf.elffile import ELFFile
from capstone import *
path=sys.argv[1]; wants=sys.argv[2:]
e=ELFFile(open(path,'rb'))
sym=[(s['st_value'],s['st_size'],s.name) for s in e.get_section_by_name('.symtab').iter_symbols() if s['st_info']['type']=='STT_FUNC' and s['st_size']>0]
byaddr={a:n for a,_,n in sym}
def fname(x):
    for a,sz,n in sym:
        if a<=x<a+sz: return n
    return '?'
md=Cs(CS_ARCH_MIPS, CS_MODE_MIPS32+CS_MODE_LITTLE_ENDIAN)
sec=e.get_section_by_name('.text')
tg={a:n for a,n in byaddr.items() if any(w in n for w in wants)}
for i in md.disasm(sec.data(),sec['sh_addr']):
    if i.mnemonic in('jal','j'):
        try: t=int(i.op_str,16)
        except: continue
        if t in tg and fname(i.address)!=tg[t]: print('%08x %-4s %s   (in %s)'%(i.address,i.mnemonic,tg[t],fname(i.address)))
