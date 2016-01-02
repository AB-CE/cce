from __future__ import division
import abce
from abce.tools import NotEnoughGoods, epsilon
from pprint import pprint
from sys import float_info


class NetExport(abce.Agent):
    def init(self, simulation_parameters, _):
        self.num_firms = simulation_parameters['num_firms']
        self.import_price_stickiness = simulation_parameters['import_price_stickiness']
        self.want_goods = {good: value for good, value in simulation_parameters['net_export'].iteritems() if value > 0}
        self.total_want = sum(self.want_goods.values())
        self.offer_goods = {good: - value for good, value in simulation_parameters['net_export'].iteritems() if value < 0}
        self.total_offer = sum(self.offer_goods.values())
        self.create('money', self.total_want)
        self.made_sales = []

    def send_demand(self):
        for i in range(self.num_firms):
            for good, share in self.want_goods.iteritems():
                demand = share / self.total_want * self.possession("money") / self.num_firms
                self.message(good, i, good, demand)

    def selling(self):
        """ receive demand from neighbors and consumer;
            calculate market_clearing_price, adapted the price slowly
            and sell the good to the neighbors, the quantity might
            be rationed.
        """
        for good, value in self.offer_goods.iteritems():
            self.create(good, value - self.possession(good))

        messages = self.get_messages_all()
        for capital_type, ct_messages in messages.iteritems():
            nominal_demand = [msg.content for msg in ct_messages]
            market_clearing_price = sum(nominal_demand) / self.possession(capital_type)
            if self.round > 5:
                self.price = price = (1 - self.import_price_stickiness) * market_clearing_price + self.import_price_stickiness * self.price
            else:
                self.price = price = market_clearing_price
            demand = sum([msg.content / price for msg in ct_messages])
            if demand < self.possession(capital_type):
                self.rationing = rationing = 1 - float_info.epsilon * self.num_firms
            else:
                self.rationing = rationing = self.possession(capital_type) / demand - float_info.epsilon * self.num_firms
            for msg in ct_messages:
                sale = self.sell(receiver_group=msg.sender_group,
                                 receiver_idn=msg.sender_idn,
                                 good=capital_type,
                                 quantity=msg.content / price * rationing,
                                 price=price)
                self.made_sales.append(sale)

    def buying(self):
        for final_good in self.want_goods:
            for offer in self.get_offers(final_good):
                self.accept(offer)

    def consuming(self):
        for good in self.want_goods:
            self.destroy(good, self.possession(good))

    def stats(self):
        self.sales = sum([sale['final_quantity'] for sale in self.made_sales])
        self.made_sales = []

