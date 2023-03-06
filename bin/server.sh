#!/bin/bash
if [ "$1" = "stop" ]; then
    echo "停止 Web 服务"
    pkill -9  -f 'quant_trader.server.server'
    exit
fi

if [ "$1" = "restart" ]; then
    echo "重启服务：停止 Web 服务"
    pkill -9  -f 'quant_trader.server.server'
    sleep 1
    echo "重启服务：启动 Web 服务"
    nohup python -m quant_trader.server.server>logs/log.txt 2>&1 &
fi

if [ "$1" = "debug" ]; then
    echo "调试模式..."
    python -m quant_trader.server.server
    exit
fi


echo "启动服务器..."
mkdir -p logs
nohup python -m quant_trader.server.server>logs/log.txt 2>&1 &