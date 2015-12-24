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

def read_sam(name):
    inputs = ['cap', 'lab', 'tools']
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
                if cellindex not in  ['index', 'sum']:
                    entries[rowindex][cellindex] = float_or_zero(cell)

    # sums the columns
    column_sum = {}
    for col in fields:
        column_sum[col] = sum(item[col] for item in entries.values())

    # the utility functions exponents as values in a dict
    utility_function = {}
    for input in fields:
        utility_function[input] = entries[input]['hoh'] / column_sum['hoh']

    print utility_function

    betas = defaultdict(dict)
    b = {}
    production_functions = {}

    # the production function
    for firm in ['brd', 'mlk', 'tools']:
        for input in inputs:
            betas[firm][input] = entries[input][firm] / column_sum[firm]

        Z = column_sum[firm]
        b[firm] = Z / np.prod([entries[input][firm] ** betas[firm][input] for input in inputs])

        production_functions[firm] = (b[firm], betas[firm])

    pprint(dict(production_functions))
    return (utility_function, production_functions)

