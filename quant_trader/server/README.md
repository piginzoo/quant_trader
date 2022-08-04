# 概述 

创立一个web服务，可以让客户端，做好了策略后，可以push上来。
这样第二天开盘，就可以根据push上来的动作进行操作了，比如是买入、还是卖出。
同时还提供了查询仓位、查询头寸的接口。
同时为了方便测试，还提供了即时买、即时卖的接口。
为了安全，设置了一个token，防止任何人都触发买卖。

当收到买卖的命令，会保存这个请求到服务器的数据库（目前用的是sqlite） 


# 可以通过以下命令测试：

## 测试查询头寸

curl -X POST http://127.0.0.1:8888/api?token=your_token \
-H 'Content-Type: application/json' \
-d '{"action":"balance"}'

## 测试查询仓位

curl -X POST http://127.0.0.1:8888/api?token=your_token \
-H 'Content-Type: application/json' \
-d '{"action":"position"}'

## 查询今日委托单

curl -X POST http://127.0.0.1:8888/api?token=your_token \
-H 'Content-Type: application/json' \
-d '{"action":"today_entrusts"}'

## 查询今日成交单

curl -X POST http://127.0.0.1:8888/api?token=your_token \
-H 'Content-Type: application/json' \
-d '{"action":"today_trades"}'


## 测试买申请：

curl -X POST http://127.0.0.1:8888/api?token=your_token \
-H 'Content-Type: application/json' \
-d '{"action":"buy","code":"600001.SH","share":100,"date":"20220612"}'

## 测试卖申请：

curl -X POST http://127.0.0.1:8888/api?token=your_token \
-H 'Content-Type: application/json' \
-d '{"action":"sell","code":"600001.SH","share":100,"date":"20220612"}'

## 测试立刻买

curl -X POST http://127.0.0.1:8888/api?token=your_token \
-H 'Content-Type: application/json' \
-d '{"action":"buy_now","code":"600002.SH","share":100}'

## 测试立刻卖

curl -X POST http://127.0.0.1:8888/api?token=your_token \
-H 'Content-Type: application/json' \
-d '{"action":"sell_now","code":"600002.SH","share":100}'

## 测试立刻撤单

curl -X POST http://127.0.0.1:8888/api?token=your_token \
-H 'Content-Type: application/json' \
-d '{"action":"cancel","entrust_no":2886312418}'
