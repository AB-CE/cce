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

text = """<b>In the Short Run We Are All Dead: Non-Equilibrium Dynamics in a Computational General Equilibrium Model.</b><br>
Studies of the economic impact and mitigation of climate change usually use computable general equilibrium models (CGE). Equilibrium models, as the name suggests, model the economy in equilibrium: the transitions to the equilibrium are ignored. In the time spend outside equilibrium, the economy produces different quantities of goods and pollution, as predicted by the equilibrium model. If the economy in this time outside of the equilibrium produces more climate gases, the predictions are dangerously wrong.
In this paper we present a computational generalization of the Arrow-Debreu general equilibrium model, which is not in equilibrium during the transitions, but converges to the same equilibrium as a CGE model with the same data and assumptions. We call this new class of models Computational Complete Economy models.
Computational Complete Economy models have other interesting applications, for example in international trade, tax policy, and macroeconomics.

On the left-hand side you can introduce a series of tax policies, the most important being the tax on carbon. This tax is applied to the carbon output of the three sectors that produce raw materials: coal mining, refined petroleum and gas works, and distribution.
"""

simulation_parameters = OrderedDict((('carbon_tax', (0, 0.0, 80.0)),
                                     ('tax_eis', (0.0, 0.012963293555430438 * 100, 100.0)),
                                     ('tax_oil', (0.0, 0.011268228015908086 * 100, 100.0)),
                                     ('tax_trn', (0.0, 0.026571679384158282 * 100, 100.0)),
                                     ('tax_gas', (0.0, 0.02444919587245515 * 100, 100.0)),
                                     ('tax_roe', (0.0, 0.02309537718734039 * 100, 100.0)),
                                     ('tax_ele', (0.0, 0.10978500776587917 * 100, 100.0)),
                                     ('tax_o_g', (0.0, 0.023756906077348067 * 100, 100.0)),
                                     ('tax_col', (0.0, 0.08872377622377624 * 100, 100.0)),
                                     ('tax_change_time', 100),
                                     ('rounds', 200)))


names = {'carbon_tax': 'Tax per ton of carbon in US dollars',
         'tax_eis': 'Tax on energy intensive industry sectors in percent',
         'tax_oil': 'Tax on refined petroleum in percent of revenue',
         'tax_trn': 'Tax on transportation in percent of revenue',
         'tax_gas': 'Tax on gas works and distribution oil in percent of revenue',
         'tax_roe': 'Tax on the rest of the economy in percent of revenue',
         'tax_ele': 'Tax on electric power in percent of revenue',
         'tax_o_g': 'Tax on crude oil and gas in percent of revenue',
         'tax_col': 'Tax on coal mining in percent of revenue',
         'tax_change_time': 'Time of policy change',
         'rounds': 'Simulation length'}

simulation_parameters['trade_logging'] = 'group'

@gui(simulation_parameters, text=text, title=title, names=names, truncate_initial_rounds=50)
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
    print sam.output_tax_shares()


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
                                  'carbon_prod': carbon_prod,
                                  'wage_stickiness': 0.5,
                                  'price_stickiness': 0.5,
                                  'network_weight_stickiness': 0.5})


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
                   (['col', 'ele', 'gas', 'o_g', 'oil', 'eis', 'trn', 'roe', 'household'], 'aggregate'),
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

    for good in ['col', 'gas', 'oil']:
        simulation.aggregate(good,
                             possessions=[],
                             variables=['price', 'produced', 'co2'])

    for good in ['ele', 'o_g', 'eis', 'trn', 'roe']:
        simulation.aggregate(good,
                             possessions=[],
                             variables=['price', 'produced'])

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
