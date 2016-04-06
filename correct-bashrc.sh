#!/bin/bash
N=1
line1=`sed -n '/case $- in/{=;q}' ~/.bashrc`
line2=`sed -n '/*i*) ;;/{=;q}' ~/.bashrc`
line3=`sed -n '/*) return;;/{=;q}' ~/.bashrc`
if [[ $line2 -eq `expr $line1 + 1` ]];then
        if [[ $line3 -eq `expr $line2 + 1` ]];then
            sed -i "$((line1)),$((line3+1)) d" ~/.bashrc
        fi
fi
