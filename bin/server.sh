#!/bin/bash
if [ "$1" = "stop" ]; then
    echo "停止 Web 服务"
    ps aux|grep quant_trader|grep -v grep|awk '{print $2}'|xargs kill -9
    exit
fi


if [ "$1" = "debug" ]; then
    echo "调试模式..."
    python -m quant_trader.server.server
    exit
fi


echo "启动服务器..."
mkdir -p logs
nohup python -m quant_trader.server.server>logs/log.txt 2>&1 &