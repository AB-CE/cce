from __future__ import division
from firm import Firm
from household import Household
from abce import Simulation
from collections import OrderedDict
import os
from sam_to_functions import read_utility_function, read_production_functions
from pprint import pprint


def main():
    utility_function = read_utility_function('hierachical.sam.csv')
    production_functions = read_production_functions('hierachical.sam.csv',
                                                     inputs=['cap', 'lab', 'tools'],
                                                     outputs=['brd', 'mlk', 'tools'])
    simulation_parameters = {'name': 'cce',
                             'random_seed': None,
                             'num_rounds': 100,
                             'trade_logging': 'off',
                             'num_household': 1,
                             'num_firms': 10,
                             'endowment_FFcap': 30,
                             'endowment_FFlab': 30,
                             'final_goods': ['brd', 'mlk'],
                             'intermediary_goods': ['tools'],
                             'capital_types': ['cap', 'lab'],
                             'wage_stickiness': 0.5,
                             'price_stickiness': 0.5,
                             'network_weight_stickiness': 0.5,
                             'dividends_percent': 0.0,
                             'production_functions': production_functions,
                             'hh': utility_function}

    firms = simulation_parameters['final_goods'] + simulation_parameters['intermediary_goods']
    firms_and_household = firms + ['household']
    simulation = Simulation(simulation_parameters)
    action_list = [(firms_and_household, 'send_demand'),
                   (firms_and_household, 'selling'),
                   (firms_and_household, 'buying'),
                   (firms, 'production'),
                   (firms, 'dividends'),
                   ('household', 'consuming'),
                   (firms, 'change_weights'),
                   (firms, 'stats'),
                   (firms_and_household, 'aggregate')]
    simulation.add_action_list(action_list)

    simulation.declare_service('endowment_FFcap', 1, 'cap')
    simulation.declare_service('endowment_FFlab', 1, 'lab')


    simulation.aggregate('household',
                         possessions=['money'],
                         variables=['utility', 'rationing'])

    for good in firms:
        simulation.aggregate(good,
                             possessions=['money'],
                             variables=['price', 'nominal_demand', 'produced', 'profit', 'dead',
                                        'inventory', 'rationing'])

    for good in firms:
        simulation.build_agents(Firm, number=simulation_parameters['num_firms'], group_name=good)
    simulation.build_agents(Household, simulation_parameters['num_household'])

    simulation.run()
    simulation.graphs()

if __name__ == '__main__':
    main()
