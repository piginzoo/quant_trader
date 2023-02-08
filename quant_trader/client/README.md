这个模块，用于向服务器通讯：
1、推送买入信号
```shell
curl -X POST http://127.0.0.1:8888/api\?token\=your_token \
-H 'Content-Type: application/json' \
-d '{"action":"buy","code":"600115","share":<仓位折算出来的股份数>,"date":<当天日期>}'
```

2、推送卖出信号
```shell
curl -X POST http://127.0.0.1:8888/api\?token\=your_token \
-H 'Content-Type: application/json' \
-d '{"action":"buy","code":"600115","share":<仓位折算出来的股份数>,"date":<当天日期>}'
```

推送后，得到一个确认成功信息就好，要生成微信机器人消息。