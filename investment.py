from __future__ import division
import abce
from abce.tools import NotEnoughGoods, epsilon
from pprint import pprint
from sys import float_info
from collections import defaultdict

class Investment(abce.Agent, abce.Household):
    def init(self, simulation_parameters, _):
        self.num_firms = num_firms = simulation_parameters['num_firms']
        self.alpha = simulation_parameters['consumption_functions']['inv']
        self.create('money', 0 )
        self.set_cobb_douglas_utility_function(self.alpha)
        self.price = 1

    def send_demand(self):
        for final_good in self.alpha:
            for i in range(self.num_firms):
                demand = self.alpha[final_good] / self.num_firms * self.possession("money")
                self.message(final_good, i, final_good, demand)


    def selling(self):
        """ receive demand from neighbors and consumer;
            calculate market_clearing_price, adapted the price slowly
            and sell the good to the neighbors, the quantity might
            be rationed.
        """
        messages = self.get_messages_all()
        for capital_type, ct_messages in messages.iteritems():
            nominal_demand = [msg.content for msg in ct_messages]
            if self.possession(capital_type) <= 0:
                continue
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
                self.sell(receiver_group=msg.sender_group,
                          receiver_idn=msg.sender_idn,
                          good=capital_type,
                          quantity=msg.content / price * rationing,
                          price=price)


    def buying(self):
        for final_good in self.alpha:
            for offer in self.get_offers(final_good):
                self.accept(offer)

    def consuming(self):
        self.consume_everything()

