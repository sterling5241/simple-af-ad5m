# Annotated Thumb disassembly of a small Cortex-M image (usage: thumb_dis.py image.bin base_hex [end_off_hex])
import sys,struct,re
from capstone import *
path=sys.argv[1]; base=int(sys.argv[2],16); end=int(sys.argv[3],16) if len(sys.argv)>3 else None
b=open(path,'rb').read()
if end: b=b[:end]
md=Cs(CS_ARCH_ARM,CS_MODE_THUMB); md.skipdata=True
def word(o): return struct.unpack('<I',b[o:o+4])[0] if 0<=o<=len(b)-4 else None
names={0x40013800:'USART1',0x40013804:'USART1_DAT?',0x40022000:'FLASH',0x40021000:'RCC',0x40010800:'GPIOA',0x40010C00:'GPIOB',0xE000ED0C:'SCB_AIRCR',0x45670123:'FLASH_KEY1',0xCDEF89AB:'FLASH_KEY2',0x08010000:'APP_BASE',0xE000E100:'NVIC_ISER',0x40004400:'USART2',0x40004800:'USART3'}
out=[]
for i in md.disasm(b,base):
    off=i.address-base; note=''
    m=re.search(r'\[pc, #(-?0x[0-9a-f]+|-?\d+)\]',i.op_str)
    if i.mnemonic.startswith('ldr') and m:
        t=((i.address+4)&~3)-base+int(m.group(1),0); w=word(t)
        if w is not None: note='   ; lit@%04X = 0x%08X %s'%(t,w,names.get(w,''))
    out.append('%04X  %-8s %s%s'%(off,i.mnemonic,i.op_str,note))
print('\n'.join(out))
