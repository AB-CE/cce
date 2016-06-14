import abce
from abce import NotEnoughGoods, epsilon

class NetExport(abce.Agent):
    def init(self, _, __):
        self.create('money', 1000000)

    def international_trade(self):
        net_income = 0
        for group in self.get_offers_all().values():
            for offer in group:
                if offer.buysell == 98:
                    self.create(offer.good, offer.quantity)
                    net_income += offer.quantity * offer.price
                else:
                    net_income -= offer.quantity * offer.price

                self.accept(offer)
        target = 1000000 - net_income
        trade_surplus = self.possession('money') - target
        self.log('', {'trade_surplus': trade_surplus})
        self.take('household', 0, good='money', quantity=max(0, - trade_surplus))
        self.give('household', 0, good='money', quantity=max(0, trade_surplus))
        self.log('money', self.possession('money'))



