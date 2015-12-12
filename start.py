from __future__ import division
from firm import Firm
from household import Household
from abce import Simulation
from collections import OrderedDict
import abceweb
import os


def main():
    simulation_parameters = {'name': 'cce',
                             'random_seed': None,
                             'num_rounds': 10,
                             'trade_logging': 'off',
                             'num_household': 1,
                             'num_firms': 2,
                             'final_goods': OrderedDict(enumerate(['brd', 'mlk'])),
                             'capital_types': OrderedDict(enumerate(['cap', 'lab'])),
                             'wage_stickiness': 0,
                             'price_stickiness': 0,
                             'dividends_percent': 0,
                             'network_weight_stickiness': 0}

    simulation = Simulation(simulation_parameters)
    action_list = [(('firm', 'household'), 'send_demand'),
                   (('firm', 'household'), 'selling'),
                   (('firm', 'household'), 'buying'),
                   ('firm', 'production'),
                   ('firm', 'dividends'),
                   ('household', 'consuming'),
                   ('firm', 'change_weights'),
                   ('firm', 'stats'),
                   (('household', 'firm'), 'aggregate'),
                   (('firm'), 'panel')]
    simulation.add_action_list(action_list)

    simulation.declare_service('endowment_FFcap', 1, 'cap')
    simulation.declare_service('endowment_FFlab', 1, 'lab')

    simulation.panel('firm', variables=['price', 'nominal_demand'])

    simulation.aggregate('firm',
                         possessions=['money'],
                         variables=['produced', 'profit', 'price', 'dead',
                                    'inventory', 'rationing'])
    simulation.aggregate('household',
                         possessions=['money'],
                         variables=['utility', 'rationing'])

    simulation.build_agents(Firm, simulation_parameters['num_firms'])
    simulation.build_agents(Household, simulation_parameters['num_household'])

    simulation.run()
    os.chdir('../..')
    abceweb.run(open=False)


if __name__ == '__main__':
    main()
