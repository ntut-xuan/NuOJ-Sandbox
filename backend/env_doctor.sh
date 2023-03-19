#!/bin/bash
cgroup_check() {
    local cgroup=$1
    if ! test -f "/sys/fs/cgroup/$cgroup/tasks" ; then
        echo "[  FAIL  ] CGroup v1"
        exit 1
    fi
}

cgroup_check memory
cgroup_check cpuacct
cgroup_check cpuset

echo "[   OK   ] CGroup v1"
exit 0