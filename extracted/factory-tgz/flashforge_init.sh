#!/bin/sh

set -xe

# workdir contains our update files
WORK_DIR=`dirname $0`
MACHINE=$1
PID=$2

zreboot() {
  sync
  echo 1 > /proc/sys/kernel/sysrq
  sync
  echo b > /proc/sysrq-trigger || echo "error sysrq-trigger"
  sync
}

# error handling
error_handler() {
  xzcat $WORK_DIR/img/factory-error.raw.xz > /dev/fb0
  sync
  # always exit without error, to prevent immediate boot of flashforge software
  sleep 30
  zreboot
  exit 0
}

init_patch() {
    echo "Installing factory..."

    xzcat $WORK_DIR/img/factory-install.raw.xz > /dev/fb0

    for i in 1 2 3 4; do
        if [ ! -e /dev/sda$i ]; then
            echo "sda$i not exist"
            if [ ! -e /dev/sda ]; then
                continue
            else
                echo "find /dev/sda. start mount."
                mount -t vfat -o,codepage=936,iocharset=utf8 /dev/sda /mnt || echo "Error mount 1"
            fi
        else
            mount -t vfat -o,codepage=936,iocharset=utf8 /dev/sda$i /mnt || echo "Error mount 2"
        fi
    done

    trap '[ $? -eq 0 ] && exit 0 || error_handler' EXIT
}

install_prepare()
{
    cd $WORK_DIR

    echo "Test Machine"
    # safety check, only install on supported printer
    if ([ "$MACHINE" != "AD5X" ]) || \
       ([ "$PID" != "0026" ]) || \
        [ "$(uname -m)" != "mips" ]
     then
        echo "Update file does not match machine type."
        xzcat $WORK_DIR/img/factory-error.raw.xz > /dev/fb0
        exit 0
    fi
}

install_factory()
{
    echo "Install factory"
    mount
    ps
    if mount |grep zmod; then
        echo "Mod launched. Installation is prohibited."
        exit 1
    fi

    df || echo "df not ok"
    mount || echo "mount not ok"
    /sbin/fdisk -l /dev/mmcblk0 || echo "fdisk not ok"

    # check free space, we require 512MB before installation for saftey reasons
    FREE_SPACE=$(df /usr/data | tail -1 | tr -s ' ' | cut -d' ' -f4)
    MIN_SPACE="819200"
    if [ "$FREE_SPACE" -lt "$MIN_SPACE" ]
    then
        echo "Not enough free space on data partition. 800MB required!";
        xzcat $WORK_DIR/img/factory-nospace.raw.xz > /dev/fb0
        exit 0
    fi

    if ! [ -f /mnt/AD5X-factory.tar.xz ]; then 
        xzcat $WORK_DIR/img/factory-notfound.raw.xz > /dev/fb0
        exit 0
    fi

    xzcat $WORK_DIR/img/factory-copy.raw.xz > /dev/fb0
    cp /mnt/AD5X-factory.tar.xz /usr/data/AD5X-factory.tar.xz

    xzcat $WORK_DIR/img/factory-check.raw.xz > /dev/fb0
    if ! md5sum -c md5.txt; then
        xzcat $WORK_DIR/img/factory-md5.raw.xz > /dev/fb0
        exit 0
    fi

    SERIAL=""
    if [ -f "/usr/prog/config/Adventurer5M.json" ]; then
        SERIAL=$(cat /usr/prog/config/Adventurer5M.json | grep "printerSerialNumber" | cut -d '"' -f4)
    fi

    rm -f /usr/prog/logo.jpeg || echo ok
    rm -rf /usr/prog/etc/ || echo ok
    rm -rf /usr/prog/PROGRAM/ || echo ok
    rm  -f /usr/data/logs/* || echo ok
    rm -rf /usr/data/config/mod_data || echo ok
    rm -rf /usr/data/config/mod || echo ok
    rm -rf /usr/data/.mod/ || echo ok

    xzcat $WORK_DIR/img/factory-extract.raw.xz > /dev/fb0
    xz -dc /usr/data/AD5X-factory.tar.xz | tar -xf - -C /
    rm -f /usr/data/AD5X-factory.tar.xz

    if [ "${SERIAL}" != "" ]; then
        sed -i "s/SNMQQE9100319/${SERIAL}/" /usr/prog/config/Adventurer5M.json
    fi

    xzcat $WORK_DIR/img/factory-config.raw.xz > /dev/fb0
    if [ -f /mnt/config.tar ]; then
        cp /mnt/config.tar /usr/data/config.tar
        tar -xf /usr/data/config.tar -C /
        rm -f /usr/data/config.tar
    fi

    sync
}
#--------------------------------------------------

install_setup()
{
    echo "Install factory!"
    install_prepare
    install_factory
    sync
    sleep 10
    sync
    echo "Factory was installed sucessfully!"
    sync
    if grep "^/dev/sd[ab12]* /mnt " /proc/mounts
        then
          rm -f /mnt/AD5X-factory*.tgz
          sync
          sleep 10
          xzcat $WORK_DIR/img/factory-complete.raw.xz > /dev/fb0
          zreboot
          exit 0
        else
          xzcat $WORK_DIR/img/factory-complete.raw.xz > /dev/fb0
    fi
}

init_patch &> /usr/data/factory_install.log
install_setup &> /mnt/factory_install.log

sync
sleep 30
zreboot
exit 0
