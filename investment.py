import abce
from abce import NotEnoughGoods, epsilon

class Investment(abce.Agent):
    def init(self, _, __):
        self.create('money', 1000000)

    def investment(self):
        for group in self.get_offers_all().values():
            for offer in group:
                self.accept(offer)
        trade_surplus = self.possession('money') - 1000000
        self.log('', {'trade_surplus': trade_surplus})
        self.take('household', 0, good='money', quantity=max(0, - trade_surplus))
        self.log('money', self.possession('money'))



