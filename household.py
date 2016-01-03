from __future__ import division
import abce
from abce.tools import NotEnoughGoods, epsilon
from pprint import pprint
from sys import float_info
from collections import defaultdict

class Household(abce.Agent, abce.Household):
    def init(self, simulation_parameters, _):
        self.num_firms = num_firms = simulation_parameters['num_firms']
        self.wage_stickiness = simulation_parameters['wage_stickiness']
        self.investment_share = simulation_parameters['investment_share']
        self.import_goods = defaultdict(float)
        self.import_goods.update({good: - value for good, value in simulation_parameters['net_export'].iteritems() if value < 0})

        self.create('money', simulation_parameters['endowment_FFcap']
                             + simulation_parameters['endowment_FFlab'])
        self.utility = 0

        self.final_goods = simulation_parameters['final_goods']
        self.alpha = simulation_parameters['consumption_functions']['hoh']
        self.create('endowment_FFcap', simulation_parameters['endowment_FFcap'])
        self.create('endowment_FFlab', simulation_parameters['endowment_FFlab'])

        self.set_cobb_douglas_utility_function(self.alpha)
        self.sells = []

    def send_demand(self):
        for good, demand in self.import_goods.iteritems():
            if demand > 0:
                self.message('netexport', 0, good, demand)

        for final_good in self.final_goods:
            for i in range(self.num_firms):
                demand = (self.alpha[final_good] / self.num_firms * ( self.possession("money") * (1 - self.investment_share))
                          - self.import_goods[final_good] / self.num_firms)
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
                sell = self.sell(receiver_group=msg.sender_group,
                                 receiver_idn=msg.sender_idn,
                                 good=capital_type,
                                 quantity=msg.content / price * rationing,
                                 price=price)
                self.sells.append(sell)


    def buying(self):
        for final_good in self.final_goods:
            for offer in self.get_offers(final_good):
                self.accept(offer)

    def investing(self):
        self.sales_earning = sum([sell['final_quantity'] for sell in self.sells])
        self.sells = []
        tax_return = self.get_messages('tax_return')[0].content
        quantity = self.investment_share * (self.sales_earning + tax_return)
        self.give('investment', 0, good='money', quantity=quantity)
        self.investment = quantity

    def consuming(self):
        self.utility = self.consume_everything()
