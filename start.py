from __future__ import division
from firm import Firm
from household import Household
from netexport import NetExport
from investment import Investment
from government import Government
from abce import Simulation
from collections import OrderedDict
import os
from sam_to_functions import Sam
from pprint import pprint
import iotable

def main():
    sam = Sam('climate_square.sam.csv',
              inputs=['col', 'ele', 'gas', 'o_g', 'oil', 'eis', 'trn', 'roe', 'lab', 'cap'],
              outputs=['col', 'ele', 'gas', 'o_g', 'oil', 'eis', 'trn', 'roe'],
              output_tax='tax',
              consumption=['col', 'ele', 'gas', 'o_g', 'oil', 'eis', 'trn', 'roe'],
              consumers=['hoh', 'inv'])

    simulation_parameters = {'name': 'cce',
                             'random_seed': None,
                             'num_rounds': 250,
                             'trade_logging': 'group',
                             'num_household': 1,
                             'num_firms': 1,
                             'endowment_FFcap': sam.endowment('cap'),
                             'endowment_FFlab': sam.endowment('lab'),
                             'final_goods': sam.consumption,
                             'capital_types': ['cap', 'lab'],
                             'wage_stickiness': 0.2,
                             'price_stickiness': 0.2,
                             'network_weight_stickiness': 0.0,
                             'import_price_stickiness': 0.0,
                             'dividends_percent': 0.0,
                             'production_functions': sam.production_functions(),
                             'consumption_functions': sam.utility_function(),
                             'output_tax_shares': sam.output_tax_shares(),
                             'net_export': sam.endowment_vector('nx'),
                             'investment_share': sam.investment_share('hoh', 'inv'),
                             'initial_investment': sam.initial_investment('inv'),
                             'money': sam.money(),
                             'inputs': sam.inputs,
                             'nx_utility_function': sam.nx_utility_function(),
                             'balance_of_payment': sam.balance_of_payment('nx', 'inv')}

    firms = sam.outputs
    firms_and_household_netexport = firms + ['household', 'netexport']
    simulation = Simulation(simulation_parameters)
    action_list = [(firms_and_household_netexport + ['inv'], 'send_demand'),
                   (firms_and_household_netexport + ['inv'], 'selling'),
                   (firms_and_household_netexport + ['inv'], 'buying'),
                   (firms, 'taxes'),
                   ('government', 'taxes_to_household'),
                   (('household', 'netexport'), 'investing'),
                   (firms, 'production'),
                   (firms, 'dividends'),
                   (firms, 'change_weights'),
                   (firms + ['netexport'], 'stats'),
                   (firms_and_household_netexport, 'aggregate'),
                   (('household', 'netexport', 'inv'), 'consuming'),
                   ('government', 'aggregate')]
    simulation.add_action_list(action_list)

    simulation.declare_service('endowment_FFcap', 1, 'cap')
    simulation.declare_service('endowment_FFlab', 1, 'lab')

    simulation.aggregate('household',
                         possessions=['money', 'labor'],
                         variables=['investment', 'sales_earning', 'rationing'])

    simulation.aggregate('netexport',
                         possessions=['brd', 'mlk', 'money'],
                         variables=['sales'])

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
    simulation.build_agents(NetExport, 1)
    simulation.build_agents(Investment, 1, group_name='inv')
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
