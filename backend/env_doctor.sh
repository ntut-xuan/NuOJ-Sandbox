#!/bin/bash
cgroup_check() {
    local cgroup=$1
    if ! test -f "/sys/fs/cgroup/$cgroup/tasks" ; then
        echo "[  FAIL  ] CGroup v1"
        exit 1
    fi
}

swap_check() {
    # If swap is disabled, there is nothing to worry about.
    local swaps
    swaps=$(swapon --noheadings)
    if [ -n "$swaps" ] ; then
        echo "[  FAIL  ] Swap"
        exit 1
    fi
}

aslr_check() {
    local val
    if val=$(cat /proc/sys/kernel/randomize_va_space 2>/dev/null) ; then
        if [ "$val" -ne 0 ] ; then
            echo "[  FAIL  ] Address Space Layout Randomization"
            exit 1
        fi
    else
        echo "[  SKIP  ] Address Space Layout Randomization"
    fi
}

thp_check() {
    local val
    if val=$(cat /sys/kernel/mm/transparent_hugepage/enabled 2>/dev/null) ; then
        case $val in
            *'[never]'*) ;;
            *)
            echo "[  FAIL  ] Transparent Hugepage Support"
            exit 1
        esac
    fi
    if val=$(cat /sys/kernel/mm/transparent_hugepage/defrag 2>/dev/null) ; then
        case $val in
            *'[never]'*) ;;
            *) 
            echo "[  FAIL  ] Transparent Hugepage Support"
            exit 1
        esac
    fi
    if val=$(cat /sys/kernel/mm/transparent_hugepage/khugepaged/defrag 2>/dev/null) ; then
        if [ "$val" -ne 0 ] ; then
            echo "[  FAIL  ] Transparent Hugepage Support"
            exit 1
        fi
    fi
}

if [ "$NUOJ_SANDBOX_ENABLE_CG" == "1" ] ; then 
    cgroup_check memory
    cgroup_check cpuacct
    cgroup_check cpuset
    echo "[   OK   ] CGroup v1"
else 
    echo "[  SKIP  ] CGroup v1"
fi

swap_check
echo "[   OK   ] Swap"

aslr_check
echo "[   OK   ] Address Space Layout Randomization"

thp_check
echo "[   OK   ] Transparent Hugepage Support"
exit 0
