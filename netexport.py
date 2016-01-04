import abce
from abce.tools import NotEnoughGoods, epsilon

class NetExport(abce.Agent):
    def init(self, _, __):
        self.create('money', 1000000)

    def international_trade(self):
        money_before = self.possession('money')
        for group in self.get_offers_all().values():
            for offer in group:
                if offer['buysell'] == 'b':
                    self.create(offer['good'], offer['quantity'])
                self.accept(offer)
        trade_surplus = self.possession('money') - money_before
        self.log('', {'trade_surplus': trade_surplus})
        self.take('household', 0, good='money', quantity=max(0, - trade_surplus))
        self.give('household', 0, good='money', quantity=max(0, trade_surplus))
        self.log('money', self.possession('money'))



