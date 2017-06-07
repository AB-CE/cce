import abce
from abce import NotEnoughGoods


class NetExport(abce.Agent):
    def init(self, _, __):
        self.create('money', 0)

    #
        # net export gets the remain money of the household

    def invest(self):
        """ see firms international_trade function """
        offers_grouped = self.get_offers_all().values()
        offers = []
        for os in offers_grouped:
            offers.extend(os)
        # demand are all buy offers
        demand = sum([offer.quantity * offer.price for offer in offers if offer.sell])
        if demand < self.possession('money'):
            self.rationing = rationing = 1
        else:
            self.rationing = rationing = self.possession('money') / demand

        self.log('netexport rationing', rationing)

        for offer in offers:
            if not offer.sell:
                self.create(offer.good, offer.quantity)
                self.accept(offer)
            else:
                self.accept(offer, offer.quantity * rationing)

        self.give(('household', 0), quantity=self.possession('money'), good='money')


