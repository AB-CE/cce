from __future__ import division
import abce
from abce.tools import NotEnoughGoods, epsilon
from pprint import pprint
from sys import float_info


class Household(abce.Agent, abce.Household):
    def init(self, simulation_parameters, _):
        self.num_firms = num_firms = simulation_parameters['num_firms']
        self.wage_stickiness = simulation_parameters['wage_stickiness']


        self.create('money', simulation_parameters['endowment_FFcap']
                             + simulation_parameters['endowment_FFlab'])
        self.utility = 0

        self.capital_types = simulation_parameters['capital_types']
        self.final_goods = simulation_parameters['final_goods']
        self.alpha = simulation_parameters['hh']
        self.create('endowment_FFcap', simulation_parameters['endowment_FFcap'])
        self.create('endowment_FFlab', simulation_parameters['endowment_FFlab'])

        self.set_cobb_douglas_utility_function(self.alpha)

    def send_demand(self):
        for i in range(self.num_firms):
            for final_good in self.final_goods:
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
            market_clearing_price = sum(nominal_demand) / self.possession(capital_type)
            if self.round > 5:
                self.price = price = (1 - self.wage_stickiness) * market_clearing_price + self.wage_stickiness * self.price
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
        for final_good in self.final_goods:
            for offer in self.get_offers(final_good):
                self.accept(offer)

    def consuming(self):
        self.utility = self.consume_everything()
