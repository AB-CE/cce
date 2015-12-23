#pylint: disable=W0201
from __future__ import division
import abce
from abce.tools import NotEnoughGoods, epsilon
import random
import numpy as np
from optimization_functions import optimization
from copy import copy
from collections import OrderedDict
from pprint import pprint


def normalized_random(length):
    random_values = [random.uniform(0.1, 0.9) for _ in range(length)]
    sum_values = sum(random_values)
    return np.array([v / sum_values for v in random_values])

class Firm(abce.Agent, abce.Firm):
    def init(self, simulation_parameters, _):
        self.num_firms = simulation_parameters['num_firms']
        self.price_stickiness = simulation_parameters['price_stickiness']
        self.dividends_percent = simulation_parameters['dividends_percent']
        self.network_weight_stickiness = simulation_parameters['network_weight_stickiness']
        self.final_goods = simulation_parameters['final_goods']
        self.capital_types = simulation_parameters['capital_types']
        production_function = simulation_parameters['production_functions'][self.group]

        self.neighbors = self.capital_types
        self.neighbors_goods = self.capital_types



        prices = normalized_random(len(self.neighbors))
        self.neighbor_prices = prices

        self.seed_weights = normalized_random(len(self.neighbors))
        self.weights = normalized_random(len(self.neighbors))

        self.create(self.group, 1)
        self.create('money', 1)
        self.money_1 = self.possession('money')

        self.price = random.uniform(0, 1)
        self.profit = 0


        if self.group == 'brd':
            self.b = production_function[0]
            self.beta = production_function[1]
        elif self.group == 'mlk':
            self.b = production_function[0]
            self.beta = production_function[1]

        self.set_cobb_douglas(self.group, self.b, self.beta)
        self.beta_list = [self.beta[capital_type] for capital_type in self.capital_types]

    def send_demand(self):
        """ send nominal demand, according to weights to neighbor """
        for neighbor, weight in zip(self.neighbors_goods, self.weights):
            self.message('household', 0,
                         neighbor,
                         weight * self.possession("money"))


    def selling(self):
        """ receive demand from neighbors and consumer;
            calculate market_clearing_price, adaped the price slowly
            and sell the good to the neighbors, the quantity might
            be rationed.
        """
        messages = self.get_messages('nominal_demand')
        nominal_demand = [msg.content for msg in messages]
        self.nominal_demand = sum(nominal_demand)
        assert self.possession(self.group) > 0
        market_clearing_price = sum(nominal_demand) / self.possession(self.group)
        self.price = (1 - self.price_stickiness) * market_clearing_price + self.price_stickiness * self.price
        demand = sum([msg.content / self.price for msg in messages])
        if demand <= self.possession(self.group):
            self.rationing = rationing = 1 - epsilon
        else:
            self.rationing = rationing = self.possession(self.group) / demand - epsilon

        for msg in messages:
            self.sell(msg.sender_group, receiver_idn=msg.sender_idn, good=self.group, quantity=msg.content / self.price * rationing, price=self.price)

    def buying(self):
        """ get offers from each neighbor, accept it and update
            neighbor_prices and neighbors_goods """
        for offers in self.get_offers_all().values():
            for offer in offers:
                self.accept(offer)
                self.neighbor_prices[self.neighbors_goods.index(offer['good'])] = offer['price']

    def production(self):
        """ produce using all goods and labor """
        input_goods = {input: self.possession(input) for input in self.beta.keys()}
        self.input_goods = copy(input_goods)
        p = self.produce(input_goods)
        self.produced = p[self.group]

    def dividends(self):
        """ pay dividends to household if profit is positive, calculate profits """
        self.profit = self.possession('money') - self.money_1
        earnings = max(0, self.profit)
        self.give('household', 0, good='money', quantity=self.dividends_percent * earnings)
        self.money_1 = self.possession('money')

    def _change_weights(self, neighbor_prices, seed_weights):
        opt = optimization(seed_weights=seed_weights,
                           input_prices=np.array(neighbor_prices),
                           b=self.b,
                           beta=self.beta_list,
                           method='SLSQP')
        if not opt.success:
            print self.round, self.name, opt.message
            seed_weights = normalized_random(len(self.neighbors))
            raise
        return opt.x

    def change_weights(self):
        self.seed_weights = optimal_weights = self._change_weights(self.neighbor_prices, self.seed_weights)
        self.weights = self.network_weight_stickiness * self.weights \
                       + (1 - self.network_weight_stickiness) * optimal_weights
        summe = np.nextafter(sum(self.weights), 2)
        self.weights = np.nextafter(self.weights / summe, 0)

    def stats(self):
        """ helper for statistics """
        if self.possession('money') > epsilon:
            self.dead = 0
        else:
            self.dead = 1
        self.inventory = self.possession(self.group)
