AD5M PROJECT - INDEX
========================
Everything below is real, SSH/local-file-confirmed fact unless marked
otherwise. See other.txt for ground rules (what's pre-authorized vs.
needs asking) before running anything against the live printer.

start here
------------
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

software/boards/  - the 4 known MCU sub-boards, one folder each
  main/chip.txt   - mainboard MCU: Nations N32G455 (512 KiB flash, decoded
                    from DBGMCU_IDCODE), NationsCommand tool, the real
                    outage + safe recovery pattern found
  eboard/chip.txt - toolhead MCU: real klipper3d/canboot bootloader,
                    IAPCommand tool, the second outage; chip ID via the
                    safe dump_mcu.py method (N32G455, 256 KiB inferred)
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
