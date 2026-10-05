Offline disassembly helpers used on 2026-09-18 for NationsCommand and IAPCommand
(MIPS32 little-endian ELFs in ../). Need: Python 3, capstone, pyelftools.
Run from firmware-recon/:   python analysis/<script>.py <ELF> [args]
  find_gpio.py   <ELF>                 list gpio-ish functions + every call site of them (with 8 insns of context)
  dump_func.py   <ELF> <name-substr>.. full disassembly of matching functions, string operands annotated
  callers.py     <ELF> <name-substr>.. who calls the named functions (jal/j only - function-pointer calls are NOT seen)
  calls.py       <ELF> <func>          call list + string literals + small immediates for one function (e.g. main)
  thumb_dis.py   <bin> <base_hex> [end_off_hex]   annotated Thumb disassembly of a small Cortex-M image
                 (literal-pool values, peripheral names); eb_boot.dis.txt is its output for
                 live-flash-dumps/eb_boot.bin (base 0x08000000, end 0x2490)
Results and interpretation: software/boards/boot-entry-and-gpio.txt,
software/boards/eboard/bootloader.txt
Limits: static analysis only; nothing was run. Indirect calls (function pointers, PLT) are not followed.
