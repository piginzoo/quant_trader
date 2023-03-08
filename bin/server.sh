#!/bin/bash

# 还是经常OOM，每晚凌晨1点重启服务，crontab -e
# 0 1 * * * /home/ubuntu/workspace/quant_trader/bin/server.sh restart

# 获得脚本所在路径
HOME_DIR=`dirname $0`

if [ "$1" = "stop" ]; then
    cd "$HOME_DIR/.."
    echo "停止 Web 服务"
    pkill -9  -f 'quant_trader.server.server'
    exit
fi

if [ "$1" = "restart" ]; then
    cd "$HOME_DIR/.."
    echo "重启服务：停止 Web 服务"
    pkill -9  -f 'quant_trader.server.server'
    sleep 3
    echo "重启服务：启动 Web 服务"
    mkdir -p logs
    nohup python -m quant_trader.server.server>logs/log.txt 2>&1 &
    exit
fi

if [ "$1" = "debug" ]; then
    cd "$HOME_DIR/.."
    echo "调试模式..."
    python -m quant_trader.server.server
    exit
fi


echo "启动服务器..."
# 进入主目录
cd "$HOME_DIR/.."
mkdir -p logs
nohup python -m quant_trader.server.server>logs/log.txt 2>&1 &