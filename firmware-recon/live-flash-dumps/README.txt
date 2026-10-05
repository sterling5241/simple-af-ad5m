LIVE FLASH DUMPS - read from the running MCUs on 2026-09-18
=============================================================
Every file here was read from a RUNNING MCU with Klipper's stock
scripts/dump_mcu.py (read-only debug_read over the normal Klipper protocol,
Klipper stopped for the read and restored afterwards, printer idle, each
command approved by the user). Nothing was written to any MCU. Method and
its safety history: memory-independent write-up in software/boards/
boot-entry-and-gpio.txt and flash-layout.txt.

File            MCU / address read                       Bytes  md5
eb_boot.bin     eboard    0x08000000 .. 0x0800FFFF       65536  780d0295f4b4c7a72ba5b6387bfc8fc7
eb_app.bin      eboard    0x08010000 .. 0x08019FFF       40960  35ebd24658be0559b11366dafe123776
mb_flash.bin    mainboard 0x08000000 .. 0x08009FFF       40960  aef5031eaa60f660b74666462413787b
eb_ob.bin       eboard    0x1FFFF800 (option bytes)         20  5e9e1681e9489d1f0e1e92a3ac8d207e
mb_optbytes.bin mainboard 0x1FFFF800 (option bytes)         20  5e9e1681e9489d1f0e1e92a3ac8d207e
eb_id.bin       eboard    0xE0042000 (DBG_ID)                4  29d803d2aa62efe0f00f262ef55f9bb8
mb_idcode.bin   mainboard 0xE0042000 (DBG_ID)                4  65173b0d98066837e5e414bdc5af62f5
eb_sysmem.bin   eboard    0x1FFFF7C0 (UCID+UID block)       64  e2051e308d66ff0990dec9b59b6df1b3
mb_sysmem.bin   mainboard 0x1FFFF7C0 (UCID+UID block)       64  88fcd40e86d8f34a58701b32878f0fb8

What they are (verified by comparing against the stock 1.1.1 package):
- mb_flash.bin, trailing 0xFF trimmed (37,504 B), is BYTE-IDENTICAL to the
  stock AD5X.bin (md5 522b4641821016952cd4504e4c2177ed).
- eb_app.bin, trimmed (36,012 B), is BYTE-IDENTICAL to the data in the stock
  1.1.1 ADM_App.hex (md5 8523f0e7e2b93c9c9982b2cb3cdbbc4d).
- eb_boot.bin has never been seen anywhere else: about 9.1 KiB of code at
  0x08000000 and the rest 0xFF (see software/boards/flash-layout.txt).
- Option bytes of both boards: a5 5a ff ff ... = read protection L0.
Coverage limits: only the first 40 KiB of the mainboard's 512 KiB flash and
the first 40 KiB of the eboard's app area (0x08010000-0x08019FFF, 256 KiB
device) were read. Bytes past those ranges, System Memory (the ROM
bootloader) and RAM were not read.
