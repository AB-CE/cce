from __future__ import division
from firm import Firm
from household import Household
from netexport import NetExport
from government import Government
from abce import Simulation, gui
from collections import OrderedDict, defaultdict
import os
from sam_to_functions import Sam
from pprint import pprint
import iotable
from scipy import optimize
from abce.abcegui import app

title = "Computational Complete Economy Model on Climate Gas Reduction"
text = """<b>In the short-run we are all dead: Non-Equilibrium Dynamics in a Computational General Equilibrium model.</b><br>
Studies of the economic impact and mitigation of climate change usually use computable general equilibrium models (CGE). Equilibrium models, as the name suggests, model the economy as in equilibrium, the transitions to the equilibrium are ignored. In the time spend outside equilibrium, the economy produces different quantities of goods and pollution as predicted by the equilibrium model. If the economy in this  time outside of the equilibrium produces more climate gasses the predictions are dangerously wrong.
We present in this paper a computational generalization of the Arrow-Debreu general equilibrium model, which is not in equilibrium during the transitions, but converges to the same equilibrium as a CGE model with the same data and assumption. We call this new class of models Computational Complete Economy models.
Computational Complete Economy models have other interesting applications for example in international trade, tax policy and macroeconomics.<br>

On the left hand side you can introduce a series of tax policies, the most important one is the tax on carbon. This tax is applied
to the carbon output of the three sectors that produce raw materials: coal, oil and gas.
"""

simulation_parameters = OrderedDict({'wage_stickiness': (0, 0.5, 1.0),
                                     'price_stickiness': (0, 0.5, 1.0),
                                     'network_weight_stickiness': (0, 0.5, 1.0),
                                     'carbon_tax': (0, 50.0, 80.0),
                                     'tax_change_time': 100,
                                     'rounds': 200})

simulation_parameters['trade_logging'] = 'group'

@gui(simulation_parameters, text=text, title=title)
def main(simulation_parameters):
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


    simulation_parameters.update({'name': 'cce',
                                  'random_seed': None,
                                  'num_household': 1,
                                  'num_firms': 1,
                                  'endowment_FFcap': sam.endowment('cap'),
                                  'endowment_FFlab': sam.endowment('lab'),
                                  'final_goods': sam.consumption,
                                  'capital_types': ['cap', 'lab'],
                                  'dividends_percent': 0.0,
                                  'production_functions': sam.production_functions(),
                                  'consumption_functions': sam.utility_function(),
                                  'output_tax_shares': sam.output_tax_shares(),
                                  'money': 2691.2641884030372,
                                  'inputs': sam.inputs,
                                  'outputs': sam.outputs,
                                  'balance_of_payment': sam.balance_of_payment('nx', 'inv'),
                                  'sam': sam,
                                  'carbon_prod': carbon_prod})


    firms = sam.outputs
    firms_and_household = firms + ['household']

    simulation = Simulation(rounds=simulation_parameters['rounds'], trade_logging='group', processes=1)
    action_list = [(firms, 'taxes_intervention'),
                   (firms_and_household, 'send_demand'),
                   (firms_and_household, 'selling'),
                   (firms_and_household, 'buying'),
                   ('household', 'money_to_nx'),
                   (firms, 'production'),
                   (firms, 'carbon_taxes'),
                   (firms, 'sales_tax'),
                   ('government', 'taxes_to_household'),
                   (firms, 'international_trade'),
                   (firms, 'invest'),
                   ('netexport', 'invest'),
                   (('household'), 'sales_accounting'),
                   (firms, 'dividends'),
                   (firms, 'change_weights'),
                   (firms, 'stats'),
                   (['col', 'oil', 'gas', 'household'], 'aggregate'),
                   (('household'), 'consuming')]

    simulation.add_action_list(action_list)

    simulation.declare_service('endowment_FFcap', 1, 'cap')
    simulation.declare_service('endowment_FFlab', 1, 'lab')
    """ every round for every endowment_FFcap the owner gets one good of lab
    similar for cap"""

    simulation.aggregate('household',
                         possessions=[],
                         variables=['welfare'])
    """ collect data """

    for good in ['col', 'oil', 'gas']:
        simulation.aggregate(good,
                             possessions=[],
                             variables=['price', 'produced', 'co2'])

    for good in firms:
        simulation.build_agents(Firm, number=simulation_parameters['num_firms'], group_name=good, parameters=simulation_parameters)
    simulation.build_agents(Household, 'household', simulation_parameters['num_household'], parameters=simulation_parameters)
    simulation.build_agents(NetExport, 'netexport', 1, parameters=simulation_parameters)
    simulation.build_agents(Government, 'government', 1, parameters=simulation_parameters)
    try:
        simulation.run()
    except Exception as e:
        print(e)
        # raise  # put raise for full traceback but no graphs in case of error
    iotable.to_iotable(simulation.path, [99, simulation_parameters['rounds'] - 1])
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
    return ((1.0 - prices) ** 2) * 100000

if __name__ == '__main__':
    main()
    #opt =  optimize.minimize_scalar(F, bracket=(2685, 2750), bounds=(2685, 2750), method='brent', options={'xtol': 0.000000000001})
    #print opt
