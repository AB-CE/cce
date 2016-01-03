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

    def send_demand(self):
        for final_good in self.alpha:
            for i in range(self.num_firms):
                demand = self.alpha[final_good] / self.num_firms * self.possession("money")
                self.message(final_good, i, final_good, demand)


    def buying(self):
        for final_good in self.alpha:
            for offer in self.get_offers(final_good):
                self.accept(offer)

    def consuming(self):
        self.consume_everything()
