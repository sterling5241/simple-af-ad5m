import sys,re
from elftools.elf.elffile import ELFFile
from capstone import *
path=sys.argv[1]; want=sys.argv[2]
e=ELFFile(open(path,'rb'))
plt={}
sym=[(s['st_value'],s['st_size'],s.name) for s in e.get_section_by_name('.symtab').iter_symbols() if s['st_info']['type']=='STT_FUNC']
byaddr={a:n for a,_,n in sym}
md=Cs(CS_ARCH_MIPS, CS_MODE_MIPS32+CS_MODE_LITTLE_ENDIAN)
def rd(addr,n=80):
    for sec in e.iter_sections():
        if sec['sh_addr'] and sec['sh_addr']<=addr<sec['sh_addr']+sec['sh_size'] and sec['sh_type']!='SHT_NOBITS':
            d=sec.data()[addr-sec['sh_addr']:addr-sec['sh_addr']+n]; return d.split(b'\0')[0].decode('latin1')
for a,sz,n in sym:
    if n==want and sz:
        sec=e.get_section_by_name('.text'); off=a-sec['sh_addr']
        hi={}
        for i in md.disasm(sec.data()[off:off+sz],a):
            if i.mnemonic=='lui':
                r,v=[x.strip() for x in i.op_str.split(',')]; hi[r]=int(v,0)<<16
            m=re.match(r'(\$\w+), (\$\w+), (-?0x[0-9a-f]+|-?\d+)$',i.op_str)
            if i.mnemonic in('addiu','ori') and m and m.group(2) in hi:
                s=rd((hi[m.group(2)]+int(m.group(3),0))&0xffffffff)
                if s and len(s)>2 and all(32<=ord(c)<127 or c in '\n' for c in s): print('   %08x str "%s"'%(i.address,s.replace('\n','\n')))
            if i.mnemonic in('jal','j','beqz','bnez','bne','beq','blez','bgtz') and i.mnemonic in ('jal','j'):
                t=int(i.op_str,16); print('%08x %s %s'%(i.address,i.mnemonic,byaddr.get(t,'sub_%x'%t)))
            if i.mnemonic=='addiu' and i.op_str.startswith('$a') and ', $zero,' in i.op_str: print('   %08x %s %s'%(i.address,i.mnemonic,i.op_str))
