#!/bin/bash
if [ $(mount -t cgroup | wc -l) == "0" ]
then 
    echo "[  FAIL  ] CGroup v1"
    exit 1
else
    echo "[   OK   ] CGroup v1"
    exit 0
fi