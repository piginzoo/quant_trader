@echo "Server start ..."
if "%1" == "debug" goto debug

:debug
    echo "Debug mode..."
    python -m quant_trader.server.server
    goto end


echo "Startup Server ..."
mkdir -p logs
nohup python -m quant_trader.server.server  &

:end
    echo "Server shutdown"