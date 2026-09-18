import sys,re
from elftools.elf.elffile import ELFFile
from capstone import *
path=sys.argv[1]; names=sys.argv[2:]
e=ELFFile(open(path,'rb'))
sym=[(s['st_value'],s['st_size'],s.name) for s in e.get_section_by_name('.symtab').iter_symbols() if s['st_info']['type']=='STT_FUNC' and s['st_size']>0]
byaddr={a:n for a,_,n in sym}
md=Cs(CS_ARCH_MIPS, CS_MODE_MIPS32+CS_MODE_LITTLE_ENDIAN)
def rd(addr,n=64):
    for sec in e.iter_sections():
        if sec['sh_addr'] and sec['sh_addr']<=addr<sec['sh_addr']+sec['sh_size'] and sec['sh_type']!='SHT_NOBITS':
            d=sec.data()[addr-sec['sh_addr']:addr-sec['sh_addr']+n]; return d.split(b'\0')[0].decode('latin1')
    return None
for a,sz,n in sym:
    if any(x in n for x in names):
        print('\n=== %s @%08x size %d'%(n,a,sz))
        sec=e.get_section_by_name('.text'); off=a-sec['sh_addr']
        code=sec.data()[off:off+sz]
        hi={}
        for i in md.disasm(code,a):
            note=''
            if i.mnemonic=='jal':
                t=int(i.op_str,16); note='  ; '+byaddr.get(t,'sub_%x'%t)
            if i.mnemonic=='lui': hi[i.op_str.split(',')[0].strip()]=int(i.op_str.split(',')[1].strip(),0)<<16
            m=re.match(r'(\$\w+), (\$\w+), (-?0x[0-9a-f]+|-?\d+)$',i.op_str)
            if i.mnemonic in('addiu','ori') and m and m.group(2) in hi:
                v=hi[m.group(2)]+int(m.group(3),0); s=rd(v&0xffffffff)
                if s and len(s)>1 and all(32<=ord(c)<127 or c in '\n\t' for c in s): note+='  ; "%s"'%s.replace('\n','\n')
            print('  %08x %-8s %s%s'%(i.address,i.mnemonic,i.op_str,note))
