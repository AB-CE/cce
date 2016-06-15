from __future__ import division
from firm import Firm
from household import Household
from investment import Investment
from government import Government
from netexport import NetExport
from abce import Simulation
from collections import OrderedDict, defaultdict
import os
from sam_to_functions import Sam
from pprint import pprint
import iotable
from scipy import optimize



def main(money):
    sam = Sam('climate_square.sam.csv',
              inputs=['col', 'ele', 'gas', 'o_g', 'oil', 'eis', 'trn', 'roe', 'lab', 'cap'],
              outputs=['col', 'ele', 'gas', 'o_g', 'oil', 'eis', 'trn', 'roe'],
              output_tax='tax',
              consumption=['col', 'ele', 'gas', 'o_g', 'oil', 'eis', 'trn', 'roe'],
              consumers=['hoh'])
    """ reads the social accounting matrix and returns coefficients of a cobb-douglas model """
    carbon_prod = defaultdict(float)
    carbon_prod.update({'col': 2112 * 1e-4,
                        'oil': 2439.4 * 1e-4,
                        'gas': 1244.3 * 1e-4})
    """ this is the co2 output per sector at the base year """
    print 'carbon_prod'
    print carbon_prod


    simulation_parameters = {'name': 'cce',
                             'random_seed': None,
                             'num_rounds': 200,
                             'tax_change_time': 100,
                             'num_household': 1,
                             'num_firms': 1,
                             'endowment_FFcap': sam.endowment('cap'),
                             'endowment_FFlab': sam.endowment('lab'),
                             'final_goods': sam.consumption,
                             'capital_types': ['cap', 'lab'],
                             'wage_stickiness': 0.0,
                             'price_stickiness': 0.0,
                             'network_weight_stickiness': 0.0,
                             'import_price_stickiness': 0.0,
                             'dividends_percent': 0.0,
                             'production_functions': sam.production_functions(),
                             'consumption_functions': sam.utility_function(),
                             'output_tax_shares': sam.output_tax_shares(),
                             'money': money,
                             'inputs': sam.inputs,
                             'outputs': sam.outputs,
                             'balance_of_payment': sam.balance_of_payment('nx', 'inv'),
                             'sam': sam,
                             'carbon_prod': carbon_prod,
                             'carbon_tax': 50}


    firms = sam.outputs
    firms_and_household = firms + ['household']

    simulation = Simulation(rounds=simulation_parameters['num_rounds'], trade_logging='group', processes=1)
    action_list = [(firms, 'taxes_intervention'),
                   (firms_and_household, 'send_demand'),
                   (firms_and_household, 'selling'),
                   (firms_and_household, 'buying'),
                   (firms, 'production'),
                   (firms, 'carbon_taxes'),
                   (firms, 'sales_tax'),
                   ('government', 'taxes_to_household'),
                   (firms, 'international_trade'),
                   (firms, 'invest'),
                   ('netexport', 'international_trade'),
                   ('inv', 'investment'),
                   ('household', 'balance_balance_of_payment'),
                   (('household'), 'sales_accounting'),
                   (firms, 'dividends'),
                   (firms, 'change_weights'),
                   (firms, 'stats'),
                   (firms_and_household, 'aggregate'),
                   (('household'), 'consuming'),
                   ('government', 'aggregate')]

    simulation.add_action_list(action_list)

    simulation.declare_service('endowment_FFcap', 1, 'cap')
    simulation.declare_service('endowment_FFlab', 1, 'lab')
    """ every round for every endowment_FFcap the owner gets one good of lab
    similar for cap"""

    simulation.aggregate('household',
                         possessions=['money', 'labor'],
                         variables=['sales_earning', 'rationing'])
    """ collect data """

    simulation.aggregate('government',
                         variables=['money'])

    for good in firms:
        simulation.aggregate(good,
                             possessions=['money'],
                             variables=['price', 'nominal_demand', 'produced', 'profit', 'dead',
                                        'inventory', 'rationing'])

    for good in firms:
        simulation.build_agents(Firm, number=simulation_parameters['num_firms'], group_name=good, parameters=simulation_parameters)
    simulation.build_agents(Household, 'household', simulation_parameters['num_household'], parameters=simulation_parameters)
    simulation.build_agents(Investment, 'inv', 1, parameters=simulation_parameters)
    simulation.build_agents(Government, 'government', 1, parameters=simulation_parameters)
    simulation.build_agents(NetExport, 'netexport', 1, parameters=simulation_parameters)
    try:
        simulation.run()
    except Exception as e:
        print(e)
        # raise  # put raise for full traceback but no graphs in case of error
    iotable.to_iotable(simulation.path, [99, 199])
    mean_price = iotable.average_price(simulation.path, 99)
    print 'mean price', mean_price
    #simulation.graphs()
    return mean_price

def F(money):
    prices = main(float(money))
    print("****")
    print 'money', money
    print 'price lvl', prices
    print("****")
    return ((1.0 - prices) ** 2) * 1000000000000

if __name__ == '__main__':
    #main(2691.28480167)
    opt =  optimize.minimize_scalar(F, bracket=(2500, 2800), bounds=(2500, 2800), method='brent', options={'disp': True}, tol=0.000000000001)
    print opt
