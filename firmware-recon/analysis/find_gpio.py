import sys
from elftools.elf.elffile import ELFFile
from capstone import *
path=sys.argv[1]
f=open(path,'rb'); e=ELFFile(f)
sym=[]
for s in e.get_section_by_name('.symtab').iter_symbols():
    if s['st_info']['type']=='STT_FUNC' and s['st_size']>0: sym.append((s['st_value'],s['st_size'],s.name))
sym.sort()
byaddr={a:n for a,_,n in sym}
def fname(addr):
    for a,sz,n in sym:
        if a<=addr<a+sz: return n
    return '?'
text=e.get_section_by_name('.text')
md=Cs(CS_ARCH_MIPS, CS_MODE_MIPS32+CS_MODE_LITTLE_ENDIAN); md.detail=False
code=text.data(); base=text['sh_addr']
ins=list(md.disasm(code,base))
print(path,'text',hex(base),len(ins),'insns')
print('GPIO-ish funcs:'); 
for a,sz,n in sym:
    if 'gpio' in n.lower() or 'Gpio' in n or 'stm32' in n.lower() or 'reboot' in n.lower() or 'unexport' in n.lower(): print('  %08x %4d %s'%(a,sz,n))
targets={a for a,_,n in sym if 'gpio' in n.lower()}
idx={i.address:k for k,i in enumerate(ins)}
print('\nCALL SITES to gpio* functions:')
for k,i in enumerate(ins):
    if i.mnemonic=='jal':
        t=int(i.op_str,16)
        if t in targets:
            print('--- %08x in %s -> %s'%(i.address,fname(i.address),byaddr[t]))
            for j in ins[max(0,k-8):k+2]: print('     %08x %-8s %s'%(j.address,j.mnemonic,j.op_str))
