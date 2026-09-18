#!/bin/sh

# Author:		chenhe
# Description:	单个固件包升级程序
# Date:			2022-01-21

set -x

WORK_DIR=`dirname $0`

#检测机器的架构,错误马上退出
CHECH_ARCH=`uname -m`
if [ "${CHECH_ARCH}" != "mips" ];then
    echo "Machine architecture error."
    echo ${CHECH_ARCH}
    exit 1
fi

#检测内核版本，错误马上退出
#CHECH_KERNEL=`uname -r`
#if [ "${CHECH_KERNEL}" != "5.6.0-svn539" ];then
#    echo "Kernel version error."
#    echo ${CHECH_KERNEL}
#    exit 1
#fi

# cp -vf /tmp/test /usr/data/
# $1  源文件路径名 /tmp/test
# $2  目标路径名   /usr/data/
cp_file()
{
	SRCFILE="$1"
	DSTFILE="$2`basename $1`"
	if [ ! -f $DSTFILE ];then
		cp -vf ${SRCFILE} $2
		chmod a+x $DSTFILE
	fi
	SRCFILEMD5=`md5sum $SRCFILE | cut -d ' ' -f 1`
	DSTFILEMD5=`md5sum $DSTFILE | cut -d ' ' -f 1`
	while [ "$SRCFILEMD5" != "$DSTFILEMD5" ];
	do
		rm -rf ${DSTFILE}
		cp -vf ${SRCFILE} $2
		chmod a+x $DSTFILE
		sync
		DSTFILEMD5=`md5sum $DSTFILE | cut -d ' ' -f 1`
	done
	#echo ${SRCFILEMD5}
	#echo ${DSTFILEMD5}
}

LOG_FILE="/usr/data/logs/kernel_update.log"
if [ -f $LOG_FILE ];then
	rm $LOG_FILE
	touch $LOG_FILE
fi

# 版本比较函数：判断版本号是否大于等于2.0.0
# 输入：待判断的版本号（如 2.0.0、1.9.9、3.1.0）
# 输出：0（≥2.0.0）/1（<2.0.0）
version_ge_200() {
    input_ver=$1
    # 拆分版本号为主/次/修订号（处理 x.y.z 格式）
    main_ver=$(echo "$input_ver" | cut -d'.' -f1)
    sub_ver=$(echo "$input_ver" | cut -d'.' -f2)
    rev_ver=$(echo "$input_ver" | cut -d'.' -f3)

    # 补全缺失的版本段（如 2 → 2.0.0，2.1 → 2.1.0）
    [ -z "$sub_ver" ] && sub_ver=0
    [ -z "$rev_ver" ] && rev_ver=0

    # 版本比较逻辑：≥2.0.0
    if [ "$main_ver" -gt 2 ] || 
	    ([ "$main_ver" -eq 2 ] && [ "$sub_ver" -gt 0 ]) || 
	    ([ "$main_ver" -eq 2 ] && [ "$sub_ver" -eq 0 ] && [ "$rev_ver" -ge 0 ]); then
        return 0
    else
        return 1
    fi
}

INPUT_VERSION=$1
# 读取SD类型和设备类型
sd_type=$(cat /sys/block/mmcblk0/device/type)
dev_type=$(cat /proc/cmdline | awk -F'dev_type=' '{split($2,a," "); print a[1]}')

if [ "$sd_type" = "SD" ] && [ "$dev_type" = "SDNAND" ]; then
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] 验证通过 - SD类型: $sd_type, 设备类型: $dev_type" >> $LOG_FILE
    if version_ge_200 "$INPUT_VERSION"; then
        if [ -f $WORK_DIR/local_ota_update.sh ]; then
        echo "update local_ota_update.sh kernel" >> $LOG_FILE
        $WORK_DIR/local_ota_update.sh $WORK_DIR/ota_kernel_sd/
    	fi
    fi
else
    if [ -f $WORK_DIR/local_ota_update.sh ]; then
    	echo "update local_ota_update.sh kernel"
    	$WORK_DIR/local_ota_update.sh $WORK_DIR/ota_kernel/
    fi
fi
sync

exit 0
