from __future__ import division
from firm import Firm
from household import Household
from government import Government
from abce import Simulation
from collections import OrderedDict
import os
from sam_to_functions import Sam
from pprint import pprint
import iotable


def main():
    sam = Sam('hirachical_taxes_nx.sam.csv',
              inputs=['cap', 'lab', 'tools'],
              outputs=['brd', 'mlk', 'tools'],
              output_tax='tax',
              consumption=['brd', 'mlk'])

    simulation_parameters = {'name': 'cce',
                             'random_seed': None,
                             'num_rounds': 60,
                             'trade_logging': 'group',
                             'num_household': 1,
                             'num_firms': 1,
                             'endowment_FFcap': sam.endowment('cap'),
                             'endowment_FFlab': sam.endowment('lab'),
                             'final_goods': sam.consumption,
                             'capital_types': ['cap', 'lab'],
                             'wage_stickiness': 0.0,
                             'price_stickiness': 0.0,
                             'network_weight_stickiness': 0.0,
                             'dividends_percent': 0.0,
                             'production_functions': sam.production_functions(),
                             'hh': sam.utility_function(),
                             'output_tax_shares': sam.output_tax_shares(),
                             'sam': sam}

    firms = sam.outputs
    firms_and_household = firms + ['household']
    simulation = Simulation(simulation_parameters)
    action_list = [
                   (firms_and_household, 'send_demand'),
                   (firms_and_household, 'selling'),
                   (firms_and_household, 'buying'),
                   (firms, 'taxes'),
                   ('government', 'taxes_to_household'),
                   (firms, 'production'),
                   (firms, 'international_trade'),
                   (firms, 'dividends'),
                   ('household', 'consuming'),
                   (firms, 'change_weights'),
                   (firms, 'stats'),
                   (firms_and_household, 'aggregate'),
                   ('government', 'aggregate')]
    simulation.add_action_list(action_list)

    simulation.declare_service('endowment_FFcap', 1, 'cap')
    simulation.declare_service('endowment_FFlab', 1, 'lab')

    simulation.aggregate('household',
                         possessions=['money'],
                         variables=[])

    simulation.aggregate('government',
                         variables=['money'])

    for good in firms:
        simulation.aggregate(good,
                             possessions=['money'],
                             variables=['price', 'nominal_demand', 'produced', 'profit', 'dead',
                                        'inventory', 'rationing'])

    for good in firms:
        simulation.build_agents(Firm, number=simulation_parameters['num_firms'], group_name=good)
    simulation.build_agents(Household, simulation_parameters['num_household'])
    simulation.build_agents(Government, 1)
    try:
        simulation.run()
    except Exception as e:
        print(e)
        raise

    iotable.to_iotable(simulation.path)
    simulation.graphs()

if __name__ == '__main__':
    main()
