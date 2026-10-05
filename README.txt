AD5M PROJECT - INDEX
========================
Everything below is real, SSH/local-file-confirmed fact unless marked
otherwise. See other.txt for ground rules (what's pre-authorized vs.
needs asking) before running anything against the live printer.

start here
------------
SUMMARY.txt - ONE-PAGE current state of knowledge (start here; supersedes older notes
              where they disagree)
other.txt   - project goal, printer access/SSH details, repo context,
              ground rules (READ THIS FIRST if you're new to this project)
plan.txt    - open items / next steps, what's resolved vs. still unknown

software/boot/  - the Linux host system: SoC, OS, rooting, A/B update
                  mechanism, bootloader
  hardware.txt      - host SoC (Ingenic X2600), eMMC identity, the
                       AD5X/AD5M/FF5M naming gotcha
  rooting.txt       - why SSH needs no exploit, the real unauthenticated
                       USB-autorun update-injection mechanism
  ab-slots.txt      - the A/B kernel+rootfs partition scheme, the "ota"
                       pointer, real uImage/squashfs container formats
  ota-system.txt    - the complete real on-device OTA toolkit
                       (/usr/prog/etc/ota_bin/): manifest format, write
                       primitive, slot-switch logic, no signing check,
                       the versioned-directory+run.sh+flag-file
                       deployment convention shared by every subsystem,
                       and the separate "recovery" (rescue OS) mechanism
                       that reuses the same A/B slots
  bootloader-spl.txt - the first-stage bootloader search - genuinely
                       blocked, needs physical hardware access
  rootfs-and-boot-chain.txt - the unpacked rootfs, the complete boot chain
                       (init -> app_startup.sh -> firmwareExe -> Klipper), vendor
                       kernel modules with pins, hazards, what a replacement
                       host OS must provide (extracted/rootfs holds the files)

software/boards/  - the 4 known MCU sub-boards, one folder each
  main/chip.txt   - mainboard MCU: Nations N32G455 (512 KiB flash, decoded
                    from DBGMCU_IDCODE), NationsCommand tool, the real
                    outage + safe recovery pattern found
  eboard/chip.txt - toolhead MCU: N32G455 with 256 KiB flash (read live),
                    app at 0x08010000 above a small custom serial
                    bootloader (NOT CanBoot - see its corrections),
                    IAPCommand tool, the second outage; chip ID via the
                    safe dump_mcu.py method
  eboard/bootloader.txt - the eboard's ~9 KiB custom serial bootloader,
                    fully disassembled: XMODEM-CRC-style protocol, 'C' erases
                    160 KiB of app, 'A' (0x41) starts the app after every
                    cold boot, the 0x1234 magic, stock checkEboard tool
  flash-layout.txt - where each MCU's firmware sits in flash (mainboard app
                    at 0x08000000, no flash bootloader; eboard app at
                    0x08010000 above a ~9 KiB custom bootloader), option
                    bytes (read protection L0), and the LIVE READBACK
                    showing both boards run the STOCK firmware
  boot-entry-and-gpio.txt - how the MCUs enter/leave bootloader mode:
                    NationsCommand's two host GPIOs (49 reset pulse, 50
                    BOOT0) decoded by disassembly, the Nations manual's
                    BOOT0/DBG_ID sections, why the mainboard outage
                    happened, the CORRECTION that IAPCommand never touches
                    a GPIO, and the eboard's serial bootloader request
  prior-art.txt   - third-party MCU findings from a web search (g992's AD5M
                    research repo/issues, Klipper forum) - a DIFFERENT
                    board revision (Allwinner host), read the caveats
  ifs/chip.txt    - a 4th board, fully resolved via safe offline
                    binary analysis + read-only live inspection: a
                    real 4-channel filament feed/switch system
                    (FlashForge's AMS-equivalent), with a complete
                    real Klipper extra (zmod_ifs.py) - inactive on
                    this specific printer's config, never queried
                    live, no outage on this one

references/  - third-party source material saved locally (not printer
               files): Nations' N32G45x user manual (816 pp) and BOOT-
               interface guide (PDF + text), g992's AD5M printer.base.cfg
               and repo file list, xblax's Klipper-mod MCU scripts.
               Summarised in software/boards/prior-art.txt and
               software/boards/boot-entry-and-gpio.txt.

firmware-recon/analysis/  - the capstone/pyelftools scripts used to
               disassemble NationsCommand/IAPCommand (see its README.txt)

software/klipper/  - the Klipper/Moonraker application layer
  pins.txt        - complete real GPIO/pin mapping, both MCUs
  load-cell.txt   - the Z-probe vs. weight-telemetry vs. staged
                    Kalico-style load-cell-probe story (3 separate things)
  moonraker.txt   - real process paths, log paths, host software stack

software/factory-packages/  - real official FlashForge packages obtained
                               and picked apart, offline, locally
  factory-reset.txt - AD5X-factory.tar.xz + its installer: a full
                      destructive reprovisioning mechanism
  main-update.txt   - the decrypted real OS update package: encryption
                      key, master orchestrator script, real kernel/
                      rootfs/control images now held locally

extracted/  - the actual extracted/decrypted files themselves (not
              documentation - the real binaries/scripts referenced
              throughout the .txt files above)
  factory-tgz/    - the small factory installer bundle, extracted
  factory-full/   - the full 798MB pristine factory /usr/prog+/usr/data
                    snapshot, extracted
  main-update/    - the decrypted OS update package + its sub-packages,
                    extracted
  rootfs/         - the unpacked rootfs squashfs (470 files; symlinks in
                    _manifest.txt), identical to what the printer runs

firmware-recon/live-flash-dumps/ - flash/option-byte/ID contents READ FROM THE
                    RUNNING MCUs (read-only): eboard 64 KiB bootloader
                    region, both apps, option bytes, DBG_ID. Its README.txt
                    has the md5s. Shows the chips run the STOCK firmware.

firmware-recon/  - MCU firmware binaries pulled directly off the live
                    printer early in the project (Mainboard.bin,
                    Eboard.hex, NationsCommand, IAPCommand). Eboard.bin
                    is confirmed byte-identical to Eboard.hex decoded
                    from Intel HEX to raw binary (an intermediate file
                    from this project's own analysis, nothing separate).
                    c_helper.so is confirmed as Klipper's own compiled
                    chelper library (real stepcompress/itersolve/trapq
                    symbols) - not MCU firmware, host-side motion-
                    planning math.
