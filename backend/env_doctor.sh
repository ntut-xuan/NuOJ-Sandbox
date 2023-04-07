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
            echo "[  FAIL  ] ASLR"
            exit 1
        fi
    else
        echo "[  SKIP  ] ASLR"
    fi
}

thp_check() {
    local val
    if val=$(cat /sys/kernel/mm/transparent_hugepage/enabled 2>/dev/null) ; then
        case $val in
            *'[never]'*) ;;
            *)
            echo "[  FAIL  ] THP"
            exit 1
        esac
    fi
    if val=$(cat /sys/kernel/mm/transparent_hugepage/defrag 2>/dev/null) ; then
        case $val in
            *'[never]'*) ;;
            *) 
            echo "[  FAIL  ] THP"
            exit 1
        esac
    fi
    if val=$(cat /sys/kernel/mm/transparent_hugepage/khugepaged/defrag 2>/dev/null) ; then
        if [ "$val" -ne 0 ] ; then
            echo "[  FAIL  ] THP"
            exit 1
        fi
    fi
}

cgroup_check memory
cgroup_check cpuacct
cgroup_check cpuset
echo "[   OK   ] CGroup v1"

swap_check
echo "[   OK   ] Swap"

aslr_check
echo "[   OK   ] ASLR"

thp_check
echo "[   OK   ] THP"
exit 0