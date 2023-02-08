TRADE_STATUS_FAIL = 'fail'
TRADE_STATUS_DONE = 'done'
TRADE_STATUS_DELETE = 'delete'

TRADE_QUERY="query"# 查看库的买卖单
TRADE_DELETE="delete" # 删除买卖单（从库里删除）
TRADE_BUY = "buy" # 触发买单（只写入库，等待调度第二天开盘买）
TRADE_SELL = "sell"
TRADE_BUY_NOW = "buy_now" # 立刻买
TRADE_SELL_NOW = "sell_now"
TRADE_BALANCE = "balance" # 查看资金
TRADE_TODAY_TRADES = "today_trades" # 查看当日成交
TRADE_TODAY_ENTRUSTS = "today_entrusts" # 查看当日委托
TRADE_TRUE_POSITION = "true_position" # 查看真实持仓
TRADE_POSITION = "position" # 查看持仓
TRADE_CANCEL = "cancel" # 取消订单
HEARTBEAT = "heartbeat" # 心跳💓

UNKNOWN = 'Unknown'