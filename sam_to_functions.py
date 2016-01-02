from __future__ import division
import csv
from pprint import pprint
from collections import defaultdict
from copy import copy
import numpy as np

def float_or_zero(value):
    try:
        return float(value)
    except ValueError:
        return 0.0

class Sam():
    def __init__(self, name, inputs, outputs, output_tax, consumption, consumers):
        self.inputs, self.outputs, self.output_tax = inputs, outputs, output_tax
        self.consumption, self.consumers = consumption, consumers

        # loads the table as dict of dict
        entries = defaultdict(dict)
        with open(name) as csvfile:
            reader = csv.DictReader(csvfile)
            fields = copy(reader.fieldnames)
            fields.remove('index')
            fields.remove('sum')
            for row in reader:
                rowindex = row['index']
                if rowindex == 'sum':
                    break
                for cellindex, cell in row.iteritems():
                    if cellindex not in ['index', 'sum']:
                        entries[rowindex][cellindex] = float_or_zero(cell)

    # sums the columns
        column_sum = {}
        for col in fields:
            column_sum[col] = sum(item[col] for item in entries.values())

        self.entries, self.column_sum = dict(entries), column_sum

    def utility_function(self):
        """ the utility functions exponents as values in a dict """
        entries, column_sum = self.entries, self.column_sum
        utility_functions = {}
        for consumer in self.consumers:
            alphas = {}
            Z = sum([entries[input][consumer] for input in self.consumption])
            for input in self.consumption:
                alphas[input] = entries[input][consumer] / Z
            utility_functions[consumer] = alphas

        return utility_functions

    def production_functions(self):
        entries, column_sum = self.entries, self.column_sum
        output_tax_shares = self.output_tax_shares()
        betas = defaultdict(dict)
        b = {}
        production_functions = {}

        for firm in self.outputs:
            Z = sum([(1 + output_tax_shares[firm]) * entries[input][firm] for input in self.inputs])

            for input in self.inputs:
                betas[firm][input] = (1 + output_tax_shares[firm]) * entries[input][firm] / Z

            b[firm] = (column_sum[firm]
                       / np.prod([entries[input][firm] ** betas[firm][input]
                                  for input in self.inputs]))

            production_functions[firm] = (b[firm], dict(betas[firm]))

        return production_functions

    def output_tax_shares(self):
        entries, column_sum, output_tax = self.entries, self.column_sum, self.output_tax
        output_tax_shares = {}
        for firm in self.outputs:
            output_tax_shares[firm] = (entries[output_tax][firm]
                                       / sum([entries[input][firm]
                                              for input in self.inputs]))
        return output_tax_shares

    def endowment(self, name):
        assert name in self.inputs
        return self.column_sum[name]

    def endowment_vector(self, column):
        return {row_name: self.entries[row_name][column] for row_name in self.entries}




