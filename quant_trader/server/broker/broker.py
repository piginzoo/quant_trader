class Broker():

    def balance(self):
        pass

    def buy(self, code, share):
        pass

    def sell(self, code, share):
        pass

    def position(self):
        """
        返回：
        list<code,buy_date,share,price>
        """
        pass

    def cancel_all(self):
        """
        撤单(所有)
        """
        pass

    def cancel(self, entrust_no):
        """
        撤单,entrust_no: 委托单号
        """
        pass


    def today_entrusts(self):
        """查询当日委托情况"""
        pass

    def today_trades(self):
        """查询当日成交情况"""
        pass