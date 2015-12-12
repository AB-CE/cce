from __future__ import division
from firm import Firm
from household import Household
from abce import Simulation, read_parameters, repeat
from random import shuffle, randrange
import sys
from collections import OrderedDict
from graphs import graph
import abceweb
import os


def main():
        simulation_parameters = {'name': 'cce',
                                 'random_seed': None,
                                 'num_rounds': 200,
                                 'trade_logging': 'off',
                                 'num_household': 1,
                                 'num_firms': 2,
                                 'final_goods': OrderedDict(enumerate(['brd', 'mlk'])),
                                 'capital_types': OrderedDict(enumerate(['cap', 'lab'])),
                                 'wage_stickiness': 0,
                                 'price_stickiness': 0,
                                 'dividends_percent': 0,
                                 'network_weight_stickiness': 0}

        s = Simulation(simulation_parameters)
        action_list = [
            (('firm', 'household'), 'send_demand'),
            (('firm', 'household'), 'selling'),
            (('firm', 'household'), 'buying'),
            ('firm', 'production'),
            ('firm', 'dividends'),
            ('household', 'consuming'),
            ('firm', 'change_weights'),
            ('firm', 'stats'),
            (('household', 'firm'), 'aggregate'),
            (('firm'), 'panel')
            ]
        s.add_action_list(action_list)

        s.declare_service('endowment_FFcap', 1 , 'cap')
        s.declare_service('endowment_FFlab', 1 , 'lab')

        s.panel('firm', variables=['price', 'nominal_demand'])

        s.aggregate('firm',
                    possessions=['money'],
                    variables=['produced', 'profit', 'price', 'dead', 'inventory', 'rationing'])  # , 'change_business_partner', 'profit_down', 'profit'])
        s.aggregate('household',
                    possessions=['money'],
                    variables=['utility', 'rationing'])

        s.build_agents(Firm, simulation_parameters['num_firms'])
        s.build_agents(Household, simulation_parameters['num_household'])

        s.run()
        os.chdir('../..')
        abceweb.run(open=False)


if __name__ == '__main__':
    main()
